import pymysql
import pymysql.cursors
import creds
import boto3


def get_conn_RDS():
    """
    Connects to my RDS instance to access data
    """
    
    return pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        db=creds.db,
        cursorclass=pymysql.cursors.DictCursor
    )

def get_conn_Dynamo():
    """
    Connects to my dynamodb to access user data
    """

    TABLE_NAME = "Voters"

    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(TABLE_NAME)
    return(table)

def execute_query_RDS(query, args=()):
    """
    formats SQL in python so that it can be read in SQL database and used there
    """
    
    conn = get_conn_RDS()
    try:
        with conn.cursor() as cur:
            cur.execute(query, args)
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()


def get_list_of_dictionaries():
    """
    finds all disney animated movies with a princess in them 
    """
    query = "SELECT DISTINCT title, overview, release_date FROM movie, movie_company, production_company, movie_keywords, keyword WHERE movie.movie_id = movie_company.movie_id AND movie_company.company_id = production_company.company_id AND movie.movie_id = movie_keywords.movie_id AND movie_keywords.keyword_id = keyword.keyword_id AND (company_name = 'Walt Disney Animation Studios' OR company_name = 'Walt Disney Feature Animation' OR company_name = 'Walt Disney Pictures' OR company_name = 'Walt Disney Productions') AND keyword_name = 'princess' AND title <> 'Dragonslayer' AND title <> 'The Princess Diaries' AND title <> 'John Carter' AND title <> 'Into the Woods' AND title <> 'Enchanted' ORDER BY release_date ASC;"
    return execute_query_RDS(query)

def add_user(username, password, ID, firstname, lastname):
    """
    Uses data entered on the html page, connects to dynamodb, and then formats the data to be
    entered into the database and create a new user
    """
    table = get_conn_Dynamo()
    table.put_item(
        Item={
            'First Name': firstname,
            'Last Name': lastname,
            'Username': username,
            'Password': password,
            'ID': ID,
            'Ratings': []
        })

def update_user_profile(ID, movie_name, rating_number):
    """
    Uses data entered on html page, connects to Dynamo, and then formats the data so it can
    update an instance that already exists in Dynamodb
    """

    table = get_conn_Dynamo()
    #formats the data in a dictionary(or map as dynamo calls it) so that it is already formatted for entry
    map_as_dictionary = {"Movie": movie_name , "Rating" : int(rating_number)}
    table.update_item(
        Key={ #tells database which instance to enter the new data under
            'ID': ID
        },
        UpdateExpression='SET Ratings = list_append(Ratings, :val1)', #combines two lists, the one already there and the new one
        ExpressionAttributeValues={
            ':val1':[map_as_dictionary] #new list to be appended with other one
            }
    )

def calculate_ratings():
    """
    combines all the ratings from dynamodb instances and then divides them by the
    amount of isntances so that you can see the total combined rating for each movie
    """

    list_of_ratings = [0,0,0,0,0,0,0] #initialize list
    i = 0 #for looping

    response = (get_conn_Dynamo()).scan() #connect to dynamo

    number_of_users = len(response["Items"])
    #loops through and adds ratings to their respective spots in the ratings list
    for person in response["Items"]:
        for rate in person["Ratings"]:
            if rate["Movie"] == "Snow White and the Seven Dwarfs":
                list_of_ratings[0] += int(rate["Rating"])
            if rate["Movie"] == "Aladdin":
                list_of_ratings[1] += int(rate["Rating"])
            if rate["Movie"] == "Pocahontas":
                list_of_ratings[2] += int(rate["Rating"])
            if rate["Movie"] == "Mulan":
                list_of_ratings[3] += int(rate["Rating"])
            if rate["Movie"] == "The Princess and the Frog":
                list_of_ratings[4] += int(rate["Rating"])
            if rate["Movie"] == "Tangled":
                list_of_ratings[5] += int(rate["Rating"])
            if rate["Movie"] == "Frozen":
                list_of_ratings[6] += int(rate["Rating"])

    for rate in list_of_ratings:#takes each rating and divides it by the number of users to find the average
        rate = int(rate/number_of_users)
        list_of_ratings[i] = rate
        i += 1

    return(list_of_ratings)#returns the list of ratings