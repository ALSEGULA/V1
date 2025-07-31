# classe et dataclass: majuscule a la premiere lettre
# fonction : CamelCase
# variable : nom_de_la_variable

# ATtention : L'ordre des points definis dans points.json est important !

from utils import *
from frontend import *

def main():
    selection_event = SelectionEvent()

    # Créer l'application UI (dans le thread principal)
    app = SelectionApp(selection_event)

    # Démarrer le thread secondaire pour gérer la sélection et le backend
    backend_thread = threading.Thread(target=startBackend, args=(selection_event,))
    backend_thread.start()

    # Lancer la boucle principale
    app.mainloop()
    
if __name__ == "__main__":
    main()