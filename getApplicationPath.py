# fonction getApplicationPath(), separee du reste pour eviter les imports circulaires

import os
import sys

# Fonction qui recupere le chemin de l'executable 
def getApplicationPath():
    if getattr(sys, 'frozen', False):
        # Si le code est exécuté sous forme d'exécutable PyInstaller
        application_path = os.path.dirname(sys.executable)
    else:
        # Si le code est exécuté sous forme de script Python normal
        application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path