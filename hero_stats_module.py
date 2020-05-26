import pandas as import pd
import numpy as np

carry_heroes = []
support_heroes = []

heroes = dota_main.Playerdata(steam_id)

def win_percentage_by_hero(df,hero): 
    #function returns the rows from the dataframe where hero_id = hero (given as argument)
    
    databyheros = df.copy()
    #Filter dataframe by games (normal game mode) with chosen hero
    databyheros = databyheros[(databyheros.hero_id==hero) & (databyheros.game_mode ==1)]
    
    wins = databyheros[databyheros.win==1].shape[0]         
    games = databyheros.shape[0]
    losses = (games - wins)

    print(f"You have a total of {games} games as {hero} with a record of {wins} / {losses} ")  

def win_percentage_by_hero(df):
    