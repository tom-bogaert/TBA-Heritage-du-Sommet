"""
Module de gestion des actions du jeu.
Contient la classe Actions et les méthodes associées aux commandes.
"""
import math
from qte import QTE

# Constantes de messages
MSG0 = "\nLa commande '{command_word}' ne prend pas de paramètre.\n"
MSG1 = "\nLa commande '{command_word}' prend 1 seul paramètre.\n"
LISTE_ACCEPTANCE = {"NORD", "SUD", "EST", "OUEST", "UP", "DOWN"}

class Actions:
    """
    Regroupe toutes les actions exécutables par le joueur via des commandes.
    Chaque méthode prend en paramètre l'instance du jeu (game), la liste des mots
    de la commande et le nombre de paramètres attendus.
    """

    @staticmethod
    def go(game, list_of_words, number_of_parameters):
        """
        Déplace le joueur dans la direction spécifiée.
        """
        player = game.player
        length = len(list_of_words)
        command_word = list_of_words[0]

        if length < number_of_parameters + 1:
            print("\nVous pensez à :")
            valid_exits = [d for d, r in player.current_room.exits.items() if r is not None]

            if not valid_exits:
                print("(|Il n'y a aucune sortie évidente.)")
            else:
                for direction in sorted(valid_exits):
                    print(f"'{command_word} {direction}'")
            print()
            return False

        if length > number_of_parameters + 1:
            print(MSG1.format(command_word=command_word))
            return False

        f_letter = list_of_words[1].upper()
        if f_letter in LISTE_ACCEPTANCE:
            direction = f_letter[0]
        else:
            direction = f_letter

        if (player.current_room.challenge is not None
                and direction == player.current_room.challenge_exit):
            return Actions.climb(game, list_of_words, number_of_parameters)

        next_room = player.current_room.exits.get(direction)

        if next_room is None:
            print("|Vous ne pouvez pas aller par là !\n")
            if direction in LISTE_ACCEPTANCE or direction in player.current_room.exits.keys():
                full_dir = [i for i in LISTE_ACCEPTANCE if str(i).startswith(direction)][0]
                print(f"|Prendre la direction '{full_dir}' est impossible !\n")
            else:
                print(f"|Cette direction '{direction}' est inconnu !\n")
            return False

        player.move(direction)
        if player.loose_heat_to_death():
            game.finished = True
        return True

    @staticmethod
    def climb(game, _list_of_words, _number_of_parameters):
        """
        Gère l'action d'escalade via un QTE.
        """
        player = game.player
        current_room = player.current_room
        if (player.inventory.get("piolet") is None
                and player.get_inventory().get("Piolet_Carbone") is None):
            print("\n|⛔ IMPOSSIBLE DE GRIMPER ! Il faut un piolet pour passer.\n")

        if current_room.challenge is None:
            print("\n|Il n'y a rien de particulier à escalader ici.\n")
            return False

        config = current_room.challenge
        item_mod = player.get_passive_modifier("q_difficulty")
        total_diff = player.q_difficulty * item_mod

        qte_climb = QTE(
            game,
            nb_tours=int(config.get("nb_tours", 3)*total_diff),
            min_inputs=math.ceil(config.get("min_inputs", 2) * total_diff),
            max_inputs=math.ceil(config.get("max_inputs", 4) * total_diff),
            temps_reaction=config.get("time", 2.0) / total_diff,
            pool_lettres=config.get("pool", "AZERTY")
        )

        print("\nVous ajustez votre baudrier et regardez la paroi...")
        reussite = qte_climb.start()

        if reussite:
            print("\n--- PAROI FRANCHIS ---")
            print("Vous avez vaincu cet obstacle. Les sorties sont maintenant accessibles.")

            player.mental_health = max(0, player.mental_health - 18)
            print("|🧠 L'effort intense et le vide entament votre lucidité (-17 santé mentale).")

            direction_sortie = current_room.challenge_exit
            if direction_sortie and direction_sortie in current_room.exits:
                player.move(direction_sortie)
            else:
                print("Erreur : La sortie d'escalade semble bloquée ou mal définie")
        else:
            print("\n|--- ÉCHEC ---")
            print("|Vous dévissez et vous retrouvez au pied de la paroi.")
            print("|Il faut réessayer pour passer.")

            if player.loose_energy_to_death(15):
                game.finished = True

        return True

    @staticmethod
    def quit(game, list_of_words, number_of_parameters):
        """
        Quitte le jeu.
        """
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        player = game.player
        msg = f"\nMerci {player.name} d'avoir joué. Au revoir.\n"
        print(msg)
        game.finished = True
        return True

    @staticmethod
    def help(game, list_of_words, number_of_parameters):
        """
        Affiche l'aide des commandes.
        """
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        print("\nVoici les commandes disponibles:")
        for command in game.commands.values():
            print("\t- " + str(command))
        print()
        return True

    @staticmethod
    def history(game, list_of_words, number_of_parameters):
        """
        Affiche la liste des lieux visités.
        """
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False

        print(game.player.get_history())
        return True

    @staticmethod
    def back(game, list_of_words, number_of_parameters):
        """
        Permet au joueur de revenir à la salle précédente.
        """
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False

        player = game.player

        if not player.history:
            print("\nImpossible de revenir en arrière : vous êtes au point de départ !\n")
            return False

        room_we_are_leaving = player.current_room
        items_to_return = []
        for item_name, (item, from_room) in player.inventory.items():
            if from_room == room_we_are_leaving:
                items_to_return.append(item_name)

        if items_to_return:
            print("\nEn revenant sur vos pas, vous redéposez les objets que vous veniez de prendre :")
            for item_name in items_to_return:
                item, _ = player.inventory[item_name]
                room_we_are_leaving.inventory[item_name] = item
                del player.inventory[item_name]
                print(f"- {item_name}")

        previous_room = player.history.pop()
        player.current_room = previous_room

        print("\n--- RETOUR ---")
        print(player.get_history())
        print(player.current_room.get_long_description())
        return True

    @staticmethod
    def talk(game, list_of_words, number_of_parameters):
        """
        Permet de discuter avec un PNJ.
        """
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            print(MSG1.format(command_word=list_of_words[0]))
            return False

        npc_name = list_of_words[1]
        current_room = game.player.current_room

        found_npc = None
        for name, npc in current_room.characters.items():
            if name.lower() == npc_name.lower():
                found_npc = npc
                break

        if found_npc:
            print(f"\n{found_npc.name} dit : \"{found_npc.get_msg()}\"\n")
            event_code = f"TALK_{found_npc.name}"
            game.quest_manager.check_events(event_code, game.player)
            return True

        print(f"\n|Il n'y a personne du nom de '{npc_name}' ici.\n")
        return False

    @staticmethod
    def look(game, list_of_words, number_of_parameters):
        """
        Affiche la description de la salle et son inventaire.
        """
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False

        print(game.player.current_room.get_long_description())
        print(game.player.current_room.get_inventory())
        return True

    @staticmethod
    def check(game, list_of_words, number_of_parameters):
        """
        Affiche l'inventaire du joueur.
        """
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False

        print(game.player.get_inventory())
        return True

    @staticmethod
    def quests(game, list_of_words, number_of_parameters):
        """Affiche les quêtes en cours."""
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False

        print(game.quest_manager.get_status())
        return True

    @staticmethod
    def quest(game, list_of_words, number_of_parameters):
        """Affiche les détails d'une quête."""
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False

        quest_name = list_of_words[1]
        print(game.quest_manager.get_quest_details(quest_name))
        return True

    @staticmethod
    def take(game, list_of_words, number_of_parameters):
        """
        Prend un objet dans la salle et vérifie les quêtes.
        """
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            print(MSG1.format(command_word=list_of_words[0]))
            return False

        item_name = list_of_words[1]
        player = game.player
        room = player.current_room

        if item_name not in room.inventory:
            print(f"\n|L'objet '{item_name}' n'est pas ici.\n")
            return False

        item = room.inventory[item_name]
        current_weight = sum(i.weight for i, _ in player.inventory.values())

        if current_weight + item.weight > player.max_weight:
            print(f"\n|Impossible de prendre '{item_name}' : trop lourd !\n")
            return False

        del room.inventory[item_name]
        player.inventory[item_name] = (item, room)

        print(f"\nVous avez pris l'objet '{item_name}'.\n")

        event_code = f"TAKE_{item_name}"
        game.quest_manager.check_events(event_code, player)

        return True

    @staticmethod
    def drop(game, list_of_words, number_of_parameters):
        """
        Pose un objet de l'inventaire dans la salle.
        """
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            print(MSG1.format(command_word=list_of_words[0]))
            return False

        item_name = list_of_words[1]
        player = game.player
        room = player.current_room

        if item_name not in player.inventory:
            print(f"\n|Vous ne possédez pas l'objet '{item_name}'.\n")
            return False

        item, _ = player.inventory[item_name]

        del player.inventory[item_name]
        room.inventory[item_name] = item

        print(f"\nVous avez déposé l'objet '{item_name}'.\n")
        return True

    @staticmethod
    def use(game, list_of_words, number_of_parameters):
        """
        Utilise un objet de l'inventaire.
        """
        if len(list_of_words) <= number_of_parameters:
            print("Quel objet de l'inventaire voulez-vous utiliser ?")
            return

        item_name = list_of_words[1]
        player = game.player

        if item_name not in player.inventory:
            print(f"|Vous ne possédez pas de {item_name}.")
            return

        item, _ = player.inventory[item_name]

        if hasattr(item, 'lore') and item.lore:
            print(f"\n--- Lecture de : {item.name} ---")
            print(f"{item.lore}\n")

        if hasattr(item, 'effect') and item.effect:
            variable = item.effect.get("variable")
            value = item.effect.get("value")

            if variable == "energy":
                player.energy = min(100, player.energy + value)
                print(f"Vous utilisez {item_name}. Énergie +{value}.")
                del player.inventory[item_name]
            elif variable == "heat":
                player.heat = min(100, player.heat + value)
                print(f"Vous utilisez {item_name}. Chaleur +{value}.")
                del player.inventory[item_name]

        elif not (hasattr(item, 'lore') and item.lore):
            print(f"|L'objet {item_name} ne peut pas être utilisé ainsi.")
