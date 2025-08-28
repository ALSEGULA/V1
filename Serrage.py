# classe serrage

import json
import numpy as np
import os
import time

from scipy.spatial import ConvexHull
from Object import Object
from dotenv import set_key
from getApplicationPath import getApplicationPath

class Serrage(Object):
    def __init__(self,env):
        self.local_stick_points = None
        self.global_stick_points = None
        self.local_rotation_axis = None
        self.global_rotation_axis = None
        self.local_collision_hull = None
        self.global_collision_hull = None
        # TODO : adapter les fonctions qui prenennt env en argument pour qu'elles recuperent la variable membre self.env
        super().__init__(env)

    # TODO : implementer la solution avec self.path
    # fonction qui recupere l'objet catia associe au serrage selectionne
    def getCatiaInstance(self,name="SERRAGE_DIN_040.1",path=[]):
        self.name = name
        self.path = self.getTreePath('SERRAGE_TREE_PATH')
        self.catia_instance = super().getChild(name,self.path)

    # fonction qui complete la variable membre local_stick_points en allant chercher les valeurs dasn le fichier points.json,
    # convertit ces points dans le repère global et enregistre le résultat dans global_stick_points
    def getStickPoints(self):
        #TODO : reflechir a mettre application_path en variable membre de la classe 
        application_path = getApplicationPath()
        parent_path = os.path.dirname(application_path)  
        # Chemin vers le fichier points.json qui doit etre place dans le repertoire parent de l'executable
        points_path = os.path.join(parent_path, 'points.json')
        with open(points_path, 'r') as f:
            data = json.load(f)
        self.local_stick_points = data.get("stickPointsSerrage", [])
        self.global_stick_points = self.convertLocalToGlobal(self.local_stick_points)

    # fonction qui complete la variable membre local_collision_hull en allant chercher les valeurs dasn le fichier points.json,
    # convertit ces points dans le repère global et enregistre le résultat dans global_collision_hull
    # TODO : mettre cette fonction dans Object et passer "collisionSerrage" en argument
    def getCollisionHull(self):
        application_path = getApplicationPath()
        parent_path = os.path.dirname(application_path)  
        # Chemin vers le fichier points.json qui doit etre place dans le repertoire parent de l'executable
        points_path = os.path.join(parent_path, 'points.json')
        time.sleep(6)
        with open(points_path, 'r') as f:
            data = json.load(f)
        self.local_collision_hull = data.get("collisionHullSerrage",[])
        self.global_collision_hull = self.convertLocalToGlobal(self.local_collision_hull)

    # fonction qui complete la variable membre local_rotation_axis en allant chercher les valeurs dasn le fichier points.json,
    # convertit ces points dans le repère global et enregistre le résultat dans global_rotation_axis
    def getRotationAxis(self):
        application_path = getApplicationPath()
        parent_path = os.path.dirname(application_path) 
        # Chemin vers le fichier points.json qui doit etre place dans le repertoire parent de l'executable
        points_path = os.path.join(parent_path, 'points.json')
        with open(points_path, 'r') as f:
            data = json.load(f)
        self.local_rotation_axis = data.get("rotationAxis", [])
        self.global_rotation_axis = self.convertLocalToGlobal(self.local_rotation_axis)

    # fonction qui renvoie -1 si l'angle de rotation est negatif pour assurer la regle de la main droite, 1 s'il est positif
    # Attention : Il semble que le signe de l'angle par defaut pour une rotation appliquée avec .move.apply soit l'oppose de celui applique avec numpy
    # Le code ci-dessous est valable pour numpy, il doit être utilisé "à l'envers" avec .move.apply
    def getRotationDirection(self,axis_vector):
        cross_product1 = np.array([-axis_vector[1]*axis_vector[2],-axis_vector[0]*axis_vector[2],2*axis_vector[0]*axis_vector[1]])
        cross_product2 = np.cross(axis_vector,cross_product1)

        if np.dot(axis_vector,np.cross(cross_product1, cross_product2)) < 0:
            return -1
        return 1

    #fonction pour faire tourner le serrage autour de l'axe rotation_axis d'un angle rotation_angle en degre
    def rotateAroundAxis(self,rotation_axis,rotation_angle):

        # Convertir les points de l'axe de rotation en vecteur
        point1 = np.array(rotation_axis[0])
        point2 = np.array(rotation_axis[1])
        axis_vector = point2 - point1

        # Normaliser le vecteur de l'axe de rotation
        axis_vector /= np.linalg.norm(axis_vector)

        # la condition suivante sert a determiner dans quel sens tourner : il depend de l'axe de rotation
        # Attention ! Il semble que le signe de l'angle par defaut pour une rotation appliquée avec .move.apply soit l'oppose
        # de celui applique avec numpy, d'ou l'inegalite etant > ici et < dans rotate_BBO_arond_axis()
        scalar = -self.getRotationDirection(axis_vector) # ici on met - car on utilise .move.apply
        rotation_angle = scalar*rotation_angle

        # TODO : voir s'il n'est pas + rentable de generer une fois la matrice de rotation pour un angle donne puis l'enregistrer
        # Créer la matrice de rotation
        cos_theta = np.cos(np.radians(rotation_angle))
        sin_theta = np.sin(np.radians(rotation_angle))
        one_minus_cos_theta = 1 - cos_theta

        ux, uy, uz = axis_vector
        rotation_matrix = (
            cos_theta + ux**2 * one_minus_cos_theta, ux * uy * one_minus_cos_theta - uz * sin_theta, ux * uz * one_minus_cos_theta + uy * sin_theta,
            uy * ux * one_minus_cos_theta + uz * sin_theta, cos_theta + uy**2 * one_minus_cos_theta, uy * uz * one_minus_cos_theta - ux * sin_theta,
            uz * ux * one_minus_cos_theta - uy * sin_theta, uz * uy * one_minus_cos_theta + ux * sin_theta, cos_theta + uz**2 * one_minus_cos_theta,
            0,0,0
        )

        translation_matrix = (
            1,0,0,
            0,1,0,
            0,0,1,
            -point1[0],-point1[1],-point1[2]
        )

        # Translater la pièce au centre de gravité
        move = self.catia_instance.move.apply(translation_matrix)

        # Appliquer la rotation
        move = self.catia_instance.move.apply(rotation_matrix)

        # Translater la pièce de retour à sa position originale
        translation_matrix = (
            1,0,0,
            0,1,0,
            0,0,1,
            point1[0],point1[1],point1[2]
        )

        move = self.catia_instance.move.apply(translation_matrix)

    # Fonction qui actualise self.global_stick_points qui ont tourne de rotation_angle autour de rotation_axis ( defini dans le repere global )
    # idem pour self.BBO et self.global_collision_hull
    def rotateStickPointsAndBBOAroundAxis(self,rotation_axis,rotation_angle):
        # Convertir les points de l'axe de rotation en vecteur
        point1 = np.array(rotation_axis[0])
        point2 = np.array(rotation_axis[1])
        axis_vector = point2 - point1

        # Normaliser le vecteur de l'axe
        axis_vector /= np.linalg.norm(axis_vector)

        # La condition suivante sert a determiner dans quel sens tourner : il depend de l'axe de rotation
        # Attention ! Il semble que le signe de l'angle par defaut pour une rotation appliquée avec .move.apply soit l'oppose
        # de celui applique avec numpy, d'ou l'inegalite etant < ici et > dans rotateAroundAxis()

        scalar = self.getRotationDirection(axis_vector) # ici on utilise + car on travaille avec numpy
        rotation_angle = scalar*rotation_angle

        # TODO : voir s'il n'est pas + rentable de generer une fois la matrice de rotation pour un angle donné puis l'enregistrer
        # Créer la matrice de rotation
        cos_theta = np.cos(np.radians(rotation_angle))
        sin_theta = np.sin(np.radians(rotation_angle))
        one_minus_cos_theta = 1 - cos_theta

        ux, uy, uz = axis_vector
        rotation_matrix = np.array([
            [cos_theta + ux**2 * one_minus_cos_theta, ux * uy * one_minus_cos_theta - uz * sin_theta, ux * uz * one_minus_cos_theta + uy * sin_theta],
            [uy * ux * one_minus_cos_theta + uz * sin_theta, cos_theta + uy**2 * one_minus_cos_theta, uy * uz * one_minus_cos_theta - ux * sin_theta],
            [uz * ux * one_minus_cos_theta - uy * sin_theta, uz * uy * one_minus_cos_theta + ux * sin_theta, cos_theta + uz**2 * one_minus_cos_theta]
        ])

        # Appliquer la rotation à chaque point des stick_points
        for index,point in enumerate(self.global_stick_points):
            # Translater le point au centre de gravité
            translated_point = np.array(point) - point1

            # Appliquer la rotation
            rotated_point = rotation_matrix @ translated_point
    
            # Translater le point de retour à sa position originale
            final_point = rotated_point + point1

            self.global_stick_points[index] = final_point.tolist()

        # Appliquer la rotation à chaque point de la BBO
        for index,point in enumerate(self.BBO):
            # Translater le point au centre de gravité
            translated_point = np.array(point) - point1

            # Appliquer la rotation
            rotated_point = rotation_matrix @ translated_point
    
            # Translater le point de retour à sa position originale
            final_point = rotated_point + point1

            self.BBO[index] = final_point.tolist()   

        # Appliquer la rotation à chaque point de global_collision_hull
        if self.global_collision_hull is not None:
            for index,point in enumerate(self.global_collision_hull):
                # Translater le point au centre de gravité
                translated_point = np.array(point) - point1

                # Appliquer la rotation
                rotated_point = rotation_matrix @ translated_point
        
                # Translater le point de retour à sa position originale
                final_point = rotated_point + point1

                self.global_collision_hull[index] = final_point.tolist()  

    # cette fonction tourne le serrage de sorte a ce que le plan ( non oriente ) defini par les trois points de stick_points_PCMFRA soit parallele au plan non oriente
    # defini par les trois points global_stick_points du serrage
    def alignPlans(self,stick_points_PCMFRA):
        # Calculer les vecteurs normaux aux plans
        normal_PCMFRA = self.planNormal(stick_points_PCMFRA)
        normal_serrage = self.planNormal(self.global_stick_points)

        if self.vectorsAreColinear(normal_PCMFRA,normal_serrage):
            return 

        # Calculer l'angle entre les deux normales
        angle_radians = np.arccos(np.dot(normal_PCMFRA, normal_serrage))
        angle_degrees = np.degrees(angle_radians)

        # Calculer l'axe de rotation (produit vectoriel des deux normales)
        rotation_axis = np.cross(normal_serrage, normal_PCMFRA) # verifier que ce n'est pas inverse
        rotation_axis /= np.linalg.norm(rotation_axis)

        rotation_points = [[self.cog[0] * 1000, self.cog[1] * 1000, self.cog[2] * 1000],
                        [self.cog[0] * 1000 + rotation_axis[0], self.cog[1] * 1000 + rotation_axis[1], self.cog[2] * 1000 + rotation_axis[2]]]
        

        # Appliquer la rotation a la piece
        self.rotateAroundAxis(rotation_points,angle_degrees)

        # appliquer la rotation aux stick points et à la BBO
        self.rotateStickPointsAndBBOAroundAxis(rotation_points,angle_degrees)

    # Cette fonction tourne le serrage de sorte que le plan oriente defini par les trois points de stick_points_PCMFRA soit parallele + avec la meme orientation
    # que le plan oriente defini par les trois stick_points du serrage
    def alignOrientedPlans(self, stick_points_PCMFRA):
        # On commence par aligner les deux plans sans se soucier de l'orientation
        self.alignPlans(stick_points_PCMFRA)

        # A ce stade les plans sont paralleles, les lignes suivantes s'occupent de la rotation de 180° si necessaire pour avoir la meme orientation
        vec1 = np.array(self.global_stick_points[3] - np.array(self.global_stick_points[1]))
        vec2 = np.array(stick_points_PCMFRA[3] - np.array(stick_points_PCMFRA[1]))
        vec1 /= np.linalg.norm(vec1) # inutile
        vec2 /= np.linalg.norm(vec2) # inutile

        if(np.dot(vec1,vec2) < 0):
            rotation_axis = [self.global_stick_points[1],self.global_stick_points[2]]
            # TODO : integrer rotateStickPointsAndBBOAroundAxis dans rotateAroundAxis ?
            self.rotateAroundAxis(rotation_axis,180)
            self.rotateStickPointsAndBBOAroundAxis(rotation_axis,180)

    # fonction qui renvoie un booleen selon que le serrage est en bonne position ou non.
    # Si non, une rotation de 180° est necessaire
    def isInGoodPosition(self,name_PCMFRA,path_PCMFRA): 
        testPointClamp1 = np.array(self.global_stick_points[2])
        testPointClamp2 = np.array(self.global_stick_points[0])

        product = self.env.product
        caa = self.env.caa

        # la fonction generate_ALLCATPart convertit tout objet convertible du fichier CATProduct ouvert en fichier CATPArt
        product.generate_ALLCATPart(product)
        document = caa.active_document
        part = document.part
        cog_touche = None
        path_name = ""
        for name in path_PCMFRA:
            path_name += name
            path_name += "\\"
        path_name += name_PCMFRA
        path_name += "\\"
        path_name += "TOUCHE"

        for body in part.bodies:
            if body.name == path_name:
                spa_workbench = document.spa_workbench()
                reference = part.create_reference_from_object(body)
                measurable = spa_workbench.get_measurable(reference)
                cog_touche = measurable.get_cog()
        document.close()

        if cog_touche is None:
            print("La touche n'a pas ete trouvee !") # faire un raiseError

        # la condition suivante permet de determiner si le serrage est correcteemnt incline ou non
        if np.linalg.norm(testPointClamp1 - cog_touche) < np.linalg.norm(testPointClamp2 - cog_touche):
            return True
        
        return False

    # Fonction qui colle le plan du serrage avec le plan du PCM_FRA
    # Apres cette etape, il manque la rotation pour bien coller les deux pieces
    def stickToPCM(self,stick_points_PCMFRA):

        # TODO : revenir sur cette partie qui est 
        # 1 trop specifique au serrage utilise pendant les tests
        # 2 pas du tout claire et documentee
        # 3 repetee dans une autre fonction

        vec1 = np.array(self.global_stick_points[0]) - np.array(self.global_stick_points[1])
        vec2 = np.array(self.global_stick_points[2]) - np.array(self.global_stick_points[1])
        middlePointClamp = np.array(self.global_stick_points[1]) + 0.5 * vec1 + 0.55 * vec2

        vec3 = np.array(stick_points_PCMFRA[0])
        vec4 = np.array(stick_points_PCMFRA[2])
        middlePointPCMFRA = (vec3+vec4)/2

        translation_vector = middlePointPCMFRA - middlePointClamp

        translation_matrix = (
            1,0,0,
            0,1,0,
            0,0,1,
            translation_vector[0],translation_vector[1],translation_vector[2]
        )
        move = self.catia_instance.move.apply(translation_matrix)

        for index,stickPoint in enumerate(self.global_stick_points):
            self.global_stick_points[index] = [stickPoint[0] + translation_vector[0],
                stickPoint[1] + translation_vector[1],
                stickPoint[2] + translation_vector[2]]

        for index,point in enumerate(self.BBO):
            self.BBO[index] = [point[0] + translation_vector[0],
                point[1] + translation_vector[1],
                point[2] + translation_vector[2]]
            
    # fonction qui definit la dernier étape pour coller le serrage avec le PCM : rotation pour que les deux pièces soient correctement alignées
    def rotateToStickToPCM(self,stick_points_PCMFRA,name_PCMFRA,path_PCMFRA):

        # TODO : revenir sur cette partie qui est 
        # 1 trop specifique au serrage utilise pendant les tests
        # 2 pas du tout claire et documentee
        # 3 repetee dans une autre fonction

        vec1 = np.array(self.global_stick_points[0]) - np.array(self.global_stick_points[1])
        vec2 = np.array(self.global_stick_points[2]) - np.array(self.global_stick_points[1])
        middle_point_clamp = np.array(self.global_stick_points[1]) + 0.5 * vec1 + 0.55 * vec2 

        vecPCMFRA = np.array(stick_points_PCMFRA[0])-np.array(stick_points_PCMFRA[1])
        vecClamp = np.array(self.global_stick_points[0])-np.array(self.global_stick_points[1])

        # TODO : revenir sur la definition de rotation_axis pour les mêmes raisons
        
        rotation_axis = [[middle_point_clamp[0]+self.global_stick_points[3][0]-self.global_stick_points[1][0],
                        middle_point_clamp[1]+self.global_stick_points[3][1]-self.global_stick_points[1][1],
                        middle_point_clamp[2]+self.global_stick_points[3][2]-self.global_stick_points[1][2]],
                        [middle_point_clamp[0],
                        middle_point_clamp[1],
                        middle_point_clamp[2]]]

        zero_angle_point = middle_point_clamp + vecPCMFRA
        point = [middle_point_clamp[0] + vecClamp[0], middle_point_clamp[1] + vecClamp[1], middle_point_clamp[2] + vecClamp[2]]
        angle_to_rotate = self.getAngle(rotation_axis,zero_angle_point,point)

        self.rotateAroundAxis(rotation_axis,angle_to_rotate)
        self.rotateStickPointsAndBBOAroundAxis(rotation_axis,angle_to_rotate)

        if not self.isInGoodPosition(name_PCMFRA,path_PCMFRA):
            # il faut tourner de 180° pour etre dans le bon sens
            self.rotateAroundAxis(rotation_axis,180)
            self.rotateStickPointsAndBBOAroundAxis(rotation_axis,180)

        # Une fois arrivé ici, le serrage est bien positionné. 
        # On actualise alors son centre de gravite, sa matrice de changement de base, sa médiane locale et son axe de rotation

    # fonction qui renvoie True si la primitive de collision du serrage est en collision avec la primitive de collision de la pince
    # On se base sur l'algorithme SAT ( Separating Axes Theorem )
    def isInCollision(self,collision_hull):

        tableau_serrage = np.array(self.global_collision_hull)
        tableau_pince = np.array(collision_hull)

        hull_serrage = ConvexHull(tableau_serrage) # enveloppe convexe des primitives de collision du serrage
        hull_pince = ConvexHull(tableau_pince) # enveloppe convexe des primitives de collison de la pince

        # Function to project a shape onto an axis
        def project_shape(shape, axis):
            projections = np.dot(shape, axis)
            return projections.min(), projections.max()
        
            # Get the edges of both shapes
        edges1 = hull_serrage.simplices
        edges2 = hull_pince.simplices

        # Define the axes to test
        axes = []

        for triangle in edges1:
            for i in range(3):
                axis = np.cross(tableau_serrage[triangle[(i+1)%3]] - tableau_serrage[triangle[i]], tableau_serrage[triangle[(i+2)%3]] - tableau_serrage[triangle[(i+1)%3]])
                if np.linalg.norm(axis) > 1e-6:
                    axes.append(axis)

        for triangle in edges2:
            for i in range(3):
                axis = np.cross(tableau_pince[triangle[(i+1)%3]] - tableau_pince[triangle[i]], tableau_pince[triangle[(i+2)%3]] - tableau_pince[triangle[(i+1)%3]])
                if np.linalg.norm(axis) > 1e-6:
                    axes.append(axis)

        # Check for separation along each axis
        for axis in axes:
            proj1 = project_shape(tableau_serrage, axis)
            proj2 = project_shape(tableau_pince, axis)
            if proj1[1] < proj2[0] or proj2[1] < proj1[0]:
                return False

        return True
    
    """
    # fonction qui tourne le serrage jusqu'a ce qu'il n'y ait plus collision entre sa primitive de collsiion et celle passe en parametre
    # ( qui est celle de la pince )
    # Si on arrive a une rotation de 180° sans avoir trouve d'angle qui convient, la fonction s'arrete
    def rotateUntilNoCollision(self,collision_hull_pince):

        application_path = getApplicationPath()
        env_path = os.path.join(application_path, '.env')

        collision_detected = False
        sense_of_rotation = 1

        for angle in range(180):
            collision_detected = False
            for collision_hull in collision_hull_pince:
                if self.isInCollision(collision_hull):
                    collision_detected = True
                    break
            if not collision_detected:
                print("Solution trouvee")
                set_key(env_path, 'TEXT_LABEL', "Solution trouvée")
                time.sleep(3)
                return

            self.rotateAroundAxis(self.global_rotation_axis,sense_of_rotation*angle)
            self.rotateStickPointsAndBBOAroundAxis(self.global_rotation_axis,sense_of_rotation*angle)
            sense_of_rotation = -sense_of_rotation

        print("Pas de solution trouvée")
        set_key(env_path, 'TEXT_LABEL', "Pas de solution trouvée")
        time.sleep(3)
        """
    
    # fonction qui tourne le serrage jusqu'a ce qu'il n'y ait plus collision entre sa primitive de collisiion et celles passees en parametre
    # ( qui sont celles des pinces a risque )
    # Si on arrive a une rotation de 180° sans avoir trouve d'angle qui convient, la fonction s'arrete
    def rotateUntilNoCollision(self,collision_hull_pinces):
        application_path = getApplicationPath()
        env_path = os.path.join(application_path, '.env')

        collision_detected = False
        sense_of_rotation = 1

        for angle in range(180):
            collision_detected = False
            for pince in collision_hull_pinces:
                for collision_hull in pince:
                    if self.isInCollision(collision_hull):
                        collision_detected = True
                        break
            if not collision_detected:
                print("Solution trouvee")
                set_key(env_path, 'TEXT_LABEL', "Solution trouvée")
                time.sleep(3)
                return

            self.rotateAroundAxis(self.global_rotation_axis,sense_of_rotation*angle)
            self.rotateStickPointsAndBBOAroundAxis(self.global_rotation_axis,sense_of_rotation*angle)
            sense_of_rotation = -sense_of_rotation

        print("Pas de solution trouvée")
        set_key(env_path, 'TEXT_LABEL', "Pas de solution trouvée")
        time.sleep(3)

    # fonction de mise à jour à appeler une fois que le serrage à bouger pour prendre en compte les modifications
    def update(self):
        application_path = getApplicationPath()
        env_path = os.path.join(application_path, '.env')
        self.getCOG()
        self.getFrameConversionMatrix()
        self.computeGeometricalCenter()
        self.getLocalCenter()
        self.getRotationAxis()
    # fonction qui effectue les trois étapes pour positionner le serrage sur le PCM dont les paramètres sont passés en argument
    def positionOntoPCM(self,stick_points_pcm,pcm_name,pcm_path):
        self.alignOrientedPlans(stick_points_pcm)
        self.stickToPCM(stick_points_pcm)
        self.rotateToStickToPCM(stick_points_pcm,pcm_name,pcm_path) 
