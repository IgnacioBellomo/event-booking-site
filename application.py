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
newUser = "INSERT INTO users ( email, pwdHash, fName, lName, zip, pic ) VALUES ( :email, :pwdHash, :fName, :lName, :zip, :pic )"
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

    """ Show a list of event thumbnail images which point to selected single event page """

    usr = session.get("userID")
    events = db.execute(allEventQry)

    return render_template("index.html", events=events, usr=usr)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form["email"]:
            return apology("You must provide your email!", 403)

        # Ensure password was submitted
        elif not request.form["password"]:
            return apology("You must provide password!", 403)

        else:

            """Check password against hash using hash function"""

            email=request.form["email"]
            password=request.form["password"]

            verifyUsr = db.execute(userLogin, email=email)

            if len(verifyUsr) != 1 or not check_password_hash(verifyUsr[0]["pwdHash"], password):

                return apology("invalid username and/or password", 403)
                # Redirect user to home page

            else:

                return redirect("/")

    if request.method == "GET":

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

    if request.method == "GET":

        return render_template("registration.html")

    elif request.method == "POST":

        """Register user"""
        email = request.form["email"]
        pwdHash = generate_password_hash(request.form["password"], method='pbkdf2:sha256', salt_length=8)
        fName = request.form["fName"]
        lName = request.form["lName"]
        zip = "33018"
        pic = "some pic url"

        # Register new login info
        result = db.execute (newUser, email=email, fName=fName, pwdHash=pwdHash, lName=lName, zip=zip, pic=pic)

        if result:
            return render_template ("login.html", msg="Congrats! You are now registered!")

    else:

        return apology(msg="Looks like the registration failed")

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