import pymysql
import pymysql.cursors
import creds
import boto3


def get_conn_RDS():
    
    return pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        db=creds.db,
        cursorclass=pymysql.cursors.DictCursor
    )

def get_conn_Dynamo():

    TABLE_NAME = "Voters"

    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(TABLE_NAME)
    return(table)

def execute_query_RDS(query, args=()):
    
    conn = get_conn_RDS()
    try:
        with conn.cursor() as cur:
            cur.execute(query, args)
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()


def get_list_of_dictionaries():

    query = "SELECT DISTINCT title, overview, release_date FROM movie, movie_company, production_company, movie_keywords, keyword WHERE movie.movie_id = movie_company.movie_id AND movie_company.company_id = production_company.company_id AND movie.movie_id = movie_keywords.movie_id AND movie_keywords.keyword_id = keyword.keyword_id AND (company_name = 'Walt Disney Animation Studios' OR company_name = 'Walt Disney Feature Animation' OR company_name = 'Walt Disney Pictures' OR company_name = 'Walt Disney Productions') AND keyword_name = 'princess' AND title <> 'Dragonslayer' AND title <> 'The Princess Diaries' AND title <> 'John Carter' AND title <> 'Into the Woods' AND title <> 'Enchanted' ORDER BY release_date ASC;"
    return execute_query_RDS(query)

def add_user(username, password, ID, firstname, lastname):
    
    table = get_conn_Dynamo()
    table.put_item(
        Item={
            'First Name': firstname,
            'Last Name': lastname,
            'Username': username,
            'Password': password,
            'ID': ID
        })

def update_user_profile(ID, movie_name, rating_number):

    table = get_conn_Dynamo()
    map_as_dictionary = {"Movie": movie_name , "Rating" : rating_number}
    table.update_item(
        Key={
            'ID': ID
        },
        UpdateExpression='SET Ratings = list_append(Ratings, :val1)',
        ExpressionAttributeValues={
            ':val1':[map_as_dictionary]
            }
    )