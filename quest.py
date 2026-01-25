class Quest:
    def __init__(self, title, description, trigger_event, reward):
        self.title = title
        self.description = description
        self.trigger_event = trigger_event
        self.reward = reward
        self.completed = False

    def check_completion(self, event_code):
        """Vérifie si l'événement correspond à l'objectif de la quête"""
        if not self.completed and event_code == self.trigger_event:
            self.completed = True
            return True
        return False

    def __str__(self):
        status = "[X]" if self.completed else "[ ]"
        return f"{status} {self.title} : {self.description}"


class QuestManager:
    def __init__(self):
        self.quests = []

    def add_quest(self, quest):
        self.quests.append(quest)

    def check_events(self, event_code, player):
        for quest in self.quests:
            if not quest.completed and quest.trigger_event == event_code:
                quest.completed = True
                print(f"\n✨ QUÊTE ACCOMPLIE : {quest.title}")
                
                if quest.reward == "Santé Mentale +1":
                    player.mental_health = min(100, player.mental_health + 1)
                    print("|🧠 Votre esprit s'apaise un peu. (+1 Santé Mentale)")

                

    def all_finished(self):
        """Retourne True si toutes les quêtes sont terminées"""
        if not self.quests:
            return False
        return all(q.completed for q in self.quests)

    def get_status(self):
        """Retourne une string listant les quêtes"""
        if not self.quests:
            return "Aucune quête active."
        res = "\n--- JOURNAL DE BORD (QUÊTES) ---\n"
        for q in self.quests:
            res += str(q) + "\n"
        return res
    
    def get_quest_details(self, quest_title):
        """Retourne les détails d'une quête spécifique"""
        for q in self.quests:
            if q.title.lower() == quest_title.lower():
                status = "Terminée" if q.completed else "En cours"
                return f"\n--- DÉTAILS DE LA QUÊTE ---\nTitre : {q.title}\nDescription : {q.description}\nStatut : {status}\nRécompense : {q.reward}\n"
        return f"|Aucune quête trouvée avec le titre '{quest_title}'."