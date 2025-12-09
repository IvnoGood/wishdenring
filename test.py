import PIL.Image
from ursina.shaders import ssao_shader
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

Sky()
for x in range(-8, 9):
    for y in range(-8, 9):
        chunk = (16*x, 0, 16*y)
        chunks.append(chunk)


print(chunks)
print(len(chunks))

for chunk in chunks:
    sol = Entity(model="cube", position=chunk,
                 color=[color.red, color.blue, color.yellow, color.green][randint(0, 3)], scale=(16, 1, 16))


def update():
    for i in range(len(chunks)):
        if (distance(player.position, chunks[i])) <= sqrt(128):
            if (str(chunks[i]) in chunkData):
                # print("already in it")
                pass
            else:
                flowers = {}
                grass = {}
                for x in range(-8, 8):
                    for y in range(-8, 8):
                        random_fact = randint(1, 8)
                        if (random_fact == 1):
                            grass[x, 0, y] = (x, 0, y)
                            print("grassfound")
                        if (random_fact == 2):
                            flowers[x, 0, y] = (x, 0, y)
                            print("flowersfound")
                chunkData[str(chunks[i])] = {
                    "grass": grass,
                    "flowers": flowers
                }
                for keys in chunkData:
                    grass = chunkData[keys]["grass"]
                    for values in grass:
                        


Sky()

app.run()
