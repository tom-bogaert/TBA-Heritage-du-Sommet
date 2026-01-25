"""
Module gérant les personnages non-joueurs (PNJ).
"""
import random

DEBUG = False

class Character:
    """
    Représente un personnage non-joueur (PNJ) dans le jeu.
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, name, description, current_room, msgs, moveable=True):
        """
        Initialise un nouveau personnage.

        Args:
            name (str): Le nom du personnage.
            description (str): La description du personnage.
            current_room (Room): La salle où se trouve le personnage initialement.
            msgs (list): Une liste de messages que le personnage peut dire.
            moveable (bool, optional): Si le personnage peut se déplacer. Par défaut True.
        """
        self.name = name
        self.description = description
        self.current_room = current_room
        self.msgs = msgs
        self.moveable = moveable

        if current_room:
            current_room.characters[self.name] = self

    def __str__(self):
        return f"{self.name} : {self.description}"

    def move(self):
        """
        Tente de déplacer le personnage aléatoirement vers une salle adjacente.
        """
        if self.moveable and random.choice([True, False]):
            valid_exits = [room for room in self.current_room.exits.values()
                           if room is not None]

            if valid_exits:
                next_room = random.choice(valid_exits)

                if self.name in self.current_room.characters:
                    del self.current_room.characters[self.name]

                self.current_room = next_room
                self.current_room.characters[self.name] = self

                if DEBUG:
                    print(str(self.name) + " se déplace dans " + str(self.current_room.name))

                return True

        return False

    def get_msg(self):
        """
        Récupère le prochain message du personnage (boucle circulaire).
        """
        if not self.msgs:
            return "|Ce personnage n'a rien à dire."

        msg = self.msgs.pop(0)
        self.msgs.append(msg)
        return msg