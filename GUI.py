import tkinter as tk
from tkinter import ttk, simpledialog
from pathlib import Path
import sys
from PIL import Image, ImageTk
from game import Game
import time

class _StdoutRedirector:
    """Redirige les print() vers le widget Text de Tkinter."""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, msg):
        if msg:
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", msg)
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")

    def flush(self):
        pass

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

        self.bg_photo = self._safe_load_icon('bzckground_image.png', size=(screen_width, screen_height))
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

        self.start_time = time.time()
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
        """Charge une image PIL brute pour l'animation (sans la convertir en PhotoImage)."""
        try:
            assets_dir = Path(__file__).parent / 'assets'
            path = assets_dir / filename
            img = Image.open(str(path))
            return img
        except Exception:
            return None

    def _apply_alpha(self, pil_img, alpha_value):
        """Applique une transparence à une image PIL."""
        img_copy = pil_img.copy()
        if img_copy.mode != 'RGBA':
            img_copy = img_copy.convert('RGBA')
        
        factor = alpha_value / 255.0
        r, g, b, a = img_copy.split()
        a = a.point(lambda i: i * factor)
        img_copy.putalpha(a)
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
                self.bg_alpha -= 20
                if self.bg_alpha < 0: self.bg_alpha = 0
            else:
                self.current_bg_file = self.target_bg_file
                if self.current_bg_file:
                    self.bg_img_object = self._load_pil_image(self.current_bg_file)
        elif self.bg_alpha < 255 and self.current_bg_file:
            self.bg_alpha += 15
            if self.bg_alpha > 255: self.bg_alpha = 255

        if self.target_char_file != self.current_char_file:
            if self.char_alpha > 0:
                self.char_alpha -= 25
                if self.char_alpha < 0: self.char_alpha = 0
            else:
                self.current_char_file = self.target_char_file
                if self.current_char_file:
                    self.char_img_object = self._load_pil_image(self.current_char_file)
        elif self.char_alpha < 255 and self.current_char_file:
            self.char_alpha += 25
            if self.char_alpha > 255: self.char_alpha = 255

        try:
            if hasattr(self, 'canvas'):
                self.canvas.delete("all")
                
                if self.bg_img_object and self.bg_alpha > 0:
                    final_bg = self._apply_alpha(self.bg_img_object, self.bg_alpha)
                    self.bg_photo_ref = ImageTk.PhotoImage(final_bg)
                    self.canvas.create_image(self.IMAGE_WIDTH/2, self.IMAGE_HEIGHT/2, image=self.bg_photo_ref)

                if self.char_img_object and self.char_alpha > 0:
                    final_char = self._apply_alpha(self.char_img_object, self.char_alpha)
                    self.char_photo_ref = ImageTk.PhotoImage(final_char)
                    self.canvas.create_image(self.IMAGE_WIDTH/2, self.IMAGE_HEIGHT/1.4, image=self.char_photo_ref)
        except Exception:
            pass

        self.after(40, self._animate_loop)

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        BG_PANEL = "#3D5C5B"
        FG_TEXT = "white"

        style = ttk.Style()
        style.theme_use('clam') 
        BAR_THICKNESS = 40 
        style.configure("Energy.Horizontal.TProgressbar", foreground='#4CAF50', background='#4CAF50', troughcolor=BG_PANEL, thickness=BAR_THICKNESS, bordercolor=BG_PANEL)
        style.configure("Mental.Horizontal.TProgressbar", foreground='#2196F3', background='#2196F3', troughcolor=BG_PANEL, thickness=BAR_THICKNESS, bordercolor=BG_PANEL)
        style.configure("Heat.Horizontal.TProgressbar", foreground='#FF5722', background='#FF5722', troughcolor=BG_PANEL, thickness=BAR_THICKNESS, bordercolor=BG_PANEL)

        # 1. ZONE IMAGE
        image_frame = tk.Frame(self, bg="black", bd=2, relief="raised")
        image_frame.grid(row=0, column=0, sticky="nw", padx=30, pady=30)
        image_frame.grid_propagate(False)
        image_frame.config(width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT)
        
        self.canvas = tk.Canvas(image_frame, width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT, bg="#111", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 2. ZONE BOUTONS
        buttons_frame = tk.Frame(self, bg=BG_PANEL, bd=2, relief="raised")
        buttons_frame.grid(row=0, column=1, sticky="ne", padx=30, pady=30)
        buttons_frame.grid_columnconfigure(0, weight=1)

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
        self._btn_talk = self._safe_load_icon('talk_image.png', size=(50, 50))

        center_container = tk.Frame(buttons_frame, bg=BG_PANEL)
        center_container.grid(row=1, column=0, sticky="ew", padx=10, pady=(20, 10))

        # Stats
        stats_frame = tk.LabelFrame(center_container, text=" État ", bg=BG_PANEL, fg=FG_TEXT, font=("Helvetica", 12, "bold"))
        stats_frame.grid(row=0, column=0, sticky="sw", padx=(0, 10))
        
        font_lbl = ("Helvetica", 14, "bold")
        BAR_LENGTH = 250

        for i, (txt, var, style_bar, var_txt) in enumerate([
            ("Énergie", self.var_energy, "Energy.Horizontal.TProgressbar", self.txt_energy),
            ("Mental", self.var_mental, "Mental.Horizontal.TProgressbar", self.txt_mental),
            ("Chaleur", self.var_heat, "Heat.Horizontal.TProgressbar", self.txt_heat)
        ]):
            tk.Label(stats_frame, text=txt, font=font_lbl, bg=BG_PANEL, fg=FG_TEXT).grid(row=i, column=0, sticky="w", padx=5)
            ttk.Progressbar(stats_frame, style=style_bar, variable=var, maximum=100, length=BAR_LENGTH).grid(row=i, column=1, padx=5, pady=5)
            tk.Label(stats_frame, textvariable=var_txt, width=4, font=font_lbl, bg=BG_PANEL, fg=FG_TEXT).grid(row=i, column=2, sticky="e", padx=5)

        timer_frame = tk.LabelFrame(center_container, text=" Chrono ", bg=BG_PANEL, fg=FG_TEXT, font=("Helvetica", 12, "bold"))
        timer_frame.grid(row=1, column=0, sticky="new", padx=(0, 10), pady=(5, 0))      
        tk.Label(timer_frame, textvariable=self.timer_var, font=("Consolas", 24, "bold"), 
                 bg=BG_PANEL, fg="#00E676").pack(pady=5)
        self._update_timer_loop()


        # Mouvements
        move_frame = tk.LabelFrame(center_container, text=" Déplacements ", bg=BG_PANEL, fg=FG_TEXT, font=("Helvetica", 12, "bold"))
        move_frame.grid(row=0, column=1, rowspan=2, sticky="sw", padx=(40, 0), pady=(10, 0))
        
        btn_opts = {'bg': BG_PANEL, 'fg': FG_TEXT, 'activebackground': '#444', 'bd': 0}
        tk.Button(move_frame, image=self._btn_up, command=lambda: self._send_command("go N"), **btn_opts).grid(row=0, column=0, columnspan=2, pady=5)
        tk.Button(move_frame, image=self._btn_left, command=lambda: self._send_command("go O"), **btn_opts).grid(row=1, column=0, padx=(5, 30))
        tk.Button(move_frame, image=self._btn_right, command=lambda: self._send_command("go E"), **btn_opts).grid(row=1, column=1, padx=(30, 5))
        tk.Button(move_frame, image=self._btn_down, command=lambda: self._send_command("go S"), **btn_opts).grid(row=2, column=0, columnspan=2, pady=5)

        # Actions
        actions_frame = tk.LabelFrame(buttons_frame, text=" Actions ", bg=BG_PANEL, fg=FG_TEXT, font=("Helvetica", 12, "bold"))
        actions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        act_opts = {'bg': BG_PANEL, 'fg': FG_TEXT, 'activebackground': '#444', 'compound': 'left', 'bd': 1, 'relief': 'flat', 'padx': 10, 'pady': 5, 'anchor': 'w'}
        
        self.btn_action_look = tk.Button(actions_frame, text="Regarder", image=self._btn_look, command=lambda: self._send_command("look"), **act_opts)
        self.btn_action_look.pack(side="left", fill="x", expand=True, padx=2)

        tk.Button(actions_frame, text="Inventaire", image=self._btn_inventory, command=lambda: self._send_command("check"), **act_opts).pack(side="left", fill="x", expand=True, padx=2)
        tk.Button(actions_frame, text="Quêtes", image=self._btn_quest, command=lambda: self._send_command("quests"), **act_opts).pack(side="left", fill="x", expand=True, padx=2)
        tk.Button(actions_frame, text="Grimper (QTE)", image=self._btn_climb, command=lambda: self._send_command("escalade"), **act_opts).pack(side="left", fill="x", expand=True, padx=2)
        
        tk.Button(buttons_frame, image=self._btn_quit, text="Quitter", bg=BG_PANEL, fg="#ff5555", activebackground="#444", bd=0,
                  command=lambda: self._send_command("quit")).grid(row=3, column=0, sticky="e", padx=10, pady=(0, 10))
        
        tk.Button(buttons_frame, image=self._btn_help, text="Aide", bg=BG_PANEL, fg=FG_TEXT, activebackground="#444", bd=0,
                  command=lambda: self._send_command("help")).grid(row=3, column=0, sticky="e", padx=80, pady=(0, 10))



        # 3. TERMINAL
        output_frame = tk.Frame(self, bg=BG_PANEL, bd=2, relief="raised")
        output_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=30, pady=(0, 30))
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(output_frame, orient="vertical")
        self.text_output = tk.Text(output_frame, wrap="word", yscrollcommand=scrollbar.set, state="disabled",
                                   bg="#111", fg="#eee", font=("Consolas", 11), bd=0, padx=10, pady=10)
        scrollbar.config(command=self.text_output.yview)
        self.text_output.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # 4. ENTRÉE TEXTE
        entry_frame = tk.Frame(self, bg=BG_PANEL, bd=2, relief="raised")
        entry_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=30, pady=(0, 30))
        entry_frame.grid_columnconfigure(0, weight=1)

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(entry_frame, textvariable=self.entry_var, bg="#333", fg="white", insertbackground="white", font=("Consolas", 12), bd=0)
        self.entry.grid(row=0, column=0, sticky="ew", ipady=8, padx=5, pady=5)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

    def _update_interface(self):
        if not self.game.player: return

        p = self.game.player
        self.var_energy.set(p.energy)
        self.var_mental.set(p.mental_health)
        self.var_heat.set(p.heat)
        self.txt_energy.set(f"{int(p.energy)}")
        self.txt_mental.set(f"{int(p.mental_health)}")
        self.txt_heat.set(f"{int(p.heat)}")

        current_room = self.game.player.current_room
        if getattr(current_room, 'image', None):
            self.target_bg_file = current_room.image
        else:
            self.target_bg_file = 'scene.png'

        found_char_file = None
        char_name_for_talk = None

        if self.last_command and ("look" in self.last_command.lower() or "talk" in self.last_command.lower()):
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
                    bg="#2E7D32",
                    activebackground="#1B5E20",
                    command=lambda: self._send_command(f"talk {char_name_for_talk}")
                )
            else:
                self.btn_action_look.config(
                    text="Regarder",
                    image=self._btn_look,
                    bg="#3D5C5B",
                    activebackground="#444",
                    command=lambda: self._send_command("look")
                )

    def _on_enter(self, _event=None):
        value = self.entry_var.get().strip()
        if value:
            self._send_command(value)
        self.entry_var.set("")

    def _send_command(self, command):
        if self.game.finished: return
        self.last_command = command
        print(f"\n> {command}")
        self.game.process_command(command)
        self._update_interface()
        if self.game.finished:
            self.entry.configure(state="disabled")
            self.after(2000, self._on_close)

    def _on_close(self):
        sys.stdout = self.original_stdout
        self.destroy()