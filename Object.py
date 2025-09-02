# classe mere de serrage, pince et PCM

from pycatia.space_analyses_interfaces.inertia import Inertia
import numpy as np
import os

import time
import win32com.client

from getApplicationPath import getApplicationPath
from dotenv import load_dotenv

import pyautogui 

class Object:
    def __init__(self,env):
        self.catia_instance = None
        self.frame_conversion_matrix = None
        self.cog = None
        self.BBO = None
        self.env = env

    def getChild(self,name,path):
        current_level = self.env.product  # Commencer à partir du produit racine

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
        children = current_level.get_children()
        for child in children:
            if child.name == name:
                return child

        raise ValueError(f"Class Object - getChild() : incorrect name {name}")
    
    # function for getting bounding box parameters associated to the object 
    def getBoundingBoxParameters(self,env):
        parameters = env.product.parameters
        BBOx,BBOy,BBOz,BBLx,BBLy,BBLz = None,None,None,None,None,None

        # fonction pour recuperer les coordonnees de la bounding box en nombre exploitable
        def cleanAndConvert(value):
            # Remove units (e.g., "mm")
            value = value.replace("mm", "").strip()
            # Replace comma with dot for decimal numbers
            value = value.replace(",", ".")
            # Convert to float
            return float(value)

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
    
    #TODO : voir s'il n'est pas possible d'alléger la fonction ( seule la mediane est importante )
    def fillBBOArray(self,env):

        BBOx,BBOy,BBOz,BBLx,BBLy,BBLz = self.getBoundingBoxParameters(env)
        BBO_BBL_parameters = [BBOx,BBOy,BBOz,BBLx,BBLy,BBLz]

        BBOx = BBO_BBL_parameters[0]
        BBOy = BBO_BBL_parameters[1]
        BBOz = BBO_BBL_parameters[2]
        BBLx = BBO_BBL_parameters[3]
        BBLy = BBO_BBL_parameters[4]
        BBLz = BBO_BBL_parameters[5]
        
        A1x = self.principal_axes[0]
        A2x = self.principal_axes[1]
        A3x = self.principal_axes[2]
        A1y = self.principal_axes[3]
        A2y = self.principal_axes[4]
        A3y = self.principal_axes[5]
        A1z = self.principal_axes[6]
        A2z = self.principal_axes[7]
        A3z = self.principal_axes[8]

        self.BBO = [
                    [BBOx, BBOy, BBOz],
                    [BBOx + A1x * BBLx, BBOy + A1y * BBLx, BBOz + A1z * BBLx],
                    [BBOx + A2x * BBLy, BBOy + A2y * BBLy, BBOz + A2z * BBLy],
                    [BBOx + A3x * BBLz, BBOy + A3y * BBLz, BBOz + A3z * BBLz],
                    [BBOx + A1x * BBLx + A2x * BBLy, BBOy + A1y * BBLx + A2y * BBLy, BBOz + A1z * BBLx + A2z * BBLy],
                    [BBOx + A1x * BBLx + A3x * BBLz, BBOy + A1y * BBLx + A3y * BBLz, BBOz + A1z * BBLx + A3z * BBLz],
                    [BBOx + A2x * BBLy + A3x * BBLz, BBOy + A2y * BBLy + A3y * BBLz, BBOz + A2z * BBLy + A3z * BBLz],
                    [BBOx + A1x * BBLx + A2x * BBLy + A3x * BBLz, BBOy + A1y * BBLx + A2y * BBLy + A3y * BBLz, BBOz + A1z * BBLx + A2z * BBLy + A3z * BBLz]
                ]
    
    # Attention : il existe à l'heure actuelle une fonction getBoundingBoxParameters definie dans la classe object
    # qui sert à récupérer les paramètres de la BBO après que la commande de mesure d'inertie ait été lancée
    # Cette fonction là est plus complète : elle lance la commande pour complète la BBO
    def getBBOParameters(self,env):
        try:
            # Ouvrir une instance de CATIA via COM
            
            # Récupérer l'objet COM du produit
            selection = env.com_object.ActiveDocument.Selection
            selection.clear()  # Vider la sélection existante

            # Ajouter l'objet COM du produit à la sélection virtuelle
            selection.Add(self.catia_instance.com_object)  # Utilisation de com_object (en minuscule)

            # Lancer la commande "Mesures d'inertie"
            env.com_object.StartCommand("Mesures d'inertie")

            # Attendre que la commande se termine (une petite pause pour s'assurer que la commande est exécutée)
            time.sleep(10)  

            self.fillBBOArray(env)

            selection.clear() # test

            # On ferme la fenêtre de mesure d'inertie
            window = env.com_object.ActiveWindow
            if window is not None:
                window.Close()  
                # Il est necessaire de simuler des appuis sur echap ( tests avec 4 OK, parfois 3 pas suffisant )
                # pour fermer correcetement les fenêtres de mesure d'inertie
                time.sleep(0.25)
                pyautogui.press('esc')
                time.sleep(0.25)
                pyautogui.press('esc')
                time.sleep(0.25)
                pyautogui.press('esc')
                time.sleep(0.25)
                pyautogui.press('esc')

        except Exception as e:
            print(f"Erreur lors du lancement de la commande inertie sur {self.name}: {e}")

    
    # fonction qui renvoie un tableau rensiegnant le chemin pour aller chercher l'objet dans l'arborescence catia
    # la valeur de ce tableau est stockée dans la variable d'environnement de cle 'key'
    # TODO : cette fonction est maintenant obsolète, il va falloir la supprimer a terme
    # La fonction utilisée est maintenant dans utils
    def getTreePath(self,key):
        application_path = getApplicationPath()
        env_path = os.path.join(application_path, '.env')
        load_dotenv(env_path,override=True)

        # / separateur et // pour ignorer /
        # TODO : a commenter et arranger
        def customSplit(s):
            parts = []
            buffer = ""
            i = 0

            if s==None:
                return parts

            if len(s) == 0:
                return parts

            while i < len(s):
                if s[i] == "/":
                    if i + 1 < len(s) and s[i + 1] == "/":
                        buffer += "/"  # Ajoute un seul slash
                        i += 2         # Ignore les deux slashes
                    else:
                        parts.append(buffer)
                        buffer = ""
                        i += 1
                else:
                    buffer += s[i]
                    i += 1
            parts.append(buffer)  # Ajouter le dernier morceau
            return parts

        chemin = os.getenv(key)
        tableau_dossiers = customSplit(chemin)

        return tableau_dossiers

    def getPrincipalAxes(self):
        if self.catia_instance is None:
            raise ValueError("Appel à getPrincipalAxes() sur un objet sans instance catia")
        try:
            inertia = Inertia(self.env.spa_i.add(self.catia_instance).com_object)
            self.principal_axes = inertia.get_principal_axes()
        except Exception as e:
            print(f"Error with getPrincipalAxes() : {e}")
        
    # return geometrical center of BBO ( mediane_global )
    def computeGeometricalCenter(self):
        # Convert the input list to a numpy array for easier manipulation
        if self.BBO is None:
            print("Appel à computeGEometricalCenter() alors que la liste BBO est vide")
            return 
        
        points = np.array(self.BBO)
        geometrical_center = np.mean(points, axis=0)

        self.mediane_global = geometrical_center.tolist()

    # function for getting center of gravtity (cog)
    def getCOG(self):
        if self.catia_instance is None:
            raise ValueError("Appel à getCOG() sur un objet sans instance catia")
        try:
            inertia = Inertia(self.env.spa_i.add(self.catia_instance).com_object)
            self.cog = inertia.get_cog_position()
        except Exception as e:
            print(f"Error with getCOG(): {e}")

    # fonction qui renvoie la matrice de changement de base pour la conversion local->global
    def getFrameConversionMatrix(self):
        try:
            self.getPrincipalAxes()

            # Vecteurs des axes locaux
            local_x_axis = np.array([self.principal_axes[0], self.principal_axes[3], self.principal_axes[6]])
            local_y_axis = np.array([self.principal_axes[1], self.principal_axes[4], self.principal_axes[7]])
            local_z_axis = np.array([self.principal_axes[2], self.principal_axes[5], self.principal_axes[8]])

            # Matrice de rotation
            self.frame_conversion_matrix = np.array([local_x_axis, local_y_axis, local_z_axis]).T
        except Exception as e:
            print(f"Error with getFrameConversionMatrix(): {e}")

    # fonction pour convertir les coordonnées de array dans le repère global en coordonnées dans le repère local de la piece
    def convertGlobalToLocal(self,array):
        try:
            if self.frame_conversion_matrix is None:
                self.getFrameConversionMatrix()
            if self.cog is None:
                self.getCOG()

            x_global = array[0]
            y_global = array[1]
            z_global = array[2]

            # Translation des coordonnées globales par rapport à l'origine locale
            translated_x = x_global - self.cog[0]*1000
            translated_y = y_global - self.cog[1]*1000
            translated_z = z_global - self.cog[2]*1000

            # Inversion de la transformation en utilisant les axes locaux
            # Cela nécessite de résoudre un système linéaire

            inverse_rotation_matrix = np.linalg.inv((self.frame_conversion_matrix))

            # Application de la matrice inverse
            local_coords = np.dot(inverse_rotation_matrix, [translated_x, translated_y, translated_z])

            local_x, local_y, local_z = local_coords

        except Exception as e:
            print(f"Error with convertGlobalToLocal(): {e}")
            return None

        return local_x/1000, local_y/1000, local_z/1000  
    
    # fonction qui convertit dans le repère local et enregistre mediane_global
    # TODO : il est surement plus simple d'ajouter cette ligne directement dans computeGeometricalCenter()
    def getLocalCenter(self):
        self.mediane_local = self.convertGlobalToLocal(self.mediane_global)

    # fonction qui convertit le tableau exprimé dans le repère local "array" dans le repère global
    def convertLocalToGlobal(self,array):
        # les parametres suivants permettent de s'adapter au sens de la piece : on regarde le signe ( dans le repere local ) du
        # centre geometrique de la bounding box pour savoir quel est le sens de la piece ( haut/bas etc. )
        # En procedant ainsi, on s'assure que le repere local de la piece y est correctement fixe, quel que soit son sens
        # Attention : cette methode ne fonctionne que pour des pieces asymeytriques !
        scaling = np.array([1 if self.mediane_local[i] >= 0 else -1 for i in range(3)])

        res = []
        for point in array:
            # Appliquer le scaling et la transformation
            scaled_point = scaling * np.array(point)
            global_point = self.cog + self.frame_conversion_matrix @ scaled_point
            res.append(global_point * 1000)

        return res
    
    # Fonction qui renvoie le vecteur normal à un plan defini par les trois points de la liste points
    # Attention : L'ordre des points dans la liste est important
    def planNormal(self, points):
        v1 = np.array(points[0]) - np.array(points[1])
        v2 = np.array(points[2]) - np.array(points[1])
        normal = np.cross(v1, v2)
        return normal / np.linalg.norm(normal)
    
    # fonction qui renvoie True si les vecteurs v1 et v2 sont colineaires, False sinon
    def vectorsAreColinear(self, v1, v2):
        # Calculer le produit vectoriel des deux vecteurs
        dot_product = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

        if abs(dot_product - 1) < 0.01 or abs(dot_product + 1) < 0.01:
            return True
        return False
    
    # function for getting angle of a point projecting onto plane normal to globalAxisRotation
    # with respect to projection of zero_angle_point
    def getAngle(self,globalRotationAxis, zero_angle_point, point):
        # Convertir les points de l'axe de rotation en vecteur
        point1 = np.array(globalRotationAxis[0]).flatten()
        point2 = np.array(globalRotationAxis[1]).flatten()
        axis_vector = point2 - point1

        # Normaliser le vecteur de l'axe
        axis_vector /= np.linalg.norm(axis_vector)

        # Convertir les points en numpy arrays
        zero_angle_point = np.array(zero_angle_point).flatten()
        point = np.array(point).flatten()

        # Calculer le vecteur de projection
        vector_to_project_point = point - point1
        vector_to_project_ref = zero_angle_point - point1

        # Projeter le vecteur sur le plan normal à l'axe
        projection_point_on_axis = np.dot(vector_to_project_point, axis_vector) * axis_vector
        projection_point_on_plane = vector_to_project_point - projection_point_on_axis

        projection_ref_on_axis = np.dot(vector_to_project_ref, axis_vector) * axis_vector
        projection_ref_on_plane = vector_to_project_ref - projection_ref_on_axis

        # Vérifier si les vecteurs sont colinéaires
        if self.vectorsAreColinear(projection_point_on_plane, projection_ref_on_plane):
            return 0

        # Calculer l'angle entre les vecteurs projetés
        angle_radians = np.arccos(np.dot(projection_ref_on_plane, projection_point_on_plane) / (np.linalg.norm(projection_ref_on_plane) * np.linalg.norm(projection_point_on_plane)))

        # Déterminer le sens de rotation
        if np.dot(np.cross(projection_ref_on_plane, projection_point_on_plane), axis_vector) > 0: 
            angle_radians = -angle_radians

        angle_degrees = np.degrees(angle_radians)

        return angle_degrees

