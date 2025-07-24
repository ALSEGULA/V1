# classe serrage

import json
from Object import Object

class Serrage(Object):
    def __init__(self):
        self.local_stick_points = None
        self.global_stick_points = None
        object_serrage = super().__init__()

    def getCatiaInstance(self,env,name="SERRAGE_DIN_040.1",path=[]):
        self.catia_instance = super().getChild(env,name,path)

    def getStickPoints(self):
        with open('points.json', 'r') as f:
            data = json.load(f)
        self.local_stick_points = data.get("stickPointsSerrage", [])
        self.global_stick_points = self.convertLocalToGlobal(self.local_stick_points)
