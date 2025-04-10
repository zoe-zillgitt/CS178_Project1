from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import creds
from dbCode import *


app = Flask(__name__)
app.secret_key = 'your_secret_key' # this is an artifact for using flash displays; 
                                   # it is required, but you can leave this alone

@app.route('/')
def home():
    movies_list = get_list_of_dictionaries()
    return render_template('home.html', movies = movies_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)