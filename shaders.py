# you have to apply this shader to enties for them to receive shadows.
from ursina.shaders import lit_with_shadows_shader
from ursina import *

app = Ursina()
EditorCamera()
Entity(model='plane', scale=10, color=color.gray,
       shader=lit_with_shadows_shader)

ThomasNpc = Entity(
    model="./assets/models/npc.obj",
    collider="box",
    scale=(1.125, 1.125, 1.125),
    texture="./assets/textures/hero_baseColor.png",
    double_sided=True,
    y=1,
    rotation=(0, 145, 0),
    shader=lit_with_shadows_shader
)


light = DirectionalLight(shadows=True)

light.look_at(Vec3(1, -1, 1))

dont_cast_shadow = Entity(
    model='cube', y=1, shader=lit_with_shadows_shader, x=2, color=color.light_gray)
dont_cast_shadow.hide(0b0001)

unlit_entity = Entity(model='cube', y=1, x=-2,
                      unlit=True, color=color.light_gray)

bar = Entity(model='cube', position=(0, 3, -2), shader=lit_with_shadows_shader,
             scale=(10, .2, .2), color=color.light_gray)

app.run()
