'''
python3.10 -m pip install mediapipe
python3.10 -m pip install colorama
pip install numpy
'''
import random
import time
import FacialRecognition
from colorama import Fore, Style
class Game:
    def __init__(self, size):
        self.size = size
        self.map = [[None for _ in range(size)] for _ in range(size)]
        self.player = None
        self.monster = None

    def generate_player(self):
        x = random.randint(0, self.size-1)
        y = random.randint(0, self.size-1)
        self.player = Player(x, y)
        self.map[y][x] = self.player

    def generate_monster(self):
        x = random.randint(0, self.size-1)
        y = random.randint(0, self.size-1)
        self.monster = Monster(x, y)
        self.map[y][x] = self.monster

    def generate_items(self, num_items):
        for _ in range(num_items):
            x = random.randint(0, self.size-1)
            y = random.randint(0, self.size-1)
            item = random.choice([Food(), Weapon(25,"💣"), Weapon(20, "🔫"), Weapon(30,"🔦") ])
            if self.map[y][x] is None:
                self.map[y][x] = item
            else:
                # Regenerar posición si ya hay un elemento en esa celda
                self.generate_items(1)

    def display_map(self):
        for row in self.map:
            for cell in row:
                if cell is None:
                    print(" -", end=" ")
                elif isinstance(cell, Player):
                    print("😾", end=" ")#Jugador
                elif isinstance(cell, Monster):
                    print("🤖", end=" ")#Mounstruo
                elif isinstance(cell, Food):
                    print(cell.symbol, end=" ")#Comida
                elif isinstance(cell, Weapon):
                    print(cell.symbol, end=" ")#Arma
            print()

    def move(self, x1, y1, x2, y2, mover):
        #Revisamos si el jugador llego a una casilla donde habia un arma para añadirla a su inventario
        if isinstance (mover, Player) and isinstance(self.map[y2][x2], Weapon):
            mover.inventory.append(self.map[y2][x2])
        
        #Revisamos si el jugador o mounstruo entró a una casilla donde habia comida para aumentarle su vida
        elif isinstance(self.map[y2][x2], Food):
            mover.health += 10
            print(Fore.GREEN + "Tu vida ha aumentado 10 puntos!" + Style.RESET_ALL)
        elif isinstance(self.map[y2][x2], Monster):
            player.health -= 10
            print("No te acerques al mounstruo si no le vas a disparar! 🤨\nAcabas de perder 10 de vida")
            return
        #Revisamos si el mounstruo iba a ponerse en la casilla donde estaba el jugador (lo que significa que lo ataca)
        elif isinstance(self.map[y2][x2], Player):
            player.health -= 10
            print("El mounstruo atacó al jugador, ahora la vida del jugador es: ", Fore.RED + str(player.health) + Style.RESET_ALL)
            return #Retornamos y no posicionamos al mounstruo en las coordenadas del jugador porque sino desaparece

        #Asignar nuevas posiciones
        self.map[y2][x2] = mover #Posicionamos al jugador o mounstruo en la nueva coordenada
        self.map[y1][x1] = None #Su antigua coordenada quedará vacia (luego se llenará con "-")
        mover.x, mover.y = x2, y2 #Asignamos el atributo de coordenadas a su nuevo valor

    def move_player(self, direction):
        #Obtenemos las coordenadas del jugador
        x, y = self.player.x, self.player.y
        #Procedemos con los respectivos movimientos en la matriz
        if direction == "Arriba" and y > 0:
            self.move(x, y, x, y-1, self.player)

        elif direction == "Abajo" and y < self.size-1:
            self.move(x, y, x, y+1, self.player)

        elif direction == "Izquierda" and x > 0:
            self.move(x, y, x-1, y, self.player)

        elif direction == "Derecha" and x < self.size-1:
            self.move(x, y, x+1, y, self.player)

    def move_monster(self):
        x, y = self.monster.x, self.monster.y #Obtenemos las coordenadas del mounstruo
        directions = ["arriba", "abajo", "izquierda", "derecha"]
        #Obtenemos una direccion aleatoria y hacemos el mismo proceso que se hizo con el jugador
        direction = random.choice(directions)

        if direction == "arriba" and y > 0:
            self.move(x, y, x, y-1, self.monster)

        elif direction == "abajo" and y < self.size-1:
            self.move(x, y, x, y+1, self.monster)

        elif direction == "izquierda" and x > 0:
            self.move(x, y, x-1, y, self.monster)

        elif direction == "derecha" and x < self.size-1:
            self.move(x, y, x+1, y, self.monster)

    #Comprobamos si el mounstruo está en el rango del jugador para ofrecerle la opcion de atacarlo
    def check_attack_status(self):
        player_x, player_y = self.player.x, self.player.y
        monster_x, monster_y = self.monster.x, self.monster.y

        if player_x == monster_x and abs(player_y - monster_y) == 1:
            return True  # El monstruo está arriba o abajo del jugador
        elif player_y == monster_y and abs(player_x - monster_x) == 1:
            return True  # El monstruo está a la izquierda o derecha del jugador
        else:
            return False  # El monstruo no está cerca del jugador

    def attack_monster(self, weapon):
        self.monster.health -= weapon.damage
        print(Fore.RED + "Haz atacado al monstruo! Ahora su vida es de", Fore.RED + str(self.monster.health) + Style.RESET_ALL)

class Player:
    def __init__(self, x, y):
        #x,y seran las coordenadas
        self.x = x
        self.y = y
        self.health = 50
        self.inventory = []

class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 40

class Item:
    def __init__(self):
        pass

class Food(Item):
    def __init__(self):
        self.symbol = "🍎"

class Weapon(Item):
    def __init__(self, damage,symbol):
        self.damage = damage
        self.symbol = symbol 

game = Game(6)
game.generate_player()
game.generate_monster()
game.generate_items(12)
game.display_map()

def get_weapon_attack():
    direction, gesture = FacialRecognition.capture_direction_and_gesture()
    weapon_dict = {weapon: weapon.symbol for weapon in player.inventory}
    if gesture == "Pulgar hacia arriba (Granada)":
        if "💣" in weapon_dict.values():
            #Como si tiene una granada en su inventario, obtenemos el objeto
            weapon = next(key for key, value in weapon_dict.items() if value == "💣")
            game.attack_monster(weapon)
            player.inventory.remove(weapon) #Finalmente borramos el arma  ya usada, del inventario del jugador
        else:
            print("No tienes ninguna granada en tu inventario, vuelve a intentarlo!")
            get_weapon_attack()

    elif gesture == "Pistola":
        if "🔫" in weapon_dict.values():
            weapon = next(key for key, value in weapon_dict.items() if value == "🔫" )
            game.attack_monster(weapon)
            player.inventory.remove(weapon)
        else:
            print("No tienes ninguna pistola en tu inventario, vuelve a intentarlo!")
            get_weapon_attack()
    elif gesture == "Dos dedos horizontales (Fusil)":
        if "🔦" in weapon_dict.values():
            weapon = next(key for key, value in weapon_dict.items() if value == "🔦")
            game.attack_monster(weapon)
            player.inventory.remove(weapon)
        else:
            print("No tienes ningún fusil en tu inventario, vuelve a intentarlo!")
            get_weapon_attack()
    else:
        print("No haz hecho un gesto correcto, vuelve a intentarlo")
        get_weapon_attack()

'''
 ██████╗  █████╗ ███╗   ███╗███████╗
██╔════╝ ██╔══██╗████╗ ████║██╔════╝
██║  ███╗███████║██╔████╔██║█████╗  
██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  
╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗
 ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝                                   
'''
while True:
    player = game.player
    print("Mira a la direccion a la que quieras atacar y presiona 'q' cuando estes listo")
    #Revisamos si el jugador dispone de algun arma en su inventario
    if len(player.inventory) != 0:
        print("Actualmente dispones de lo siguiente en tu inventario: ")
        weapons = [weapon.symbol for weapon in player.inventory] #Sacamos los simbolos de las armas para mostrarlos
        print(",".join(weapons))
        if (game.check_attack_status()):
            attack = input("Deseas atacar al mounstruo con tu arma? (s/n): ").lower()
            if attack == "s":
                print("A continuacion realiza el gesto correspondiente al arma que quieres usar")
                #Le pedimos al usuario que utilice un arma
                get_weapon_attack()
                #El usuario podrá hacer su movimiento luego de atacar
                print("Haz atacado bien!, realiza tu siguiente movimiento")
                #Comprobamos de una si el jugador mató o no al Mounstruo
                if game.monster.health <= 0:
                    print("El juego ha terminado!")
                    print("El ganador es el jugador!")
                    break 
                
    #Obtenemos la direccion a la que se moverá el jugador con MediaPipe
    direction, gesture = FacialRecognition.capture_direction_and_gesture() #Cuando MediaPipe detecte la direccion a la que quieres ir, debes
                                                             #presionar Q para que sea leida, y asi cada que hagas un movimiento
    while direction == "Frente":
            print("Debes mirar hacia alguna direccion, moverse hacia al frente no es una opción")
            direction, gesture = FacialRecognition.capture_direction_and_gesture()
        
    game.move_player(direction)                              
    print("Tu vida actual es: ", player.health)
    game.display_map()

    #Se procede con el movimiento aleatorio del mounstruo
    print("Preparando movimiento del mounstruo...")
    time.sleep(3)
    game.move_monster()
    print("La vida del mounstruo es: ", game.monster.health)
    game.display_map()


    #Comprobamos si la vida del jugador o del mounstruo es 0 o menor, para asi acabar con el ciclo while True, sino se repite
    if game.player.health <= 0:
        print("El juego ha terminado!")
        print("El ganador es el mounstruo!")
        break
    elif game.monster.health <= 0:
        print("El juego ha terminado!")
        print("El ganador es el jugador!")
        break 
