import os

from datetime import datetime
from pytz import timezone

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd


def month_convert(month):
    import calendar
    month = calendar.month_name[month]
    return month


# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Display Sales Journal"""
    try:
        date = datetime.now(timezone('Asia/Manila')).strftime('%Y-%m-%d')
        sales = db.execute(
            "SELECT time, SUM(quantity) as quantity, SUM(total) as total FROM sales WHERE id = ? AND date = ? GROUP BY time ORDER BY time DESC", session["user_id"], date)
        for sale in sales:
            sale['total'] = usd(sale['total'])
        total = usd(db.execute("SELECT SUM(total) as total FROM sales WHERE id = ? AND date = ?", session["user_id"], date)[0]['total'])
        return render_template("index.html", date=date, sales=sales, total=total)
    except:
        return render_template("index.html", total=usd(0))


@app.route("/transaction", methods=["POST"])
@login_required
def transaction():
    """Display specific transaction"""
    show = request.form.get("show")
    date = datetime.now(timezone('Asia/Manila')).strftime('%Y-%m-%d')
    transacts = db.execute("SELECT * FROM sales WHERE id = ? AND date = ? AND time = ?", session["user_id"], date, show)
    for transact in transacts:
        transact['total'] = usd(transact['total'])
    total = usd(db.execute("SELECT SUM(total) as total FROM sales WHERE id = ? AND date = ? AND time = ?", session["user_id"], date, show)[0]['total'])
    return render_template("transaction.html", transacts=transacts, total=total)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Successfully Logged In!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if not username or len(rows) == 1:
            return apology("Username is not available")
        elif not password:
            return apology("Missing password")
        elif password != confirmation:
            return apology("Password do not match")

        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?,?)", username, hash)

        rows = db.execute("SELECT * from users WHERE username = ?", username)
        session["user_id"] = rows[0]['id']
        flash("Registered!")
        return redirect("/stock")

    else:
        return render_template("register.html")


@app.route("/sale", methods=["GET", "POST"])
@login_required
def sale():
    """Add sales"""
    q = request.args.get("q")
    if q:
        items = db.execute("SELECT * FROM stocks WHERE id = ? AND itemname LIKE ? ORDER BY itemname", session["user_id"], "%" + q + "%")
    else:
        items = db.execute("SELECT itemname FROM stocks WHERE id = ? ORDER BY itemname", session["user_id"])

    if request.method == "POST":
        now = datetime.now(timezone('Asia/Manila'))
        date = now.strftime('%Y-%m-%d')
        time = now.strftime('%H:%M:%S')

        item = request.form.get("item")
        quantity = request.form.get("quantity")

        if not item or not quantity:
            return redirect("/sale")

        row1 = db.execute("SELECT quantity, sellingprice, costprice, profit FROM stocks WHERE id = ? AND itemname = ?", session["user_id"], item)
        if int(quantity) > row1[0]['quantity']:
            return apology("Insufficient stock!")

        total = 0
        profit = 0

        row2 = db.execute("SELECT * FROM temp WHERE id = ? AND itemname = ?", session["user_id"], item)
        if len(row2) == 1:
            quantities = (int(quantity) + row2[0]['quantity'])
            if quantities > row1[0]['quantity']:
                return apology("Insufficient stock!")
            else:
                total = row1[0]['sellingprice'] * quantities
                profit = (row1[0]['profit']) * quantities
                db.execute("UPDATE temp SET quantity = ?, total = ?, profit = ? WHERE id = ? AND itemname = ?", quantities, total, profit, session["user_id"], item)
                db.execute("UPDATE temp SET date = ?, time = ? WHERE id = ?", date, time, session["user_id"])
        else:
            total = row1[0]['sellingprice'] * int(quantity)
            profit = (row1[0]['profit']) * int(quantity)
            db.execute("INSERT INTO temp (id, date, time, itemname, quantity, sellingprice, total, profit) VALUES (?,?,?,?,?,?,?,?)",
                   session["user_id"], date, time, item, int(quantity), row1[0]['sellingprice'], total, profit)
            db.execute("UPDATE temp SET date = ?, time = ? WHERE id = ?", date, time, session["user_id"])

        sales = db.execute("SELECT * FROM temp WHERE id = ?", session["user_id"])
        for sale in sales:
            sale['sellingprice'] = usd(sale['sellingprice'])
            sale['total'] = usd(sale['total'])
        total = usd(db.execute("SELECT SUM(total) as total FROM temp WHERE id = ?", session["user_id"])[0]['total'])
        return render_template("sale.html", items=items, sales=sales, total=total)

    else:
        sales = db.execute("SELECT * FROM temp WHERE id = ?", session["user_id"])
        for sale in sales:
            sale['sellingprice'] = usd(sale['sellingprice'])
            sale['total'] = usd(sale['total'])
        try:
            total = usd(db.execute("SELECT SUM(total) as total FROM temp WHERE id = ?", session["user_id"])[0]['total'])
            return render_template("sale.html", items=items, sales=sales, total=total)
        except:
            return render_template("sale.html", items=items, sales=sales, total=usd(0))


@app.route("/insert", methods=["POST"])
@login_required
def insert():
    """Insert transactions into sales table"""
    x = db.execute("SELECT EXISTS (SELECT 1 FROM temp  WHERE id = ?) as exist", session["user_id"])
    if x[0]['exist']:
        db.execute("INSERT INTO sales (id, date, time, itemname, quantity, sellingprice, total, profit) SELECT id, date, time, itemname, quantity, sellingprice, total, profit FROM temp")
        rows = db.execute("SELECT itemname, quantity FROM temp WHERE id = ?", session["user_id"])
        for row in rows:
            db.execute("UPDATE stocks SET quantity =  quantity - ? WHERE id = ? AND itemname = ?", row['quantity'], session["user_id"], row['itemname'])
        db.execute("DELETE FROM temp WHERE id = ?", session["user_id"])
        flash("Purchase Complete!")
    return redirect("/sale")


@app.route("/cancel", methods=["POST"])
@login_required
def cancel():
    """Cancel transactions"""
    db.execute("DELETE FROM temp WHERE id = ?", session["user_id"])
    return redirect("/sale")


@app.route("/remove_item", methods=["POST"])
@login_required
def remove_item():
    """Remove transaction item"""
    item_name = request.form.get("item_name")
    db.execute("DELETE FROM temp WHERE id = ? AND itemname = ?", session["user_id"], item_name)
    return redirect("/sale")


@app.route("/stock", methods=["GET", "POST"])
@login_required
def stock():
    """Display stocks of items"""
    if request.method == "POST":
        item_name = request.form.get("item_name")
        item = db.execute("SELECT * FROM stocks WHERE id = ? AND itemname = ?", session["user_id"], item_name)
        for x in item:
            x['sellingprice'] = usd(x['sellingprice'])
            x['costprice'] = usd(x['costprice'])
        return render_template("update.html", item=item, item_name=item_name)
    else:
        q = request.args.get("q")
        if q:
            stocks = db.execute("SELECT * FROM stocks WHERE id = ? AND itemname LIKE ? ORDER BY itemname ASC", session["user_id"], "%" + q + "%")
        else:
            stocks = db.execute("SELECT * FROM stocks WHERE id = ? ORDER BY itemname ASC", session["user_id"])
        for stock in stocks:
            stock['costprice'] = usd(stock['costprice'])
            stock['sellingprice'] = usd(stock['sellingprice'])
        return render_template("stock.html", stocks=stocks)


@app.route("/add_item", methods=["GET", "POST"])
@login_required
def add_item():
    """Add item to stocks table"""
    if request.method == "POST":
        item_name = request.form.get("item_name")
        quantity = request.form.get("quantity")
        sell_price = request.form.get("sell_price")
        cost_price = request.form.get("cost_price")
        rows = db.execute("SELECT * FROM stocks WHERE id = ? AND itemname = ?", session["user_id"], item_name)

        if not item_name or not quantity or not sell_price or not cost_price:
            return apology("Missing fields")
        elif len(rows) == 1:
            return apology("Item already exist!")

        db.execute("INSERT INTO stocks (id, itemname, quantity, sellingprice, costprice, profit) VALUES (?,?,?,?,?,?)",
                   session["user_id"], item_name, quantity, sell_price, cost_price, int(sell_price) - int(cost_price))
        flash("Item Added!")
        return redirect("/stock")
    else:
        return render_template("add_item.html")


@app.route("/update", methods=["POST"])
@login_required
def update():
    """Update stocks list"""
    item_name = request.form.get("item")
    quantity = request.form.get("quantity")
    sell_price = request.form.get("sell_price")
    cost_price = request.form.get("cost_price")

    if not item_name or not quantity or not sell_price or not cost_price:
        return apology("Missing fields")

    db.execute("UPDATE stocks SET quantity = ?, sellingprice = ?, costprice = ? WHERE id = ? AND itemname = ?",
               int(quantity), int(sell_price), int(cost_price), session["user_id"], item_name)
    flash("Item Updated!")
    return redirect("/stock")


@app.route("/delete_item", methods=["POST"])
@login_required
def delete_item():
    """Delete item from stocks"""
    item_name = request.form.get("item_name")
    db.execute("DELETE FROM stocks WHERE id = ? AND itemname = ?", session["user_id"], item_name)
    flash("Item Deleted!")
    return redirect("/stock")


@app.route("/history")
@login_required
def history():
    """Display history of transactions"""
    try:
        dates = db.execute(
            "SELECT date, SUM(quantity) as quantity, SUM(total) as total, SUM(profit) as profit FROM sales  WHERE id = ? GROUP BY date ORDER BY date DESC", session["user_id"])
        for date in dates:
            date['total'] = usd(date['total'])
            date['profit'] = usd(date['profit'])
        total = usd(db.execute("SELECT SUM(total) as total FROM sales WHERE id = ?", session["user_id"])[0]['total'])
        profit = usd(db.execute("SELECT SUM(profit) as profit FROM sales WHERE id = ?", session["user_id"])[0]['profit'])
        return render_template("history.html", dates=dates, total=total, profit=profit)
    except:
        return render_template("history.html", total=usd(0), profit=usd(0))


@app.route("/day_transaction", methods=["POST"])
@login_required
def day_transaction():
    """Display transactions on specific day"""
    show = request.form.get("show")
    transacts = db.execute("SELECT * FROM sales WHERE id = ? AND date = ? ORDER BY time DESC", session["user_id"], show)
    for transact in transacts:
        transact['total'] = usd(transact['total'])
    total = usd(db.execute("SELECT SUM(total) as total FROM sales WHERE id = ? AND date = ?", session["user_id"], show)[0]['total'])
    return render_template("transaction.html", transacts=transacts, total=total)


@app.route("/dashboard")
@login_required
def dashboard():
    months = [("January", 1), ("February", 2), ("March", 3), ("April", 4), ("May", 5), ("June", 6), ("July", 7), ("August", 8), ("September", 9), ("October", 10), ("November", 11), ("December", 12)]
    years = db.execute("SELECT strftime('%Y', date) AS year FROM sales WHERE id = ? GROUP by year", session["user_id"])

    date = datetime.now(timezone('Asia/Manila'))
    thismonth = date.month
    thisyear = date.year

    lookMonth = request.args.get("month")
    lookYear = request.args.get("year")

    if lookMonth:
        thismonth = int(lookMonth)
    if lookYear:
        thisyear = lookYear

    data1 = db.execute(
        "SELECT CAST(strftime('%m', date) AS INTEGER) as month, date, SUM(total) as total, SUM(profit) as profit FROM sales WHERE id = ? AND CAST(strftime('%Y', date) AS INTEGER) = ? AND month = ? GROUP BY date", session["user_id"], thisyear, thismonth)
    labels = [row['date'] for row in data1]
    values = [row['total'] for row in data1]
    profit = [row['profit'] for row in data1]

    data2 = db.execute(
        "SELECT CAST(strftime('%m', date) AS INTEGER) as month, SUM(total) as total FROM sales WHERE id = ? AND CAST(strftime('%Y', date) AS INTEGER) = ? GROUP BY month", session["user_id"], thisyear)
    month = [month_convert(row['month']) for row in data2]
    total = [row['total'] for row in data2]
    return render_template("dashboard.html", labels=labels, values=values, profit=profit, month=month, total=total, thismonth=month_convert(thismonth), thisyear=thisyear, months=months, years=years)


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Change user password"""

    if request.method == "POST":
        previous = request.form.get("previous")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        rows = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])

        if not previous or not new_password or not confirmation:
            return apology("Missing password")
        elif not check_password_hash(rows[0]["hash"], previous):
            return apology("Incorrect password")
        elif new_password != confirmation:
            return apology("Password don't match")

        db.execute("UPDATE users SET hash = ?  WHERE id = ?", generate_password_hash(new_password), session["user_id"])
        flash("Password Updated!")
        return redirect("/")

    else:
        return render_template("password.html")
