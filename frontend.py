# frontend.py

import customtkinter as ctk
import threading
import os

from getApplicationPath import getApplicationPath
from dotenv import load_dotenv

# Cette classe va permettre au frontend de communiquer avec le backend 
class SelectionEvent:
    def __init__(self):
        self.event = threading.Event()
        self.selected_item = None

    def set(self, item):
        self.selected_item = item
        self.event.set()

    def wait(self):
        self.event.wait()

    def clear(self):
        self.event.clear()

    def get(self):
        return self.selected_item

class SelectionApp(ctk.CTk):
    def __init__(self,selection_event):
        super().__init__()

        self.selection_event = selection_event

        self.title("Selection App")
        self.geometry("400x200")

        self.label = ctk.CTkLabel(self, text="Selectionner le PCMFRA")
        self.label.pack(pady=20)

        self.confirmed_button = ctk.CTkButton(self, text="Confirmer la sélection", command=self.pressConfirmedButton)
        self.confirmed_button.pack(pady=10)

        # Lancer la mise à jour du label toutes les 100 ms (cela vérifie régulièrement la valeur dans le fichier .env)
        self.updateLabelPeriodically()

    def pressConfirmedButton(self):
        self.selection_event.set("confirmed") 

    def updateLabel(self, text):
        self.label.configure(text=text)

    def updateLabelPeriodically(self):
        """Fonction qui vérifie périodiquement la valeur de la clé 'TEXT_LABEL' dans le fichier .env"""
        # Lire la clé 'TEXT_LABEL' dans le fichier .env
        # load_dotenv(override=True)  # Recharger les variables d'environnement pour obtenir les dernières valeurs
        application_path = getApplicationPath()
        env_path = os.path.join(application_path, '.env')
        load_dotenv(env_path,override=True)

        label_text = os.getenv('TEXT_LABEL',"La cle TEXT_LABEL n'a pas ete trouvée")

        # Mettre à jour le label si nécessaire
        if label_text != self.label.cget("text"):
            self.updateLabel(label_text)
        #self.updateLabel(label_text)
        
        # Appeler cette fonction encore dans 100 ms
        self.after(100, self.updateLabelPeriodically)

def run(selection_event):
    app = SelectionApp(selection_event)
    app.mainloop()