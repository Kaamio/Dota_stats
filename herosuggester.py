import pandas as pd
from dota_main import Playerdata


def get_matchups(self, herolist):
    df = pd.read_csv('./df_with_enemy_teams.csv')
    print



def get_hero_matchups(self,herolist):       
       
        enemy_lineup = []               
        
        for hero in herolist:
            query = f"SELECT id from HEROES where localized_name = '{hero}' "  
            hero = self.execute_query(query)
            enemy_lineup.append(hero)        

        matchup_df = pd.DataFrame()

        for idx,heroid in enumerate(enemy_lineup):            
            data = self.getdata(f"https://api.opendota.com/api/heroes/{heroid[0][0]}/matchups")
            df = pd.DataFrame.from_dict(data)
            df['win%'] = df['wins']/df['games_played']
            df.drop(columns=['games_played', 'wins'],inplace=True)
            df.set_index('hero_id',inplace=True)
            
            if matchup_df.empty:
                matchup_df = df                
            else:
                matchup_df = matchup_df.merge(df,left_index=True, right_index=True,suffixes=(f'_{enemy_lineup[idx-1][0][0]}',f'_{heroid[0][0]}'))    
        
        matchup_df['combined_win_%'] = matchup_df.mean(axis=1)        
        matchup_df.sort_values(by='combined_win_%',inplace=True)
        print(matchup_df.head())
        
        query = (f"SELECT localized_name from HEROES where id = '77' ")
       
        suggestion = self.execute_query(query)
        print(suggestion)