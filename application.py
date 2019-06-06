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
userQry = "SELECT * FROM users WHERE userID = :userID"
ticketSale = "UPDATE events SET ticketsLeft = ticketsLeft - :tic WHERE eventID = :eventID"
ticketReturn = "UPDATE events SET ticketsLeft = ticketsLeft + :tickets WHERE eventID = :eventID"
allTicketQry = "SELECT eventID, SUM(tickets), time FROM transactions GROUP BY eventID HAVING userID = :userID"
eventTicketQry = "SELECT SUM(tickets) AS totalTickets FROM transactions GROUP BY eventID HAVING userID = :userID AND eventID = :eventID"
userReservations = "SELECT *, SUM(tickets) AS totalTickets FROM (SELECT * FROM venues, events, transactions WHERE venues.venueID=events.venueID AND transactions.eventID = events.eventID AND transactions.userID = :userID) GROUP BY eventID"
editProfileInfo = "UPDATE users SET fName = :fName, lName = :lName, email = :email WHERE userID = :userID"
editPassword = "UPDATE users SET pwdHash = :pwdHash WHERE userID = :userID"

# Both
venueQry = "SELECT * FROM venues WHERE venueID = :venueID"
eventQry = "SELECT * FROM events WHERE eventID = :eventID"
allEventQry = "SELECT * FROM events"
allVenueQry = "SELECT * FROM venues"

# Admin
editEvent = "UPDATE events SET eventName = :eventName, ticketsLeft = :ticketsLeft, description = :description WHERE eventID = :eventID"
newVenue = "INSERT INTO venues (venueName, capacity, address1, address2, city, state, zip, adminID) VALUES (:venueName, :capacity, :address1, :address2, :city, :state, :zipCode, :adminID )"
newEvent = "INSERT INTO events (eventName, ticketsLeft, type, startDate, startTime, endDate, endTime, description, venueID, adminID) VALUES (:eventName, :tickets, :eventType, :startDate, :startTime, :endDate, :endTime, :description, :venueID, :adminID )"
adminLogin = "SELECT * FROM admin WHERE email = :email"
newAdmin = "INSERT INTO admin ( email, pwdHash ) VALUES ( :email, :pwdHash )"
editVenue = "UPDATE venues SET venueName = :venueName, capacity = :capacity WHERE venueID = :venueID"
adminReservations = "SELECT *, SUM(tickets) AS totalTickets FROM (SELECT * FROM venues, events, transactions WHERE venues.venueID=events.venueID AND transactions.eventID = events.eventID) GROUP BY eventID"


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
    if 'admin' in session.keys():
        return redirect("/admin")
    """ Show a list of event thumbnail images which point to selected single event page """
    events = db.execute(allEventQry)
    venues = db.execute(allVenueQry)
    for event in events:
        for venue in venues:
            if venue["venueID"] == event["venueID"]:
                event["venueName"] = venue["venueName"]
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
    if 'admin' in session.keys():
        return redirect("/admin")
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
    if 'admin' in session.keys():
        return redirect("/admin")
    if request.method == "GET":
        if not eventID or eventID.isdigit() is False:
            return redirect("/")

        else:

            events = db.execute(eventQry, eventID=eventID)
            venues = db.execute(allVenueQry)
            for event in events:
                for venue in venues:
                    if venue["venueID"] == event["venueID"]:
                        event["venueName"] = venue["venueName"]

            if len(events) != 1:

                return redirect("/")

            else:

                return render_template("event.html", event=events[0])

@app.route("/my-reservations", methods=["GET"])
@login_required
def myReservations():
    if 'admin' in session.keys():
        return redirect("/admin")
    userTicket = db.execute(userReservations, userID=session["user_id"])
    remover = []
    for tic in userTicket:
        if tic["totalTickets"] == 0:
            remover.append(tic)
        confirmation = "T"
        tran = int(tic["tranID"]) + 12340
        confirmation = confirmation + str(tran)
        tic["confirmation"] = confirmation
    userTickets = [x for x in userTicket if x not in remover]
    return render_template("my-reservations.html", userTickets=userTickets)

@app.route("/myProfile", methods=["GET", "POST"])
@login_required
def myProfile():
    if 'admin' in session.keys():
        return redirect("/admin")\

    if request.method == "POST":
        if request.form.get("editType") == "info":
            if not request.form.get("fName"):
                msg = "You didn't enter a first name."
                return render_template("error.html", msg=msg)
            elif not request.form.get("lName"):
                msg = "You didn't enter a last name."
                return render_template("error.html", msg=msg)
            elif not request.form.get("email"):
                msg = "You didn't enter an email."
                return render_template("error.html", msg=msg)
            else:
                db.execute(editProfileInfo, fName=request.form.get("fName"), lName=request.form.get("lName"), email=request.form.get("email"), userID=session["user_id"])
                msg = "Profile succesfully updated."
                return render_template("confirmation.html", msg=msg)
        elif request.form.get("editType") == "pass":
            if not request.form.get("oldPassword"):
                msg = "You didn't enter your old password."
                return render_template("error.html", msg=msg)
            elif not request.form.get("newPassword"):
                msg = "You didn't enter a new password."
                return render_template("error.html", msg=msg)
            elif not request.form.get("confirmPassword"):
                msg = "You didn't confirm your password."
                return render_template("error.html", msg=msg)
            elif not passwordValid(request.form.get("newPassword")):
                msg = "Password must contain at least 1 letter,1 number, and be at least 8 characters long."
                return render_template("error.html", msg=msg)
            elif request.form.get("newPassword") != request.form.get("confirmPassword"):
                msg = "Passwords didn't match!"
                return render_template("error.html", msg=msg)
            else:
                pwdHash = generate_password_hash(request.form.get("newPassword"), method='pbkdf2:sha1', salt_length=8)
                db.execute(editPassword, pwdHash=pwdHash, userID=session["user_id"])
                msg = "Password updated."
                return render_template("confirmation.html", msg=msg)
        else:
            return redirect("/myProfile")
    else:
        user = db.execute(userQry, userID=session["user_id"])
        return render_template("editProfile.html", user=user[0])

@app.route("/change-password", methods=["GET"])
@login_required
def change_Password():
    return render_template("editPassword.html")





@app.route("/book/<eventID>", methods=["POST", "GET"])
@login_required
def book(eventID):
    if 'admin' in session.keys():
        return redirect("/admin")
    if request.method == "POST":
        if not request.form.get("tickets"):
            msg = "no tic"
            return render_template("error.html", msg=msg)
        if not eventID:
            msg = "no id"
            return render_template("error.html", msg=msg)
        else:
            db.execute(newTransaction, userID=session["user_id"], eventID=eventID, tickets=request.form.get("tickets"))
            db.execute(ticketSale, tic=request.form.get("tickets"), eventID=eventID)
            msg = "Success!"
            return render_template("confirmation.html", msg=msg)
    else:
        if not eventID:
            msg = "no id"
            return render_template("error.html", msg=msg)
        event = db.execute(eventQry, eventID=eventID)
        event = event[0]
        venue = db.execute(venueQry, venueID=event["venueID"])
        venue = venue[0]
        usr = db.execute(userQry, userID=session["user_id"])
        usr = usr[0]
        return render_template("booking.html", event=event, venue=venue, usr=usr)


@app.route("/return/<eventID>", methods=["POST", "GET"])
@login_required
def cancel(eventID):
    if 'admin' in session.keys():
        return redirect("/admin")
    if request.method == "POST":
        if not eventID:
            msg = "no id"
            return render_template("error.html")
        if not request.form.get("tickets"):
            msg = "no tic"
            return render_template("error.html")
        tickets = db.execute(eventTicketQry, eventID=eventID, userID=session["user_id"])
        db.execute(ticketReturn, tickets=request.form.get("tickets"), eventID=eventID)
        db.execute(newTransaction, userID=session["user_id"], eventID=eventID, tickets=(int(request.form.get("tickets"))) * -1)
        msg = "Tickets returned."
        return render_template("confirmation.html", msg=msg)
    else:
        event = db.execute(eventQry, eventID=eventID)
        event = event[0]
        venue = db.execute(venueQry, venueID=event["venueID"])
        venue = venue[0]
        usr = db.execute(userQry, userID=session["user_id"])
        usr = usr[0]
        tickets = db.execute(eventTicketQry, eventID=eventID, userID=session["user_id"])
        tickets = tickets[0]
        return render_template("modifyMyReservation.html", event=event, venue=venue, usr=usr, tickets=tickets)


@app.route("/admin-login", methods=["GET", "POST"])
def admin_Login():

    """Login page for admin"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form["email"]:
            msg = "You didn't enter an email."
            return render_template("error.html", msg=msg)

        # Ensure password was submitted
        elif not request.form["password"]:
            msg = "You must provide password!"
            return render_template("error.html", msg=msg)

        else:

            """Check password against hash using hash function"""

            email=request.form["email"]
            password=request.form["password"]

            verifyAdmin = db.execute(adminLogin, email=email)

            if len(verifyAdmin) != 1 or not check_password_hash(verifyAdmin[0]["pwdHash"], password):
                msg = "invalid username and/or password"
                return render_template("error.html", msg=msg)

            else:
                # Remember which user has logged in
                session["user_id"] = verifyAdmin[0]["adminID"]
                session["admin"] = "yes"

            # Redirect user to admin home page
            return redirect("/admin")
    else:

        return render_template("admin-login.html")


@app.route("/admin", methods=["GET"])
@login_required
def admin():
    if 'admin' not in session.keys():
        return redirect("/")
    if request.method == "GET":
        events = db.execute(adminReservations)
        return render_template("admin-index.html", events=events)

        events = db.execute(adminReservations)
        return render_template("admin-index.html", events=events)



@app.route("/admin-register", methods=["GET", "POST"])
def adminRegister():

    # code must be matched to register
    adminCode = "100"

    if request.method == "POST":

        # Form validation
        if request.form.get("adminCode") != adminCode:
            msg = "You didn't enter an admin code."
            return render_template("error.html", msg=msg)

        elif not request.form.get("email"):
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

        elif request.form.get("adminCode") != adminCode:
            msg = "Invalid admin code."
            return render_template("error.html", msg=msg)

        # Query database for username
        rows = db.execute(adminLogin, email=request.form.get("email"))

        # Ensure username doesn't exist, add to database if it doesn't
        if len(rows) > 0:
            msg = "That email is already in use."
            return render_template("error.html", msg=msg)

        else:

            email = request.form.get("email").lower()
            pwdHash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha1', salt_length=8)

            db.execute(newAdmin, email=email, pwdHash=pwdHash)
            msg = "Congrats! You are now registered as an admin! You may now log in."
            return render_template("admin-login.html")


    # User reached route via GET (as by clicking a link or via redirect)
    else:

        return render_template("admin-register.html")

@app.route("/admin-events", methods=["GET"])
@login_required
def adminEvents():
    if 'admin' not in session.keys():
        return redirect("/")
    if request.method == "GET":
        events = db.execute(allEventQry)
        return render_template("admin-events.html", events=events)

@app.route("/admin-venues", methods=["GET"])
@login_required
def adminVenues():
    if 'admin' not in session.keys():
        return redirect("/")
    if request.method == "GET":
        venues = db.execute(allVenueQry)
        return render_template("admin-venues.html", venues=venues)

@app.route("/admin-reservations", methods=["GET", "POST"])
@login_required
def admin_Reservations():
    if 'admin' not in session.keys():
        return redirect("/")
    if request.method == "POST":
        user = db.execute("SELECT * FROM users WHERE userID = :userID", userID=request.form.get("userID"))
        userTicket = db.execute(userReservations, userID=request.form.get("userID"))
        remover = []
        for tic in userTicket:
            if tic["totalTickets"] == 0:
                remover.append(tic)
            confirmation = "T"
            tran = int(tic["tranID"]) + 12340
            confirmation = confirmation + str(tran)
            tic["confirmation"] = confirmation
        userTickets = [x for x in userTicket if x not in remover]
        return render_template("admin-reservations.html", userTickets=userTickets, user=user[0])
    else:
        users = db.execute("SELECT * FROM users")
        return render_template("admin-users.html", users=users)






@app.route("/add-venue", methods=["GET", "POST"])
@login_required
def addVenue():
    if 'admin' not in session.keys():
        return redirect("/")

    if request.method == "POST":
        if not request.form.get("venueName"):
            msg = "You did not enter a name for the venue."
            return render_template("error.html", msg=msg)
        elif not request.form.get("venueAddress1"):
            msg = "You didn't fill out the Address 1 line."
            return render_template("error.html", msg=msg)
        elif not request.form.get("venueAddress2"):
            msg = "You didn't fill out the Address 2 line."
            return render_template("error.html", msg=msg)
        elif not request.form.get("venueCity"):
            msg = "You didn't fill out the City line."
            return render_template("error.html", msg=msg)
        elif not request.form.get("state"):
            msg = "You didn't fill out the State line."
            return render_template("error.html", msg=msg)
        elif not request.form.get("zip"):
            msg = "You didn't fill out the Zip Code line."
            return render_template("error.html", msg=msg)
        elif not request.form.get("capacity"):
            msg = "You didn't fill out the Capacity line."
            return render_template("error.html", msg=msg)
        else:
            db.execute(newVenue, venueName=request.form.get("venueName"), capacity=request.form.get("capacity"), address1=request.form.get("venueAddress1"), address2=request.form.get("venueAddress2"), city=request.form.get("venueCity"), state=request.form.get("state"), zipCode=request.form.get("zip"), adminID=session["user_id"])
            msg = "Venue created"
            return render_template("admin-index.html", msg=msg)
    else:
        return render_template("addNewVenue.html")

@app.route("/add-event", methods=["GET", "POST"])
@login_required
def addEvent():
    if 'admin' not in session.keys():
        return redirect("/")

    if request.method == "POST":

        if not request.form.get("eventName"):
            msg = "You did not enter a name for the event."
            return render_template("error.html", msg=msg)

        elif not request.form.get("venue"):
            msg = "You didn't choose a venue."
            return render_template("error.html", msg=msg)

        elif not request.form.get("eventType"):
            msg = "You didn't write what kind of event this is."
            return render_template("error.html", msg=msg)

        elif not request.form.get("eventStartDate"):
            msg = "You didn't choose a starting date for the event."
            return render_template("error.html", msg=msg)

        elif not request.form.get("eventStartTime"):
            msg = "You didn't choose a starting time for the event."
            return render_template("error.html", msg=msg)

        elif not request.form.get("eventEndDate"):
            msg = "You didn't choose an ending date for the event."
            return render_template("error.html", msg=msg)

        elif not request.form.get("eventEndTime"):
            msg = "You didn't choose an ending time for the event."
            return render_template("error.html", msg=msg)

        elif not request.form.get("tickets"):
            msg = "You didn't input the amount of tickets.."
            return render_template("error.html", msg=msg)

        elif not request.form.get("eventDescription"):
            msg = "You didn't write a description."
            return render_template("error.html", msg=msg)

        else:
            db.execute(newEvent, eventName=request.form.get("eventName"), tickets=request.form.get("tickets"), eventType=request.form.get("eventType"), startDate=request.form.get("eventStartDate"), startTime=request.form.get("eventStartTime"), endDate=request.form.get("eventEndDate"), endTime=request.form.get("eventEndTime"), description=request.form.get("eventDescription"), venueID=request.form.get("venue"), adminID=session["user_id"])
            msg = "Event created."
            return redirect ("/admin")
    else:
        venues = db.execute(allVenueQry)
        return render_template("addNewEvent.html", venues=venues)

@app.route("/edit-venue/<venueID>", methods=["GET", "POST"])
@login_required
def edit_Venue(venueID):
    if 'admin' not in session.keys():
        return redirect("/")
    if request.method == "POST":
        if not venueID:
            msg = "no venue id"
            return render_template("error.html", msg=msg)
        if not request.form.get("venueName"):
            msg = "You did not enter a name for the venue."
            return render_template("error.html", msg=msg)
        elif not request.form.get("capacity"):
            msg = "You didn't fill out the Capacity line."
            return render_template("error.html", msg=msg)
        else:
            db.execute(editVenue, venueName=request.form.get("venueName"), capacity=request.form.get("capacity"), venueID=venueID)
            msg = "Venue updated."
            return redirect("/admin")
    else:
        if not venueID:
            msg = "no venue id"
            return render_template("error.html", msg=msg)
        else:
            venue = db.execute(venueQry, venueID=venueID)
            return render_template("editVenue.html", venue=venue[0])

@app.route("/edit-event/<eventID>", methods=["GET", "POST"])
@login_required
def edit_Event(eventID):
    if 'admin' not in session.keys():
        return redirect("/")
    if request.method == "POST":
        if not eventID:
            msg = "no event id"
            return render_template("error.html", msg=msg)
        if not request.form.get("eventName"):
            msg = "You did not enter a name for the event."
            return render_template("error.html", msg=msg)
        elif not request.form.get("tickets"):
            msg = "You didn't enter a number of tickets."
            return render_template("error.html", msg=msg)
        elif not request.form.get("eventDescription"):
            msg = "You didn't enter a description for the event."
            return render_template("error.html", msg=msg)
        else:
            db.execute(editEvent, eventName=request.form.get("eventName"), ticketsLeft=request.form.get("tickets"), description=request.form.get("eventDescription"), eventID=eventID)
            msg = "Venue updated."
            return redirect("/admin")
    else:
        if not eventID:
            msg = "no event id"
            return render_template("error.html", msg=msg)
        else:
            event = db.execute(eventQry, eventID=eventID)
            return render_template("editEvent.html", event=event[0])

