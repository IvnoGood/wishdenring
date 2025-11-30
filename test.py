from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *

data = [
    {
        "f6fecddf-d9b2-4e9c-9507-7c87d7114d67": {
            "data": {
                "identifier": "f6fecddf-d9b2-4e9c-9507-7c87d7114d67"},
            "player": {
                "location": [0, 6.777659893035889, 0],
                "rotation": [0, 0, 0]
            }
        }
    }
]


app = Ursina(title="Snake 3D", fullscreen=False)

# map entities
""" map = Entity(model="cube", position=(0, 0, 0),
             collider="box", ignore=True, origin_y=0) """

for client in data:
    val = next(iter(client))
    print(val)
    loc = client[val]["player"]["location"]
    rot = client[val]["player"]["rotation"]
    print(loc)
    map = Entity(model="cube", position=loc,
                 collider="box", ignore=True, origin_y=0.5, color=color.orange, rotation=rot)


ground = Entity(model='plane', scale=60, texture='./assets/textures/concrete_0.png',
                collider='box', origin_y=0, texture_scale=(60, 60))


EditorCamera()

Sky()
app.run()
