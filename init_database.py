import sqlite3
import os
from sqlite3 import Error

def delete_table(table):
   print("je")
   #Not implemented

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print('Database connection established')
    except Error as e:
        print(f'the error {e} occured')
    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def create_tables(conn):
   
    create_player_table = """
    CREATE TABLE IF NOT EXISTS player (
    id INTEGER PRIMARY KEY,
    name TEXT   
    );
    """ 
    execute_query(conn, create_player_table)


    