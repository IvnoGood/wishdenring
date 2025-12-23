from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *


app = Ursina(title="Snake 3D", fullscreen=False)

# map entities
map = Entity(model="./assets/models/hyundai_porter.obj", texture="./assets/textures/truck/h-porter-gray.jpg",
             position=(0, 0, 0),
             collider="box",
             scale=0.01,
             ignore=True,
             origin_y=0,
             double_sided=True)

ground = Entity(model='plane', scale=60, texture='./assets/textures/concrete_0.png',
                collider='box', origin_y=0, texture_scale=(60, 60))


EditorCamera()

Sky()
app.run()
