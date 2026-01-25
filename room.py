"""
Ce module contient la classe Room, qui représente un lieu dans le jeu.
"""

class Room:
    """
    Cette classe représente un lieu (une salle) dans le jeu.

    Attributes:
        name (str): Le nom court de la salle (ex: "Tower").
        description (str): La description complète de la salle.
        exits (dict): Un dictionnaire mappant les directions (str) aux objets Room (ou None).
        image (str): Le nom de l'image associée à la salle (optionnel).
        inventory (dict): Les objets présents dans la salle.
        characters (dict): Les personnages présents dans la salle.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, name, description, image=None):
        self.name = name
        self.description = description
        self.image = image
        self.exits = {}
        self.challenge = None
        self.challenge_exit = None
        self.solved = False
        self.inventory = {}
        self.characters = {}
        self.danger = None

    def get_exit(self, direction):
        """Retourne la salle correspondante à la direction donnée."""
        if direction in self.exits:
            return self.exits[direction]
        return None

    def get_exit_string(self):
        """Retourne une chaîne décrivant les sorties disponibles."""
        exit_string = "Sorties: "
        for exit_direction in self.exits:
            if self.exits.get(exit_direction) is not None:
                exit_string += exit_direction + ", "
        exit_string = exit_string.strip(", ")
        return exit_string

    def get_long_description(self):
        """Retourne une description complète de la salle (nom + desc + sorties)."""
        return f"\n{self.name} :\n {self.description}\n\n{self.get_exit_string()}\n"

    def get_inventory(self):
        """Retourne une chaîne listant les objets et personnages présents."""
        result = ""

        if not self.inventory:
            result += "Il n'y a aucun objet ici.\n"
        else:
            result += "\nObjets dans la pièce:\n"
            for item in self.inventory.values():
                result += f"  - {item}\n"

        if self.characters:
            result += "\nPersonnages présents:\n"
            for char in self.characters.values():
                result += f"  - {char}\n"

        return result
