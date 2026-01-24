from room import Room
from player import Player
from command import Command
from actions import Actions
from chargement import Chargement
from character import Character
from quest import Quest, QuestManager
import sys

# DEBUG = True

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

        q1 = Quest("Sécurité_avant_tout", "Trouver un piolet au Mess.", "TAKE_piolet", "Maîtrise du piolet")
        q2 = Quest("Première_Ascension", "Grimper la première paroi.", "MOVE_Entrée Glacier (E)", "Acclimatation")
        q3 = Quest("Le_toit_du_monde", "Atteindre le sommet.", "MOVE_LE LOCUS (Fin)", "Gloire éternelle")
        q4 = Quest("Bienvenue", "Parler au Sherpa", "TALK_Sherpa", "Infos montagne")
        
        self.quest_manager.add_quest(q1)
        self.quest_manager.add_quest(q2)
        self.quest_manager.add_quest(q3)
        self.quest_manager.add_quest(q4)

        Character("Sherpa", "Un guide expérimenté.", salle_depart, ["Attention aux crevasses.", "Prends le piolet !"])

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
        current_room_name = self.player.current_room.name
        if current_room_name == "Glacier (S)" and "piolet" not in self.player.inventory:
            print("\n💀 DÉFAITE : Vous avez glissé sur le glacier sans piolet.")
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
        print(f"Erreur lors du lancement de l'interface graphique : {e}")
        print("Passage automatique en mode console.")
        Game().play()

if __name__ == "__main__":
    main()