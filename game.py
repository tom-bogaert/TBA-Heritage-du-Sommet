from room import Room
from player import Player
from command import Command
from actions import Actions
from chargement import Chargement
from character import Character
from quest import Quest, QuestManager
from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk, simpledialog

# Import de Pillow pour le redimensionnement
from PIL import Image, ImageTk 

DEBUG = True

class Game:

    def __init__(self):
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
        self.npcs = []
        self.quest_manager = QuestManager()
        self.gui = None # Référence vers l'interface graphique
        
    def setup(self, player_name=None):
        self.commands["help"] = Command("help", " : afficher cette aide", Actions.help, 0)
        self.commands["quit"] = Command("quit", " : quitter le jeu", Actions.quit, 0)
        self.commands["go"] = Command("go", " <direction> : se déplacer (N, E, S, O, U, D)", Actions.go, 1)
        self.commands["history"] = Command("history", " : afficher les lieux visités", Actions.history, 0)
        self.commands["back"] = Command("back", " : revenir au lieu précédent", Actions.back, 0)
        self.commands["look"] = Command("look", " : observer les lieux et les objets", Actions.look, 0)
        self.commands["take"] = Command("take", " <objet> : prendre un objet", Actions.take, 1)
        self.commands["drop"] = Command("drop", " <objet> : poser un objet", Actions.drop, 1)
        self.commands["check"] = Command("check", " : vérifier son inventaire", Actions.check, 0)
        self.commands["talk"] = Command("talk", " <nom> : parler à un personnage", Actions.talk, 1)
        self.commands["escalade"] = Command("escalade", " : Tenter de grimper (QTE)", Actions.climb, 0)
        
        self.commands["quests"] = Command("quests", " : afficher le journal des quêtes", Actions.quests, 0)
        self.commands["quest"] = Command("quest", " <nom> : afficher les détails d'une quête", Actions.quest, 1)

        fichier_config_jeu = "data.json"
        salles_chargees, salle_depart = Chargement.charger_depuis_json(fichier_config_jeu)
        
        if not salles_chargees or not salle_depart:
            print("\nERREUR FATALE: Impossible de charger les données du jeu.")
            self.finished = True
            return

        self.rooms = salles_chargees
        
        # Gestion du nom pour compatibilité GUI/Console
        if player_name is None:
            player_name = input("\nEntrez votre nom: ")
            
        self.player = Player(player_name)
        self.player.current_room = salle_depart

        q1 = Quest(
            "Sécurité_avant_tout", 
            "Trouver un piolet au Mess pour pouvoir aller sur le glacier.", 
            "TAKE_piolet", 
            "Maîtrise du piolet (+Skill)"
        )
        
        q2 = Quest(
            "Première_Ascension",
            "Grimper la première paroi pour atteindre l'Entrée du Glacier.",
            "MOVE_Entrée Glacier (E)", 
            "Acclimatation (+Endurance)"
        )

        q3 = Quest(
            "Le_toit_du_monde", 
            "Atteindre le sommet de la montagne.", 
            "MOVE_LE LOCUS (Fin)",
            "Gloire éternelle"
        )

        q4 = Quest(
            "Bienvenue", 
            "Parler au Sherpa", 
            "TALK_Sherpa",
            "Informations sur la montagne"
        )
        
        self.quest_manager.add_quest(q1)
        self.quest_manager.add_quest(q2)
        self.quest_manager.add_quest(q3)
        self.quest_manager.add_quest(q4)

        guide = Character("Sherpa", "Un guide expérimenté.", salle_depart, ["Attention aux crevasses.", "Prends le piolet !"])
        
        self.npcs = []
        for room in self.rooms:
            for char in room.characters.values():
                self.npcs.append(char)


    def check_win(self):
        if self.quest_manager.all_finished():
            print("\n🏆 VICTOIRE ABSOLUE ! Vous avez conquis la montagne et rempli tous vos objectifs !")
            self.finished = True
            return True
        return False

    def check_loose(self):
        current_room_name = self.player.current_room.name
        
        if current_room_name == "Glacier (S)" and "piolet" not in self.player.inventory:
            print("\n💀 DÉFAITE : Vous avez glissé sur le glacier sans piolet pour vous retenir.")
            print("Votre corps glisse vers la crevasse...")
            self.finished = True
            return True
        return False

    def play(self):
        self.setup()
        if self.finished: return
            
        self.print_welcome()
        
        while not self.finished:
            if self.check_loose(): break
            
            ancienne_salle = self.player.current_room
            
            self.process_command(input("> "))
            
            if self.player.current_room != ancienne_salle:
                event_move = f"MOVE_{self.player.current_room.name}"
                self.quest_manager.check_events(event_move, self.player)
                
                for npc in self.npcs:
                    npc.move()
            
            if self.check_win(): break

        return None

    def process_command(self, command_string) -> None:
        stripped_input = command_string.strip()
        if not stripped_input:
            print() 
            return

        list_of_words = stripped_input.split(" ")
        command_word = list_of_words[0]

        if command_word not in self.commands.keys():
            print(f"\nVous ne savez pas ce qu'est '{command_word}'\n")
        else:
            command = self.commands[command_word]
            command.action(self, list_of_words, command.number_of_parameters)

    def print_welcome(self):
        print(f"\nBienvenue {self.player.name} dans ce jeu d'aventure !")
        print("Entrez 'help' si vous avez besoin d'aide.")
        print(self.player.current_room.get_long_description())
    

class _StdoutRedirector:
    """Redirect sys.stdout writes into a Tkinter Text widget."""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, msg):
        """Write message to the Text widget."""
        if msg:
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", msg)
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")

    def flush(self):
        """Flush method required by sys.stdout interface (no-op for Text widget)."""


class GameGUI(tk.Tk):
    """Tkinter GUI for the text-based adventure game."""

    IMAGE_WIDTH = 600
    IMAGE_HEIGHT = 600
    
    def __init__(self):
        super().__init__()
        self.title("TBA - Héritage du Sommet")
        
        # Fenêtre large pour accommoder les barres géantes
        self.geometry("1600x950") 
        self.minsize(1200, 700)

        # Underlying game logic instance
        self.game = Game()
        self.game.gui = self
        
        # Ask player name via dialog (fallback to 'Joueur')
        name = simpledialog.askstring("Nom", "Entrez votre nom:", parent=self)
        if not name:
            name = "Joueur"
        self.game.setup(player_name=name)

        # --- VARIABLES POUR LES STATS ---
        # Ces variables stockent les valeurs pour les barres de progression
        self.var_energy = tk.DoubleVar(value=100)
        self.var_mental = tk.DoubleVar(value=100)
        self.var_heat = tk.DoubleVar(value=100)
        
        # Ces variables stockent le texte à afficher (ex: "100")
        self.txt_energy = tk.StringVar(value="100")
        self.txt_mental = tk.StringVar(value="100")
        self.txt_heat = tk.StringVar(value="100")

        # Build UI layers
        self._build_layout()

        # Redirect stdout so game prints appear in terminal output area
        self.original_stdout = sys.stdout
        sys.stdout = _StdoutRedirector(self.text_output)

        # Print welcome text in GUI
        self.game.print_welcome()

        # Update stats and images
        self._update_interface()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)


    # -------- Method Helper : Chargement sécurisé --------
    def _safe_load_icon(self, filename, size=None):
        """
        Essaie de charger une icône via Pillow pour redimensionnement.
        """
        assets_dir = Path(__file__).parent / 'assets'
        file_path = assets_dir / filename
        try:
            # On ouvre avec Pillow (PIL)
            pil_image = Image.open(str(file_path))
            
            # Si une taille est demandée, on redimensionne
            if size:
                pil_image = pil_image.resize(size, Image.Resampling.LANCZOS)
                
            return ImageTk.PhotoImage(pil_image)
        except Exception as e:
            # print(f"Icone manquante ou erreur : {filename} ({e})")
            return None

    # -------- Layout construction --------
    def _build_layout(self):
        # Configure root grid: 3 rows
        self.grid_rowconfigure(0, weight=0)  # Image/buttons fixed height
        self.grid_rowconfigure(1, weight=1)  # Terminal output expands
        self.grid_rowconfigure(2, weight=0)  # Entry fixed
        self.grid_columnconfigure(0, weight=1)

        # --- CONFIGURATION DU STYLE (BARRES DE PROGRESSION GÉANTES) ---
        style = ttk.Style()
        style.theme_use('clam') 
        
        # Épaisseur : 90px
        BAR_THICKNESS = 50
        
        style.configure("Energy.Horizontal.TProgressbar", 
                        foreground='green', background='#4CAF50', 
                        troughcolor='#333', thickness=BAR_THICKNESS)
                        
        style.configure("Mental.Horizontal.TProgressbar", 
                        foreground='blue', background='#2196F3', 
                        troughcolor='#333', thickness=BAR_THICKNESS)
                        
        style.configure("Heat.Horizontal.TProgressbar", 
                        foreground='red', background='#FF5722', 
                        troughcolor='#333', thickness=BAR_THICKNESS)


        # L3 Top frame
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=(6,3))
        top_frame.grid_columnconfigure(0, weight=0)
        top_frame.grid_columnconfigure(1, weight=1)

        # L3L Image area (left)
        image_frame = ttk.Frame(top_frame, width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT)
        image_frame.grid(row=0, column=0, sticky="nw", padx=(0,6))
        image_frame.grid_propagate(False)  # Keep requested size
        self.canvas = tk.Canvas(image_frame,
                                width=self.IMAGE_WIDTH,
                                height=self.IMAGE_HEIGHT,
                                bg="#222")
        self.canvas.pack(fill="both", expand=True)

        self._image_ref = None  # Reference to prevent GC

        # L3R Buttons area (right)
        buttons_frame = ttk.Frame(top_frame)
        buttons_frame.grid(row=0, column=1, sticky="ne", padx=5)
        buttons_frame.grid_columnconfigure(0, weight=1)

        # =========================================================
        # CHARGEMENT DES IMAGES (Toutes en 50x50 pour les actions)
        # =========================================================
        self._btn_help = self._safe_load_icon('help-50.png')
        self._btn_up = self._safe_load_icon('up-arrow-50.png')
        self._btn_down = self._safe_load_icon('down-arrow-50.png')
        self._btn_left = self._safe_load_icon('left-arrow-50.png')
        self._btn_right = self._safe_load_icon('right-arrow-50.png')
        self._btn_quit = self._safe_load_icon('quit-50.png')
        
        self._btn_look = self._safe_load_icon('look_button.png', size=(50, 50)) or self._safe_load_icon('look_image.png', size=(50, 50))
        self._btn_inventory = self._safe_load_icon('inventory_button.png', size=(50, 50))
        self._btn_quest = self._safe_load_icon('quest_button.png', size=(50, 50))
        self._btn_climb = self._safe_load_icon('climb_button.png', size=(50, 50))

        # =========================================================
        # 1. BOUTON AIDE (Tout en haut)
        # =========================================================
        tk.Button(buttons_frame,
                  image=self._btn_help,
                  text="Aide" if not self._btn_help else "",
                  command=lambda: self._send_command("help"),
                  bd=0).grid(row=0, column=0, sticky="ew", pady=(0, 5))


        # =========================================================
        # 2. ZONE CENTRALE (STATS à GAUCHE | DÉPLACEMENTS à DROITE)
        # =========================================================
        center_container = ttk.Frame(buttons_frame)
        center_container.grid(row=1, column=0, sticky="ew", pady=5)
        center_container.grid_columnconfigure(0, weight=1) # Stats prennent de la place
        center_container.grid_columnconfigure(1, weight=0) # Déplacements fixes

        # --- A. FRAME STATISTIQUES (Gauche) ---
        stats_frame = ttk.LabelFrame(center_container, text="État Physique")
        stats_frame.grid(row=0, column=0, sticky="nw", padx=(0, 5), pady=0)
        
        # Police agrandie
        font_lbl = ("Helvetica", 18, "bold")
        # Longueur géante : 690px
        BAR_LENGTH = 345

        # Énergie
        ttk.Label(stats_frame, text="Énergie", font=font_lbl).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Progressbar(stats_frame, style="Energy.Horizontal.TProgressbar", 
                        variable=self.var_energy, maximum=100, length=BAR_LENGTH).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(stats_frame, textvariable=self.txt_energy, width=4, font=font_lbl).grid(row=0, column=2, sticky="e", padx=5)

        # Mental
        ttk.Label(stats_frame, text="Mental", font=font_lbl).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Progressbar(stats_frame, style="Mental.Horizontal.TProgressbar", 
                        variable=self.var_mental, maximum=100, length=BAR_LENGTH).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(stats_frame, textvariable=self.txt_mental, width=4, font=font_lbl).grid(row=1, column=2, sticky="e", padx=5)

        # Chaleur
        ttk.Label(stats_frame, text="Chaleur", font=font_lbl).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Progressbar(stats_frame, style="Heat.Horizontal.TProgressbar", 
                        variable=self.var_heat, maximum=100, length=BAR_LENGTH).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(stats_frame, textvariable=self.txt_heat, width=4, font=font_lbl).grid(row=2, column=2, sticky="e", padx=5)

        # --- B. FRAME DÉPLACEMENTS (Droite) ---
        move_frame = ttk.LabelFrame(center_container, text="Déplacements")
        move_frame.grid(row=0, column=1, sticky="ne", padx=(5, 0))
        
        tk.Button(move_frame, image=self._btn_up, text="N", 
                  command=lambda: self._send_command("go N"), bd=0).grid(row=0, column=0, columnspan=2, pady=2)
        tk.Button(move_frame, image=self._btn_left, text="O", 
                  command=lambda: self._send_command("go O"), bd=0).grid(row=1, column=0, padx=2)
        tk.Button(move_frame, image=self._btn_right, text="E", 
                  command=lambda: self._send_command("go E"), bd=0).grid(row=1, column=1, padx=2)
        tk.Button(move_frame, image=self._btn_down, text="S", 
                  command=lambda: self._send_command("go S"), bd=0).grid(row=2, column=0, columnspan=2, pady=2)


        # =========================================================
        # 3. ACTIONS RAPIDES (En dessous)
        # =========================================================
        actions_frame = ttk.LabelFrame(buttons_frame, text="Actions")
        # On ne met PAS sticky="ew" ici pour éviter que le cadre s'étire sur 700px
        actions_frame.grid(row=2, column=0, pady=10)

        # Bouton LOOK (On enlève fill="x")
        comp_look = "left" if self._btn_look else "none"
        ttk.Button(actions_frame, text="Regarder (Look)", image=self._btn_look, compound=comp_look, 
                   command=lambda: self._send_command("look")).pack(pady=2, padx=10, ipadx=5)
        
        # Bouton INVENTAIRE
        comp_inv = "left" if self._btn_inventory else "none"
        ttk.Button(actions_frame, text="Inventaire (Check)", image=self._btn_inventory, compound=comp_inv,
                   command=lambda: self._send_command("check")).pack(pady=2, padx=10, ipadx=5)
        
        # Bouton QUETES
        comp_quest = "left" if self._btn_quest else "none"
        ttk.Button(actions_frame, text="Quêtes (Quests)", image=self._btn_quest, compound=comp_quest,
                   command=lambda: self._send_command("quests")).pack(pady=2, padx=10, ipadx=5)
        
        # Bouton ESCALADE
        comp_climb = "left" if self._btn_climb else "none"
        ttk.Button(actions_frame, text="Escalade (QTE)", image=self._btn_climb, compound=comp_climb,
                   command=lambda: self._send_command("escalade")).pack(pady=2, padx=10, ipadx=5)

        # =========================================================
        # 4. BOUTON QUITTER
        # =========================================================
        tk.Button(buttons_frame,
                  image=self._btn_quit,
                  text="Quitter" if not self._btn_quit else "",
                  command=lambda: self._send_command("quit"),
                  bd=0).grid(row=3, column=0, sticky="ew", pady=(10,2))


        # =========================================================
        # ZONE TERMINAL ET ENTRÉE (Reste inchangé)
        # =========================================================
        output_frame = ttk.Frame(self)
        output_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=3)
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(output_frame, orient="vertical")
        self.text_output = tk.Text(output_frame,
                                   wrap="word",
                                   yscrollcommand=scrollbar.set,
                                   state="disabled",
                                   bg="#111", fg="#eee", font=("Consolas", 10))
        scrollbar.config(command=self.text_output.yview)
        self.text_output.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        entry_frame = ttk.Frame(self)
        entry_frame.grid(row=2, column=0, sticky="ew", padx=6, pady=(3,6))
        entry_frame.grid_columnconfigure(0, weight=1)

        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(entry_frame, textvariable=self.entry_var)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

    # -------- Mise à jour Globale (Interface) --------
    def _update_interface(self):
        """Met à jour l'image ET les statistiques."""
        if not self.game.player:
            return

        # 1. Mise à jour des Stats
        p = self.game.player
        
        # Mise à jour des barres (valeurs)
        self.var_energy.set(p.energy)
        self.var_mental.set(p.mental_health)
        self.var_heat.set(p.heat)
        
        # Mise à jour du texte à côté (entier)
        self.txt_energy.set(f"{int(p.energy)}")
        self.txt_mental.set(f"{int(p.mental_health)}")
        self.txt_heat.set(f"{int(p.heat)}")

        # 2. Mise à jour de l'Image de la salle
        if self.game.player.current_room:
            room = self.game.player.current_room
            assets_dir = Path(__file__).parent / 'assets'
            if getattr(room, 'image', None):
                image_path = assets_dir / room.image
            else:
                image_path = assets_dir / 'scene.png'

            try:
                pil_image = Image.open(str(image_path))
                pil_image = pil_image.resize((self.IMAGE_WIDTH, self.IMAGE_HEIGHT), Image.Resampling.LANCZOS)
                self._image_ref = ImageTk.PhotoImage(pil_image)
                
                self.canvas.delete("all")
                self.canvas.create_image(
                    self.IMAGE_WIDTH/2,
                    self.IMAGE_HEIGHT/2,
                    image=self._image_ref
                )
            except Exception:
                self.canvas.delete("all")
                self.canvas.create_text(
                    self.IMAGE_WIDTH/2, self.IMAGE_HEIGHT/2,
                    text=f"Image manquante: {room.name}", fill="white", font=("Helvetica", 14)
                )


    # -------- Event handlers --------
    def _on_enter(self, _event=None):
        """Handle Enter key press in the entry field."""
        value = self.entry_var.get().strip()
        if value:
            self._send_command(value)
        self.entry_var.set("")


    def _send_command(self, command):
        if self.game.finished:
            return
        
        # Echo the command in output area
        print(f"\n> {command}")
        
        # Process command
        self.game.process_command(command)
        
        # Update everything
        self._update_interface()
        
        if self.game.finished:
            self.entry.configure(state="disabled")
            self.after(2000, self._on_close)


    def _on_close(self):
        sys.stdout = self.original_stdout
        self.destroy()


def main():
    args = sys.argv[1:]
    if '--cli' in args:
        Game().play()
        return
    try:
        app = GameGUI()
        app.mainloop()
    except Exception as e:
        print(f"Erreur GUI ({e}). Passage en mode console.")
        Game().play()
    

if __name__ == "__main__":
    main()