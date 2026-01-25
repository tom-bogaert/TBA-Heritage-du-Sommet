"""
Ce module contient la classe Item représentant les objets du jeu.
"""

class Item:
    """
    Cette classe représente un objet (item) dans le jeu.

    Attributes:
        name (str): Le nom de l'objet.
        description (str): La description de l'objet.
        weight (float): Le poids de l'objet en kg.
        effect (dict): Les effets de l'objet (optionnel).
        lore (str): Le texte narratif lié à l'objet (optionnel).
    """

    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, name, description, weight, effect, lore=None):
        """
        Initialise un nouvel objet.
        """
        self.name = name
        self.description = description
        self.weight = weight
        self.effect = effect
        self.lore = lore

    def __str__(self):
        """Retourne une représentation textuelle de l'objet."""
        return f"{self.name} : {self.description} ({self.weight} kg)"
