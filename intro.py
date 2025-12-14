from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *


app = Ursina(title="Snake 3D", fullscreen=False)

# map entities
map = Entity(model="./assets/models/MEDICAL_SISTER.obj", position=(0, 0, 0),
             collider="box", scale=0.01, ignore=True, origin_y=0, texture="./assets/textures/MEDICAL_SISTER_BaseColor.png", double_sided=True)

ground = Entity(model='plane', scale=60, texture='./assets/textures/concrete_0.png',
                collider='box', origin_y=0, texture_scale=(60, 60))


EditorCamera()

Sky()
app.run()
