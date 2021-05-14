import psycopg2
from psycopg2 import OperationalError, Error


def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection


def execute_query(connection, query, values=None):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query, values)
        print("Query executed successfully")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    except Error as e:
        print(f"The error '{e}' occurred")
