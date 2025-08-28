# Fonctions qui ne sont pas liees a une classe

import Environnement 
import mainDependencies
import pythoncom
import os
import numpy as np
import time # pour les tests

from Serrage import Serrage
from Pcm import Pcm
from Pince import Pince
from Sphere import Sphere
from getApplicationPath import getApplicationPath

from dotenv import set_key

import win32con
import win32gui

import win32com.client # pour les tests

from pycatia.space_analyses_interfaces.inertia import Inertia # pour les tests : voir si on garde ou pas

#TODO : ecrire une fonction pour fermer automatiquement la fenêtre qui s'ouvre  a l'appel de la fonction de mesure d'inertie

# Fonction pour fermer la fenetre de mesure d'inertie quand la commande est appelee
# TODO : ne fonctionne pas, a debugger
def closeInertiaWindow():
    handle = win32gui.FindWindow(None, "Mesure d'inertie")
    win32gui.PostMessage(handle, win32con.WM_CLOSE, 0, 0)

# Function for giving all children in a specified path given in argument
def getChildrenFromPath(env,path):
    current_level = env.product
    # Parcourir chaque niveau du chemin
    for folder_name in path:
        children = current_level.get_children()
        found = False
        for child in children:
            if child.name == folder_name:
                current_level = child
                found = True
                break
        if not found:
            raise ValueError(f"Class Object - getChild() : incorrect path {path}")
        
    # Une fois au bon niveau, rechercher la pièce
    return current_level.get_children()


def selectPinces(env,names):
    array = []

    pince = Pince(env)
    path = pince.getTreePath('PINCE_TREE_PATH')

    # recuperation du chemin ou est situe l'executable
    application_path = getApplicationPath()
    # On en deduit que le fichier .env se situe dans le même répertoire
    env_path = os.path.join(application_path, '.env')

    set_key(env_path, 'TEXT_LABEL', f"Patienter - Sélection des pinces en cours")
        
    # Une fois au bon niveau, rechercher la pièce
    children = getChildrenFromPath(env,path)
    count = 0
    for child in children:
        # pour les tests, on choisit les pinces que le programme sélectionne
        if child.name in names:
            pince_studied = Pince(env)
            pince_studied.getCatiaInstance(child.name)
            pince_studied.getPrincipalAxes()
            pince_studied.getBBOParameters(env)
            pince_studied.computeGeometricalCenter()
            pince_studied.getLocalCenter()
            pince_studied.getCollisionHull()
            array.append(pince_studied)
            count+=1
            set_key(env_path, 'TEXT_LABEL', f"Patienter - {count} pinces ont été enregistrées")

    print("Fin de selectPinces")
    return array

def selectPCM(env,names):
    array = []

    pcm = Pcm(env)
    path = pcm.getTreePath('PCM_TREE_PATH')

    # recuperation du chemin ou est situe l'executable
    application_path = getApplicationPath()
    # On en deduit que le fichier .env se situe dans le même répertoire
    env_path = os.path.join(application_path, '.env')

    set_key(env_path, 'TEXT_LABEL', f"Patienter - Sélection des PCM en cours")
        
    # Une fois au bon niveau, rechercher la pièce
    children = getChildrenFromPath(env,path)
    count = 0
    for index,child in enumerate(children):
        # pour les tests, on choisit les pinces que le programme sélectionne
        if child.name in names:
            pcm_studied = Pcm(env)
            pcm_studied.getCatiaInstance(child.name)
            pcm_studied.getPrincipalAxes()
            pcm_studied.getBBOParameters(env)
            pcm_studied.computeGeometricalCenter()
            pcm_studied.getLocalCenter()
            pcm_studied.getStickPoints()
            array.append(pcm_studied)
            count += 1
            set_key(env_path, 'TEXT_LABEL', f"Patienter - {count} PCM ont été enregistrés")

    print("Fin de selectPcm")
    return array

def selectSerrages(env,names):
    array = []

    pcm = Pcm(env)
    path = pcm.getTreePath('SERRAGE_TREE_PATH')

    # recuperation du chemin ou est situe l'executable
    application_path = getApplicationPath()
    # On en deduit que le fichier .env se situe dans le même répertoire
    env_path = os.path.join(application_path, '.env')

    set_key(env_path, 'TEXT_LABEL', f"Patienter - Enregistrement des serrages en cours")
        
    # Une fois au bon niveau, rechercher la pièce
    children = getChildrenFromPath(env,path)
    count = 0
    for index,child in enumerate(children):
        # pour les tests, on choisit les pinces que le programme sélectionne
        if child.name in names:
            serrage_studied = Serrage(env)
            serrage_studied.getCatiaInstance(child.name)
            serrage_studied.getPrincipalAxes()
            serrage_studied.getBBOParameters(env)
            serrage_studied.computeGeometricalCenter()
            serrage_studied.getLocalCenter()
            serrage_studied.getStickPoints()
            array.append(serrage_studied)
            count += 1
            set_key(env_path, 'TEXT_LABEL', f"Patienter - {count} serrages ont été enregistrés")

    print("Fin de selectSerrage")
    return array

"""
def selectParts(env,pince,serrage,pcm,selection_event):
    inertia_cmd_name = "Mesures d'inertie" 
    selection = env.document.selection
    selection.clear

    # recuperation du chemin ou est situe l'executable
    application_path = getApplicationPath()
    # On en deduit que le fichier .env se situe dans le même répertoire
    env_path = os.path.join(application_path, '.env')

    c = 0
    #c = 1 # pour les tests, on enregistre uniquement le serrage
    while c < 3:

        # On demande a l'utilisateur de selectionner le PCM, puis le serrage, puis le(s) pince(s)
        if c == 0:
            set_key(env_path, 'TEXT_LABEL', "Sélectionner le PCM")
            selection_event.wait()
            while selection_event.get() != "confirmed": 
                # cette partie là est inutile pour le moment ( un seul bouton )
                print("Il faut confirmer la sélection")
            selection_event.clear()
            set_key(env_path, 'TEXT_LABEL', "Patienter")

        elif c == 1:
            set_key(env_path, 'TEXT_LABEL', "Sélectionner le serrage")
            selection_event.wait()
            while selection_event.get() != "confirmed":
                print("Il faut confirmer la sélection")
            selection_event.clear()
            set_key(env_path, 'TEXT_LABEL', "Patienter")

        else:
            set_key(env_path, 'TEXT_LABEL', "Sélectionner la pince")
            selection_event.wait()
            while selection_event.get() != "confirmed":
                print("Il faut confirmer la sélection")
            selection_event.clear()
            set_key(env_path, 'TEXT_LABEL', "Patienter") 

        # on recupere l'objet selectionne par l'utilisateur
        selection = env.document.selection
        selected_item = selection.item(1)
        catia_object = selected_item.reference
        object_selected_name = catia_object.name

        #env.caa.start_command(inertia_cmd_name)

        try:
            if c == 0:
                pcm.getCatiaInstance(object_selected_name)
                pcm.getPrincipalAxes()
                pcm.getBBOParameters(env)
                pcm.computeGeometricalCenter()
                pcm.getLocalCenter()
                pcm.getStickPoints()
            elif c == 1:
                serrage.getCatiaInstance(object_selected_name)
                serrage.getPrincipalAxes()
                serrage.getBBOParameters(env)
                serrage.computeGeometricalCenter()
                serrage.getLocalCenter()
                serrage.getStickPoints()
                # Pour les tests : on ne selectionne plus les pinces
                c += 1
            else:
                pince.getCatiaInstance(object_selected_name)
                pince.getPrincipalAxes()
                pince.getBBOParameters(env)
                pince.computeGeometricalCenter()
                pince.getLocalCenter()
                pince.getCollisionHull()

        except Exception as e:
            set_key(env_path, 'TEXT_LABEL', f"L'exception {e} s'est produite")
            time.sleep(12)
            print(f"Error retrieving parameters: {e}")
            continue

        selection.clear()
        #closeInertiaWindow()

        print("OK suivant")

        c += 1
"""

# TODO : il va falloir appeler une seule fois generate_ALLCATPart pour tous les PCM sinon il y aura le problème de surcharge memoire
# TODO : Autre probleme -> quand on cree un executable, on est oblige de kill le processus main.exe manuellement uune fois le programme termine

def startBackend(selection_event):

    # Initialiser COM dans ce thread
    pythoncom.CoInitialize()

    try:
        env = Environnement.Environnement()
        env.caa = mainDependencies.catia()
        env.document = env.caa.active_document  # recuperer le document catia ouvert au lancement du programme
        env.product = env.document.product
        env.spa_i = env.document.spa_workbench().inertias

        # test : initiliaser l'environnement com_object au demarrage
        env.com_object = win32com.client.Dispatch("CATIA.Application")
        env.com_object.Visible = True  # Optionnel : rendre CATIA visible ou non

        continuer = True

        while continuer:
            try:
                #serrage = Serrage(env)
                #pcm = Pcm(env)
                #pince = Pince(env) # inutile pour le test
                
                tab_pinces = selectPinces(env,["PINCE_A04_A05.7","PINCE_A04_A05.9"]) # pour les tests, on choisit les pinces que l'on sélectionne
                #tab_pinces_collision_hulls = [p.global_collision_hull for p in tab_pinces]
                tab_pcm = selectPCM(env,["APPUI-TOUCHE-PCM.3","APPUI-TOUCHE-PCM.8"]) # pour les tests, on choisit les pcm que l'on sélectionne
                tab_serrages = selectSerrages(env,["SERRAGE_DIN_040.1","SERRAGE_DIN_040.3"])

                #selectParts(env,pince,serrage,pcm,selection_event)
                print("tab_serrages : ", tab_serrages)

                for index,serrage in enumerate(tab_serrages):
                    print("\nOn va placer un nouveau serrage\n")
                    serrage.positionOntoPCM(tab_pcm[index].global_stick_points,tab_pcm[index].name,tab_pcm[index].path)
                    serrage.update()
                    serrage.getCollisionHull()
                    risky_pinces_collision_hulls = []
                    # on ne recupere que les pinces dans un certain rayon du PCM
                    for pince in tab_pinces:
                        # TODO : ATtention -> Cete definition de la grande diagonale est trop dependante de la manière dont les BBO de la pince ont été définis
                        longueur_grande_diagonale = np.linalg.norm(np.array(pince.BBO[0]) - np.array(pince.BBO[7]))
                        if 1000*np.linalg.norm(np.array(pince.cog)-np.array(tab_pcm[index].cog)) < longueur_grande_diagonale:
                            risky_pinces_collision_hulls.append(pince.global_collision_hull)
                            print("Ajout d'une pince a risque")
                    serrage.rotateUntilNoCollision(risky_pinces_collision_hulls)

                if input("Continuer ?") == 'n':
                    continuer = False
                

            except Exception as e:
                # recuperation du chemin ou est situe l'executable
                application_path = getApplicationPath()
                # On en deduit que le fichier .env se situe dans le même répertoire
                env_path = os.path.join(application_path, '.env')
                set_key(env_path, 'TEXT_LABEL', f"Erreur rencontrée : {e}")
                time.sleep(5)

    finally:
        # Nettoyage COM
        pythoncom.CoUninitialize()