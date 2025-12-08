# Define the Room class.

class Room:
    """
    Cette classe représente un lieu (une salle) dans le jeu.

    Attributes:
        name (str): Le nom court de la salle (ex: "Tower").
        description (str): La description complète de la salle.
        exits (dict): Un dictionnaire mappant les directions (str) aux objets Room (ou None).

    Methods:
        __init__(self, name, description): Initialise une nouvelle salle.
        get_exit(self, direction): Retourne la salle dans une direction donnée (ou None).
        get_exit_string(self): Retourne la chaîne de caractères formatée des sorties.
        get_long_description(self): Retourne la description longue (description + sorties).

    Examples:
    
        >>> # Setup des salles
        >>> cuisine = Room("Cuisine", "une cuisine")
        >>> salon = Room("Salon", "un salon")
        >>> cuisine.exits = {"N": salon, "S": None, "E": salon}
        
        >>> cuisine.get_exit("N") == salon
        True
        >>> cuisine.get_exit("O") is None
        True
        
        >>> print(cuisine.get_exit_string())
        Sorties: N, E
        
        >>> print(cuisine.get_long_description())
        Vous êtes dans une cuisine
        Sorties: N, E
    """
    # Define the constructor. 
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.exits = {}
        self.challenge = None
        self.challenge_exit = None
        self.solved = False
    
    # Define the get_exit method.
    def get_exit(self, direction):

        # Return the room in the given direction if it exists.
        if direction in self.exits.keys():
            return self.exits[direction]
        else:
            return None
    
    # Return a string describing the room's exits.
    def get_exit_string(self):
        exit_string = "Sorties: " 
        for exit in self.exits.keys():
            if self.exits.get(exit) is not None:
                exit_string += exit + ", "
        exit_string = exit_string.strip(", ")
        return exit_string

    # Return a long description of this room including exits.
    def get_long_description(self):
        return f"\n {self.description}\n\n{self.get_exit_string()}\n"
