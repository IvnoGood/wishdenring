# Ce code consiste a générer les blocs d'herbe dans le chunk ou se situe le joueur
# Soucis les blocs se génèrent dans d'autres chunk pour une raison inconnue ce qui surcharge légèrement la mémoire de l'ordinateur qui n'aime pas trop ca
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *
# from time import time
from random import randint
from math import sqrt

app = Ursina(title="Snake 3D", fullscreen=False)

# cela contient le préfabriqué pour les contrôles du joueur on utilisera pas ca sur le proj final
# la doc: https://www.ursinaengine.org/api_reference.html#FirstPersonController
player = FirstPersonController()

sol = Entity(model='plane', scale=264, texture='grass',
             # on crée une plane pour le sol
             collider='box', origin_y=0, texture_scale=(200, 200))

chunks = []
chunkData = {}

grassEnt = []
flowersEnt = []

flowers = {}
grass = {}

Sky()  # un ciel car pourquoi pas

for x in range(-8, 9):
    for y in range(-8, 9):
        # on génère les chunks dans une liste pour pouvoir les réutiliser plus tard
        chunk = (16*x, 0, 16*y)
        chunks.append(chunk)


print(chunks)
print(len(chunks))

""" for chunk in chunks:
    sol = Entity(model="cube", position=chunk,
                 color=[color.red, color.blue, color.yellow, color.green][randint(0, 3)], scale=(16, 1, 16))
 """  # ca affiche tous les chunks avec des petits carrés mais c'est que pr le test


def update():  # boucle qui s'execute a chque frame
    global flowers, grass
    for i in range(len(chunks)):
        if (distance(player.position, chunks[i])) <= sqrt(128):
            """ on vérifie la ditance avec le joueur et le centre du chunk 
            si inf a la val
            (trouvée grace au théorème de pythagore pour avoir les coins c'est pas le plus précis mais ca marche pr ca) 
             alors suite """
            if (str(chunks[i]) in chunkData):
                # on vérifie si le chunk a déja été enregistré
                print("already in it")
                pass
            else:
                print(chunks[i])
                # on vas chercher toutes les coordonnées dans le chunk dans x
                for x in range(chunks[i][0]+(-8), chunks[i][2]+8):
                    # on vas chercher toutes les coordonnées dans le chunk dans y
                    for y in range(chunks[i][0]+(-8), chunks[i][2]+8):
                        print("Range is: ", chunks[i][0]+(-8), chunks[i][0]+8,
                              " chunk is: ", chunks[i], " player is at: ", player.position)
                        # ici c le hasard pr générer des plantes c'est pas non plus le meilleur mais c simple et ca marche
                        random_fact = randint(1, 64)
                        if (random_fact == 1):
                            # on stocke ces vals dans un dict
                            grass[x, .5, y] = (x, .5, y)
                        if (random_fact == 2):
                            flowers[x, .5, y] = (x, .5, y)
                chunkData[str(chunks[i])] = {
                    "grass": grass,
                    "flowers": flowers
                }
                for keys in chunkData:
                    grass = chunkData[keys]["grass"]
                    for values in grass:
                        print("New ent: ", values)
                        # type = randint(1, 3)  # le type d'herbe
                        # on génère ici les entitées d'herbe en les ajoutants a une liste qui pourras les supprimer plus tard
                        grass1 = Entity(
                            model="plane", color=color.green, position=values, rotation=(270, 45, 0), double_sided=True)
                        grass2 = Entity(
                            model="plane", color=color.green, position=values, rotation=(270, -45, 0), double_sided=True)
                        grassEnt.append(grass1)
                        grassEnt.append(grass2)
                # affiche le nmb tot entitées + joueur et sol
                print("All entities: ", len(grassEnt) + 2)


Sky()

app.run()
