import dota_main
import init_database

class Player:

    def __init__(self,steam_id):
        self.steam_id = steam_id

    def insert_player_to_db(self,conn):
        print("Enter steam ID:")
        while(True):
            steam_id = input()
            try:
                value = int(steam_id)
            except ValueError:
                ("Steam id must an integer")
                continue
            if len(steam_id) == 8:
                break
            else:
                ("Length of the ID must be 8")
        
        player_instance = dota_main.Playerdata(steam_id)
        df = player_instance.getPlayerData() 
        
    def get_steamid(self):
        return self.steam_id    




   