import os

#import sqlite3
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import json

# Personal functions and methods
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///taskfloat.db")

@app.route("/", methods=["GET", "POST"])
#@login_required #login not required for some pages.
def index():
    """Show main page"""
    if request.method == "GET":
        #if session.get("user_id") is None:
        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Get all usernames for checking input against
    usernames = [item['username'] for item in db.execute("SELECT username FROM users")]

    # User is submitting via post
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("username required", 403)
        # Ensure that a first password was provided
        elif not request.form.get("password"):
            return apology("password required", 403)
        # Ensure a confirmation password was provided
        elif not request.form.get("confirmation"):
            return apology("password confirmation", 403)
        # Ensure that the registration passowrd and confirmation passowrd match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 403)
        # Ensure username doesnt already exist
        elif request.form.get("username") in usernames:
            return apology("username already taken", 403)
        # Ensure email is entered
        # TODO: need to make sure to check this is a real email
        elif request.form.get("user_email") in usernames:
            return apology("email required", 403)
        # Ensure user agrees to the terms and conditions
        elif not request.form.get("user_confirmation"):
            return apology("agreement to terms and conditions required", 403)

        # Enter the username and password into the database
        else:
            # Variables to collect user name and password for code readability
            username_input = request.form.get("username")
            print(f"HERE IS THE USERNAME INPUT!!!!!!{username_input}")
            password = request.form.get("password")
            password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            # Add variable inputs into db to create user
            db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                        username = username_input,
                        hash = password_hash)

            # Create new account info table for user
            first_name = request.form.get("first_name") if True else "no entry"
            last_name = request.form.get("last_name")  if True else "no entry"
            user_email = request.form.get("user_email")
            user_company = request.form.get("user_company") if True else "no entry"

            # Add user account info to accounts db and join this with the user
            db.execute("INSERT INTO accounts (first_name, last_name, email, company_name)\
                        VALUES (:first_name, :last_name, :user_email, :user_company);",
                        first_name = first_name,
                        last_name = last_name,
                        user_email = user_email,
                        user_company = user_company)
            # Add user id and account id to user_accounts to link accounts and users
            account_id = db.execute("SELECT account_id FROM accounts ORDER BY account_id DESC limit 1;")

            db.execute("INSERT INTO user_accounts (user_id, account_id)\
                        VALUES (:user_id, :account_id);",
                        user_id = session.get("user_id"),
                        account_id = account_id[0]['account_id'])

            return redirect("/login")
    # User got here through GET or redirect
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as in by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database to ensure username exists and passowrd hashes match
        username = request.form.get("username")
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if len(rows) != 1 or not check_password_hash(rows[0]['hash'], request.form.get("password")):
            bottom = "invalid username and or password"
            num = 403
            return apology(bottom, num)

        # Remember which user has logged in
        session["user_id"] = rows[0]['id']

        # Redirect user to their page
        return redirect("/tasks")

    # User reached route via GET (as in by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/login")

@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    """task list"""
    if request.method == "POST":
        column_names = ["task_id", "start_time", "end_time", "job_number", "task", "importance", "deadline", "complete"]
        # Get data from incoming task
        update_type = request.json['task_post_type']

        #TODO: need to change this - i feel like it poses a big overloading threat...
        # If the task type is update
        if update_type == "task_update":
            task_id = request.json['task_id']
            task_data = request.json['data']
            col_heading = column_names[int(request.json['col_heading'])]
            # Update the database with incoming data
            db.execute("UPDATE tasks SET :col_heading = :task_data WHERE task_id = :task_id;",
                        col_heading = col_heading,
                        task_data = task_data,
                        task_id = task_id,
                        )
            return render_template('tasks.html')


        elif update_type == "add_new_row":
            # Add new task to db
            db.execute("INSERT INTO tasks (task, job_number )\
                        VALUES (:task, :job_number);",
                        task = "new_task",
                        job_number = "000000-00")
            # Add new join table entry to connect user with their new task
            last_row_id = db.execute('SELECT last_insert_rowid()')
            db.execute("INSERT INTO user_tasks (user_id, task_id)\
                        VALUES (:user_id, :task_id);",
                        user_id = session.get("user_id"),
                        task_id = int(last_row_id[0]['last_insert_rowid()']))
            return render_template('tasks.html')

        elif update_type == "task_complete":
            task_id = request.json['task_id']
            task_data = request.json['data']
            col_heading = column_names[int(request.json['col_heading'])]
            # Update the database with incoming data
            db.execute("UPDATE tasks SET :col_heading = :task_data WHERE task_id = :task_id;",
                        col_heading = col_heading,
                        task_data = task_data,
                        task_id = task_id,
                        )
            return render_template('tasks.html')


    else:
        # Get all the incomplete tasks in the db
        tasks = db.execute("SELECT \
                            tasks.task_id, \
                            tasks.start_time, \
                            tasks.end_time, \
                            tasks.job_number, \
                            tasks.task, \
                            tasks.importance, \
                            tasks.complete, \
                            tasks.deadline \
                            FROM users \
                            JOIN user_tasks ON users.id = user_tasks.user_id \
                            JOIN tasks ON tasks.task_id = user_tasks.task_id \
                            WHERE users.id == :user_id AND tasks.complete = :false;",
                            user_id = session.get('user_id'),
                            false = 0)
        # Render the page
        return render_template("tasks.html", tasks=tasks)
    #if the user is posting need to get the name of each item thats changing.
    # then we need to check it for accuracy somehow...
    # if it passes the test it gets to go back into the db.

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """account info and history"""
    ###### TODO: Make super duper join table so that we link all the accounts
    ######## that have that user id... i guess?
    if request.method == "GET":
        info = db.execute("SELECT * FROM accounts WHERE account_id == :user_id;",
                            user_id = session.get('user_id'))
        print(f"HERE IS THE INFO!!!! ---{info}")
        return render_template("account_info.html", info=info)



@app.route("/complete", methods=["GET"])
@login_required
def complete():
    """task list"""
    if request.method == "GET":
        tasks = db.execute("SELECT \
                            tasks.start_time, \
                            tasks.end_time, \
                            tasks.job_number, \
                            tasks.task, \
                            tasks.importance, \
                            tasks.complete, \
                            tasks.deadline \
                            FROM users \
                            JOIN user_tasks ON users.id = user_tasks.user_id \
                            JOIN tasks ON tasks.task_id = user_tasks.task_id \
                            WHERE users.id == :user_id AND tasks.complete = :true;",
                            user_id = session.get('user_id'),
                            true = 1)

        #print(f"HERE ARE THE TASKS!!!! ---{tasks}")

        return render_template("complete.html", tasks=tasks)
    #if the user is posting need to get the name of each item thats changing.
    # then we need to check it for accuracy somehow...
    # if it passes the test it gets to go back into the db.


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

# Custom - checks if incoming number is cash float
def is_cash(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
