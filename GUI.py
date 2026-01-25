"""
Module gérant l'interface graphique (GUI) du jeu avec Tkinter.
"""
import time
import sys
import tkinter as tk
from tkinter import ttk, simpledialog
from pathlib import Path
from PIL import Image, ImageTk
from game import Game

# pylint: disable=too-many-instance-attributes, too-many-statements
# pylint: disable=too-many-locals, too-many-branches, broad-exception-caught

class _StdoutRedirector:
    """Redirige les print() vers le widget Text de Tkinter."""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, msg):
        """Écrit le message dans le widget texte avec le bon tag."""
        if not msg or msg == "\n":
            self._insert_text(msg, None)
            return

        self.text_widget.configure(state="normal")
        msg_lower = msg.lower()
        tag = "info"

        if msg.strip().startswith(">"):
            tag = "cmd"
        elif "|" in msg:
            tag = "error"
        elif any(w in msg_lower for w in ["inventaire", "quête", "journal", "objectif"]):
            tag = "inv"
        elif ":" in msg and not msg.strip().startswith("http"):
            tag = "npc"

        self._insert_text(msg, tag)

    def _insert_text(self, msg, tag):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", msg, tag)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def flush(self):
        """Méthode requise par sys.stdout."""

class GameGUI(tk.Tk):
    """Interface graphique Tkinter pour le jeu."""

    IMAGE_WIDTH = 600
    IMAGE_HEIGHT = 600

    def __init__(self):
        super().__init__()
        self.title("TBA - Héritage du Sommet")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.attributes('-fullscreen', True)
        self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))

        self.game = Game()
        self.game.gui = self

        name = simpledialog.askstring("Nom", "Entrez votre nom:", parent=self)
        if not name:
            name = "Joueur"
        self.game.setup(player_name=name)

        self.bg_photo = self._safe_load_icon('bzckground_image.png',
                                             size=(screen_width, screen_height))
        if self.bg_photo:
            self.bg_label = tk.Label(self, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()

        self.last_command = ""
        self.var_energy = tk.DoubleVar(value=100)
        self.var_mental = tk.DoubleVar(value=100)
        self.var_heat = tk.DoubleVar(value=100)
        self.txt_energy = tk.StringVar(value="100")
        self.txt_mental = tk.StringVar(value="100")
        self.txt_heat = tk.StringVar(value="100")

        self.start_time = None
        self.timer_var = tk.StringVar(value="00:00:00")

        self.current_bg_file = None
        self.target_bg_file = None
        self.bg_alpha = 0
        self.bg_img_object = None
        self.bg_photo_ref = None

        self.current_char_file = None
        self.target_char_file = None
        self.char_alpha = 0
        self.char_img_object = None
        self.char_photo_ref = None
        self._sherpa_ref = None

        self.canvas = None
        self.text_output = None
        self.entry_var = None
        self.entry = None
        self.btn_action_look = None
        self._btn_help = None
        self._btn_up = None
        self._btn_down = None
        self._btn_left = None
        self._btn_right = None
        self._btn_quit = None
        self._btn_look = None
        self._btn_inventory = None
        self._btn_quest = None
        self._btn_climb = None
        self._btn_talk = None

        self._build_layout()

        self.original_stdout = sys.stdout
        sys.stdout = _StdoutRedirector(self.text_output)

        self.game.print_welcome()
        self._update_interface()

        self._animate_loop()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _safe_load_icon(self, filename, size=None):
        """Charge une icône de manière sécurisée."""
        assets_dir = Path(__file__).parent / 'assets'
        file_path = assets_dir / filename
        try:
            pil_image = Image.open(str(file_path))
            if size:
                pil_image = pil_image.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(pil_image)
        except Exception:
            return None

    def _load_pil_image(self, filename):
        """Charge une image PIL brute pour l'animation."""
        try:
            assets_dir = Path(__file__).parent / 'assets'
            path = assets_dir / filename
            return Image.open(str(path))
        except Exception:
            return None

    def _apply_alpha(self, pil_img, alpha_value):
        """Applique une transparence à une image PIL."""
        img_copy = pil_img.copy()
        if img_copy.mode != 'RGBA':
            img_copy = img_copy.convert('RGBA')

        factor = alpha_value / 255.0
        _, _, _, alpha = img_copy.split()
        alpha = alpha.point(lambda i: int(i * factor))
        img_copy.putalpha(alpha)
        return img_copy

    def _update_timer_loop(self):
        """Met à jour le chronomètre."""
        if self.game.finished:
            return

        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        centiseconds = int((elapsed * 100) % 100)

        time_str = f"{minutes:02}:{seconds:02}:{centiseconds:02}"
        self.timer_var.set(time_str)
        self.after(50, self._update_timer_loop)

    def _animate_loop(self):
        """Boucle d'animation pour les transitions fluides."""
        if self.target_bg_file != self.current_bg_file:
            if self.bg_alpha > 0:
                self.bg_alpha = max(0, self.bg_alpha - 20)
            else:
                self.current_bg_file = self.target_bg_file
                if self.current_bg_file:
                    self.bg_img_object = self._load_pil_image(self.current_bg_file)
        elif self.bg_alpha < 255 and self.current_bg_file:
            self.bg_alpha = min(255, self.bg_alpha + 15)

        if self.target_char_file != self.current_char_file:
            if self.char_alpha > 0:
                self.char_alpha = max(0, self.char_alpha - 25)
            else:
                self.current_char_file = self.target_char_file
                if self.current_char_file:
                    self.char_img_object = self._load_pil_image(self.current_char_file)
        elif self.char_alpha < 255 and self.current_char_file:
            self.char_alpha = min(255, self.char_alpha + 25)

        try:
            if hasattr(self, 'canvas'):
                self.canvas.delete("all")
                if self.bg_img_object and self.bg_alpha > 0:
                    final_bg = self._apply_alpha(self.bg_img_object, self.bg_alpha)
                    self.bg_photo_ref = ImageTk.PhotoImage(final_bg)
                    self.canvas.create_image(self.IMAGE_WIDTH/2, self.IMAGE_HEIGHT/2,
                                             image=self.bg_photo_ref)

                if self.char_img_object and self.char_alpha > 0:
                    current_alpha = self.char_alpha
                    if self.current_char_file and "ivan" in self.current_char_file.lower():
                        current_alpha = int(self.char_alpha * 0.8)
                    final_char = self._apply_alpha(self.char_img_object, current_alpha)
                    self.char_photo_ref = ImageTk.PhotoImage(final_char)
                    self.canvas.create_image(self.IMAGE_WIDTH/2, self.IMAGE_HEIGHT/1.4,
                                             image=self.char_photo_ref)
        except Exception:
            pass
        self.after(40, self._animate_loop)

    def _build_layout(self):
        """Construit l'interface graphique."""
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        bg_panel = "#3D5C5B"
        fg_text = "white"

        style = ttk.Style()
        style.theme_use('clam')
        bar_thickness = 40
        style.configure("Energy.Horizontal.TProgressbar", foreground='#4CAF50',
                        background='#4CAF50', troughcolor=bg_panel,
                        thickness=bar_thickness, bordercolor=bg_panel)
        style.configure("Mental.Horizontal.TProgressbar", foreground='#2196F3',
                        background='#2196F3', troughcolor=bg_panel,
                        thickness=bar_thickness, bordercolor=bg_panel)
        style.configure("Heat.Horizontal.TProgressbar", foreground='#FF5722',
                        background='#FF5722', troughcolor=bg_panel,
                        thickness=bar_thickness, bordercolor=bg_panel)

        # 1. ZONE IMAGE
        image_frame = tk.Frame(self, bg="black", bd=2, relief="raised")
        image_frame.grid(row=0, column=0, sticky="nw", padx=30, pady=30)
        image_frame.grid_propagate(False)
        image_frame.config(width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT)

        self.canvas = tk.Canvas(image_frame, width=self.IMAGE_WIDTH,
                                height=self.IMAGE_HEIGHT, bg="#111", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 2. ZONE BOUTONS
        buttons_frame = tk.Frame(self, bg=bg_panel, bd=2, relief="raised")
        buttons_frame.grid(row=0, column=1, sticky="ne", padx=30, pady=30)
        buttons_frame.grid_columnconfigure(0, weight=1)

        self._load_all_icons()

        center_container = tk.Frame(buttons_frame, bg=bg_panel)
        center_container.grid(row=1, column=0, sticky="ew", padx=10, pady=(20, 10))

        # Stats
        stats_frame = tk.LabelFrame(center_container, text=" État ", bg=bg_panel,
                                    fg=fg_text, font=("Helvetica", 12, "bold"))
        stats_frame.grid(row=0, column=0, sticky="sw", padx=(0, 10))

        font_lbl = ("Helvetica", 14, "bold")
        bar_length = 250

        for i, (txt, var, style_bar, var_txt) in enumerate([
            ("Énergie", self.var_energy, "Energy.Horizontal.TProgressbar", self.txt_energy),
            ("Mental", self.var_mental, "Mental.Horizontal.TProgressbar", self.txt_mental),
            ("Chaleur", self.var_heat, "Heat.Horizontal.TProgressbar", self.txt_heat)
        ]):
            tk.Label(stats_frame, text=txt, font=font_lbl, bg=bg_panel, fg=fg_text)\
                .grid(row=i, column=0, sticky="w", padx=5)
            ttk.Progressbar(stats_frame, style=style_bar, variable=var,
                            maximum=100, length=bar_length).grid(row=i, column=1, padx=5, pady=5)
            tk.Label(stats_frame, textvariable=var_txt, width=4, font=font_lbl,
                     bg=bg_panel, fg=fg_text).grid(row=i, column=2, sticky="e", padx=5)

        timer_frame = tk.LabelFrame(center_container, text=" Chrono ", bg=bg_panel,
                                    fg=fg_text, font=("Helvetica", 12, "bold"))
        timer_frame.grid(row=1, column=0, sticky="new", padx=(0, 10), pady=(5, 0))
        tk.Label(timer_frame, textvariable=self.timer_var, font=("Consolas", 24, "bold"),
                 bg=bg_panel, fg="#00E676").pack(pady=5)

        # Mouvements
        move_frame = tk.LabelFrame(center_container, text=" Déplacements ", bg=bg_panel,
                                   fg=fg_text, font=("Helvetica", 12, "bold"))
        move_frame.grid(row=0, column=1, rowspan=2, sticky="sw", padx=(40, 0), pady=(10, 0))

        btn_opts = {'bg': bg_panel, 'fg': fg_text, 'activebackground': '#444', 'bd': 0}
        tk.Button(move_frame, image=self._btn_up,
                  command=lambda: self._send_command("go N"), **btn_opts)\
            .grid(row=0, column=0, columnspan=2, pady=5)
        tk.Button(move_frame, image=self._btn_left,
                  command=lambda: self._send_command("go O"), **btn_opts)\
            .grid(row=1, column=0, padx=(5, 30))
        tk.Button(move_frame, image=self._btn_right,
                  command=lambda: self._send_command("go E"), **btn_opts)\
            .grid(row=1, column=1, padx=(30, 5))
        tk.Button(move_frame, image=self._btn_down,
                  command=lambda: self._send_command("go S"), **btn_opts)\
            .grid(row=2, column=0, columnspan=2, pady=5)

        # Actions
        actions_frame = tk.LabelFrame(buttons_frame, text=" Actions ", bg=bg_panel,
                                      fg=fg_text, font=("Helvetica", 12, "bold"))
        actions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        act_opts = {'bg': bg_panel, 'fg': fg_text, 'activebackground': '#444', 'compound': 'left',
                    'bd': 1, 'relief': 'flat', 'padx': 10, 'pady': 5, 'anchor': 'w'}

        self.btn_action_look = tk.Button(actions_frame, text="Regarder", image=self._btn_look,
                                         command=lambda: self._send_command("look"), **act_opts)
        self.btn_action_look.pack(side="left", fill="x", expand=True, padx=2)

        tk.Button(actions_frame, text="Inventaire", image=self._btn_inventory,
                  command=lambda: self._send_command("check"), **act_opts)\
            .pack(side="left", fill="x", expand=True, padx=2)
        tk.Button(actions_frame, text="Quêtes", image=self._btn_quest,
                  command=lambda: self._send_command("quests"), **act_opts)\
            .pack(side="left", fill="x", expand=True, padx=2)
        tk.Button(actions_frame, text="Grimper (QTE)", image=self._btn_climb,
                  command=lambda: self._send_command("escalade"), **act_opts)\
            .pack(side="left", fill="x", expand=True, padx=2)

        tk.Button(buttons_frame, image=self._btn_quit, text="Quitter", bg=bg_panel,
                  fg="#ff5555", activebackground="#444", bd=0,
                  command=lambda: self._send_command("quit"))\
            .grid(row=3, column=0, sticky="e", padx=10, pady=(0, 10))

        tk.Button(buttons_frame, image=self._btn_help, text="Aide", bg=bg_panel,
                  fg=fg_text, activebackground="#444", bd=0,
                  command=lambda: self._send_command("help"))\
            .grid(row=3, column=0, sticky="e", padx=80, pady=(0, 10))

        # 3. TERMINAL
        output_frame = tk.Frame(self, bg=bg_panel, bd=2, relief="raised")
        output_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=30, pady=(0, 30))
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(output_frame, orient="vertical")
        self.text_output = tk.Text(output_frame, wrap="word", yscrollcommand=scrollbar.set,
                                   state="disabled", bg="#111", fg="#eee",
                                   font=("Consolas", 11), bd=0, padx=10, pady=10)

        self.text_output.tag_configure("error", foreground="#FF5252", font=("Consolas", 11, "bold"))
        self.text_output.tag_configure("cmd", foreground="#00E676", font=("Consolas", 11, "italic"))
        self.text_output.tag_configure("inv", foreground="#BA68C8", font=("Consolas", 11))
        self.text_output.tag_configure("npc", foreground="#FFD700", font=("Consolas", 11))
        self.text_output.tag_configure("info", foreground="#81D4FA", font=("Consolas", 11))

        scrollbar.config(command=self.text_output.yview)
        self.text_output.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # 4. ENTRÉE TEXTE
        entry_frame = tk.Frame(self, bg=bg_panel, bd=2, relief="raised")
        entry_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=30, pady=(0, 30))
        entry_frame.grid_columnconfigure(0, weight=1)

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(entry_frame, textvariable=self.entry_var, bg="#333",
                              fg="white", insertbackground="white", font=("Consolas", 12), bd=0)
        self.entry.grid(row=0, column=0, sticky="ew", ipady=8, padx=5, pady=5)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

    def _load_all_icons(self):
        """Charge toutes les icônes."""
        self._btn_help = self._safe_load_icon('help-50.png')
        self._btn_up = self._safe_load_icon('up-arrow-50.png')
        self._btn_down = self._safe_load_icon('down-arrow-50.png')
        self._btn_left = self._safe_load_icon('left-arrow-50.png')
        self._btn_right = self._safe_load_icon('right-arrow-50.png')
        self._btn_quit = self._safe_load_icon('quit-50.png')
        self._btn_look = (self._safe_load_icon('look_button.png', size=(50, 50)) or
                          self._safe_load_icon('look_image.png', size=(50, 50)))
        self._btn_inventory = self._safe_load_icon('inventory_button.png', size=(50, 50))
        self._btn_quest = self._safe_load_icon('quest_button.png', size=(50, 50))
        self._btn_climb = self._safe_load_icon('climb_button.png', size=(50, 50))
        self._btn_talk = self._safe_load_icon('talk_image.png', size=(50, 50))

    def _update_interface(self):
        """Met à jour les barres de statut et l'image."""
        if not self.game.player:
            return

        player = self.game.player
        self.var_energy.set(player.energy)
        self.var_mental.set(player.mental_health)
        self.var_heat.set(player.heat)
        self.txt_energy.set(f"{int(player.energy)}")
        self.txt_mental.set(f"{int(player.mental_health)}")
        self.txt_heat.set(f"{int(player.heat)}")

        current_room = self.game.player.current_room
        if getattr(current_room, 'image', None):
            self.target_bg_file = current_room.image
        else:
            self.target_bg_file = 'scene.png'

        found_char_file = None
        char_name_for_talk = None

        if self.last_command and ("look" in self.last_command.lower() or
                                  "talk" in self.last_command.lower()):
            if current_room.characters:
                first_char_name = list(current_room.characters.keys())[0]
                found_char_file = f"{first_char_name.lower()}_image.png"
                char_name_for_talk = first_char_name

        self.target_char_file = found_char_file

        if hasattr(self, 'btn_action_look'):
            if char_name_for_talk:
                self.btn_action_look.config(
                    text="Parler     ",
                    image=self._btn_talk if self._btn_talk else self._btn_look,
                    bg="#2E7D32", activebackground="#1B5E20",
                    command=lambda: self._send_command(f"talk {char_name_for_talk}")
                )
            else:
                self.btn_action_look.config(
                    text="Regarder",
                    image=self._btn_look,
                    bg="#3D5C5B", activebackground="#444",
                    command=lambda: self._send_command("look")
                )

    def _on_enter(self, _event=None):
        value = self.entry_var.get().strip()
        if value:
            self._send_command(value)
        self.entry_var.set("")

    def _send_command(self, command):
        if self.game.finished:
            return
        ancienne_salle = self.game.player.current_room

        if self.start_time is None:
            self.start_time = time.time()
            self._update_timer_loop()

        self.last_command = command
        print(f"\n> {command}")
        self.game.process_command(command)
        self.game.update_after_turn(ancienne_salle)
        self._update_interface()

        if self.game.finished:
            self.entry.configure(state="disabled")
            print("\n" + "="*30)
            print(" APPUYEZ SUR [ENTRÉE] POUR QUITTER ")
            print("="*30)
            self.bind("<Return>", lambda e: self._on_close())

    def _on_close(self):
        sys.stdout = self.original_stdout
        self.destroy()

    def log(self, message, tag=None):
        """Affiche un message dans le terminal."""
        self.text_output.configure(state="normal")
        self.text_output.insert("end", message + "\n", tag)
        self.text_output.see("end")
        self.text_output.configure(state="disabled")
