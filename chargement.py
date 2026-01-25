"""
Module responsable du chargement des données du jeu depuis un fichier JSON.
"""
import json
from room import Room
from item import Item
from character import Character

class Chargement:
    """
    Cette classe utilitaire gère le chargement des données du jeu
    (salles, sorties, items, personnages) à partir d'un fichier JSON.
    """

    @classmethod
    def charger_depuis_json(cls, fichier_json: str):
        """
        Charge les données du jeu à partir d'un fichier JSON.

        Args:
            fichier_json (str): Le chemin vers le fichier JSON.

        Returns:
            tuple: (liste des objets Room, objet Room de départ) ou ([], None) si erreur.
        """
        try:
            with open(fichier_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return [], None

        if 'rooms' not in data:
            return [], None

        salles_creees = cls._creer_salles(data['rooms'])
        cls._lier_salles(data['rooms'], salles_creees)

        start_room_id = data.get('start_room')
        start_room_obj = salles_creees.get(start_room_id) if start_room_id else None

        return list(salles_creees.values()), start_room_obj

    @classmethod
    def _creer_salles(cls, rooms_data):
        """
        Crée les objets Room et leur contenu (items, personnages) sans les lier entre eux.
        """
        salles_creees = {}

        for room_id, room_data in rooms_data.items():
            try:
                nom_image = room_data.get('image')
                new_room = Room(room_data['name'], room_data['description'], nom_image)

                if 'danger' in room_data:
                    new_room.danger = room_data['danger']

                cls._ajouter_items(new_room, room_data)
                cls._ajouter_personnages(new_room, room_data)

                salles_creees[room_id] = new_room

            except KeyError:
                continue

        return salles_creees

    @staticmethod
    def _ajouter_items(room, room_data):
        """Ajoute les objets à l'inventaire de la salle."""
        if 'items' in room_data:
            for item_data in room_data['items']:
                name = item_data.get('name') or item_data.get('id')
                description = item_data.get('description', "Pas de description")
                weight = item_data.get('weight', 0.1)
                effect = item_data.get('effect')
                lore = item_data.get('lore')
                new_item = Item(name, description, weight, effect, lore)
                room.inventory[new_item.name] = new_item

    @staticmethod
    def _ajouter_personnages(room, room_data):
        """Ajoute les personnages à la salle."""
        if 'characters' in room_data:
            for char_data in room_data['characters']:
                Character(
                    char_data['name'],
                    char_data['description'],
                    room,
                    char_data['msgs']
                )

    @classmethod
    def _lier_salles(cls, rooms_data, salles_creees):
        """
        Lie les salles entre elles (création des sorties) et configure les challenges.
        """
        for room_id, room_data in rooms_data.items():
            if room_id not in salles_creees:
                continue

            current_room_obj = salles_creees[room_id]

            if 'exits' in room_data:
                for direction, destination_id in room_data['exits'].items():
                    if destination_id is None:
                        current_room_obj.exits[direction] = None
                    elif destination_id in salles_creees:
                        current_room_obj.exits[direction] = salles_creees[destination_id]

            if "challenge" in room_data:
                current_room_obj.challenge = room_data["challenge"]

            current_room_obj.challenge_exit = room_data.get("challenge_exit", "N")
