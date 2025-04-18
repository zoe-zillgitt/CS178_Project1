from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
import creds
from dbCode import *


app = Flask(__name__)
app.secret_key = 'your_secret_key' # this is an artifact for using flash displays; 
                                   # it is required, but you can leave this alone

@app.route('/')
def home():

    ratings_list = calculate_ratings() #gets calculated ratings list
    movies_list = get_list_of_dictionaries()#gets list of movies

    i = 0
    for movie in movies_list: #for each movie in the list, it adds it's respective rating to it's dictionary
        movie.update({"rating": ratings_list[i]})
        i += 1

    return render_template('home.html', movies = movies_list)#sends movie list to be displayed

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #gets username and password from html page
        username = request.form['username']
        password = request.form['password']

        response = (get_conn_Dynamo()).scan()
        for person in response["Items"]: 
            if (person['Username'] == username and person['Password'] == password): #goes through and checks if this person does exist
                
                session['username'] = person['ID'] #sets flask session to keep track of user
                flash('You have logged in!', 'success') #lets user known it's been accomplished
                return redirect(url_for('home'))#sends the user back to the homepage
        #if the user doesn't exist then it lets the user known and sends them back to home
        flash('Something was wrong and we could not log you in, please try again!', 'warning')
        return redirect(url_for('home'))

    else:
        # Render the form page if the request method is GET
        return render_template('login.html')

@app.route('/signup', methods = ['GET','POST'])
def signup():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        password = request.form['password']
        ID = int(request.form['ID'])
        firstname = request.form['firstname']
        lastname = request.form['lastname']

        response = (get_conn_Dynamo()).scan()
        for person in response["Items"]: #checks if this user is already in the dynamodb
            if (person['Username'] == username and person['Password'] == password):
                #lets user known it already exists and sends them home
                flash('This user already exists, please login instead!', 'warning')
                return redirect(url_for('home'))
        #if doesn't exist, sends data to dbcode function to add it to dynamo db
        add_user(username, password, ID, firstname, lastname)
        flash('User added, please also login!', 'success')
        # Redirect to home page on success
        return redirect(url_for('home'))
    else:
        # Render the form page if the request method is GET
        return render_template('signup.html')

@app.route('/ratings', methods = ['GET', 'POST'])
def rate():
    movies_list = get_list_of_dictionaries()
    if request.method == 'POST':
        try:#gets data from html
            user_id = {"Name":session['username']}
            user_id = int(user_id.get('Name'))
            selected_movie = request.form['movies']
            movie_rating = request.form['rating']

            response = (get_conn_Dynamo().scan())
            for person in response["Items"]: 
                if person['ID'] == user_id:
                    for rate in person['Ratings']:
                        if rate["Movie"] == selected_movie: #digs into the instance to find if the movie is already in the user's rating list
                            flash('You have already rated this movie, please rate another one!', 'warning')
                            return render_template('rating.html', movies = movies_list) #reloads the rating page
            #if not already in their ratings list then adds it using dbcode function
            update_user_profile(user_id, selected_movie, movie_rating)
            flash('Successfully added movie rating', 'success')
            return render_template('rating.html', movies = movies_list) #reloads on success
            
        except:
            #if something goes wrong it tells the user and then sends them to the home page
            flash('Something went wrong, please try logging in if you have not!', 'warning')
            return redirect(url_for('home'))
        
    return render_template('rating.html', movies = movies_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)