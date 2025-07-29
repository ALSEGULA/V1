# classe et dataclass: majuscule a la premiere lettre
# fonction : CamelCase
# variable : nom_de_la_variable

# ATtention : L'ordre des points definis dans points.json est important !

import mainDependencies
from utils import *
import Environnement 

from Serrage import Serrage
from Pcm import Pcm
from Pince import Pince
from Sphere import Sphere

def main():
    env = Environnement.Environnement()
    env.caa = mainDependencies.catia()
    env.document = env.caa.active_document  # recuperer le document catia ouvert au lancement du programme
    env.product = env.document.product
    env.spa_i = env.document.spa_workbench().inertias

    serrage = Serrage(env)
    pcm = Pcm(env)
    pince = Pince(env)

    selectParts(env,pince,serrage,pcm)

    pcm.getStickPoints()
    serrage.getStickPoints()

    serrage.alignOrientedPlans(pcm.global_stick_points)
    serrage.stickToPCM(pcm.global_stick_points)
    serrage.rotateToStickToPCM(pcm.global_stick_points,pcm.name,pcm.path)

    # mise a jour
    serrage.getCOG()
    serrage.getFrameConversionMatrix()
    serrage.computeGeometricalCenter()
    serrage.getLocalCenter()
    serrage.getRotationAxis()
    ##

    pince.getCollisionHull()
    serrage.getCollisionHull()

    serrage.rotateUntilNoCollision(pince.global_collision_hull)

    """
    input("Continuer ? ")

    sphere1 = Sphere(env,"Sphere3.1",[])
    sphere2 = Sphere(env,"Sphere3.2",[])
    sphere3 = Sphere(env,"Sphere3.3",[])
    sphere4 = Sphere(env,"Sphere3.4",[])
    sphere5 = Sphere(env,"Sphere3.5",[])
    sphere6 = Sphere(env,"Sphere3.6",[])
    sphere7 = Sphere(env,"Sphere3.7",[])
    sphere8 = Sphere(env,"Sphere3.8",[])

    sphere1.positionInGlobalCoordinates(serrage.global_collision_hull[0][0],serrage.global_collision_hull[0][1],serrage.global_collision_hull[0][2])
    sphere2.positionInGlobalCoordinates(serrage.global_collision_hull[1][0],serrage.global_collision_hull[1][1],serrage.global_collision_hull[1][2])
    sphere3.positionInGlobalCoordinates(serrage.global_collision_hull[2][0],serrage.global_collision_hull[2][1],serrage.global_collision_hull[2][2])
    sphere4.positionInGlobalCoordinates(serrage.global_collision_hull[3][0],serrage.global_collision_hull[3][1],serrage.global_collision_hull[3][2])
    sphere5.positionInGlobalCoordinates(serrage.global_collision_hull[4][0],serrage.global_collision_hull[4][1],serrage.global_collision_hull[4][2])
    sphere6.positionInGlobalCoordinates(serrage.global_collision_hull[5][0],serrage.global_collision_hull[5][1],serrage.global_collision_hull[5][2])
    sphere7.positionInGlobalCoordinates(serrage.global_collision_hull[6][0],serrage.global_collision_hull[6][1],serrage.global_collision_hull[6][2])
    sphere8.positionInGlobalCoordinates(serrage.global_collision_hull[7][0],serrage.global_collision_hull[7][1],serrage.global_collision_hull[7][2])
    """
    
if __name__ == "__main__":
    main()