from flask import Flask, request, redirect, render_template
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

from helpers import login_required, error

# Configure the application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = "no-cache, no-store, must-revalidate"
    response.headers['Expires'] = 0
    response.headers['Pragma'] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    return render_template("index.html.j2")

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Render the login page or process the login request"""

    if request.method == "GET":
        return render_template("login.html.j2")
    elif request.method == "POST":
        return render_template("index.html.j2")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return error(e.name, e.code)

for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
