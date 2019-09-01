from flask import Flask, flash, request, redirect, render_template, session, url_for
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp

from helpers import login_required, error
from modelconnector import get_user, changeUserPassword

import os

# Configure the application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True

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
key = os.urandom(16)
print(key)
app.secret_key = key


@app.route("/")
@login_required
def index():
    return render_template("index.html.j2")

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Show user the login form or process the login request by authenticating user"""
    # Reroute if user already logged in
    if "username" in  session:
        print('username in session')
        print(session)
        return redirect(url_for('index'))

    # Display the login form to the user
    if request.method == "GET":
        return render_template("login.html.j2")
    # User submitted a login request
    elif request.method == "POST":
        # Ensure submission of credentials
        # Indicate failure to do so
        username = request.form.get("username")
        if not username:
            flash("Must provide username!", "warning")
            return redirect(url_for('login'))
        password = request.form.get("password")
        if not password:
            flash("Must provide the password!", "warning")
            return redirect(url_for('login'))

        user = get_user(username)
        if not user:
            flash("Username does not exist!", "danger")
            return redirect(url_for('login'))
        else:
            if not check_password_hash(user['password'], password):
                flash("Incorrect password entered!", "danger")
                return redirect(url_for('login'))
            else:
                flash("Welcome " + user['fullname'] + "!", "success")
                session['username'] = user['username']
                session['fullname'] = user['fullname']
                session['type'] = user['type']
                return redirect(url_for('index'))

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    """Clear the session"""
    session.clear()
    flash("You have logged out of the system", "info")
    return redirect(url_for('login'))

@app.route('/changePassword', methods=['POST'])
@login_required
def changePassword():
    """Change the password of the current user"""

    # Get the passwords from the form submission
    current = request.form.get("current")
    if not current:
        flash("Please enter current password!", "warning")
        return redirect(url_for("index"))
    new = request.form.get("new")
    if not new:
        flash("Please enter new password!", "warning")
        return redirect(url_for("index"))
    confirm = request.form.get("confirm")
    if not confirm:
        flash("Please confirm the new password!", "warning")
        return redirect(url_for("index"))

    # Check the inputs
    # Verify that new and confirmation are same
    if new != confirm:
        flash("Passwords are not same!", "warning")
        return redirect(url_for("index"))

    # Verify correct current password
    user = get_user(session['username'])
    if not check_password_hash(user['password'], current):
        flash("Incorrect current password entered!", "danger")
        return redirect(url_for("index"))

    # Change the password in the database
    changeUserPassword(session['username'], generate_password_hash(confirm))
    flash("Password successfully changed!", "success")
    return redirect(url_for("index"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """DevFeature: Registration of a new user"""
    if request.method == "GET":
        return render_template("register.html.j2")
    elif request.method == "POST":
        # Get parameters from form submission
        username = request.form.get("username")
        if not username:
            flash("Enter username", "warning")
            return redirect(url_for("register"))

        password = request.form.get("password")
        if not password:
            flash("Enter password", "warning")
            return redirect(url_for("register"))

        confirm = request.form.get("confirm")
        if not confirm:
            flash("Enter confirmation", "warning")
            return redirect(url_for("register"))

        fullname = request.form.get("fullname")
        if not fullname:
            flash("Enter fullname", "warning")
            return redirect(url_for("register"))

        type = request.form.get("type")
        if not type:
            flash("Select account type", "warning")
            return redirect(url_for("register"))

        # Verify parameters
        if password != confirm:
            flash("Passwords do not match", "warning")
            return redirect(url_for("register"))

        user = get_user(username)
        if user:
            flash("Pick another username", "danger")
            return redirect(url_for("register"))

        flash("Registration request complete and valid", "info")
        return redirect(url_for("register"))




def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return error(e.name, e.code)

for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
