# classe PCM

import json
import os

from Object import Object
from getApplicationPath import getApplicationPath

class Pcm(Object):
    def __init__(self,env):
        self.local_stick_points = None
        self.global_stick_points = None
        self.name = None
        self.path = None
        super().__init__(env)

    def getCatiaInstance(self,name,path=["ENVIRONNEMENT.1","PCM_FRA.1","PCM.1"]):
        self.name = name
        self.path = path
        self.catia_instance = super().getChild(name,path)

    def getStickPoints(self):
        application_path = getApplicationPath()
        parent_path = os.path.dirname(application_path)  
        # Chemin vers le fichier points.json qui doit etre place dans le repertoire parent de l'executable
        points_path = os.path.join(parent_path, 'points.json')
        with open(points_path, 'r') as f:
            data = json.load(f)
        self.local_stick_points = data.get("stickPointsPCM", [])
        self.global_stick_points = self.convertLocalToGlobal(self.local_stick_points)