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

for chunk in chunks:
    sol = Entity(model="cube", position=chunk,
                 color=[color.red, color.blue, color.yellow, color.green][randint(0, 3)], scale=(16, 1, 16))
  # ca affiche tous les chunks avec des petits carrés mais c'est que pr le test


def update():  # boucle qui s'execute a chque frame
    global flowers, grass
    for i in range(len(chunks)):
        if (distance(player.position, chunks[i])) <= sqrt(128):
            #print("chunk actuel: ",  chunks[i])
            """ on vérifie la ditance avec le joueur et le centre du chunk 
            si inf a la val
            (trouvée grace au théorème de pythagore pour avoir les coins c'est pas le plus précis mais ca marche pr ca) 
             alors suite """
            if (str(chunks[i]) in chunkData):
                # on vérifie si le chunk a déja été enregistré
                #print("already in it")
                pass
            else:
                print(chunks[i])
                hashed = str(abs(hash(chunks[i]))) # on enlève le moins devant pour ceux qui en ont un
                print("Hash: ", hashed, " len of hash: ", len(hashed))
                print(hashed[-19])
                grassNum = round(int(hashed[len(hashed)-1])/2) # on récup le nmb d'herbes gen dans le chunk avc le dernier char du hash
                print("Number of grass: ", grassNum)

                round(int(hashed[len(hashed)-1])/2)

                for j in range(2, 19, 2):
                    print("Coords: ",(int(hashed[-j])*2, int(hashed[-j])+(-1)*2))
                    

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
