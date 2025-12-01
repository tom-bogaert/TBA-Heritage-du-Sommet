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

    # Define the constructor.
    def __init__(self, name):
        self.name = name
        self.current_room = None
        self.history = []
    
    # Define the move method.
    def move(self, direction):
        # Get the next room from the exits dictionary of the current room.
        next_room = self.current_room.exits[direction]

        # If the next room is None, print an error message and return False.
        if next_room is None:
            print("\nAucune porte dans cette direction !\n")
            return False
        
        self.history.append(self.current_room)
        
        # Set the current room to the next room.
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
        