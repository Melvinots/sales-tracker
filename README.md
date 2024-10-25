# CS50 Sales Tracker
#### Video Demo:  https://youtu.be/Wwle64ZoPvU
#### Description:

    CS50 Sales Tracker is a web-based application designed to monitor the sales of your stores. The creation of this project was influenced by the need to simplify the process of tracking sales and profits in our store, and it aims to provide a user-friendly platform that allows for efficient monitoring and management of store sales and profits. This project was inspired by the previous problem set "Finance" in the CS50 course and I've expanded upon the concepts learned there to create a comprehensive and user-friendly tool. This project was built using HTML, CSS, JavaScript, Bootstrap, and Chart.js for the frontend, and Flask, Python, and SQLite3 for the backend.
    In this project, I utilized several files to build the application. It includes the 'app.py' for the main application logic, 'helpers.py' for auxiliary functions, and 'project.db' for the database where all the data is stored and managed. The project also encompasses a variety of HTML files, namely 'layout.html', 'index.html', 'sale.html', 'stock.html', 'history.html', 'dashboard.html', 'transaction.html', 'add_item.html', 'update.html', 'login.html', 'register.html', 'password.html', and 'apology.html'. This project also includes several tables in the database,  namely 'users', 'sales', 'temp', and 'stocks'. Each of these files contributes to different functionalities and views within the application.
    The 'app.py' is structured around several key routes. The home page of the application, accessed through the / route, displays the sales for the current day. The /transaction route allows users to view specific transactions made on the current day. The /sale route leads to a page where users can record a sale. The /insert route is used to mark the completion of item purchases and record them in the database. If needed, the recorded purchase of items can be cancelled using the /cancel route or specific items can be removed from the recorded purchase via the /remove_item route. The /stock route directs users to a page where they can view the current stock. New items can be added to the stock through the /add_item route, and the details of an item or the item itself can be updated or deleted via the /update and /delete_item routes, respectively. The /history route leads to a page where users can view the sales history, and the /day_transaction route allows users to view transactions made on a selected day. The /dashboard route leads to a page that provides an overview of sales and profit. For user management, the /login route leads to the login page for users, the /logout route logs out the user, the /register route leads to the registration page for new users, and the /password route allows users to change their password. Lastly, the /apology route leads to a page that displays when an error occurs.
    During the development of my project, I encountered several challenges that led to significant learning experiences. One of the main challenges was managing data and creating tables for the database. I was wondering If I should reference a column of a table from another table. However, I chose not to because my program involves deleting rows from the table. If a row is referenced elsewhere, it cannot be deleted.  So, the only column that I have referenced to other tables is the user’s ID. I was also contemplating how to make the ordering of items more efficient, so that I wouldn’t have to record it immediately due to the possibility of cancellation. Therefore, I decided to create another table, ‘temp’, similar to ‘sales’. This way, before recording it in the ‘sales’ table, it will first be recorded in the ‘temp’ table, where the user can still add or delete transactions, which will be deleted once the purchased items are finalized. This challenge taught me the importance of good management and understanding of how data is stored in databases.
    Another challenge I faced was integrating the Chart.js library to visually represent sales and profits on the dashboard page. I had to be particularly mindful of the format of the variables I was passing in, such as the data I wanted to display on the dashboard. If not done correctly, it often resulted in errors or failed to display anything. Learning to work with this technology was a challenge, especially since it was my first time using it. However, this challenge deepened my understanding of Chart.js and how it can be integrated with other technologies to build web applications.
    This project, called CS50 Sales Tracker, is primarily designed for small to medium-sized store owners, managers, and employees who need a simple yet effective tool to monitor and manage their sales and profits.
