import dota_main
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from PIL import Image
import WordCloud, STOPWORDS, ImageColorGenerator

def herodata(df,hero): 
    #function returns the rows from the dataframe where hero_id = hero (given as argument)
       
    databyheros = df.copy()
    #Filter dataframe by games (normal game mode) with chosen hero
    databyheros = databyheros[(databyheros.hero_id==hero) & (databyheros.game_mode ==1)]
    
    wins = databyheros[databyheros.win==1].shape[0]         
    games = databyheros.shape[0]
    losses = (games - wins)

    print(f"You have a total of {games} games as {hero} with a record of {wins} / {losses} ")   
    

print("Welcome to DotaData!")
print("Enter steam id:")
steam_id = int(input())

player_instance = dota_main.Playerdata(steam_id)
player_instance.getPlayerData()
player_data = player_instance.returndata()

while(True):
    print("Choose option:")
    print("1 - Hero stats")
    print("2 - Game stats")
    print("3 - Player stats")

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
            wc = WordCloud(background_color="white", max_words=10).generate
            plt.imshow(wc)