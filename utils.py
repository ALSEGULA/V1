# Fonctions qui ne sont pas liees a une classe

import Environnement 
import mainDependencies
import pythoncom
import os
import sys
import time # pour les tests

from Serrage import Serrage
from Pcm import Pcm
from Pince import Pince
from getApplicationPath import getApplicationPath

from dotenv import set_key

#TODO : ecrire une fonction pour fermer automatiquement la feneêtre qui s'ouvre  a l'appel de la fonction de mesure d'inertie

# fonction pour recuperer les coordonnees de la bounding box en nombre exploitable
def cleanAndConvert(value):
    # Remove units (e.g., "mm")
    value = value.replace("mm", "").strip()
    # Replace comma with dot for decimal numbers
    value = value.replace(",", ".")
    # Convert to float
    return float(value)

# function for getting bounding box parameters associated to a specified product of name 'product_name' in the active document
# if the object studied is not a product, the name of the parent product has to be given
def getBoundingBoxParameters(env):
    parameters = env.product.parameters
    BBOx,BBOy,BBOz,BBLx,BBLy,BBLz = None,None,None,None,None,None

    for p in parameters:
        if env.product.name in p.name:
            if "BBOx" in p.name:
                BBOx = cleanAndConvert(p.value_as_string())
            elif "BBOy" in p.name:
                BBOy = cleanAndConvert(p.value_as_string())
            elif "BBOz" in p.name:
                BBOz = cleanAndConvert(p.value_as_string())
            elif "BBLx" in p.name:
                BBLx = cleanAndConvert(p.value_as_string())
            elif "BBLy" in p.name:
                BBLy = cleanAndConvert(p.value_as_string())
            elif "BBLz" in p.name:
                BBLz = cleanAndConvert(p.value_as_string())

    if None in [BBOx, BBOy, BBOz, BBLx, BBLy, BBLz]:
        raise ValueError(f"get_bounding_box_parameters : impossible to get BBO and BBL parameters for {env.product.name}")

    return [BBOx,BBOy,BBOz,BBLx,BBLy,BBLz]

# probleme : les arguments sont des copies de l'objet, pas l'objet...
def selectParts(env,pince,serrage,pcm,selection_event):
    inertia_cmd_name = "Mesures d'inertie" 
    selection = env.document.selection
    selection.clear

    # recuperation du chemin ou est situe l'executable
    application_path = getApplicationPath()
    # On en deduit que le fichier .env se situe dans le même répertoire
    env_path = os.path.join(application_path, '.env')

    c = 0
    while c < 3:

        # On demande a l'utilisateur de selectionner le PCM, puis le serrage, puis le(s) pince(s)
        if c == 0:
            #set_key('.env', 'TEXT_LABEL', "Sélectionner le PCMFRA") # ne fonctionne pas
            set_key(env_path, 'TEXT_LABEL', "Sélectionner le PCMFRA")
            selection_event.wait()
            while selection_event.get() != "confirmed":
                print("Il faut confirmer la sélection")
            selection_event.clear()
            set_key(env_path, 'TEXT_LABEL', "Patientez")
        elif c == 1:
            set_key(env_path, 'TEXT_LABEL', "Sélectionner le serrage")
            selection_event.wait()
            while selection_event.get() != "confirmed":
                print("Il faut confirmer la sélection")
            selection_event.clear()
            set_key(env_path, 'TEXT_LABEL', "Patientez")
        else:
            set_key(env_path, 'TEXT_LABEL', "Sélectionner la pince")
            selection_event.wait()
            while selection_event.get() != "confirmed":
                print("Il faut confirmer la sélection")
            selection_event.clear()
            set_key(env_path, 'TEXT_LABEL', "Patientez")

        # on recupere l'objet selectionne par l'utilisateur
        selection = env.document.selection
        selected_item = selection.item(1)
        catia_object = selected_item.reference
        object_selected_name = catia_object.name

        env.caa.start_command(inertia_cmd_name)

        try:

            # Retrieve the bounding box parameters from the CATPart
            BBOx,BBOy,BBOz,BBLx,BBLy,BBLz = getBoundingBoxParameters(env)
            BBO_BBL_parameters = [BBOx,BBOy,BBOz,BBLx,BBLy,BBLz]

            if c == 0:
                pcm.getCatiaInstance(object_selected_name)
                pcm.getPrincipalAxes()
                pcm.fillBBOArray(BBO_BBL_parameters)
                pcm.computeGeometricalCenter()
                pcm.getLocalCenter()
                pcm.getStickPoints()
            elif c == 1:
                serrage.getCatiaInstance(object_selected_name)
                serrage.getPrincipalAxes()
                serrage.fillBBOArray(BBO_BBL_parameters)
                serrage.computeGeometricalCenter()
                serrage.getLocalCenter()
                serrage.getStickPoints()
            else:
                pince.getCatiaInstance(object_selected_name)
                pince.getPrincipalAxes()
                pince.fillBBOArray(BBO_BBL_parameters)
                pince.computeGeometricalCenter()
                pince.getLocalCenter()
                pince.getCollisionHull()

        except Exception as e:
            set_key(env_path, 'TEXT_LABEL', f"L'exception {e} s'est produite")
            time.sleep(12)
            print(f"Error retrieving parameters: {e}")
            continue

        selection.clear()

        print("OK suivant")

        c += 1

def startBackend(selection_event):

    # Initialiser COM dans ce thread
    pythoncom.CoInitialize()

    try:

        env = Environnement.Environnement()
        env.caa = mainDependencies.catia()
        env.document = env.caa.active_document  # recuperer le document catia ouvert au lancement du programme
        env.product = env.document.product
        env.spa_i = env.document.spa_workbench().inertias

        serrage = Serrage(env)
        pcm = Pcm(env)
        pince = Pince(env)

        selectParts(env,pince,serrage,pcm,selection_event)

        serrage.positionOntoPCM(pcm.global_stick_points,pcm.name,pcm.path)

        serrage.update() # mise a jour necessaire car le serrage a bouge

        serrage.getCollisionHull()

        serrage.rotateUntilNoCollision(pince.global_collision_hull)

    finally:
        # Nettoyage COM
        pythoncom.CoUninitialize()