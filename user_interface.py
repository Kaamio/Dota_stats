import dota_main
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import init_database
import os.path
import player
from init_database import DotaDB

def main():

    dbms = init_database.DotaDB()    
    #dbms.initiate_database()
    

    OPTIONS = 4


    print("Welcome to DotaData!")                     
    print("1 - Insert player into database")
    print("2 - View matches")
    print("3 - Read matches to csv")    
    print("4 - View stats")
    print("5 - Suggest hero")
    
    while(True):
        print("Choose option")
        option = input()
        try:
            value = int(option)
        except ValueError:
            print("Please select a numeric value")
            continue        
        if value == 1:
            insert_player_to_db(dbms)

        if value == 2:
            dbms.print_all_data(table='matches')
                      
        if value == 3:
           df = dbms.read_matches_to_df()
           df = dbms.fill_team_data_to_matches(df)
           df.to_csv("./matches_with_teams.csv")
                 
        if value==4:
            view_player_stats(dbms)

        if value == 5:
            suggest_hero(dbms)

        if value == 6:
            df = dbms.read_heroes_to_df()
            df.to_csv("./heroes_with_roles.csv")
        else:
            print(f"Please select a valid number, maximum is {OPTIONS}")     

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

def get_steam_id():
    print("Enter steam ID:")
    while(True):
        steam_id = input()
        try:
            value = int(steam_id)
        except ValueError:
            ("Steam id must an integer")
            continue
        if len(steam_id) >= 5:
            break
        else:
            ("Length of the ID must be 8")
    return value    

def insert_player_to_db(database):
    steam_id = get_steam_id()
        
    player_instance = dota_main.Playerdata(steam_id)
    df = player_instance.getPlayerData()     
    #player_id = player.Player(steam_id)    
    database.write_df_to_database(table='matches',df=df)
    #database.insert_player_data(player_id.get_steamid())

def view_player_stats(database):
    steam_id = get_steam_id()
    df = database.view_data(steam_id)
    print(df)

def suggest_hero(database):
    opponent_lineup = []
    while True:
        print(f"Enter enemy hero, enter 0 to stop ")
        hero = input()
        if hero == '0' : break   
        if len(opponent_lineup)<5:
            opponent_lineup.append(hero)
    database.get_hero_matchups(opponent_lineup)

if __name__ == "__main__":
    main()