"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db



app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()

    return render_template("user_list.html", users=users)


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by('title').all()

    return render_template("movie_list.html", movies=movies)


@app.route("/register")
def register():
    """Show registration form."""

    return render_template("register.html")


@app.route("/handle-registration", methods=["POST"])
def register_user():
    """Register a new user."""

    new_email = request.form.get("email")
    new_password = request.form.get("password")

    if User.query.filter_by(email=new_email).first() is None:
        user = User(email=new_email, password=new_password)
        db.session.add(user)
        db.session.commit()
        flash("New user created.")
        return redirect("/")
    else:
        flash("This user already exists.")
        return redirect("/register")


@app.route("/login")
def show_login_form():
    """Show login form."""

    return render_template("login.html")


@app.route("/handle-login", methods=["POST"])
def login():
    """Login user."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if password == user.password:
        flash("Login successful.")
        session["logged_in_user"] = user.user_id
        return redirect(f"/user-information?user={user.user_id}")
    else:
        flash("Incorrect email or password.")
        return redirect("/login")


@app.route("/user-information")
def view_user_data():

    user_id = request.args.get('user')

    user = User.query.filter_by(user_id=user_id).first()

    return render_template("users.html", user=user)


@app.route("/movies/<int:movie_id>")
def view_movie_info(movie_id):

    movie = Movie.query.filter_by(movie_id=movie_id).first()

    return render_template("movie_info.html", movie=movie)


@app.route("/new-rating/<int:movie_id>", methods=["POST"])
def add_new_rating(movie_id):
    """Add a new rating to a movie."""

    score = request.form.get('score')

    user_id = session["logged_in_user"]

    user = User.query.get(user_id)

    rating_object = Rating.query.filter_by(user_id=user_id,
                                           movie_id=movie_id).first()

    if rating_object:
        rating_object.score = score
        flash("Movie score updated.")
    else:
        new_rating = Rating(movie_id=movie_id, score=score, user_id=user_id)
        user.ratings.append(new_rating)
        db.session.add(new_rating)
        flash("New rating added.")

    db.session.commit()

    return redirect(f"/movies/{movie_id}")


@app.route("/logout")
def logout():
    """Logout user."""

    del session["logged_in_user"]
    flash("Logout successful.")

    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5000, host="0.0.0.0")
