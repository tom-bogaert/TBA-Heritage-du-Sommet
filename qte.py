import random
import time
import os
import sys
import tkinter as tk
from tkinter import ttk

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
        self.game = game
        self.nb_tours = nb_tours
        self.min_inputs = min_inputs
        self.max_inputs = max_inputs
        self.temps_reaction = temps_reaction
        self.pool_lettres = pool_lettres.upper()
        self.score = 0

    def start(self):
        """Lance la version appropriée du QTE."""
        if hasattr(self.game, 'gui') and self.game.gui:
            return self.start_gui()
        else:
            return self.start_console()

    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _get_key_timed(self, timeout):
        start_time = time.time()
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

    def start_gui(self):
        """Lance le QTE dans une fenêtre modale Tkinter."""
        self.root = self.game.gui
        self.gui_success = False
        
        self.top = tk.Toplevel(self.root)
        self.top.title("⚠️ ESCALADE EN COURS ⚠️")
        self.top.geometry("1000x800")
        self.top.transient(self.root)
        self.top.grab_set()
        self.top.configure(bg="#222")
        
        self.current_round = 0
        self.current_sequence = []
        self.current_input_index = 0
        self.timer_job = None
        self.start_input_time = 0 
        self.progress_var = tk.DoubleVar(value=0)
        
        self.current_timeout = self.temps_reaction 

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=30, troughcolor='#333', background='red')
        
        self.lbl_timer_title = tk.Label(self.top, text="TEMPS LIMITE", font=("Helvetica", 12, "bold"), fg="#f55", bg="#222")
        self.lbl_timer_title.pack(pady=(20, 5))

        self.progress_bar = ttk.Progressbar(self.top, variable=self.progress_var, maximum=100, length=800, style="TProgressbar")
        self.progress_bar.pack(pady=(0, 20))

        self.lbl_info = tk.Label(self.top, text="PRÉPAREZ-VOUS...", font=("Helvetica", 20), fg="white", bg="#222")
        self.lbl_info.pack(pady=10)
        
        self.txt_seq = tk.Text(
            self.top, 
            height=5,
            width=30,
            font=("Courier", 45, "bold"), 
            bg="#222", 
            fg="#0ff", 
            bd=0, 
            highlightthickness=0,
            wrap="word"
        )
        self.txt_seq.pack(pady=20, padx=10)
        
        self.txt_seq.tag_configure("center", justify='center')
        self.txt_seq.tag_configure("done", foreground="#177808")
        self.txt_seq.tag_configure("current", foreground="yellow")
        self.txt_seq.tag_configure("todo", foreground="#555")
        
        self.txt_seq.insert("1.0", "")
        self.txt_seq.configure(state="disabled")

        self.lbl_status = tk.Label(self.top, text="", font=("Helvetica", 14), fg="#f55", bg="#222")
        self.lbl_status.pack(pady=20)
        
        self.top.bind("<Key>", self.on_gui_key)
        self.top.focus_set()

        self.top.after(1500, self.gui_next_round)
        
        self.root.wait_window(self.top)
        
        return self.gui_success

    def _update_colors(self):
        """Met à jour les couleurs des lettres sans changer le texte."""
        self.txt_seq.configure(state="normal")
        
        self.txt_seq.tag_remove("done", "1.0", "end")
        self.txt_seq.tag_remove("current", "1.0", "end")
        self.txt_seq.tag_remove("todo", "1.0", "end")
        
        for i in range(len(self.current_sequence)):
            start_pos = f"1.{i*2}"
            end_pos = f"1.{i*2 + 1}"
            
            if i < self.current_input_index:
                self.txt_seq.tag_add("done", start_pos, end_pos)
            elif i == self.current_input_index:
                self.txt_seq.tag_add("current", start_pos, end_pos)
            else:
                self.txt_seq.tag_add("todo", start_pos, end_pos)
        
        self.txt_seq.configure(state="disabled")

    def gui_next_round(self):
        """Prépare le prochain round."""
        self.progress_var.set(0)

        if self.current_round >= self.nb_tours:
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
        
        self.txt_seq.configure(state="normal")
        self.txt_seq.delete("1.0", "end")
        self.txt_seq.insert("1.0", "...")
        self.txt_seq.tag_add("center", "1.0", "end")
        self.txt_seq.configure(state="disabled")
        
        self.lbl_status.config(text="")
        
        delay = random.randint(1000, 2000)
        self.top.after(delay, self.gui_start_sequence)

    def gui_start_sequence(self):
        """Génère et affiche la séquence à taper."""
        nb_inputs = random.randint(self.min_inputs, self.max_inputs)
        self.current_sequence = random.choices(self.pool_lettres, k=nb_inputs)
        self.current_input_index = 0
        
        self.current_timeout = self.temps_reaction

        seq_str = " ".join(self.current_sequence)
        
        self.txt_seq.configure(state="normal")
        self.txt_seq.delete("1.0", "end")
        self.txt_seq.insert("1.0", seq_str)
        self.txt_seq.tag_add("center", "1.0", "end")
        self.txt_seq.configure(state="disabled")
        
        self._update_colors()
        
        self.lbl_status.config(text="TAPPEZ LES LETTRES !", fg="yellow")
        
        self.gui_start_timer()

    def _animate_timer(self):
        """Fonction appelée en boucle pour mettre à jour la barre de temps."""
        if not self.timer_job: return

        elapsed = time.time() - self.start_input_time
    
        ratio = (elapsed / self.current_timeout) * 100
        self.progress_var.set(ratio)

        if elapsed >= self.current_timeout:
            self.gui_timeout()
        else:
            self.timer_job = self.top.after(20, self._animate_timer)

    def gui_start_timer(self):
        """Lance le timer au début du round."""
        self.start_input_time = time.time()
        self.progress_var.set(0)
        self.timer_job = self.top.after(20, self._animate_timer)

    def gui_timeout(self):
        """Appelé si le joueur est trop lent."""
        if self.timer_job:
            self.top.after_cancel(self.timer_job)
            self.timer_job = None
            
        self.lbl_status.config(text="TROP LENT ! VOUS GLISSEZ !", fg="red")
        self.gui_fail()

    def on_gui_key(self, event):
        """Gestion de la frappe clavier."""
        if not self.current_sequence or self.timer_job is None:
            return

        if self.timer_job:
            self.top.after_cancel(self.timer_job)
            self.timer_job = None

        char_pressed = event.char.upper()
    
        if len(char_pressed) != 1 or char_pressed not in "AZERTYUIOPQSDFGHJKLMWXCVBN":
             self.timer_job = self.top.after(20, self._animate_timer)
             return

        expected = self.current_sequence[self.current_input_index]

        if char_pressed == expected:
            self.current_input_index += 1
            self._update_colors()

            if self.current_input_index >= len(self.current_sequence):
                self.lbl_status.config(text="PRISE VALIDÉE", fg="#0f0")
                self.progress_var.set(0)
                self.current_sequence = []
                self.top.after(800, self.gui_next_round)
            else:
                self.timer_job = self.top.after(20, self._animate_timer)
        else:
            self.lbl_status.config(text=f"ERREUR ! ({char_pressed} au lieu de {expected})", fg="red")
            self.gui_fail()

    def gui_fail(self):
        """Gestion de l'échec."""
        self.lbl_info.config(text="--- CHUTE ! ---", fg="red")
        self.gui_success = False
        self.current_sequence = []
        self.top.after(2000, self.top.destroy)