import random
import time
import os
import sys

# Importations spécifiques à l'OS
if os.name == 'nt':
    import msvcrt
else:
    import tty
    import termios
    import select


class QTE:
    """
    Gère un jeu de Quick Time Event (QTE) intégré au lore de l'escalade.
    """

    def __init__(self, nb_tours, min_inputs, max_inputs, temps_reaction, pool_lettres="AZERTY"):
        self.nb_tours = nb_tours
        self.min_inputs = min_inputs
        self.max_inputs = max_inputs
        self.temps_reaction = temps_reaction
        self.pool_lettres = pool_lettres.upper()
        self.score = 0

    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _get_key_timed(self, timeout):
        start_time = time.time()

        # WINDOWS
        if os.name == 'nt':
            while True:
                if msvcrt.kbhit():
                    try:
                        key = msvcrt.getch().decode('utf-8').upper()
                        return key, time.time() - start_time
                    except UnicodeDecodeError:
                        continue 
                if time.time() - start_time > timeout:
                    return None, timeout
                time.sleep(0.01)
        
        # UNIX
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                if rlist:
                    key = sys.stdin.read(1).upper()
                    return key, time.time() - start_time
                else:
                    return None, timeout
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def start(self):
        self._clear_screen()
        print("\n    /!\\ ATTENTION : TERRAIN TECHNIQUE DÉTECTÉ /!\\")
        print("    ---------------------------------------------")
        print(f"    Concentration requise : {self.temps_reaction}s par action.")
        time.sleep(2)
        
        self.score = 0
        success_total = True

        for i in range(self.nb_tours):
            self._clear_screen()
            print(f"--- SECTION {i + 1} SUR {self.nb_tours} ---")
            time.sleep(random.uniform(0.8, 1.5))
            
            nb_inputs = random.randint(self.min_inputs, self.max_inputs)
            sequence = random.choices(self.pool_lettres, k=nb_inputs)
            
            self._clear_screen()
            print(f"SECTION : {i + 1}/{self.nb_tours}")
            print("\n")
            
            sequence_str = "  ".join(sequence)
            print(f"   ACTION REQUISE : [ {sequence_str} ]")
            print("\n")
            print("Exécution : ", end="", flush=True)
            
            round_success = True
            
            for lettre_attendue in sequence:
                key_pressed, time_taken = self._get_key_timed(self.temps_reaction)
                
                if key_pressed is None:
                    print(f"\n\n⚠️  TROP LENT ! La prise vous échappe !")
                    round_success = False
                    break
                
                elif key_pressed != lettre_attendue:
                    print(f"\n\n❌  ERREUR ! Vous glissez ({key_pressed} au lieu de {lettre_attendue}) !")
                    round_success = False
                    break
                
                else:
                    print(f"{key_pressed}..", end="", flush=True)
            
            print() 
            if not round_success:
                print("\n--- 🛑 CHUTE ! ---")
                time.sleep(2)
                success_total = False
                break
            else:
                print("\n--- ✅ PRISE VALIDÉE ---")
                time.sleep(0.5)

        self._clear_screen()
        if success_total:
            print("\n    *** ASCENSION RÉUSSIE ***")
            print("    Vous reprenez votre souffle.\n")
            return True
        else:
            print("\n    *** ÉCHEC DE L'ASCENSION ***")
            print("    Vous avez dû reculer pour ne pas mourir.\n")
            return False