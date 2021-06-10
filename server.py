from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "Secret Key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/content")
def content():
    if "name" in session:
        return render_template("content.html")
    else:
        flash("Not Logged In!")
        return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]

        found_user_name = Users.query.filter_by(name=name).first()
        found_user_email = Users.query.filter_by(email=email).first()

        if found_user_name:
            flash("Name Already Taken")
            redirect("signup")

        elif found_user_email:
            flash("Email Already Taken")
            redirect("signup")
        else:
            made_user = Users(name, email)
            db.session.add(made_user)
            db.session.commit()

            session["name"] = name
            session["email"] = email
            flash("Successfully Signed In")
        return redirect(url_for("user"))
    else:
        if "name" in session:
            flash("Already Signed In!")
            return redirect(url_for("home"))

        return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        found_user = Users.query.filter_by(name=name).first()

        if found_user:
            if found_user.name != name or found_user.email != email:
                flash("Username Or Email Is Not Correct :(")
            else:
                session["name"] = found_user.name
                session["email"] = found_user.email
                flash("Successfully Logged In")
            return redirect(url_for("user"))
        else:
            flash("Not Signed In :(")
            return redirect(url_for("signup"))
    else:
        if "name" in session:
            flash("Already Logged In!")
            return redirect(url_for("home"))
        return render_template("login.html")


@app.route("/logout")
def logout():
    if "name" in session:
        session.pop("name")
        session.pop("email")
        flash("Successfully Logged Out")

    else:
        flash("Not Logged In :P")
    return redirect(url_for("home"))


@app.route("/user", methods=["GET", "POST"])
def user():
    if request.method == "POST":
        if "submit" in request.form:
            session_name = session["name"]
            name = request.form["name"]
            email = request.form["email"]
            found_user = Users.query.filter_by(name=session_name).first()

            if found_user.name == name and found_user.email == email:
                flash("No Changes Observed")

            else:
                found_user.name = name
                found_user.email = email
                db.session.commit()

                session["name"] = name
                session["email"] = email
                flash("Values Updated :)")
            return render_template("user.html")

        elif "delete" in request.form:
            name = session["name"]
            found_user = Users.query.filter_by(name=name)
            found_user.delete()
            db.session.commit()

            session.pop("name")
            session.pop("email")
            flash("Account Successfully Deleted")
            return redirect(url_for("home"))

        return "Invalid Request :) Mr. Haxer 1337"

    else:
        if "name" in session:
            return render_template("user.html")
        flash("Not Logged In!")
        return redirect(url_for("login"))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    user_list = Users.query.all()

    if request.method == "POST":
        if "delete" in request.form:

            name = request.form["delete"]
            Users.query.filter_by(name=name).delete()
            db.session.commit()

            flash("Account Successfully Deleted!")
            return redirect(url_for("admin"))

        return "Invalid Request :) Mr. Haxer 1337"

    else:
        if "name" in session:
            if session["name"] == "admin" and session["email"] == "admin@gmail.com":
                return render_template("admin.html", user_list=user_list)
            flash("Not An Admin")
            return redirect(url_for("home"))

        flash("Not Logged In!")
        return redirect(url_for("login"))


if __name__ == '__main__':
    db.create_all()
    app.run()
