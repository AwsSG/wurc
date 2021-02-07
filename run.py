import os
from flask import (Flask, flash, render_template,
                   redirect, session, request, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/getwurc")
def getwurc():
    matches = mongo.db.job_list.find()
    return render_template("getwurc.html", job_matches=matches)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if the username already exist
        existing_user = mongo.db.members.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists!")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "company": False
        }
        mongo.db.members.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/register_business", methods=["GET", "POST"])
def register_business():
    if request.method == "POST":
        # check if the username already exist
        existing_user = mongo.db.members.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists!")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "company": True
        }
        mongo.db.members.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/log_in", methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        # check if the user exists
        existing_user = mongo.db.members.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches what the user provided
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect username and/or password")
                return redirect(url_for("log_in"))

        else:
            # username does not exist
            flash("Incorrect username and/or password")
            return redirect(url_for("log_in"))

    return render_template("log_in.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session's user username from db
    username = mongo.db.members.find_one(
        {"username": session["user"]})
    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("log_in"))


@app.route("/log_out")
def log_out():
    # remove user from session cookie
    flash("You have been logged out successfully!")
    session.pop("user")
    return redirect(url_for("log_in"))


@app.route("/fill_prof/<username>", methods=["GET", "POST"])
def fill_prof(username):
    # generating selection options from db
    industries = mongo.db.industry.find().sort("ind_name", 1)
    job_func = mongo.db.job_func.find().sort("func", 1)
    # grab the session's user username from db
    username = mongo.db.members.find_one(
        {"_id": ObjectId(username)})
    if session["user"]:
        return render_template(
            "fill_prof.html",
            username=username,
            industries=industries,
            job_func=job_func)

    return redirect(url_for("login"))


@app.route("/edit_prof/<prof_id>", methods=["GET", "POST"])
def edit_prof(prof_id):
    if request.method == "POST":
        reg_inputs = mongo.db.members.find_one({"_id": ObjectId(prof_id)})
        remote = "yes" if request.form.get("remote") else "no"
        updated = {
            "username": reg_inputs["username"],
            "password": reg_inputs["password"],
            "company": reg_inputs["company"],
            "fname": request.form.get("fname"),
            "lname": request.form.get("lname"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "role": request.form.get("role"),
            "drate": request.form.get("drate"),
            "location": request.form.get("location"),
            "website": request.form.get("website"),
            "remote": remote
        }
        mongo.db.members.update({"_id": ObjectId(prof_id)}, updated)
        flash("Your profile was updated successfully!")
        return redirect(url_for('profile', username=session['user']))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
