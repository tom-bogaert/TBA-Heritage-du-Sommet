class Item:
    """
    Cette classe représente un objet (item) dans le jeu.

    Attributes:
        name (str): Le nom de l'objet.
        description (str): La description de l'objet.
        weight (float): Le poids de l'objet en kg.
    """

    def __init__(self, name, description, weight):
        self.name = name
        self.description = description
        self.weight = weight

    def __str__(self):
        return f"{self.name} : {self.description} ({self.weight} kg)"