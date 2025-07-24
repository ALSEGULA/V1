# classe mere de serrage, pince et PCM

from pycatia.space_analyses_interfaces.inertia import Inertia
import numpy as np

class Object:
    def __init__(self):
        self.catia_instance = None
        self.frame_conversion_matrix = None
        self.cog = None
        self.BBO = None
        """
        try:
            self.catia_instance = self.getChild(env,name,path) # initialisation de l'instance objet
        except Exception as e:
            print("Probleme de Object.__init__ : ", e)
        """

    def getChild(self,env,name,path):
        current_level = env.product  # Commencer à partir du produit racine

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
                raise ValueError(f"Class Object - get_child() : incorrect path {path}")

        # Une fois au bon niveau, rechercher la pièce
        children = current_level.get_children()
        for child in children:
            if child.name == name:
                return child

        raise ValueError(f"Class Object - get_child() : incorrect name {name}")

    def getPrincipalAxes(self,env):
        if self.catia_instance is None:
            raise ValueError("Appel() à getPrincipalAxes() sur un objet sans instance catia")
        try:
            inertia = Inertia(env.spa_i.add(self.catia_instance).com_object)
            self.principal_axes = inertia.get_principal_axes()
        except Exception as e:
            print(f"Error with getPrincipalAxes() : {e}")

    #TODO : voir s'il n'est pas possible d'alléger la fonction ( seule la mediane est importante )
    def fillBBOArray(self,BBO_BBL_parameters):
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
    def getCOG(self,env):
        if self.catia_instance is None:
            raise ValueError("Appel à getCOG() sur un objet sans instance catia")
        try:
            inertia = Inertia(env.spa_i.add(self.catia_instance).com_object)
            self.cog = inertia.get_cog_position()
        except Exception as e:
            print(f"Error with getCOG(): {e}")

# fonction qui renvoie la matrice de changement de base pour la conversion local->global
    def getFrameConversionMatrix(self):
        try:
            if self.principal_axes is None:
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
    def convertGlobalToLocal(self,env,array):
        try:

            if self.frame_conversion_matrix is None:
                self.getFrameConversionMatrix()
            if self.cog is None:
                self.getCOG(env)

            x_global = array[0]
            y_global = array[1]
            z_global = array[2]

            # Translation des coordonnées globales par rapport à l'origine locale
            translated_x = x_global - self.cog[0]*1000
            translated_y = y_global - self.cog[1]*1000
            translated_z = z_global - self.cog[2]*1000

            # Inversion de la transformation en utilisant les axes locaux
            # Cela nécessite de résoudre un système linéaire
            # On utilise la matrice inverse des axes principaux
            # Calcul de la matrice inverse

            inverse_rotation_matrix = np.linalg.inv((self.frame_conversion_matrix))

            # Application de la matrice inverse
            local_coords = np.dot(inverse_rotation_matrix, [translated_x, translated_y, translated_z])

            local_x, local_y, local_z = local_coords

        except Exception as e:
            print(f"Error with convertGlobalToLocal(): {e}")
            return None

        return local_x/1000, local_y/1000, local_z/1000  
    
    # fonction qui convertit dans le repère local et enregistre mediane_global
    def getLocalCenter(self,env):
        self.mediane_local = self.convertGlobalToLocal(env,self.mediane_global)

    # fonction qui convertit le tableau exprimé dasn le repère local "array" dans le repère global
    def convertLocalToGlobal(self,array):
        # les parametres suivants permettent de s'adapter au sens de la piece : on regarde le signe ( dans le repere local ) de la 
        # mediane d'une grande diagonale de la bounding box pour savoir que est le sens de la piece ( haut/bas etc. )
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
