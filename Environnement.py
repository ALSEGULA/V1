# Infos liees a l'environnement de travail reunies dans une structure ( dataclass en python)

from dataclasses import dataclass

@dataclass
class Environnement:
    caa: object = None
    document: object = None
    product: object = None
    spa_i: object = None
    com_object: object = None