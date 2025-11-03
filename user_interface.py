import dota_main
import pandas as pd
import numpy as np
import init_database
import dota_main
import os.path
from init_database import DotaDB
from datetime import date

def main():
    #Main loop for program execution.
    dbms = init_database.DotaDB()    
    
    #Uncomment these two lines to recreate the database
    #dbms.create_tables()
    #dbms.insert_heroes()

    OPTIONS = 4


    print("Welcome to DotaData!")                     
    print("1 - Insert players matches into database")
    print("2 - View database statistics")
    print("3 - Read players matches to csv")       
    print("4 - Suggest hero")
    
    while(True):
        print("Choose option")
        option = input()
        try:
            value = int(option)
        except ValueError:
            print("Please select a numeric value")
            continue   

        if value == 1:
            # Inserts player and their match data to the database based on the users steam id.
            # Luo Player - olion, joka hakee tietokannasta tiedot -> init -> getplayerdata(päiviä taaksepäin) ->  insert_matches_to_db(Player-olio) ->  write df to database 
            steamid = get_steam_id()            
            #dbms.insert_player_to_db(dota_main.Playerdata(steamid))
            dbms.insert_matches_to_db(dota_main.Playerdata(steamid,100))            
            continue

        if value == 2:
            # Check the players currently in the database + the amount of matches.           
            dbms.get_summary()
            continue 

        if value == 3:
            # Writes player data to a csv-file based on steam id. 
           steamid = get_steam_id()
           current_date = date.today() 
           df = dbms.read_matches_to_df(dota_main.Playerdata(steamid).steamid)
           df = dbms.fill_team_data_to_matches(df)
           df.to_csv(f'./matches_{steamid}_{current_date}.csv')
           continue 

        if value==4:
            suggest_hero(dbms)   
            continue        

        else:
            print(f"Please select a valid number, maximum is {OPTIONS}")     

def get_steam_id():  
      
    while(True):
        print("Enter steam ID:")
        steam_id = input()
        try:
            value = int(steam_id)
        except ValueError:
            print("Steam id must an integer")
            continue
        if len(steam_id) >= 5:
            break
        else:
            print("Length of the ID must be 8")
    return value  

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