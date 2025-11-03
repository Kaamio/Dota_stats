import sqlite3
import os
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import select
from datetime import date
import sqlalchemy
import pandas as pd
import numpy as np
import requests
import time

roles = ['Carry', 'Support', 'Disabler', 'Lane support', 'Initiator', 'Jungler', 'Support', 'Durable', 'Nuker', 'Pusher', 'Escape']

class DotaDB:
    
    db_engine = None

    def __init__(self, username='', password=''):   
        self.db_engine = create_engine(f'sqlite:///dotadata.db')        
        self.metadata = MetaData()
        self.players = Table('players', self.metadata,   # Define the 'players' table
            Column('steam_id', Integer, primary_key=True))
        
        self.matches = Table('matches', self.metadata, # Define 'matches' table
            Column('match_id', Integer),
            Column('player_slot', Integer),    
            Column('radiant_win', Integer),
            Column('duration', Integer),
            Column('game_mode', Integer),
            Column('lobby_type', Integer),
            Column('hero_id', String),    
            Column('start_time', String),
            Column('version', String),
            Column('kills', Integer),
            Column('deaths', Integer),
            Column('assists', Integer),
            Column('skill', Integer),  
            Column('leaver_status', Integer),
            Column('average_rank', Integer),
            Column('party_size', Integer),
            Column('win', Integer),
            Column('steam_id', Integer))

    def insert_heroes(self):
        # Insert heroes into database        
        data = self.getdata(f"https://api.opendota.com/api/heroes")
        heroes_df = pd.DataFrame.from_dict(data)  
        
        role_matrix = np.zeros((heroes_df.shape[0], len(roles)))
        role_matrix = pd.DataFrame(role_matrix)

        heroes_df = pd.concat([heroes_df,role_matrix],axis=1) 
        for idx,role in enumerate(roles):
            heroes_df.rename(columns={idx : role},inplace=True)        

        for idx,row in heroes_df.iterrows():
            for role in row['roles']:
                heroes_df.iloc[idx,heroes_df.columns.get_loc(role)] = 1
        heroes_df.drop(['roles'],axis=1,inplace=True)
        print(heroes_df.columns)
        self.write_df_to_database(table='heroes',df = heroes_df)

    def getdata(self,urli):              
        result = requests.get(urli)
        data = result.json()
        return data    

    #def delete_table(self,table):        
        #Not implemented

    

    def insert_player_to_db(self,player):
        if player.steamid:
            id = player.steamid
            connection = self.db_engine.connect() 
            insert_stmt = sqlalchemy.insert(self.players).values(steam_id =id)
            results = connection.execute(insert_stmt)   
            print(results.rowcount)
        else:
            print('Steam id not found!')   
        

    def insert_matches_to_db(self,player):       
        self.write_df_to_database(table='matches',df=player.df)     

    def create_tables(self):
        metadata = MetaData()

        self.matches.drop(self.db_engine)

        self.matches = Table('matches', metadata,
        Column('match_id', Integer),
        Column('player_slot', Integer),    
        Column('radiant_win', Integer),
        Column('duration', Integer),
        Column('game_mode', Integer),
        Column('lobby_type', Integer),
        Column('hero_id', String),    
        Column('start_time', String),
        Column('version', String),
        Column('kills', Integer),
        Column('deaths', Integer),
        Column('assists', Integer),
        Column('skill', Integer),       
        Column('leaver_status', Integer),
        Column('average_rank', Integer),
        Column('party_size', Integer),
        Column('win', Integer),
        Column('steam_id', Integer))      
        
        self.players = Table('players', metadata,
        Column('steam_id', Integer, primary_key=True))        

        self.heroes = Table('heroes', metadata,               
        Column('id', Integer, primary_key=True),
        Column('name',String),
        Column('localized_name', String),
        Column('primary_attr', String),
        Column('attack_type',String),
        Column('legs', Integer),
        Column('Carry', Integer),
        Column('Support', Integer),
        Column('Disabler',Integer),
        Column('Lane Support', Integer),
        Column('Initiator', Integer),
        Column('Jungler', Integer),      
        Column('Durable', Integer),
        Column('Nuker', Integer),
        Column('Pusher', Integer),
        Column('Escape', Integer))
        

        try:
            metadata.create_all(self.db_engine)
            print("Tables created")
        except Exception as e:
            print("Error occurred during Table creation!")
            print(e)

    def execute_query(self, query, params):
        if query == "" : return
        
        with self.db_engine.connect() as connection:
            try:
                results = connection.execute(query, params)
                return results.fetchall()
            except Exception as e:
                print(e)   

    def get_summary(self):
        connection = self.db_engine.connect()         
        select_stmt = sqlalchemy.select(self.players)  
        results = connection.execute(select_stmt)


        print('Matches in database:')
        select_stmt = sqlalchemy.select(self.matches)
        results = connection.execute(select_stmt)
        print(len(results.fetchall()))
            



    def print_all_data(self, table='', query=''):
        query = f"SELECT * FROM {table};"
        
        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)
            except Exception as e:
                print(e)
            else:
                for row in result:
                    print(row)
                result.close()
        print("\n")

    def read_matches_to_df(self,steamid):
        query = (f"SELECT * FROM matches WHERE steam_id = {steamid}")
        conn = self.db_engine.connect()
        df = pd.read_sql(query, conn) 
     
        zeros = np.zeros((df.shape[0],1))
        df['enemy_team'] = zeros
        df['ally_team'] = zeros
        df = df.astype({'enemy_team':object, 'ally_team':object})        
        resulting_df = self.fill_team_data_to_matches(df)
        return(resulting_df) 

    def read_heroes_to_df(self):
        query = "SELECT * FROM heroes"
        conn = self.db_engine.connect()
        df = pd.read_sql(query,conn)
        return df

    def fill_team_data_to_matches(self,df):
        url = 'https://api.opendota.com/api/matches/'        
        for ind,row in df.iterrows():            
            #if row['enemy_team'] != '0.0':
            #    continue
            
            radiant = []
            dire =[]
            
            #If match duration is less than 10 minutes, skip it
            if row['duration']<600:
                continue
            
            #Get match data from open dota, parse response
            match = row['match_id']    
            player_req = requests.get(f"{url}{match}")            
            if player_req:
                time.sleep(0.2) 
                print(row['match_id'])           
                try:
                    players_data = player_req.json()
                except Exception as e:
                    print(f'exception {e} occured in parsing')
                    df.to_csv(f"C:/Users/Markus/Python projects/Dota_stats/Dota_stats/matches_with_teams_{match}.csv")
                    time.sleep(5)
                    continue

                #Iterate over players in response, which contains the hero_id-value. Divide players into radiant/dire based on
                #the hero_id of the player.
    
                try:
                    for player in players_data['players']:                               
                        current_player = player['hero_id']
                        if player['isRadiant'] == True :           
                            radiant.append(current_player)
                        elif player['isRadiant'] == False:
                            dire.append(current_player)
                    if df.at[ind,'hero_id'] in radiant:
                        df.at[ind,'ally_team'] = radiant
                        df.at[ind,'enemy_team'] = dire
                    else:
                        df.at[ind,'ally_team'] = dire
                        df.at[ind,'enemy_team'] = radiant    
                
                except KeyError as e :                               
                    print(f"Something went wrong with {match}")
                    print(f'The error was {e}')
                    time.sleep(5)  
            else:
                print(f"something went wrong while fetching data for {match}")
                time.sleep(1)
        return df
        
    def view_data(self, playerid):
        query = f"select * from matches where steam_id = {playerid}"        
     
        try:
            result = pd.read_sql(query,
            con=self.db_engine,
            parse_dates = ['start_time'])
            
        except Exception as e:
            print(f"Exception {e} occured!")
        try:
            return result
        except UnboundLocalError as e:
            print('Player not found!')
            return
    
    def write_df_to_database(self,table,df):               
        df.to_sql(f"{table}", self.db_engine, if_exists="append",index=False)


 



    