import json
from room import Room
from item import Item

class Chargement:
    """
    Cette classe utilitaire gère le chargement des données du jeu
    (salles, sorties, etc.) à partir d'un fichier JSON.
    """

    @classmethod
    def charger_depuis_json(cls, fichier_json: str):
        try:
            with open(fichier_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            return [], None
        except json.JSONDecodeError:
            return [], None

        salles_creees = {}

        if 'rooms' not in data:
            return [], None

        for room_id, room_data in data['rooms'].items():
            try:
                new_room = Room(room_data['name'], room_data['description'])
                
                if 'items' in room_data:
                    for item_data in room_data['items']:
                        new_item = Item(item_data['name'], item_data['description'], item_data['weight'])
                        new_room.inventory[new_item.name] = new_item
                
                salles_creees[room_id] = new_room
            except KeyError:
                continue
        
        for room_id, room_data in data['rooms'].items():
            if room_id not in salles_creees:
                continue
                
            current_room_obj = salles_creees[room_id]
            
            if 'exits' in room_data:
                for direction, destination_id in room_data['exits'].items():
                    if destination_id is None:
                        current_room_obj.exits[direction] = None
                    elif destination_id in salles_creees:
                        current_room_obj.exits[direction] = salles_creees[destination_id]
                    else:
                        continue
            
            if "challenge" in room_data:
                current_room_obj.challenge = room_data["challenge"]

            if "challenge_exit" in room_data:
                current_room_obj.challenge_exit = room_data["challenge_exit"]
            else:
                current_room_obj.challenge_exit = "N"

        start_room_id = data.get('start_room')
        start_room_obj = None
        
        if start_room_id:
            start_room_obj = salles_creees.get(start_room_id)

        return list(salles_creees.values()), start_room_obj