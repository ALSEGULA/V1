# classe Pince

import json
import os

from Object import Object
from getApplicationPath import getApplicationPath

class Pince(Object):
    def __init__(self,env):
        super().__init__(env)
        self.local_collision_hull = None
        self.global_collision_hull = []

    def getCatiaInstance(self,name,path=["ENVIRONNEMENT.1", "CYCLE/MURS.1","SOUDURE.1","OP95_PINCE_A6.1"]):
        self.catia_instance = super().getChild(name,path)

    # fonction qui complete la variable membre local_collision_hull en allant chercher les valeurs dasn le fichier points.json,
    # convertit ces points dans le repère global et enregistre le résultat dans global_collision_hull
    def getCollisionHull(self):
        application_path = getApplicationPath()
        parent_path = os.path.dirname(application_path)  
        # Chemin vers le fichier points.json qui doit etre place dans le repertoire parent de l'executable
        points_path = os.path.join(parent_path, 'points.json')
        with open(points_path, 'r') as f:
            data = json.load(f)
        self.local_collision_hull = data.get("collisionHullPince",[])
        for collision_hull in self.local_collision_hull:
            self.global_collision_hull.append(self.convertLocalToGlobal(collision_hull))