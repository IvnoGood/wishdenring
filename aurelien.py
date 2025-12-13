from ursina import *

from ursina.prefabs.first_person_controller import *

items = []


def update():

    for entity in items:
        if distance(player, entity) < 4:
            inventaire[1] = entity
            print(inventaire)
            destroy(entity)
            items.clear
            break
        else:
            entity.rotation_y += 50 * time.dt

    direction_x = player.x - ennemi.x
    direction_z = player.z - ennemi.z
    direction = Vec3(direction_x, 0, direction_z)
    ennemi.position = ennemi.position + direction * time.dt * 0.5
    if ennemi.hovered and distance(player, ennemi) <= 9:
        ennemi.color = color.gray
    else:
        ennemi.color = color.white
    ennemi.look_at(ennemi.position + (direction_x, 0, direction_z))
    if player.x > 23 and player.z < 4.64 and player.z > -6:
        player.position = (10, 10, 10)


pv_ennemi = 5


def input(key):
    global pv_ennemi
    if key == 'left mouse down':
        clique_gauche = True
    if key == 'left mouse down' and ennemi.hovered and distance(player, ennemi) <= 9:
        pv_ennemi -= 1
    if pv_ennemi == 5:
        scale = (2.5, 0.1, 0.1)
    if pv_ennemi == 4:
        bare_de_vie_ennemi.scale = (2, 0.1, 0.1)
    if pv_ennemi == 3:
        bare_de_vie_ennemi.scale = (1.5, 0.1, 0.1)
    if pv_ennemi == 2:
        bare_de_vie_ennemi.scale = (1, 0.1, 0.1)
    if pv_ennemi == 1:
        bare_de_vie_ennemi.scale = (0.5, 0.1, 0.1)
    if pv_ennemi == 0:
        ennemi.visible = False
        ennemi.collider = None
    else:
        clique_gauche = False
    if key == 'right mouse down':
        clique_droit = True
    else:
        clique_droit = False
    if key == 'left mouse down':
        print("Point 3D sous la souris :", mouse.world_point)


app = Ursina()

entité1 = Entity(model='cube',
                 color=color.red,
                 texture='brick',
                 rotation=(0, 0, 0),
                 position=(10, 0, 0),
                 scale=(1, 1, 1))
items.append(entité1)

player = FirstPersonController(position=(0, 0, 0), scale=(1, 4, 1))

item = Entity(parent=player,
              model='cube',
              texture='brick',
              position=(1, 1.7, 1),
              scale=(0.5, 0.5, 0.5))


sol = Entity(model='cube',
             position=(0, -50, 0),
             texture_scale=(50, 50),
             scale=(100),
             texture='grass',
             collider='mesh')
inventaire = {}

donjon = Entity(model='cube',
                position=(35, 25, 0),
                scale=(20, 70, 20),
                texture_scale=(3, 3),
                texture='brick',
                collider='mesh')
donjon2 = Entity(model='cube',
                 position=(31.7, 17, 0),
                 scale=(15, 60, 15),
                 texture_scale=(3, 3),
                 texture='brick',
                 collider='mesh')

entrée_donjon = Entity(model='cube',
                       position=(29, 17, 0),
                       scale=(10, 50, 10),
                       color=color.black)

ennemi = Entity(model='cube',
                scale=(1, 12, 1),
                color=color.white,
                position=(0, 3, 0),
                collider='mesh',
                visible=True)

bare_de_vie_ennemi = Entity(parent=ennemi,
                            model='cube',
                            color=color.green,
                            position=(0, 0.7, 0),
                            scale=(2.5, 0.1, 0.1))


app.run()
