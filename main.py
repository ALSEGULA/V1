# classe et dataclass: majuscule a la premiere lettre
# fonction : CamelCase
# variable : nom_de_la_variable

import mainDependencies
from functions import *
import Environnement 

from Serrage import Serrage
from Pcm import Pcm
from Pince import Pince

def main():
    env = Environnement.Environnement()
    env.caa = mainDependencies.catia()
    env.document = env.caa.active_document  # recuperer le document catia ouvert au lancement du programme
    env.product = env.document.product
    env.spa_i = env.document.spa_workbench().inertias

    serrage = Serrage()
    pcm = Pcm()
    pince = Pince()

    selectParts(env,pince,serrage,pcm)

    pcm.getStickPoints()
    serrage.getStickPoints()

if __name__ == "__main__":
    main()