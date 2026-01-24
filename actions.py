# Description: The actions module.

MSG0 = "\nLa commande '{command_word}' ne prend pas de paramètre.\n"
MSG1 = "\nLa commande '{command_word}' prend 1 seul paramètre.\n"
liste_acceptance = set(["NORD", "SUD", "EST", "OUEST", "UP", "DOWN"])

from qte import QTE

class Actions:

    def go(game, list_of_words, number_of_parameters):
        """
        Move the player in the direction specified by the parameter.
        The parameter must be a cardinal direction (N, E, S, O).

        Args:
            game (Game): The game object.
            list_of_words (list): The list of words in the command.
            number_of_parameters (int): The number of parameters expected by the command.

        Returns:
            bool: True if the command was executed successfully, False otherwise.

        Examples:
        
        >>> from game import Game
        >>> game = Game()
        >>> game.setup()
        >>> go(game, ["go", "N"], 1)
        True
        >>> go(game, ["go", "N", "E"], 1)
        False
        >>> go(game, ["go"], 1)
        False

        """
        
        player = game.player
        l = len(list_of_words)
        command_word = list_of_words[0]

        if l < number_of_parameters + 1:
            print("\nVous pensez à :")
            
            valid_exits = []
            for direction, room in player.current_room.exits.items():
                if room is not None:
                    valid_exits.append(direction)
            
            if not valid_exits:
                print("(|Il n'y a aucune sortie évidente.)")
            else:
                for direction in sorted(valid_exits):
                    print(f"'{command_word} {direction}'")
            print() 
            return False

        if l > number_of_parameters + 1:
            print(MSG1.format(command_word=command_word))
            return False

        f_letter = list_of_words[1].upper()
        if f_letter in liste_acceptance :
            direction = f_letter[0]
        else :
            direction = f_letter

        if (player.current_room.challenge is not None
            and direction == player.current_room.challenge_exit):
            return Actions.climb(game, list_of_words, number_of_parameters)


        next_room = player.current_room.exits.get(direction)

        if next_room is None:
            print("|Vous ne pouvez pas aller par là !\n")
            if direction in liste_acceptance or direction in player.current_room.exits.keys() :
                print(f"|Prendre la direction '{str([i for i in liste_acceptance if str(i).startswith(direction)][0])}' est impossible !\n")
            else :
                print("|Cette direction '" + str(direction) + "' est inconnu !\n")
            return False
        
        player.move(direction)
        if player.loose_heat_to_death():
            game.finished = True
        return True


    def climb(game, list_of_words, number_of_parameters):
        player = game.player
        current_room = player.current_room
        
        if current_room.challenge is None:
            print("\n|Il n'y a rien de particulier à escalader ici.\n")
            return False

        config = current_room.challenge
        item_mod = player.get_passive_modifier("q_difficulty")
        total_diff = player.q_difficulty * item_mod
        
        qte_climb = QTE(
            game,  
            nb_tours=int(config.get("nb_tours", 3) * total_diff),
            min_inputs=int(config.get("min_inputs", 2) * total_diff),
            max_inputs=int(config.get("max_inputs", 4) * total_diff),
            temps_reaction=config.get("time", 2.0),
            pool_lettres=config.get("pool", "AZERTY")
        )
        
        print("\nVous ajustez votre baudrier et regardez la paroi...")
        reussite = qte_climb.start()

        if reussite:
            print("\n--- PAROI FRANCHIS ---")
            print("Vous avez vaincu cet obstacle. Les sorties sont maintenant accessibles.")
            
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


    def quit(game, list_of_words, number_of_parameters):
        """
        Quit the game.

        Args:
            game (Game): The game object.
            list_of_words (list): The list of words in the command.
            number_of_parameters (int): The number of parameters expected by the command.

        Returns:
            bool: True if the command was executed successfully, False otherwise.

        Examples:

        >>> from game import Game
        >>> game = Game()
        >>> game.setup()
        >>> quit(game, ["quit"], 0)
        True
        >>> quit(game, ["quit", "N"], 0)
        False
        >>> quit(game, ["quit", "N", "E"], 0)
        False

        """
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False
        
        player = game.player
        msg = f"\nMerci {player.name} d'avoir joué. Au revoir.\n"
        print(msg)
        game.finished = True
        return True

    def help(game, list_of_words, number_of_parameters):
        """
        Print the list of available commands.
        
        Args:
            game (Game): The game object.
            list_of_words (list): The list of words in the command.
            number_of_parameters (int): The number of parameters expected by the command.

        Returns:
            bool: True if the command was executed successfully, False otherwise.

        Examples:

        >>> from game import Game
        >>> game = Game()
        >>> game.setup()
        >>> help(game, ["help"], 0)
        True
        >>> help(game, ["help", "N"], 0)
        False
        >>> help(game, ["help", "N", "E"], 0)
        False

        """

        l = len(list_of_words)
        if l != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False
        
        print("\nVoici les commandes disponibles:")
        for command in game.commands.values():
            print("\t- " + str(command))
        print()
        return True
    

    def history(game, list_of_words, number_of_parameters):
        """
        Affiche la liste des lieux visités.
        """
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False
        
        print(game.player.get_history())
        return True


    def back(game, list_of_words, number_of_parameters):
        """
        Permet au joueur de revenir à la salle précédente.
        Les objets pris dans la salle actuelle sont redéposés.
        """
        l = len(list_of_words)
        if l != number_of_parameters + 1:
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
    

    def talk(game, list_of_words, number_of_parameters):
        """
        Permet de discuter avec un PNJ présent dans la salle.
        """
        l = len(list_of_words)
        if l != number_of_parameters + 1:
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
        else:
            print(f"\n|Il n'y a personne du nom de '{npc_name}' ici.\n")
            return False
    

    def look(game, list_of_words, number_of_parameters):
        """
        Affiche la description de la salle et son inventaire.
        """
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False
        
        print(game.player.current_room.get_long_description())
        print(game.player.current_room.get_inventory())
        return True


    def check(game, list_of_words, number_of_parameters):
        """
        Affiche l'inventaire du joueur.
        """
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False
        
        print(game.player.get_inventory())
        return True


    def quests(game, list_of_words, number_of_parameters):
        """Affiche les quêtes en cours."""
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False
        
        print(game.quest_manager.get_status())
        return True
    
    def quest(game, list_of_words, number_of_parameters):
        """Affiche les détails d'une quête."""
        l = len(list_of_words)
        print(l)
        print(number_of_parameters)
        if l != number_of_parameters + 1:
            print(MSG0.format(command_word=list_of_words[0]))
            return False

        quest_name = list_of_words[1]
        print(game.quest_manager.get_quest_details(quest_name))
        return True

    def take(game, list_of_words, number_of_parameters):
        """
        Prend un objet dans la salle et vérifie les quêtes.
        """
        l = len(list_of_words)
        if l != number_of_parameters + 1:
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
    

    def drop(game, list_of_words, number_of_parameters):
        """
        Pose un objet de l'inventaire dans la salle.
        """
        l = len(list_of_words)
        if l != number_of_parameters + 1:
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


    def use(game, list_of_words, number_of_parameters):
        if len(list_of_words) <= number_of_parameters:
            print("Quel objet de l'inventaire voulez-vous utiliser ?")
            return

        item_name = list_of_words[1]
        player = game.player

        if item_name not in player.inventory:
            print(f"|Vous ne possédez pas de {item_name}.")
            return

        item, from_room = player.inventory[item_name] 
        
        if hasattr(item, 'effect') and item.effect:
            variable = item.effect.get("variable")
            value = item.effect.get("value")

            if variable == "energy":
                player.energy = min(100, player.energy + value)
                print(f"Vous utilisez {item_name}. Énergie +{value}.")
            elif variable == "heat":
                player.heat = min(100, player.heat + value)
                print(f"Vous utilisez {item_name}. Chaleur +{value}.")
            
            del player.inventory[item_name]
        else:
            print(f"|L'objet {item_name} ne peut pas être utilisé ainsi.")