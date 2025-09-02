# frontend.py

import customtkinter as ctk
import threading
import os

from getApplicationPath import getApplicationPath
from dotenv import load_dotenv, set_key

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

        # Variables pour stocker les valeurs précédentes
        self.previous_pcm = None
        self.previous_serrage = None
        self.previous_solution_found = None
        self.previous_solution_unfound = None

        # on recupere le chemin de .env
        self.application_path = getApplicationPath()
        self.env_path = os.path.join(self.application_path, '.env')

        self.title("Logiciel d'automatisation TAS")
        self.geometry("800x300")

        self.label = ctk.CTkLabel(self, text="Selectionner le PCM")
        self.label.grid(row=0, column=0, columnspan=3, pady=20)

        self.pcm_label = ctk.CTkLabel(self, text="Arborescence du PCM:")
        self.pcm_label.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")

        self.pcm_textbox = ctk.CTkEntry(self, placeholder_text="Chemin du PCM")
        self.pcm_textbox.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="we")

        self.serrage_label = ctk.CTkLabel(self, text="Arborescence du serrage:")
        self.serrage_label.grid(row=1, column=1, padx=20, pady=(0, 5), sticky="w")

        self.serrage_textbox = ctk.CTkEntry(self, placeholder_text="Chemin du serrage")
        self.serrage_textbox.grid(row=2, column=1, padx=20, pady=(0, 10), sticky="we")

        self.pince_label = ctk.CTkLabel(self, text="Arborescence de la pince:")
        self.pince_label.grid(row=1, column=2, padx=20, pady=(0, 5), sticky="w")

        self.pince_textbox = ctk.CTkEntry(self, placeholder_text="Chemin de la pince")
        self.pince_textbox.grid(row=2, column=2, padx=20, pady=(0, 10), sticky="we")

        # Créer un cadre pour le tableau
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=4, column=0, columnspan=3, pady=20, sticky="nsew")

        # Initialiser le tableau
        self.table_rows = []

        self.confirmed_button = ctk.CTkButton(self, text="Confirmer la sélection", command=self.pressConfirmedButton)
        self.confirmed_button.grid(row=3, column=0, columnspan=3, pady=20)

        # Configuration des colonnes pour que les champs s’étirent si la fenêtre s’agrandit
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.fillTextBox()

        # Lancer la mise à jour du label toutes les 100 ms (cela vérifie régulièrement la valeur dans le fichier .env)
        self.updateLabelPeriodically()
        # Lancer la mise à jour du tableau
        self.updateTablePeriodically()

    def fillTextBox(self):
        load_dotenv(self.env_path,override=True)

        texte = os.getenv('PCM_TREE_PATH')
        if texte is not None:
            self.pcm_textbox.insert(0,texte)

        texte = os.getenv('SERRAGE_TREE_PATH')
        if texte is not None:
            self.serrage_textbox.insert(0,texte)

        texte = os.getenv('PINCE_TREE_PATH')
        if texte is not None:
            self.pince_textbox.insert(0,texte)

    def pressConfirmedButton(self):
        self.selection_event.set("confirmed") 

    def updateLabel(self, text):
        self.label.configure(text=text)

    def updateLabelPeriodically(self):
        """Fonction qui vérifie périodiquement la valeur de la clé 'TEXT_LABEL' dans le fichier .env"""
        # Lire la clé 'TEXT_LABEL' dans le fichier .env
        load_dotenv(self.env_path,override=True)

        label_text = os.getenv('TEXT_LABEL',"La cle TEXT_LABEL n'a pas ete trouvée")

        # Mettre à jour le label si nécessaire
        if label_text != self.label.cget("text"):
            self.updateLabel(label_text)
        
        # Appeler cette fonction encore dans 100 ms
        self.after(100, self.updateLabelPeriodically)

    def updatePCMTreePlace(self,event):
        """Fonction qui met à jour la variable d'environnement PCM_TREE_PATH avec la valeur de la textbox"""
        set_key(self.env_path, 'PCM_TREE_PATH', self.pcm_textbox.get())

    def updateSerrageTreePlace(self,event):
        """Fonction qui met à jour la variable d'environnement SERRAGE_TREE_PATH avec la valeur de la textbox"""
        set_key(self.env_path, 'SERRAGE_TREE_PATH', self.serrage_textbox.get())

    def updatePinceTreePlace(self,event):
        """Fonction qui met à jour la variable d'environnement PINCE_TREE_PATH avec la valeur de la textbox"""
        set_key(self.env_path, 'PINCE_TREE_PATH', self.pince_textbox.get())

    def updateTablePeriodically(self):
        """Fonction qui vérifie périodiquement les valeurs des clés 'NEW_SERRAGE' et 'NEW_PCM' dans le fichier .env"""
        load_dotenv(self.env_path, override=True)

        new_serrage = os.getenv('NEW_SERRAGE')
        new_pcm = os.getenv('NEW_PCM')
        serrage_solution_found = os.getenv('SOLUTION_FOUND')
        serrage_solution_unfound = os.getenv('SOLUTION_UNFOUND')

        # Vérifier si les nouvelles valeurs sont différentes des valeurs précédentes
        if (new_serrage and new_serrage != self.previous_serrage) or (new_pcm and new_pcm != self.previous_pcm):
            self.addRowToTable(new_serrage, new_pcm)
            self.previous_serrage = new_serrage
            self.previous_pcm = new_pcm
            self.updateTableDisplay()

        # Vérifier si les solutions ont changé
        if serrage_solution_found and serrage_solution_found != self.previous_solution_found:
            self.updateSolutionInTable(serrage_solution_found, "V")
            self.previous_solution_found = serrage_solution_found

        if serrage_solution_unfound and serrage_solution_unfound != self.previous_solution_unfound:
            self.updateSolutionInTable(serrage_solution_unfound, "X")
            self.previous_solution_unfound = serrage_solution_unfound

        # Appeler cette fonction encore dans 100 ms
        self.after(100, self.updateTablePeriodically)

    def addRowToTable(self, serrage, pcm):
        """Fonction qui ajoute une ligne au tableau"""
        # Vérifier s'il y a une ligne vide à remplir
        for row in self.table_rows:
            if row[0].cget("text") == "" or row[1].cget("text") == "":
                if serrage and row[0].cget("text") == "":
                    row[0].configure(text=serrage)
                    return # on part du principe que l'on n'a pas simultanement un nouveau serrage et un nouveau PCM
                if pcm and row[1].cget("text") == "":
                    row[1].configure(text=pcm)
                    return

        # Si aucune ligne vide n'est trouvée, ajouter une nouvelle ligne
        row_frame = ctk.CTkFrame(self.table_frame)
        row_frame.pack(fill="x", pady=2)

        serrage_label = ctk.CTkLabel(row_frame, text=serrage if serrage else "")
        serrage_label.pack(side="left", padx=5, pady=5, expand=True, fill="x")

        pcm_label = ctk.CTkLabel(row_frame, text=pcm if pcm else "")
        pcm_label.pack(side="left", padx=5, pady=5, expand=True, fill="x")

        result_label = ctk.CTkLabel(row_frame, text="")
        result_label.pack(side="left", padx=5, pady=5, expand=True, fill="x")

        self.table_rows.append((serrage_label, pcm_label, result_label))

    def updateSolutionInTable(self, serrage_name, result):
        """Fonction qui met à jour la solution dans le tableau"""
        for row in self.table_rows:
            serrage_label, pcm_label, result_label = row
            if serrage_label.cget("text") == serrage_name:
                result_label.configure(text=result)
                break
        self.updateTableDisplay()

    def updateTableDisplay(self):
        """Fonction qui met à jour l'affichage du tableau"""
        for row in self.table_rows:
            serrage_label, pcm_label, result_label = row
            serrage_label.update()
            pcm_label.update()
            result_label.update()

# Attention ! run n'est pas appel dans le main, cette foction est intuile pour le moment
def run(app):
    # recuperer l'appui sur une touche dans les textbox
    app.pcm_textbox.bind("<KeyRelease>", app.updatePCMTreePlace)
    app.serrage_textbox.bind("<KeyRelease>", app.updateSerrageTreePlace)
    app.pince_textbox.bind("<KeyRelease>", app.updatePinceTreePlace)
    app.mainloop()