import random
import time
import os
import sys
import tkinter as tk

# Importations spécifiques à l'OS pour le mode console
if os.name == 'nt':
    import msvcrt
else:
    import tty
    import termios
    import select


class QTE:
    """
    Gère un jeu de Quick Time Event (QTE).
    S'adapte automatiquement au mode Console ou GUI (Interface Graphique).
    """

    def __init__(self, game, nb_tours, min_inputs, max_inputs, temps_reaction, pool_lettres="AZERTY"):
        self.game = game  # Référence au jeu pour détecter le GUI
        self.nb_tours = nb_tours
        self.min_inputs = min_inputs
        self.max_inputs = max_inputs
        self.temps_reaction = temps_reaction
        self.pool_lettres = pool_lettres.upper()
        self.score = 0

    def start(self):
        """Lance la version appropriée du QTE."""
        # On vérifie si le jeu a une interface graphique attachée
        if hasattr(self.game, 'gui') and self.game.gui:
            return self.start_gui()
        else:
            return self.start_console()

    # -------------------------------------------------------------------------
    # VERSION CONSOLE (Code d'origine)
    # -------------------------------------------------------------------------
    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _get_key_timed(self, timeout):
        start_time = time.time()
        # WINDOWS
        if os.name == 'nt':
            while True:
                if msvcrt.kbhit():
                    try:
                        key = msvcrt.getch().decode('utf-8').upper()
                        return key, time.time() - start_time
                    except UnicodeDecodeError:
                        continue 
                if time.time() - start_time > timeout:
                    return None, timeout
                time.sleep(0.01)
        # UNIX
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                if rlist:
                    key = sys.stdin.read(1).upper()
                    return key, time.time() - start_time
                else:
                    return None, timeout
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def start_console(self):
        self._clear_screen()
        print("\n    /!\\ ATTENTION : TERRAIN TECHNIQUE DÉTECTÉ /!\\")
        print("    ---------------------------------------------")
        print(f"    Concentration requise : {self.temps_reaction}s par action.")
        time.sleep(2)
        
        self.score = 0
        success_total = True

        for i in range(self.nb_tours):
            self._clear_screen()
            print(f"--- SECTION {i + 1} SUR {self.nb_tours} ---")
            time.sleep(random.uniform(0.8, 1.5))
            
            nb_inputs = random.randint(self.min_inputs, self.max_inputs)
            sequence = random.choices(self.pool_lettres, k=nb_inputs)
            
            self._clear_screen()
            print(f"SECTION : {i + 1}/{self.nb_tours}")
            print("\n")
            
            sequence_str = "  ".join(sequence)
            print(f"   ACTION REQUISE : [ {sequence_str} ]")
            print("\n")
            print("Exécution : ", end="", flush=True)
            
            round_success = True
            
            for lettre_attendue in sequence:
                key_pressed, time_taken = self._get_key_timed(self.temps_reaction)
                
                if key_pressed is None:
                    print(f"\n\n⚠️  TROP LENT ! La prise vous échappe !")
                    round_success = False
                    break
                elif key_pressed != lettre_attendue:
                    print(f"\n\n❌  ERREUR ! Vous glissez ({key_pressed} au lieu de {lettre_attendue}) !")
                    round_success = False
                    break
                else:
                    print(f"{key_pressed}..", end="", flush=True)
            
            print() 
            if not round_success:
                print("\n--- 🛑 CHUTE ! ---")
                time.sleep(2)
                success_total = False
                break
            else:
                print("\n--- ✅ PRISE VALIDÉE ---")
                time.sleep(0.5)

        self._clear_screen()
        if success_total:
            print("\n    *** ASCENSION RÉUSSIE ***")
            print("    Vous reprenez votre souffle.\n")
            return True
        else:
            print("\n    *** ÉCHEC DE L'ASCENSION ***")
            print("    Vous avez dû reculer pour ne pas mourir.\n")
            return False

    # -------------------------------------------------------------------------
    # VERSION GUI (Interface Graphique Tkinter)
    # -------------------------------------------------------------------------
    def start_gui(self):
        """Lance le QTE dans une fenêtre modale Tkinter."""
        self.root = self.game.gui
        self.gui_success = False
        
        # Création de la fenêtre popup
        self.top = tk.Toplevel(self.root)
        self.top.title("⚠️ ESCALADE EN COURS ⚠️")
        self.top.geometry("1000x800")
        self.top.transient(self.root)
        self.top.grab_set()  # Bloque les interactions avec la fenêtre principale
        self.top.configure(bg="#222")
        
        # Variables d'état GUI
        self.current_round = 0
        self.current_sequence = []
        self.current_input_index = 0
        self.timer_job = None
        
        # Widgets
        self.lbl_info = tk.Label(self.top, text="PRÉPAREZ-VOUS...", font=("Helvetica", 20), fg="white", bg="#222")
        self.lbl_info.pack(pady=30)
        
        # --- MODIFICATION ICI ---
        # Hauteur passée de 3 à 10 pour afficher plus de lignes
        # Largeur passée de 30 à 40 pour profiter de la fenêtre large
        self.txt_seq = tk.Text(
            self.top, 
            height=10,    # <--- Plus de lignes visibles
            width=40,     # <--- Plus de caractères par ligne
            font=("Courier", 35, "bold"), 
            bg="#222", 
            fg="#0ff", 
            bd=0, 
            highlightthickness=0,
            wrap="word"
        )
        self.txt_seq.pack(pady=20, padx=10)
        
        # Configuration des "tags" (styles de couleurs)
        self.txt_seq.tag_configure("center", justify='center')
        self.txt_seq.tag_configure("done", foreground="#0f0")     # Vert pour les lettres réussies
        self.txt_seq.tag_configure("current", foreground="blue") # Orange pour la lettre ACTUELLE
        self.txt_seq.tag_configure("todo", foreground="white")     # Cyan pour les lettres à venir
        
        # Initialisation vide et désactivée (lecture seule)
        self.txt_seq.insert("1.0", "")
        self.txt_seq.configure(state="disabled")

        self.lbl_status = tk.Label(self.top, text="", font=("Helvetica", 14), fg="#f55", bg="#222")
        self.lbl_status.pack(pady=20)
        
        # Bind des touches
        self.top.bind("<Key>", self.on_gui_key)
        self.top.focus_set()

        # Lancement du premier tour après un court délai
        self.top.after(1500, self.gui_next_round)
        
        # On attend la fermeture de la fenêtre
        self.root.wait_window(self.top)
        
        return self.gui_success

    def _update_colors(self):
        """Met à jour les couleurs des lettres sans changer le texte."""
        self.txt_seq.configure(state="normal")
        
        # On nettoie les anciens tags de couleur (on garde le centrage)
        self.txt_seq.tag_remove("done", "1.0", "end")
        self.txt_seq.tag_remove("current", "1.0", "end")
        self.txt_seq.tag_remove("todo", "1.0", "end")
        
        # On parcourt chaque lettre de la séquence
        for i in range(len(self.current_sequence)):
            # Dans le widget Text, la position est "ligne.colonne".
            # Comme on a mis des espaces ("A B C"), chaque lettre est à l'index i*2.
            start_pos = f"1.{i*2}"
            end_pos = f"1.{i*2 + 1}"
            
            if i < self.current_input_index:
                # Lettres déjà tapées -> Vert
                self.txt_seq.tag_add("done", start_pos, end_pos)
            elif i == self.current_input_index:
                # Lettre actuelle -> JAUNE/ORANGE
                self.txt_seq.tag_add("current", start_pos, end_pos)
            else:
                # Lettres futures -> Cyan
                self.txt_seq.tag_add("todo", start_pos, end_pos)
        
        self.txt_seq.configure(state="disabled")

    def gui_next_round(self):
        """Prépare le prochain round."""
        if self.current_round >= self.nb_tours:
            # Victoire totale
            self.lbl_info.config(text="*** ASCENSION RÉUSSIE ***", fg="#0f0")
            
            self.txt_seq.configure(state="normal")
            self.txt_seq.delete("1.0", "end")
            self.txt_seq.insert("1.0", "SOMMET ATTEINT")
            self.txt_seq.tag_add("center", "1.0", "end")
            self.txt_seq.configure(state="disabled")
            
            self.gui_success = True
            self.top.after(2000, self.top.destroy)
            return

        self.current_round += 1
        self.lbl_info.config(text=f"SECTION {self.current_round} / {self.nb_tours}", fg="white")
        
        # Affichage "..."
        self.txt_seq.configure(state="normal")
        self.txt_seq.delete("1.0", "end")
        self.txt_seq.insert("1.0", "...")
        self.txt_seq.tag_add("center", "1.0", "end")
        self.txt_seq.configure(state="disabled")
        
        self.lbl_status.config(text="")
        
        # Délai aléatoire avant d'afficher la séquence
        delay = random.randint(1000, 2000)
        self.top.after(delay, self.gui_start_sequence)

    def gui_start_sequence(self):
        """Génère et affiche la séquence à taper."""
        nb_inputs = random.randint(self.min_inputs, self.max_inputs)
        self.current_sequence = random.choices(self.pool_lettres, k=nb_inputs)
        self.current_input_index = 0
        
        # Affichage initial
        seq_str = " ".join(self.current_sequence)
        
        self.txt_seq.configure(state="normal")
        self.txt_seq.delete("1.0", "end")
        self.txt_seq.insert("1.0", seq_str)
        self.txt_seq.tag_add("center", "1.0", "end") # Centrage
        self.txt_seq.configure(state="disabled")
        
        # Application des couleurs (la première lettre sera jaune)
        self._update_colors()
        
        self.lbl_status.config(text="TAPPEZ LES LETTRES !", fg="yellow")
        
        # On attend la première touche
        self.gui_wait_for_input()

    def gui_wait_for_input(self):
        """Lance le timer pour la prochaine touche attendue."""
        # Temps en ms
        timeout_ms = int(self.temps_reaction * 1000)
        self.timer_job = self.top.after(timeout_ms, self.gui_timeout)

    def gui_timeout(self):
        """Appelé si le joueur est trop lent."""
        self.lbl_status.config(text="TROP LENT ! VOUS GLISSEZ !", fg="red")
        self.gui_fail()

    def on_gui_key(self, event):
        """Gestion de la frappe clavier."""
        # Si on n'est pas en train de jouer une séquence (ex: pause entre tours), on ignore
        if not self.current_sequence or self.timer_job is None:
            return

        # Annuler le timer en cours car une touche a été pressée
        if self.timer_job:
            self.top.after_cancel(self.timer_job)
            self.timer_job = None

        char_pressed = event.char.upper()
        expected = self.current_sequence[self.current_input_index]

        # Vérification
        if char_pressed == expected:
            # Correct
            self.current_input_index += 1
            
            # Mise à jour UNIQUEMENT des couleurs (pas de changement de texte -> pas de décalage)
            self._update_colors()

            if self.current_input_index >= len(self.current_sequence):
                # Séquence finie -> Round gagné
                self.lbl_status.config(text="PRISE VALIDÉE", fg="#0f0")
                self.current_sequence = []  # Reset
                self.top.after(1000, self.gui_next_round)
            else:
                # On attend la lettre suivante
                self.gui_wait_for_input()
        else:
            # Mauvaise touche
            self.lbl_status.config(text=f"ERREUR ! ({char_pressed} au lieu de {expected})", fg="red")
            self.gui_fail()

    def gui_fail(self):
        """Gestion de l'échec."""
        self.lbl_info.config(text="--- CHUTE ! ---", fg="red")
        self.gui_success = False
        self.current_sequence = []
        # Ferme la fenêtre après 2 secondes
        self.top.after(2000, self.top.destroy)