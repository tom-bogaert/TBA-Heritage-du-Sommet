from room import Room
from player import Player
from command import Command
from actions import Actions
from chargement import Chargement
from character import Character

DEBUG = True

class Game:

    def __init__(self):
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
        self.npcs = []
        
    
    def setup(self):
        fichier_config_jeu = "data.json"

        help = Command("help", " : afficher cette aide", Actions.help, 0)
        self.commands["help"] = help
        
        quit = Command("quit", " : quitter le jeu", Actions.quit, 0)
        self.commands["quit"] = quit
        
        go = Command("go", " <direction> : se déplacer dans une direction cardinale (N, E, S, O)", Actions.go, 1)
        self.commands["go"] = go

        history_cmd = Command("history", " : afficher les lieux visités", Actions.history, 0)
        self.commands["history"] = history_cmd
        
        back_cmd = Command("back", " : revenir au lieu précédent", Actions.back, 0)
        self.commands["back"] = back_cmd
        
        escalade = Command("escalade", " : Tenter de grimper la paroi (lance un QTE)", Actions.climb, 0)
        self.commands["escalade"] = escalade

        look = Command("look", " : observer les lieux et les objets", Actions.look, 0)
        self.commands["look"] = look
        
        take = Command("take", " <objet> : prendre un objet", Actions.take, 1)
        self.commands["take"] = take
        
        drop = Command("drop", " <objet> : poser un objet", Actions.drop, 1)
        self.commands["drop"] = drop
        
        check = Command("check", " : vérifier son inventaire", Actions.check, 0)
        self.commands["check"] = check

        talk_cmd = Command("talk", " <nom> : parler à un personnage", Actions.talk, 1)
        self.commands["talk"] = talk_cmd

        salles_chargees, salle_depart = Chargement.charger_depuis_json(fichier_config_jeu)
        if not salles_chargees or not salle_depart:
            print("\nERREUR FATALE: Impossible de charger les données du jeu.")
            print("Vérifiez que 'data.json' existe et est correct.")
            self.finished = True
            return

        self.rooms = salles_chargees

        self.player = Player(input("\nEntrez votre nom: "))
        self.player.current_room = salle_depart
        
        self.npcs = []
        for room in self.rooms:
            for char in room.characters.values():
                self.npcs.append(char)


    def play(self):
        self.setup()
        if self.finished:
            print("Erreur de chargement.")
            return None
            
        self.print_welcome()
        
        while not self.finished:
            ancienne_salle = self.player.current_room
            
            self.process_command(input("> "))
            
            if self.player.current_room != ancienne_salle:
                for npc in self.npcs:
                    moved = npc.move()
                    if DEBUG and moved:
                        print(f"DEBUG: {npc.name} s'est déplacé vers {npc.current_room.name}")

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
        #
        print(self.player.current_room.get_long_description())
    

def main():
    Game().play()
    

if __name__ == "__main__":
    main()