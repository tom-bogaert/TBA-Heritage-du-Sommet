"""
Ce module contient la classe Command.
"""

# pylint: disable=too-few-public-methods
class Command:
    """
    Cette classe représente une commande. Une commande est composée d'un mot-clé,
    d'une chaîne d'aide, d'une action et d'un nombre de paramètres.

    Attributes:
        command_word (str): Le mot de commande.
        help_string (str): La chaîne d'aide.
        action (function): L'action à exécuter lorsque la commande est appelée.
        number_of_parameters (int): Le nombre de paramètres attendus par la commande.

    Methods:
        __init__(self, command_word, help_string, action, number_of_parameters) : Le constructeur.
        __str__(self) : La représentation en chaîne de la commande.
    """

    def __init__(self, command_word, help_string, action, number_of_parameters):
        """Le constructeur."""
        self.command_word = command_word
        self.help_string = help_string
        self.action = action
        self.number_of_parameters = number_of_parameters

    def __str__(self):
        """La représentation en chaîne de la commande."""
        return self.command_word + self.help_string
