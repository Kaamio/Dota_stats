import sqlite3
import os
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import select
import sqlalchemy as db
import pandas as pd
import numpy as np
import api_connect
import requests
import time

#Table names
#PLAYERS = "players"
#MATCHES = 'matches'
#HEROES = "heroes"
roles = ['Carry', 'Support', 'Disabler', 'Lane support', 'Initiator', 'Jungler', 'Support', 'Durable', 'Nuker', 'Pusher', 'Escape']

class DotaDB:
    
    db_engine = None

    def __init__(self, username='', password=''):   
        self.db_engine = create_engine(f'sqlite:///dotadata.db')
        
    def initiate_database(self):

        # Create Tables
        self.create_db_tables()
        # Insert heroes into database
        self.insert_heroes_to_db()

    #def delete_table(self,table):        
        #Not implemented

    def get_hero_matchups(self,herolist):       
       
        enemy_lineup = []               
        
        for hero in herolist:
            query = f"SELECT id from HEROES where localized_name = '{hero}' "  
            hero = self.execute_query(query)
            enemy_lineup.append(hero)        

        matchup_df = pd.DataFrame()

        for idx,heroid in enumerate(enemy_lineup):
            matchups = api_connect.Api(f"https://api.opendota.com/api/heroes/{heroid[0][0]}/matchups")
            data = matchups.getdata()
            df = pd.DataFrame.from_dict(data)
            df['win%'] = df['wins']/df['games_played']
            df.drop(columns=['games_played', 'wins'],inplace=True)
            df.set_index('hero_id',inplace=True)
            
            if matchup_df.empty:
                matchup_df = df                
            else:
                matchup_df = matchup_df.merge(df,left_index=True, right_index=True,suffixes=(f'_{enemy_lineup[idx-1][0][0]}',f'_{heroid[0][0]}'))    
        
        matchup_df['combined_win_%'] = matchup_df.mean(axis=1)
        #hero_suggestion = matchup_df[matchup_df['combined_win_%'] == matchup_df['combined_win_%'].min()]
        matchup_df.sort_values(by='combined_win_%',inplace=True)
        print(matchup_df.head())
        
        query = (f"SELECT localized_name from HEROES where id = '77' ")
       
        suggestion = self.execute_query(query)
        print(suggestion)
        
      

    def insert_heroes_to_db(self):
        
        api_connection = api_connect.Api(f"https://api.opendota.com/api/heroes")
        data = api_connection.getdata()
        heroes_df = pd.DataFrame.from_dict(data)
        

        role_matrix = np.zeros((heroes_df.shape[0], len(roles)))
        role_matrix = pd.DataFrame(role_matrix)

        heroes_df = pd.concat([heroes_df,role_matrix],axis=1) 
        for idx,role in enumerate(roles):
            heroes_df.rename(columns={idx : role},inplace=True )
        

        for idx,row in heroes_df.iterrows():
            for role in row['roles']:
                heroes_df.iloc[idx,heroes_df.columns.get_loc(role)] = 1
        heroes_df.drop(['roles'],axis=1,inplace=True)
        self.write_df_to_database('heroes',heroes_df)   

   
    def insert_player_data(self,data):
        # Insert Data 
        query = f"INSERT INTO players (steam_id) " \
                "VALUES ({data});"
        self.execute_query(query)
        

    def create_db_tables(self):
        metadata = MetaData()

        matches = Table('matches', metadata,
        Column('match_id', Integer, primary_key=True),
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
        Column('lane', Integer),
        Column('lane_role', Integer),
        Column('is_roaming', Integer),
        Column('cluster', Integer),
        Column('leaver_status', Integer),
        Column('party_size', Integer),
        Column('win', Integer))      
        
        players = Table('players', metadata,
        Column('steam_id', Integer, primary_key=True))        

        heroes = Table('heroes', metadata,
        Column('id', Integer, primary_key=True),
        Column('name',String),
        Column('localized_name', String),
        Column('primary_attr', String),
        Column('attack_type',String),
        Column('roles', String))

        try:
            metadata.create_all(self.db_engine)
            print("Tables created")
        except Exception as e:
            print("Error occurred during Table creation!")
            print(e)

    def execute_query(self, query):
        if query == "" : return
        print(query)
        with self.db_engine.connect() as connection:
            try:
                results = connection.execute(query)
                return results.fetchall()
            except Exception as e:
                print(e)   

    def print_all_data(self, table='', query=''):
        query = f"SELECT * FROM {table};"
        print(query)
        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)
            except Exception as e:
                print(e)
            else:
                for row in result:
                    print(row) # print(row[0], row[1], row[2])
                result.close()
        print("\n")

    def read_matches_to_df(self):
        query = "SELECT * FROM matches"
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
            if row['enemy_team'] != '0.0':
                continue
            radiant = []
            dire =[]
            #If match duration is less than 10 minutes, skip it
            if row['duration']<600:
                continue
            
            #Get match data from open dota, parse response
            match = row['match_id']    
            player_req = requests.get(f"{url}{match}")
            if player_req:
                time.sleep(1)            
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
        df.to_sql(f"{table}", self.db_engine, if_exists="append")


 



    