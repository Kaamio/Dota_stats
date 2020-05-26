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
        Playerdata.df['steam_id'] = self.player
        return Playerdata.df

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

#    def returndata(self):
#        return Playerdata.df
'''
df['start_time']<'2012-10-21' = 6.75
df['start_time']<'2012-12-15' = 6.76
df['start_time']<'2013-05-03' = 6.77
df['start_time']<'2013-10-21' = 6.78
df['start_time']<'2014-01-27' = 6.80
df['start_time']<'2014-04-29' = 6.81
df['start_time']<'2014-09-24' = 6.82
df['start_time']<'2014-12-17' = 6.83
df['start_time']<'2015-04-30' = 6.84
df['start_time']<'2015-09-24' = 6.85
df['start_time']<'2015-12-16' = 6.86
df['start_time']<'2016-04-25' = 6.87
df['start_time']<'2016-06-12' = 6.88
df['start_time']<'2016-12-12' = 7.00
df['start_time']<'2017-05-15' = 7.06
df['start_time']<'2017-10-31' = 7.07
df['start_time']<'2018-03-01' = 7.10
df['start_time']<'2018-03-29' = 7.12
df['start_time']<'2018-04-26' = 7.14
df['start_time']<'2018-05-27' = 7.16
df['start_time']<'2018-07-29' = 7.19
df['start_time']<'2018-11-19' = 7.20
df['start_time']<'2019-01-29' = 7.21
df['start_time']<'2019-05-24' = 7.22
df['start_time']<'2019-11-26' = 7.23
df['start_time']<'2020-01-26' = 7.24
df['start_time']<'2020-03-17' = 7.25
df['start_time']<'2020-04-17' = 7.26
'''
