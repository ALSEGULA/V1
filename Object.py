# classe mere de serrage, pince et PCM

class Object:
    def __init__(self,product,path,name):
        catia_instance = self.get_child(product,path,name) # initialisation de l'instance objet

    def get_child(product,path,name):
        current_level = product  # Commencer à partir du produit racine

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
