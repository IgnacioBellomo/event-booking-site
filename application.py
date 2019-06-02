import os

from cs50 import SQL
from flask import Flask, flash, json, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from datetime import datetime
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Database queries

# User
newUser = "INSERT INTO users ( userID, email, pwdHash, fName, lName, zip, pic ) VALUES ( NULL, :email, :pwdHash, :fName, :lName, :zip, :pic )"
newTransaction = "INSERT INTO transactions (tranID, userID, eventID, tickets, time) VALUES ( NULL, :userID, :eventID, :tickets, NULL )"
userLogin = "SELECT * FROM users WHERE email = :email"
ticketSale = "UPDATE events SET tickets = :tickets WHERE eventID = :eventID"
allTicketQry = "SELECT eventID, SUM(tickets) FROM transactions GROUP BY eventID HAVING userID = :userID"
eventTicketQry = "SELECT SUM(tickets) FROM transactions GROUP BY eventID HAVING userID = :userID AND eventID = :eventID"

# Both
venueQry = "SELECT * FROM venues WHERE venueID = :venueID"
eventQry = "SELECT * FROM events WHERE eventID = :eventID"
allEventQry = "SELECT * FROM events"
allVenueQry = "SELECT * FROM venues"

# Admin
editEvent = "UPDATE events SET name = :name, tickets = :tickets, type = :type, description = :description, venueID = :venueID WHERE eventID = :eventID"
newVenue = "INSERT INTO venues (venueID, name, capacity, address1, address2, city, state, zip, adminID) VALUES ( NULL, :name, :capacity, :address1, :address2, :city, :state, :zip, :adminID )"
newEvent = "INSERT INTO events (eventID, name, tickets, type, start, finish, description, venueID, adminID) VALUES ( NULL, :name, :tickets, :type, :start, :finish, :description, :venueID, :adminID )"
adminLogin = "SELECT * FROM admin WHERE email = :email"


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['TESTING'] = True

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
db = SQL("sqlite:///bookThatThang.db")

@app.route("/")
def index():


    """

    >>> Show a list of event thumbnail images which point to selected single event page <<<

    If session.get is not null:

        DB: using sessionID (from session.get) variable

        return render_template("user-index.html")

    else:

        Display regular homepage

        DB: query all future active events to display on homepage

        return render_template("index.html")

     """


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        """
        >>> Query DB to return matching hash stored in 'users' table <<<

        if successful:

            # Redirect user to home page
            return redirect("/")

        Else:

            return render_template("login.html")

        """

    if request.method == "GET":

        """
            return render_template("index.html")

        """

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":

        return render_template("register.html")

    elif request.method == "POST":

        """
        DB query: Register user, Inserting all info into user's row insde DB

        if result:
            return render_template ("login.html", msg="Congrats! You are now registered!")

        else:

            return apology("TODO")

        """

@app.route("/event/<eventId>", methods=["GET", "POST"])
def event(eventId):

    if request.method == "GET":

        """

        if eventId is not null:

            Query DB to see if user has already gotten tickets

                if result NOT 0: print message on page "You have bought tickets for this event"
                            and show controls for editing ticket quantity

        else:

            apology("unable to find this event")

        """

    elif request.method == "POST":

        """

        Save results of ticket quantity change inside DB

        if new ticket count is 0:

            redirect("/", msg="your tickets for (eventTitle) have been cancelled")

        else:

            redirect("/thank-you.html", msg="your tickets for (eventTitle) have been saved")

        """

@app.route("/my-reservations", methods=["GET"])
@login_required
def myReservations():

        """
        Query DB for all reservations belonging to USER and display them in a table with related info

        if user clicks on a row or link of an event, a get request will go out with the varible in the URL

        """