from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import ssao_shader
from ursina import *


app = Ursina(title="Snake 3D", fullscreen=False)

# map entities
map = Entity(model='./labyrinthe.obj',
             position=(0, 0, 0),
             scale=(100, 100, 100),
             texture='brick',
             collider='mesh',
             texture_scale=(100, 100),
             double_sided=True)

""" ground = Entity(model='plane', scale=60, texture='../assets/textures/concrete_0.png',
                collider='box', origin_y=0, texture_scale=(60, 60))
 """

EditorCamera()
camera.shader = ssao_shader

Sky()
app.run()
