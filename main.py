from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

#  ------------- Create app & database ------------- #
app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top-movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
db = SQLAlchemy(app=app)

# ---------------- Create table using SQLAlchemy ---------------- #





@app.route("/")
def home():
    return render_template("index.html")


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        new_rating = request.form.to_dict()
        return redirect(url_for('home', edit=new_rating))
    return render_template('edit.html')


@app.route('/add')
def add_movie():
    return render_template('add.html')


if __name__ == '__main__':
    app.run(debug=True)
