from functools import wraps
from flask import session, request, render_template, redirect, url_for

def error(message, code=400):
    """Render a page indicating an error"""
    return render_template("error.html.j2", top=code, bottom=message), code

def login_required(f):
    """
    Decorate routess to require login_required

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'username' in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
