import PIL.Image
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *
from perlin_noise import PerlinNoise
# from time import time
from random import randint
from math import sqrt
import json

app = Ursina(title="Snake 3D", fullscreen=False)

player = FirstPersonController()

sol = Entity(model='plane', scale=264, texture='grass',
             collider='box', origin_y=0, texture_scale=(200, 200))

chunks = []
chunkData = {}

grassEnt = []
flowersEnt = []

flowers = {}
grass = {}

Sky()
for x in range(-8, 9):
    for y in range(-8, 9):
        chunk = (16*x, 0, 16*y)
        chunks.append(chunk)


print(chunks)
print(len(chunks))

""" for chunk in chunks:
    sol = Entity(model="cube", position=chunk,
                 color=[color.red, color.blue, color.yellow, color.green][randint(0, 3)], scale=(16, 1, 16))
 """

def update():
    global flowers, grass
    for i in range(len(chunks)):
        if (distance(player.position, chunks[i])) <= sqrt(128):
            if (str(chunks[i]) in chunkData):
                print("already in it")
                pass
            else:
                print(chunks[i])
                for x in range(chunks[i][0]+(-8), chunks[i][2]+8):
                    for y in range(chunks[i][0]+(-8), chunks[i][2]+8):
                        print("Range is: ",chunks[i][0]+(-8), chunks[i][0]+8, " chunk is: ", chunks[i], " player is at: ", player.position)
                        random_fact = randint(1, 64)
                        if (random_fact == 1):
                            grass[x, 1, y] = (x, 1, y)
                        if (random_fact == 2):
                            flowers[x, 1, y] = (x, 1, y)
                chunkData[str(chunks[i])] = {
                    "grass": grass,
                    "flowers": flowers
                }
                for keys in chunkData:
                    grass = chunkData[keys]["grass"]
                    for values in grass:
                        print("New ent: ", values)
                        type = randint(1, 3)
                        grass1 = Entity(
                            model="plane", texture=f"./assets/textures/plants/Grass_0{type}.png", position=values, rotation=(270, 45, 0), double_sided=True)
                        grass2 = Entity(
                            model="plane", texture=f"./assets/textures/plants/Grass_0{type}.png", position=values, rotation=(270, -45, 0), double_sided=True)
                        grassEnt.append(grass1)
                        grassEnt.append(grass2)
                print("All entities: ", len(grassEnt) +293)


Sky()

app.run()
