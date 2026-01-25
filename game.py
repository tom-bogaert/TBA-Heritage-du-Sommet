from time import sleep
from room import Room
from player import Player
from command import Command
from actions import Actions
from chargement import Chargement
from character import Character
from quest import Quest, QuestManager
from epreuve_danger import EpreuveDanger 
import sys


class Game:

    def __init__(self):
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
        self.npcs = []
        self.quest_manager = QuestManager()
        self.gui = None
        
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
        self.commands["use"] = Command("use", " <objet> : utiliser un objet de l'inventaire", Actions.use, 1)
        
        self.commands["quests"] = Command("quests", " : afficher le journal des quêtes", Actions.quests, 0)
        self.commands["quest"] = Command("quest", " <nom> : afficher les détails d'une quête", Actions.quest, 1)

        fichier_config_jeu = "data.json"
        salles_chargees, salle_depart = Chargement.charger_depuis_json(fichier_config_jeu)
        
        if not salles_chargees or not salle_depart:
            print("\nERREUR FATALE: Impossible de charger les données du jeu.")
            self.finished = True
            return

        self.rooms = salles_chargees
        
        if player_name is None:
            player_name = input("\nEntrez votre nom: ")
            
        self.player = Player(player_name)
        self.player.current_room = salle_depart

        # --- QUÊTES ---
        q1 = Quest("Sécurité_avant_tout", "Trouver un piolet au Mess.", "TAKE_piolet", "Maîtrise du piolet")
        q2 = Quest("Première_Ascension", "Grimper la première paroi.", "MOVE_Entrée Glacier (E)", "Santé Mentale +1")
        q3 = Quest("Legende_du_Froid", "Trouver le légendaire Dôme de glace.", "MOVE_Le Dôme de Glace", "Santé Mentale +1")
        q4 = Quest("Rencontre_Ivan", "Parler à l'alpiniste russe Ivan.", "TALK_Ivan", "Santé Mentale +1")
        q5 = Quest("Remise_en_question", "Se remettre en question face à son reflet (autre_d).", "TALK_Autre_d", "Santé Mentale +1")
        q6 = Quest("Paix_interieure", "Faire la paix avec soi-même (autre_b).", "TALK_Autre_b", "Acceptation de sois")
        q7 = Quest("Appel_du_vide", "Retrouver la radio de Pégase.", "TAKE_Radio de Pégase", "Santé Mentale +1")
        q8 = Quest("Secrets_de_Pegase", "Trouver le Carnet de Pégase.", "TAKE_Carnet_de_Pegase", "Santé Mentale +1")
        q9 = Quest("Survie_passée", "Rejoindre le camp abandonné.", "MOVE_Camp 1.5 Abandonné", "Santé Mentale +1")
        q10 = Quest("Porte_de_la_mort", "Rejoindre le camp 'Le Nid'.", "MOVE_Le Nid (Camp 2) (E)", "Santé Mentale +1")
        q11 = Quest("Les_anciens_passages", "Trouver le Piolet Rouge'.", "MOVE_Le Piolet Rouge", "Santé Mentale +1")
        

        qf = Quest("Le_toit_du_monde", "Atteindre le sommet.", "MOVE_LE LOCUS (Fin)", "Gloire éternelle")

        
        for q in [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, qf]:
            self.quest_manager.add_quest(q)

        # --- PNJs ---
        dialogues_sherpa = [
            "Namaste. La montagne nous observe. Ne l'insulte pas en partant les mains nues. Ce glacier est plus dur que l'acier. Sans un bon PIOLET, tu ne passeras pas le premier mur. Va au Mess, trouves-en un.",
            "L'ascension n'est pas une marche continue, c'est un escalier de géants. À chaque palier d'altitude, un mur vertical te barrera la route. Tu devras grimper ces parois pour t'élever vers l'air raréfié.",
            "Écoute bien : plus haut, le sol devient traître. Tu entreras dans des ZONES DE DANGERS. Là-bas, ne cours pas. Tu dois SONDER LA GLACE pour révéler les failles cachées. Identifie les passages sûrs avant de poser le pied, ou la montagne t'avalera."
        ]

        dialogues_ivan = [
            "Привет, друг! Kamarad ? Tu as les batteries ? Ma lampe faiblit. Les ombres... elles ont des dents.",
            "L'Américain... Pégase. Je l'ai vu. Il est passé par là. Il parlait tout seul, des cercles, de la montagne vivante. Fou !",
            "Ne monte pas au sommet. Il n'y a rien. Juste le bruit. Le bruit qui gratte derrière le ciel.",
            "Tu as froid ? C'est bon signe. Quand tu n'auras plus froid, c'est que tu appartiens à la montagne."
        ]

        dialogues_autre_1 = [
            "Pourquoi tu t'accroches si fort ? La chute n'est qu'un envol qui a mal tourné.",
            "Regarde en bas. Ce n'est pas effrayant. C'est calme. Tout est silencieux en bas. Comme nous.",
            "Tu as mal aux jambes, je le sais. Je le sens. Assieds-toi. Juste une minute. La neige est chaude si tu fermes les yeux."
        ]

        dialogues_autre_2 = [
            "Alors comme ça... tu as continué. Je pensais que le froid t'aurait eu.",
            "Tu es plus fort que Pégase. Lui, il a cherché l'or. Toi, tu as cherché la fin.",
            "Il ne te reste qu'une chose à faire pour réaliser ton rêve.",
            "Va finir ton ascension. C'est juste derrière moi. C'est là que tout s'arrête... ou que tout commence."
        ]

        Character("Sherpa", "Un vieux guide au visage brûlé par le soleil et le vent.", salle_depart, dialogues_sherpa)
        Character("Ivan", "Un echo, alpiniste russe au regard hagard, emmitouflé dans des couches de vêtements usés.", self.rooms[27], dialogues_ivan, moveable=False)
        Character("Autre_d", "Un reflèt de vous même.", self.rooms[30], dialogues_autre_1,moveable=False)
        Character("Autre_b", "Un reflèt de vous même.", self.rooms[40], dialogues_autre_2,moveable=False)


        self.npcs = []
        for room in self.rooms:
            for char in room.characters.values():
                self.npcs.append(char)

    def check_win(self):
        if self.quest_manager.all_finished():
            print("\n🏆 VICTOIRE ABSOLUE ! Vous avez conquis la montagne !")
            self.finished = True
            return True
        return False

    def check_loose(self):
        if self.player.energy <= 0:
            print("\n|💀 DÉFAITE : Vous n'avez plus d'énergie pour continuer.")
            self.finished = True
            return True
        return False

    def update_after_turn(self, ancienne_salle):
        """Méthode appelée par la GUI après chaque action."""
        
        if self.player.current_room != ancienne_salle:
            nouvelle_salle = self.player.current_room

            if nouvelle_salle.name == "LE LOCUS (Fin)":
                print("\n|--- L'HÉRITAGE DU SOMMET ---")
                print("|Vous atteignez enfin le point culminant. L'air est trop rare, le silence trop lourd.")
                print("|La 'Veine Jaune' brille d'un éclat insoutenable. Votre esprit se fissure.")
                print("|Avant de vous éteindre vous repensez au chemin parcouru jusqu'à présent et regrettez vos QUÊTES non acomplis...")
                print("|💀 DÉFAITE : Vous avez atteint le sommet, mais vous avez perdu la raison.")
                print("|Votre corps reste prostré, fixant l'éternité...")
                
                self.player.mental_health = 0
                self.finished = True
                return
            
            event_move = f"MOVE_{nouvelle_salle.name}"
            self.quest_manager.check_events(event_move, self.player)
            
            for npc in self.npcs:
                if npc.moveable:
                    npc.move()

            if hasattr(nouvelle_salle, 'danger') and nouvelle_salle.danger:
                infos = nouvelle_salle.danger
                print(f"\n|⚠️  ZONE DANGEREUSE : {nouvelle_salle.name}")

                item_mod = self.player.get_passive_modifier("d_difficulty")
                
                epreuve = EpreuveDanger(self,
                                      rows=infos.get("rows", 6), 
                                      cols=infos.get("cols", 6), 
                                      mines=int(infos.get("mines", 5)*item_mod))
                
                reussite = epreuve.start()
                
                if reussite:
                    print("✅ Vous avez traversé la zone dangereuse sans encombre.")
                    nouvelle_salle.danger = None
                else:
                    print("💥 CRACK ! La glace cède sous vos pieds !")
                    if self.player.loose_energy_to_death(25):
                        self.finished = True

        if self.check_loose(): return
        self.check_win()

    def play(self):
        """Boucle principale pour le mode Console uniquement."""
        self.setup()
        if self.finished: return
        self.print_welcome()
        
        while not self.finished:
            ancienne_salle = self.player.current_room
            self.process_command(input("> "))
            self.update_after_turn(ancienne_salle)

    def process_command(self, command_string) -> None:
        """Traite la commande entrée par le joueur."""
        stripped_input = command_string.strip()
        if not stripped_input: return
        
        list_of_words = stripped_input.split()
        command_word = list_of_words[0].lower()

        if self.player and self.player.current_room.name == "Glacier (S)":
            bloquer_action = False

            if command_word == "go" and len(list_of_words) > 1:
                if list_of_words[1].upper() == "U":
                    bloquer_action = True
            
            elif command_word == "escalade":
                bloquer_action = True

            if bloquer_action:
                if "piolet" not in self.player.inventory:
                    print("\n|⛔ IMPOSSIBLE DE GRIMPER !")
                    print("|La paroi est trop abrupte et la glace trop dure.")
                    print("|Vous avez besoin d'un piolet pour assurer votre ascension.")
                    return 

        if command_word not in self.commands.keys():
            print(f"\nVous ne savez pas ce qu'est '{command_word}'\n")
        else:
            command = self.commands[command_word]
            command.action(self, list_of_words, command.number_of_parameters)
            

    def print_welcome(self):
        print(f"\nBienvenue {self.player.name} dans ce jeu d'aventure !")
        print("La Face Est du K2 est le dernier grand problème de l'himalayisme. Trop raide, trop exposée aux avalanches, jamais vaincue. ")
        print("Le passé (Projet Pégase) : Il y a 5 ans, une expédition ultra-médiatisée et suréquipée, menée par un alpiniste charismatique surnommé \"Pégase\", a tenté l'impossible. Ils ont disparu corps et biens après le Camp 2. ")
        print("Le présent (Vous) : Vous êtes là pour réaliser l'incomplit, sur les traces de leurs aventures.")
        print("Entrez 'help' si vous avez besoin d'aide.")
        print(self.player.current_room.get_long_description())

def main():
    args = sys.argv[1:]
    if '--cli' in args:
        Game().play()
        return
    
    try:
        from GUI import GameGUI 
        app = GameGUI()
        app.mainloop()
    except Exception as e:
        print(f"|Erreur lors du lancement de l'interface graphique : {e}")
        print("|Passage automatique en mode console.")
        Game().play()

if __name__ == "__main__":
    main()