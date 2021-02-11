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


def match(skills_personal, skills_req):
    # the overal matching score
    score = 0
    # turning skills in db into list
    skill_list_personal = list(x.strip() for x in skills_personal.split(','))
    skill_list_job = list(x.strip() for x in skills_req.split(','))

    # find the total number of skills in a job
    total = len(skill_list_job)

    # getting the matches from the two lists
    matches = list(set(skill_list_job) & set(skill_list_personal))

    score = "{:.0%}".format((len(matches)/total))

    return score, matches


@app.route("/")
@app.route("/getwurc")
def getwurc():
    all_jobs = mongo.db.job_list.find()
    if session.get('user'):
        member = mongo.db.members.find_one(
                 {"username": session["user"]})
        match_list = []
        for job in all_jobs:
            match_job = match(member["skills"], job["skills"])
            match_list.append(match_job)
    else:
        return render_template("getwurc.html", job_matches=all_jobs,
                               member="no member")
    return render_template("getwurc.html", job_matches=all_jobs, member=member,
                           match_list=match_list)


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
            if check_password_hash(existing_user["password"],
                                   request.form.get("password")):
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
    # get jobs from job_list
    jobs = list(mongo.db.job_list.find())
    if session["user"]:
        return render_template("profile.html", username=username, jobs=jobs)

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
    industries = list(mongo.db.industry.find().sort("ind_name", 1))
    job_func = list(mongo.db.job_func.find().sort("func", 1))
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
            "industry": request.form.get("industry"),
            "proj_role1": request.form.get("proj_role1"),
            "industry1": request.form.get("industry1"),
            "job_func1": request.form.get("job_func1"),
            "proj_role2": request.form.get("proj_role2"),
            "industry2": request.form.get("industry2"),
            "job_func2": request.form.get("job_func2"),
            "proj_role3": request.form.get("proj_role3"),
            "industry3": request.form.get("industry3"),
            "job_func3": request.form.get("job_func3"),
            "skills": request.form.get("skills"),
            "desc": request.form.get("desc"),
            "remote": remote
        }
        mongo.db.members.update({"_id": ObjectId(prof_id)}, updated)
        flash("Your profile was updated successfully!")
        return redirect(url_for('profile', username=session['user']))


@app.route("/post_job", methods=["GET", "POST"])
def post_job():
    if request.method == "POST":
        remote = "yes" if request.form.get("remote") else "no"
        job = {
            "role": request.form.get("role"),
            "location": request.form.get("location"),
            "proj_name": request.form.get("proj_name"),
            "industry": request.form.get("industry"),
            "jfunc": request.form.get("jfunc"),
            "desc": request.form.get("desc"),
            "remote": remote,
            "skills": request.form.get("skills"),
            "created_by": session["user"]
        }
        mongo.db.job_list.insert_one(job)
        flash("Job posted successfully!")
        return redirect(url_for('profile', username=session['user']))

    # generating selection options from db
    industries = mongo.db.industry.find().sort("ind_name", 1)
    job_func = mongo.db.job_func.find().sort("func", 1)
    return render_template("post_job.html", industries=industries,
            job_func=job_func)


@app.route("/edit_job/<job_id>", methods=["GET", "POST"])
def edit_job(job_id):
    if request.method == "POST":
        remote = "yes" if request.form.get("remote") else "no"
        job_update = {
            "role": request.form.get("role"),
            "location": request.form.get("location"),
            "proj_name": request.form.get("proj_name"),
            "industry": request.form.get("industry"),
            "jfunc": request.form.get("jfunc"),
            "desc": request.form.get("desc"),
            "remote": remote,
            "skills": request.form.get("skills"),
            "created_by": session["user"]
        }
        mongo.db.job_list.update({"_id": ObjectId(job_id)}, job_update)
        flash("Changes applied successfully!")
        return redirect(url_for('profile', username=session['user']))

    job = mongo.db.job_list.find_one({"_id": ObjectId(job_id)})
    # generating selection options from db
    industries = mongo.db.industry.find().sort("ind_name", 1)
    job_func = mongo.db.job_func.find().sort("func", 1)
    return render_template("edit_job.html", industries=industries,
            job_func=job_func, job=job)


@app.route("/delete_job/<job_id>")
def delete_job(job_id):
    mongo.db.job_list.remove({"_id": ObjectId(job_id)})
    flash("Job deleted successfully")
    return redirect(url_for('profile', username=session['user']))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
