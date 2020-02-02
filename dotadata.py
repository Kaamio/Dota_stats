import sqlite3
import os
match_id  player_slot  radiant_win  duration  game_mode  lobby_type          hero_id  start_time  version  kills  deaths  assists  skill  leaver_status  party_size  win
def deletetable():
    os.remove("DotaData.db")

def createdb():
    try:
        sqliteConnection = sqlite3.connect('DotaData.db')
        cursor = sqliteConnection.cursor()

        cursor.execute('''SELECT count(name) from sqlite_master WHERE type='table' AND name ='Heroes' ''')
        if cursor.fetchone()[0] == 1:
            print("Table allready exists")
            return
        createtable = '''CREATE TABLE Matchdata (
            id INTEGER PRIMARY KEY,
            player_slot INTEGER,
            radiant_win TEXT,
            duration INTEGER,
            game_mode INTEGER,
            lobby_type INTEGER,
            hero_name TEXT,
            start_time TIMESTAMP,
            version TEXT,
            kills INTEGER,
            deaths INTEGER,
            assists INTEGER,
            leaver_status INTEGER,
            party_size INTEGER,
            win INTEGER
        )'''

        
        print("Successfully Connected to SQLite")    
        cursor.execute(createtable)
        sqliteConnection.commmit()
        print("SQLite table created")
        cursor.close()

    except sqlite3.Error as error:
        print("Error while creating a sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("sqlite connection is closed")

deletetable()
#createdb()