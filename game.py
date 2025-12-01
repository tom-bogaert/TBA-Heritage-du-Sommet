# Description: Game class

# Import modules

from room import Room
from player import Player
from command import Command
from actions import Actions
from chargement import Chargement

class Game:

    # Constructor
    def __init__(self):
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
    
    # Setup the game
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
        
        salles_chargees, salle_depart = Chargement.charger_depuis_json(fichier_config_jeu)
        if not salles_chargees or not salle_depart:
            print("\nERREUR FATALE: Impossible de charger les données du jeu.")
            print("Vérifiez que 'data.json' existe et est correct.")
            self.finished = True
            return

        self.rooms = salles_chargees

        # Setup player and starting room
        self.player = Player(input("\nEntrez votre nom: "))
        self.player.current_room = salle_depart


    # Play the game
    def play(self):
        self.setup()
        if self.finished:
            print("Erreur de chargement.")
            return None
            
        self.print_welcome()
        while not self.finished:
            self.process_command(input("> "))
        return None

    # Process the command entered by the player
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

    # Print the welcome message
    def print_welcome(self):
        print(f"\nBienvenue {self.player.name} dans ce jeu d'aventure !")
        print("Entrez 'help' si vous avez besoin d'aide.")
        #
        print(self.player.current_room.get_long_description())
    

def main():
    # Create a game object and play the game
    Game().play()
    

if __name__ == "__main__":
    main()