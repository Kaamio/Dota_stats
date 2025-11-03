import requests
cimport numpy as np
import pandas as pd


class Playerdata:

    def __init__(self, steamid, days_backwards=''):
        self.steamid = steamid
        self.df = self._getPlayerData(days_backwards)
        self.ef = 0    
    
    def _getPlayerData(self,days_back):
    
        #get wins      
        data = self.getdata(f"https://api.opendota.com/api/players/{self.steamid}/matches?win=1&date={days_back}")
        if data:         
            df = pd.DataFrame.from_dict(data)
            wins = np.ones(len(df))
            df['win'] = wins.astype(int)       
            df['hero_id'] = df['hero_id'].map(self.getheroes())
        else:            
            return False

        #get losses        
        data2 = self.getdata(f"https://api.opendota.com/api/players/{self.steamid}/matches?win=0&date={days_back}")
        self.ef = pd.DataFrame.from_dict(data2)
        losses = np.zeros(len(self.ef))
        self.ef['win'] = losses.astype(int)
        self.ef['hero_id'] = self.ef['hero_id'].map(self.getheroes())
     
        #combine wins and losses
        df = pd.concat([df,self.ef],ignore_index=True)
        df = self.convertTime(df)
        df['steam_id'] = self.steamid

        return df

    def getdata(self,urli):              
        result = requests.get(urli)
        if result:
            data = result.json()
        else:
            print("No data for that player")
            return False    
        return data

    def getheroes(self):  
        URL = "https://api.opendota.com/api/heroes"
        r = requests.get(url=URL)
        data = r.json()
        heroes = {}
        for i in range(len(data)):
            heroes[data[i]["id"]] = data[i]["localized_name"]
        return heroes   

    def convertTime(self,df):
        #Convert timestamp from s since epoch to datetime
        df['start_time'] = df['start_time'].astype('float64')
        df['start_time'] = pd.to_datetime(df['start_time'],unit='s')
        df['start_time'] = df['start_time'].dt.date
        return(df)
    


