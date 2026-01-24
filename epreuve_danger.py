import tkinter as tk
from tkinter import ttk
import random

class EpreuveDanger:
    """
    Mini-jeu de type Démineur (Style Glace/Crevasse).
    Le joueur doit révéler les cases sûres sans tomber dans une crevasse.
    """

    def __init__(self, game, rows=6, cols=6, mines=6):
        self.game = game
        self.rows = rows
        self.cols = cols
        self.mines = mines
        
        self.buttons = {}  
        self.mine_positions = set()
        self.revealed_count = 0
        self.total_safe_cells = (rows * cols) - mines
        
        self.is_game_over = False
        self.success = False
        
        self.COLOR_ICE = "#54C5D4"  
        self.COLOR_SNOW = "#FFFFFF" 
        self.COLOR_CREVASSE = "#006064" 
        self.COLOR_TEXT = "#00BCD4" 
        self.COLORS_NUM = {
            1: "#0288D1",
            2: "#00574B",
            3: "#D32F2F",
            4: "#7B1FA2", 
            5: "#FFC107" 
        }

    def start(self):
        """Lance l'épreuve graphique et retourne True si réussi, False sinon."""
        if not hasattr(self.game, 'gui') or not self.game.gui:
            print("Erreur: Cette épreuve nécessite l'interface graphique.")
            return True

        self.root = self.game.gui
        

        self.top = tk.Toplevel(self.root)
        self.top.title("🧊 SONDAGE DE LA GLACE 🧊")
        self.top.geometry("600x700")
        self.top.transient(self.root)
        self.top.grab_set()
        self.top.configure(bg="#263238") 

        # En-tête
        tk.Label(self.top, text="DANGER : CREVASSES DÉTECTÉES", 
                 font=("Helvetica", 16, "bold"), fg="#FF5252", bg="#263238").pack(pady=(20, 5))
        
        tk.Label(self.top, text=f"Sondez la glace pour trouver un chemin sûr.\nIl y a {self.mines} crevasses cachées.", 
                 font=("Helvetica", 12), fg=self.COLOR_ICE, bg="#263238").pack(pady=(0, 20))

        self.grid_frame = tk.Frame(self.top, bg="#263238")
        self.grid_frame.pack()

        self._init_game()

        self.root.wait_window(self.top)
        
        return self.success

    def _init_game(self):
        """Initialise la grille et place les mines."""
        while len(self.mine_positions) < self.mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            self.mine_positions.add((r, c))

        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(
                    self.grid_frame,
                    width=4, height=2,
                    bg=self.COLOR_ICE,
                    activebackground="#80DEEA",
                    relief="raised",
                    bd=3,
                    font=("Arial", 14, "bold"),
                    command=lambda r=r, c=c: self._on_click(r, c)
                )
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.buttons[(r, c)] = {
                    "widget": btn,
                    "is_mine": (r, c) in self.mine_positions,
                    "revealed": False,
                    "neighbors": 0
                }

        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in self.mine_positions:
                    continue
                
                count = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= r + i < self.rows and 0 <= c + j < self.cols:
                            if (r + i, c + j) in self.mine_positions:
                                count += 1
                self.buttons[(r, c)]["neighbors"] = count

    def _on_click(self, r, c):
        """Gestion du clic sur une case."""
        if self.is_game_over: return

        cell = self.buttons[(r, c)]
        
        if cell["revealed"]: return

        if cell["is_mine"]:
            self._game_over_loss(r, c)
        else:
            self._reveal(r, c)
            self._check_win()

    def _reveal(self, r, c):
        """Révèle une case (et ses voisines si c'est un 0) - Algorithme Flood Fill."""
        if not (0 <= r < self.rows and 0 <= c < self.cols): return
        
        cell = self.buttons[(r, c)]
        if cell["revealed"]: return

        cell["revealed"] = True
        self.revealed_count += 1
        
        btn = cell["widget"]
        btn.config(relief="sunken", bg=self.COLOR_SNOW, state="disabled")

        if cell["neighbors"] > 0:
            color = self.COLORS_NUM.get(cell["neighbors"], "black")
            btn.config(text=str(cell["neighbors"]), disabledforeground=color)
        else:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0: continue
                    self._reveal(r + i, c + j)

    def _check_win(self):
        """Vérifie si le joueur a gagné."""
        if self.revealed_count == self.total_safe_cells:
            self.is_game_over = True
            self.success = True
            
            for pos, data in self.buttons.items():
                if data["is_mine"]:
                    data["widget"].config(bg="#A5D6A7", text="🚩")
            
            tk.Label(self.top, text="✅ PASSAGE SÉCURISÉ !", 
                     font=("Helvetica", 18, "bold"), fg="#69F0AE", bg="#263238").pack(pady=20)
            
            self.top.after(2000, self.top.destroy)

    def _game_over_loss(self, hit_r, hit_c):
        """Gère la défaite (tomber dans une crevasse)."""
        self.is_game_over = True
        self.success = False
        
        for (r, c), data in self.buttons.items():
            if data["is_mine"]:
                bg_color = self.COLOR_CREVASSE
                text = "🕳️"
                if r == hit_r and c == hit_c:
                    bg_color = "#FF5252"
                    text = "☠️"
                
                data["widget"].config(bg=bg_color, text=text, state="disabled")

        tk.Label(self.top, text="💀 LA GLACE CÈDE...", 
                 font=("Helvetica", 18, "bold"), fg="#FF5252", bg="#263238").pack(pady=20)
        
        self.top.after(3000, self.top.destroy)