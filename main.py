from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import config


MOVIE_DB_URL = 'https://api.themoviedb.org/3/search/movie'
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/movie/"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
API_KEY = config.API_KEY        # "41ef05c95affa23574000ce2d32297fc"

#  ------------- Create app & database ------------- #
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY    # '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top-movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app=app)


# ---------------- Create table using SQLAlchemy ---------------- #
class NewMovie(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(100), nullable=False)
    overview = db.Column(db.String(300), nullable=False)
    img_url = db.Column(db.Text, nullable=False)

    # def __repr__(self):
    #     return f"{self.title} - {self.year} - {self.year}"


db.create_all()

# -------------- Create new movie -------------- #
# new_movie = NewMovie(
#     title=" The Hate U Give",
#     year="2018",
#     rating=9,
#     review="The message is wonderful!",
#     overview="A teenage girl who grapples with racism, police brutality, and activism after witnessing her "
#              "Black friend murdered by the police."
# )


# ----------- Add and commit new movie to database. ------------ #
# db.session.add(new_movie)
# db.session.commit()


class RateMovieForm(FlaskForm):
    rating = StringField("Your rating out of 10 e.g. 7.5")
    review = StringField("Your review")
    submit = SubmitField("Done")


class AddMovie(FlaskForm):
    title = StringField("Movie title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


class FindMovieForm(FlaskForm):
    title = StringField("Movie title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


# ------------ All routes ------------- #
@app.route("/")
def home():
    # --- create list of movies sorted by rating --- #
    all_movies = NewMovie.query.order_by(NewMovie.rating).all()
    print(all_movies)
    for i in all_movies:
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route('/add', methods=['GET', 'POST'])
def add_movie():
    add_form = AddMovie()
    if add_form.validate_on_submit():
        movie_title = add_form.title.data
        params = {'api_key': config.API_KEY, 'query': movie_title}
        response = requests.get(url=MOVIE_DB_URL, params=params).json()
        # print(response)
        data = response["results"]
        print(data)
        return render_template('select.html', options=data)

    return render_template('add.html', form=add_form)


@app.route('/find')
def find():
    movie_api_id = request.args.get('id')
    if movie_api_id:
        search_params = {'movie_id': movie_api_id, 'api_key': config.API_KEY}
        response = requests.get(url=MOVIE_DB_SEARCH_URL, params=search_params).json()
        new_movie = NewMovie(
            title=response['original_title'],
            year=response['release_date'].strftime("%Y"),
            rating=round(response['average_vote'], 1),
            overview=response['overview'],
            img_url=f"{MOVIE_DB_IMAGE_URL}/{movie_api_id}{response['poster_path']}"
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('rate_movie', id=new_movie.id))


@app.route('/edit', methods=['GET', 'POST'])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get('id')
    print(movie_id)
    movie = NewMovie.query.get(movie_id)
    print(movie)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        # new_rating = request.form.to_dict()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie, form=form)


@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie = NewMovie.query.get(movie_id)
    db.seesion.delete(movie)
    db.session.commit()
    return render_template(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
