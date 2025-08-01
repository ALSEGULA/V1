# classe sphere utilisee pour positionner des spheres dans l'espace et visualiser des coordonnées dans le repere global

from Object import Object

class Sphere(Object):
    def __init__(self,env,name,path):
        super().__init__(env)
        self.catia_instance = self.getChild(name,path)
        self.getCOG()

    def positionInGlobalCoordinates(self,x,y,z):
        global_cog_sphere = [1000*self.cog[0],1000*self.cog[1],1000*self.cog[2]]
        position_matrix = (
            1, 0, 0,
            0, 1, 0,
            0, 0, 1,
            x-global_cog_sphere[0], y-global_cog_sphere[1], z-global_cog_sphere[2]
        )
        move = self.catia_instance.move.apply(position_matrix)
