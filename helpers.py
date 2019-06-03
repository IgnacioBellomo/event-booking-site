import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(msg, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(msg)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("userID") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def passwordValid(password):
    hasLetter = False
    hasNumber = False
    longEnough = False

    if len(password) > 7:
        longEnough = True

    for i in range(len(password)):
        letter = password[i]
        if letter.isalpha():
            hasLetter = True
        elif letter.isdigit():
            hasNumber = True
    return hasLetter and hasNumber and longEnough