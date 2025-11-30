from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *


app = Ursina(title="Snake 3D", fullscreen=False)

# map entities
map = Entity(model="cube", position=(0, 0, 0),
             collider="box", ignore=True, origin_y=0)

ground = Entity(model='plane', scale=60, texture='./assets/textures/concrete_0.png',
                collider='box', origin_y=0, texture_scale=(60, 60))


EditorCamera()

Sky()
app.run()
