import requests
import pandas as pd
import numpy as np
import api_connect

class Playerdata:

    def __init__(self, playerid):
        self.player = playerid
        self.df = 0
        self.ef = 0
    
    def getheroes(self):  
        URL = "https://api.opendota.com/api/heroes"
        r = requests.get(url=URL)
        data = r.json()
        heroes = {}
        for i in range(len(data)):
            heroes[data[i]["id"]] = data[i]["localized_name"]
        return heroes   
 
    #Fetch match data for Player -> create dataframe
    
    def getPlayerData(self):   
    
        #get wins
        x = api_connect.Api(f"https://api.opendota.com/api/players/{self.player}/matches?win=1")
        data = x.getdata()  
        Playerdata.df = pd.DataFrame.from_dict(data)
        wins = np.ones(len(Playerdata.df))
        Playerdata.df['win'] = wins.astype(int)       
        Playerdata.df['hero_id'] = Playerdata.df['hero_id'].map(self.getheroes())

        #get losses
        y = api_connect.Api(f"https://api.opendota.com/api/players/{self.player}/matches?win=0")
        data2 = y.getdata()
        Playerdata.ef = pd.DataFrame.from_dict(data2)
        losses = np.zeros(len(Playerdata.ef))
        Playerdata.ef['win'] = losses.astype(int)
        Playerdata.ef['hero_id'] = Playerdata.ef['hero_id'].map(self.getheroes())
     
        #combine wins and losses
        Playerdata.df = pd.concat([Playerdata.df,Playerdata.ef],ignore_index=True)
        Playerdata.df = self.convertTime(Playerdata.df)

    def convertTime(self,df):
        #Convert timestamp from s since epoch to datetime
        df['start_time'] = df['start_time'].astype('float64')
        df['start_time'] = pd.to_datetime(df['start_time'],unit='s')
        df['start_time'] = df['start_time'].dt.date
        return(df)
    
    def wordCloud(self):
        x = api_connect.Api(f"https://api.opendota.com/api/players/{self.player}/wordcloud")
        data = x.getdata()
        return data 

    def returndata(self):
        return Playerdata.df


