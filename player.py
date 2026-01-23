# Define the Player class.
class Player():
    """
    Cette classe représente le joueur.

    Attributes:
        name (str): Le nom du joueur.
        current_room (Room): La salle où se trouve actuellement le joueur.

    Methods:
        __init__(self, name): Initialise un nouveau joueur.
        move(self, direction): Déplace le joueur dans une direction donnée.

    Examples:
        
        >>> p = Player("Joueur Test")
        >>> salle1 = Room("Départ", "la salle de départ")
        >>> salle2 = Room("Arrivée", "la salle d'arrivée")
        >>> salle1.exits = {"N": salle2, "S": None}
        >>> p.current_room = salle1
        
        >>> p.move("O")
        Aucune porte dans cette direction !
        False

        >>> p.move("S")
        Aucune porte dans cette direction !
        False

        >>> p.move("N")
        Vous êtes dans la salle d'arrivée
        True

        >>> p.current_room.name
        'Arrivée'
    """
class Player():
    def __init__(self, name):
        self.name = name
        self.current_room = None
        self.history = []
        self.inventory = {}
        self.max_weight = 10.0
        self.rewards = []
        self.energy = 100
        self.mental_health = 100
        self.heat = 100
        self.difficulty = 1


    def move(self, direction):
        next_room = self.current_room.exits[direction]
        if next_room is None:
            print("\nAucune porte dans cette direction !\n")
            return False
        
        self.history.append(self.current_room)
        self.current_room = next_room
        print(self.current_room.get_long_description())
        return True

    def get_history(self):
        if not self.history:
            return "\nVous n'avez visité aucune autre zone.\n"
        result = "\nVous avez déjà visité les zones suivantes:\n"
        for room in self.history:
            result += f"        - {room.name}\n"
        return result

    def get_inventory(self):
        if not self.inventory:
            return "Votre inventaire est vide.\n"
        result = "Vous disposez des items suivants :\n"
        for item, _ in self.inventory.values():
            result += f"    - {item}\n"
        return result

    def add_reward(self, reward):
        self.rewards.append(reward)

    def loose_heat_to_death(self):
        self.heat -= self.difficulty * 2
        if self.heat < 0:
            self.heat = 0
            print("\n💀 DÉFAITE : Vous êtes mort de froid.")
            print("Votre corps resteras congelé ici jusqu'as la fin des temps...")
            return True
        return False

