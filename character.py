import random

class Character:
    def __init__(self, name, description, current_room, msgs):
        self.name = name
        self.description = description
        self.current_room = current_room
        self.msgs = msgs
        
        if current_room:
            current_room.characters[self.name] = self

    def __str__(self):
        return f"{self.name} : {self.description}"

    def move(self):
        if random.choice([True, False]):
            valid_exits = [room for room in self.current_room.exits.values() if room is not None]
            
            if valid_exits:
                next_room = random.choice(valid_exits)
                
                if self.name in self.current_room.characters:
                    del self.current_room.characters[self.name]
                
                self.current_room = next_room
                
                self.current_room.characters[self.name] = self
                
                return True
        return False

    def get_msg(self):
        if not self.msgs:
            return "Ce personnage n'a rien à dire."
        
        msg = self.msgs.pop(0)
        self.msgs.append(msg)
        return msg