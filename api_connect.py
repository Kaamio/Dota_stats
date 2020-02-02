
import requests

class Api:

    def __init__(self, url):
        self.urli = url        

    def getdata(self):        
        result = requests.get(url=self.urli)
        data = result.json()
        return data

