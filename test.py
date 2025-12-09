import PIL.Image
from ursina.shaders import ssao_shader
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *
from perlin_noise import PerlinNoise
# from time import time

app = Ursina(title="Snake 3D", fullscreen=False)

player = FirstPersonController()

sol = Entity(model='plane', scale=264, texture='grass',
             collider='box', origin_y=0, texture_scale=(200, 200))

chunks = []
Sky()
for x in range (-8,9):
    for y in range(-8,9):
        chunk = (16*x, 0, 16*y)
        chunks.append(chunk)


print(chunks)
print(len(chunks))

for chunk in chunks:
    sol = Entity(model="plane", position=chunk, color=color.red)


def update():
    for i in range(len(chunks)):
        if(distance(player.position, chunks[i]))<=11.5:
            print(chunks[i])



Sky()

app.run()
