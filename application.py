import os

from cs50 import SQL
from flask import Flask, flash, json, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from datetime import datetime
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, passwordValid

# Database queries

# User
newUser = "INSERT INTO users ( email, pwdHash, fName, lName, zip, pic ) VALUES ( :email, :pwdHash, :fName, :lName, :zipCode, :pic )"
newTransaction = "INSERT INTO transactions (userID, eventID, tickets) VALUES (:userID, :eventID, :tickets)"
userLogin = "SELECT * FROM users WHERE email = :email"
ticketSale = "UPDATE events SET tickets = tickets - :tic WHERE eventID = :eventID"
allTicketQry = "SELECT eventID, SUM(tickets), time FROM transactions GROUP BY eventID HAVING userID = :userID"
eventTicketQry = "SELECT SUM(tickets) FROM transactions GROUP BY eventID HAVING userID = :userID AND eventID = :eventID"
userReservations = "SELECT * FROM venues, events, transactions WHERE venues.venueID=events.venueID AND transactions.eventID = events.eventID AND transactions.userID = :userID"

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
    events = db.execute(allEventQry)
    return render_template("index.html", events=events)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form["email"]:
            msg = "You must provide your email!"
            return render_template("error.html", msg=msg)

        # Ensure password was submitted
        elif not request.form["password"]:
            msg = "You must provide password!"
            return render_template("error.html", msg=msg)

        else:

            """Check password against hash using hash function"""

            email=request.form["email"]
            password=request.form["password"]

            verifyUsr = db.execute(userLogin, email=email)

            if len(verifyUsr) != 1 or not check_password_hash(verifyUsr[0]["pwdHash"], password):
                msg = "invalid username and/or password"
                return render_template("error.html", msg=msg)

            else:
                # Remember which user has logged in
                session["user_id"] = verifyUsr[0]["userID"]

                # Redirect user to home page
                return redirect("/")
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
    if request.method == "POST":

        # Form validation
        if not request.form.get("email"):
            msg = "You didn't enter an email."
            return render_template("error.html", msg=msg)

        elif not request.form.get("password"):
            msg = "You didn't enter a password."
            return render_template("error.html", msg=msg)

        elif not request.form.get("confirmPassword"):
            msg = "You didn't confirm your password."
            return render_template("error.html", msg=msg)

        elif not passwordValid(request.form.get("password")):
            msg = "Password must contain at least 1 letter,1 number, and be at least 8 characters long."
            return render_template("error.html", msg=msg)

        elif request.form.get("password") != request.form.get("confirmPassword"):
            msg = "Passwords did not match."
            return render_template("error.html", msg=msg)

        elif not request.form.get("fName"):
            msg = "You didn't enter a first name."
            return render_template("error.html", msg=msg)

        elif not request.form.get("lName"):
            msg = "You didn't enter a last name."
            return render_template("error.html", msg=msg)


        # Query database for username
        rows = db.execute(userLogin, email=request.form.get("email"))

        # Ensure username doesn't exist, add to database if it doesn't
        if len(rows) > 0:
            msg = "That email is already in use."
            return render_template("error.html", msg=msg)

        else:

            email = request.form.get("email").lower()
            pwdHash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha1', salt_length=8)
            fName = request.form.get("fName")
            lName = request.form.get("lName")
            zipCode = request.form.get("zipCode")
            pic = request.form.get("pic")

            db.execute(newUser, email=email, pwdHash=pwdHash, fName=fName, lName=lName, zipCode=zipCode, pic=pic)

            # Redirect user to log in page
            msg = "Congrats! You are now registered! You may now log in."
            return render_template("login.html", msg=msg)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("registration.html")

@app.route("/checkReg")
def checkRegistration():
    email = request.args['email']
    rows = db.execute( userLogin, email = email )
    return  jsonify( exists = len( rows ) > 0 )



@app.route("/event/<eventID>", methods=["GET", "POST"])
def event(eventID):
    if request.method == "GET":
        if not session:
            msg = "no sesh"
            return render_template("error.html", msg=msg)
        if not eventID or eventID.isdigit() is False:
            return redirect("/")

        else:

            event = db.execute(eventQry, eventID=eventID)

            if len(event) != 1:

                return redirect("/")

            else:

                return render_template("event.html", event=event[0])


    """

    elif request.method == "POST":



        Save results of ticket quantity change inside DB

        if new ticket count is 0:

            redirect("/", msg="your tickets for (eventTitle) have been cancelled")

        else:

            redirect("/thank-you.html", msg="your tickets for (eventTitle) have been saved")

        """

@app.route("/my-reservations", methods=["GET"])
@login_required
def myReservations():

    #i=0
    #reservations = []
    userTickets = db.execute(userReservations, userID=session["user_id"])
    #db.execute(allTicketQry, userID=session['user_id'])
    #for tic in userTics:
     #   event = db.execute(eventQry, eventID=tic["eventID"])
      #  venue = db.execute(venueQry, venueID=event["venueID"])
       # reservations.append(event)
        #reservations.append(venue)
        #reservations.append(userTics[i])
        #i += 1
    return render_template("my-reservations.html", userTickets=userTickets)
        #Query DB for all reservations belonging to USER and display them in a table with related info
        #if user clicks on a row or link of an event, a get request will go out with the varible in the URL
@app.route("/book", methods=["POST"])
@login_required
def book():
    if request.method == "POST":
        if not request.form.get("eventID") or not request.form.get("tickets"):
            return render_template("error.html")
        else:
            db.execute(newTransaction, userID=session["user_id"], eventID=request.form.get("eventID"), tickets=request.form.get("tickets"))
            db.execute(ticketSale, tic=request.form.get("tickets"), eventID=request.form.get("eventID"))
            msg = "Success!"
            return render_template("confirmation.html", msg=msg)
