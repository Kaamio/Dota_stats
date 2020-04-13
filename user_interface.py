import dota_main
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import init_database
import os.path
import player
'''
def herodata(df,hero): 
    #function returns the rows from the dataframe where hero_id = hero (given as argument)
       
    databyheros = df.copy()
    #Filter dataframe by games (normal game mode) with chosen hero
    databyheros = databyheros[(databyheros.hero_id==hero) & (databyheros.game_mode ==1)]
    
    wins = databyheros[databyheros.win==1].shape[0]         
    games = databyheros.shape[0]
    losses = (games - wins)

    print(f"You have a total of {games} games as {hero} with a record of {wins} / {losses} ")   
    



while(True):
    print("Choose option:                   ")
    print("1 - Hero stats                   ")
    print("2 - Game stats                   ")
    print("3 - Player stats                 ")
    print("4 - Display wordcloud of chat    ")

    selection = 0
    while selection not in [1,2,3]: 
        selection = int(input())
        
        if selection == 1:            
            print("Enter hero name")            
            hero = input()
            herodata(player_data,hero)                
            break

        if selection == 4:
            wc_data = player_instance.wordCloud()            
            list_of_words = (wc_data.get("my_word_counts"))
            wc = WordCloud(background_color="white",width=1000,height=1000, max_words=20,relative_scaling=0.5,normalize_plurals=False).generate_from_frequencies(list_of_words) 
            plt.imshow(wc)
            plt.show()
'''
def create_db_tables(connection):
    create_matches = """
    CREATE TABLE IF NOT EXISTS match (
    match_id INTEGER PRIMARY KEY,
    player_slot INTEGER,    
    radiant_win BOOLEAN,
    duration INTEGER,
    game_mode INTEGER,
    lobby_type INTEGER,
    hero_id TEXT,    
    start_time TIMESTAMP,
    version TEXT,
    kills INTEGER,
    deaths INTEGER,
    assists INTEGER,
    skill INTEGER,
    lane INTEGER,
    lane_role INTEGER,
    is_roaming BOOLEAN,
    cluster INTEGER,
    leaver_status INTEGER,
    party_size INTEGER,
    win INTEGER      
    );
    """
    init_database.execute_query(connection,create_matches)

    create_player = """
    CREATE TABLE IF NOT EXISTS player(
        steam_id INTEGER PRIMARY KEY
    );
    """
    init_database.execute_query(connection,create_player)

def insert_player(conn, steam_id):
    
    query = f"""
    INSERT INTO player VALUES ({int(steam_id)})
    """
    
    init_database.execute_query(conn, query)

def view_players(conn):

    cur = conn.cursor()
    cur.execute("SELECT * FROM player")
 
    rows = cur.fetchall()
 
    for row in rows:
        print(row)

def view_matches(conn):
    print("Enter steam ID to view player stats, 0 = list everything")
    cur = conn.cursor()
    selection = int(input())
    if selection == 0:
        cur.execute("SELECT * FROM match")
    elif selection > 0:
        cur.execute(f"SELECT * FROM match where steam_id = {selection}")
    rows = cur.fetchall()
    for row in rows:
       print(row)

def insert_player_to_db(conn):
    print("Enter steam ID:")
    while(True):
        steam_id = input()
        try:
            value = int(steam_id)
        except ValueError:
            ("Steam id must an integer")
            continue
        if len(steam_id) == 8:
            break
        else:
            ("Length of the ID must be 8")
        
    player_instance = dota_main.Playerdata(steam_id)
    df = player_instance.getPlayerData()     
     
    
    write_df_to_database(df, conn, 'match')
    insert_player(conn,int(value))
    

def write_df_to_database(df,conn,table):
    df.to_sql(f"{table}", conn, if_exists="replace") 
    

def main():
    OPTIONS = 4
    path = (f'{os.getcwd()}/dota.sqlite')    
    conn = init_database.create_connection(path)  
    create_db_tables(conn)

    print("Welcome to DotaData!")                     
    print("1 - Insert player into database                   ")
    print("2 - View players               ")
    print("3 - View matches                             ")
    print("4 - Display wordcloud of chat                 ")
    
    while(True):
        print("Choose option")
        option = input()
        try:
            value = int(option)
        except ValueError:
            print("Please select a numeric value")
            continue        
        if int(option) == 1:
            insert_player_to_db(conn)
        if int(option)== 2:
            view_players(conn)
        if int(option)== 3:
            view_matches(conn)

        else:
            print(f"Please select a valid number, maximum is {OPTIONS}")     

  
    #write_database(df,conn) 


if __name__ == "__main__":
    main()