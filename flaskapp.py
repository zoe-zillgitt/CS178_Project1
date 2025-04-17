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
    voter = get_voters()
    return render_template('home.html', movies = movies_list, voters = voter)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        password = request.form['password']

        response = (get_conn_Dynamo()).scan()
        for person in response["Items"]:
            if (person['Username'] == username and person['Password'] == password):
                
                flash('User added successfully!', 'success') 
            else:

                flash('Something was wrong and we could not log you in, please try again!', 'warning')
        # Redirect to home page or another page upon successful submission
        return redirect(url_for('home'))
    else:
        # Render the form page if the request method is GET
        return render_template('login.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)