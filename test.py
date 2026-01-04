
from ursina import *
from random import randint
import requests
import json
import uuid
import websockets
from websockets.sync.client import connect
import asyncio
import json
import time
import argparse
from panda3d.core import GraphicsPipeSelection

print(GraphicsPipeSelection.get_global_ptr(
).get_default_pipe().get_interface_name())


app = Ursina(icon="./assets/icons/app.ico", title="WishDenRing")


class Inventory(Entity):
    def __init__(self, width=8, height=5, **kwargs):
        super().__init__(
            parent=camera.ui,
            model=Quad(radius=.015),
            texture='white_cube',
            texture_scale=(width, height),
            scale=(width*.1, height*.1),
            origin=(-.5, .5),
            position=(-.3, .4),
            color=color.hsv(0, 0, .1, .9),
        )

        self.width = width
        self.height = height

        for key, value in kwargs.items():
            setattr(self, key, value)

    def find_free_spot(self):
        for y in range(self.height):
            for x in range(self.width):
                grid_positions = [(int(e.x*self.texture_scale[0]),
                                   int(e.y*self.texture_scale[1])) for e in self.children]
                print(grid_positions)

                if not (x, -y) in grid_positions:
                    print('found free spot:', x, y)
                    return x, y

    def append(self, item, x=0, y=0):
        print('add item:', item)

        if len(self.children) >= self.width*self.height:
            print('inventory full')
            error_message = Text('<red>Inventory is full!',
                                 origin=(0, -1.5), x=-.5, scale=2)
            destroy(error_message, delay=1)
            return

        x, y = self.find_free_spot()

        icon = Draggable(
            parent=self,
            model='quad',
            texture=item,
            color=color.white,
            scale_x=1/self.texture_scale[0],
            scale_y=1/self.texture_scale[1],
            origin=(-.5, .5),
            x=x * 1/self.texture_scale[0],
            y=-y * 1/self.texture_scale[1],
            z=-1,
        )
        name = item.replace('_', ' ').title()

        if random.random() < .25:
            icon.color = color.gold
            name = '<orange>Rare ' + name

        icon.tooltip = Tooltip(name)
        icon.tooltip.background_entity.color = color.hsv(0, 0, 0, .8)

        def drag():
            icon.org_pos = (icon.x, icon.y)
            icon.z = -2   # ensure the dragged item overlaps the rest

        def drop():
            icon.x = int((icon.x + (icon.scale_x/2)) * self.width) / self.width
            icon.y = int((icon.y - (icon.scale_y/2))
                         * self.height) / self.height
            icon.z = -1

            # if outside, return to original position
            if icon.x < 0 or icon.x >= 1 or icon.y > 0 or icon.y <= -1:
                icon.position = (icon.org_pos)
                return

            # if the spot is taken, swap positions
            for c in self.children:
                if c == icon:
                    continue

                if c.x == icon.x and c.y == icon.y:
                    print('swap positions')
                    c.position = icon.org_pos

        icon.drag = drag
        icon.drop = drop


def add_item():
    inventory.append(random.choice(
        ('bag', 'bow_arrow', 'gem', 'orb', 'sword')))


""" add_item_button = Button(
    scale=(.1, .1),
    x=-.5,
    color=color.lime.tint(-.25),
    text='+',
    tooltip=Tooltip('Add random item'),
    on_click=add_item
) """

inventory = Inventory()
isInv = False

for i in range(0, 10):
    add_item()


class Character(Entity):
    def __init__(self):
        super().__init__(
            model='sphere',
            color=color.red,
            position=(0, 7, 0),
            collider='box'
        )


class Players(Entity):
    def __init__(self, position=(0, 10, 0), rotation=(0, 0, 0), **kwargs):
        # Initialize the parent entity at the networked position/rotation
        # gpt pr cette ligne utilisat de vecteurs pour faire le multijoueur
        super().__init__(position=Vec3(*position), **kwargs)

        # Create children using local coordinates and parent=self so moving this Entity moves them all
        self.sphere = Entity(
            parent=self,
            model='sphere',
            color=color.red,
            position=Vec3(0, 0, 0),
            collider='box',
            scale=1
        )

        self.torso = Entity(
            parent=self,
            model='cube',
            color=color.red,
            position=Vec3(0, 1.5, 0),
            scale=Vec3(1, 2, 1),
            collider='box'
        )

        self.head = Entity(
            parent=self,
            model='cube',
            color=color.red,
            position=Vec3(0, 3.25, 0),
            scale=Vec3(1, 1, 1),
            collider='box',
        )


class BottomBar(Entity):
    def __init__(self):
        player.enabled = False
        super().__init__(
            parent=camera.ui,

        )

        self.iventory = Entity(parent=self,
                               model='quad',
                               scale=(0.65, 0.08),
                               origin=(0, 0),
                               position=(0, -0.4),
                               texture='white_cube',
                               texture_scale=(8, 1),
                               enable=True,
                               color=color.hsv(0, 0, .1, .9),
                               )
        self.width = "width"
        self.height = "height"
        self.selected = Entity(parent=self,
                               model='quad',
                               scale=(0.08, 0.08),
                               origin=(0, 0),
                               position=(0, -0.4),  # slot 1
                               texture='white_cube',
                               texture_scale=(1, 1),
                               enable=True,
                               color=color.white,
                               )

        self.health = Entity(parent=self,
                             model='quad',
                             scale=(0.32, 0.04),  # full = 0.32 50%: 16
                             origin=(0, 0),
                             position=(-0.6, -0.4),
                             color=color.green,
                             texture_scale=(8, 1),
                             enable=True
                             )


player = Character()
inv = BottomBar()

checkpoints = {
    0: Entity(model='cube', color=color.green, scale=(1, 0.001, 1), position=(0, 0.5, 0), collider='box'),
    1: Entity(model='cube', color=color.green, scale=(1, 0.001, 1), position=(3, 0.5, 3), collider='box')
}


platforme = Entity(model='cube', color=color.orange, scale=(
    1, 1, 1), position=(-1, -2, -7), collider='box')

zero = Entity(model='cube', color=color.red, scale=(
    1, 1, 1), position=(0, 0, 0), collider='box')

sol = Entity(model='plane', scale=60, texture='./assets/textures/concrete_0.png',
             collider='box', origin_y=0, texture_scale=(60, 60))


player.rotation_y = 180
vitesse_chute = 0
force_gravite = -1
last_chesckpoint = player.position

camera.rotation_x = 0
camera.rotation_y = 0
sensitivity = 3

pause = False
footstepsIsPlaying = False

random_uuid = uuid.uuid4()
uri = "ws://localhost:8080"
user_data = {
    str(random_uuid): {
        "data": {
            "identifier": str(random_uuid)
        },
        "player": {
            "location": (0, 0, 0),
            "rotation": (0, 0, 0)
        }
    }
}

other_users = []
connected_users = []
connected_user_entities = {}
counter = 0


parser = argparse.ArgumentParser(description='WishDenring config files')
parser.add_argument('-m', '--multiplayer', action='store_true',
                    help='Activate multiplayer mode')
parser.add_argument('-ip', '--ipaddr', type=str,
                    help='Specify ip address and port as parameter (default: ws://localhost:8080)')
args = parser.parse_args()

if args.ipaddr:
    uri = args.ipaddr


def lerp(a, b, t):
    return a + t * (b - a)


async def sendToServer(data, uri):
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps({"identifier": str(random_uuid)}))
            response_status = await websocket.recv()

            await websocket.send(json.dumps(data))

            users_data_raw = await websocket.recv()
            other_users = json.loads(users_data_raw)["playersData"]
            connected_users = json.loads(users_data_raw)["connected_users"]
            return other_users, connected_users

    except ConnectionRefusedError:
        print(
            f"\033[91m Connection to websocket '{uri}' failed. Exiting... \033[0m")
        exit()
        return


def placeOtherPlayers():
    for client in other_users:
        val = next(iter(client))
        if (val in connected_user_entities):
            connectedPlayer = connected_user_entities[val]
            loc = client[val]["player"]["location"]
            rot = client[val]["player"]["rotation"]
            connectedPlayer.position = Vec3(loc[0], loc[1], loc[2])
            connectedPlayer.rotation = Vec3(rot[0], rot[1], rot[2])
        else:
            if (val != str(random_uuid)):
                loc = client[val]["player"]["location"]
                rot = client[val]["player"]["rotation"]
                newPlayer = Players(position=loc, rotation=rot)
                connected_user_entities[val] = newPlayer
                print(connected_user_entities)
            pass


def update():
    vitesse = 4 * time.dt
    global vitesse_chute
    global last_checkpoint
    global sensitivity
    global pause
    global footstepsIsPlaying
    global counter
    global connected_users
    global other_users
    global connected_user_entities
    global isInv

    camera.parent = player
    camera.position = Vec3(0, 3, 0)

    for i in checkpoints:
        if distance(player.position, checkpoints[i].position) <= 1.5:
            last_checkpoint = checkpoints[i]
            checkpoints[i].color = color.yellow

    if held_keys['right mouse']:

        camera.rotation_x -= mouse.delta[1] * sensitivity
        camera.rotation_y += mouse.delta[0] * sensitivity
        # Limit vertical rotation
    camera.rotation_x = clamp(camera.rotation_x, -80, 80)

    v1 = Vec3(0, 0, 0)  # pour assigne le vecteur du déplacement

    direction = Vec3(camera.forward.x, 0, camera.forward.z).normalized()

    if held_keys['w'] and held_keys['shift']:
        v1 += direction * vitesse * 2
    if held_keys['w']:
        v1 += direction * vitesse
        # will play after 2 seconds
        # TODO: alors l'audio ca marche a moitié mais flm
        """ if not footstepsIsPlaying:
            invoke(Audio, './assets/sounds/footsteps.mp3', delay=0)
            footstepsIsPlaying = True """
    if held_keys['s']:
        v1 -= direction * vitesse
    if held_keys['a']:
        v1 -= Vec3(camera.right.x, 0, camera.right.z).normalized() * vitesse
    if held_keys['d']:
        v1 += Vec3(camera.right.x, 0, camera.right.z).normalized() * vitesse
        # Déplacement sur l'axe x
    old_x = player.x  # assigne la vielle coordonné x en cas de collision
    player.x += v1.x  # bouge le joueur
    if player.intersects().hit:  # detecte les collisions
        player.x = old_x  # si il y a une collision, revenir sur l'ancienne coordoné pour ne pas passer dans le mur

    # Déplacement sur l'axe z même fonctionnement que pour l'axe x
    old_z = player.z
    player.z += v1.z
    if player.intersects().hit:
        player.z = old_z

    old_y = player.y
    # défini la vitesse de chute pour avoir une chute qui n'est pas constante la vitesse peut être
    vitesse_chute += force_gravite*0.1
    # changé pour avoir une gravité + forte mais peut faire des bugs (passer dans le sol)
    player.y += vitesse_chute*time.dt  # fait chuter les perso
    if player.intersects().hit:
        player.y = old_y  # revenir sur le dessus de la plateforme car il y a eu une collision
        vitesse_chute = 0  # fin de la chute

    # saut possible que si le perso est sur une surface plate où il ne chute pas
    if held_keys['space'] and vitesse_chute == 0:
        # met une vitesse de chute positive pour que le joueur "tombe" vers le haut puis il chute avec la
        vitesse_chute = 6
        # gravité
    if player.y <= -5:
        player.position = (last_checkpoint.x,
                           last_checkpoint.y + 2, last_checkpoint.z)

    if held_keys['e']:
        pause = True
        print("pause")
        mouse.locked = False
        mouse.visible = True

    if held_keys['r'] == True:
        pause = False
    # pour la chute
    if pause == False:
        mouse.locked = True
        mouse.visible = False

    if held_keys['h']:
        if isInv:
            isInv = False
        else:
            isInv = True

    if held_keys['j']:
        inventory.enabled = False

    inventory.enabled = isInv

    user_data[str(random_uuid)]['player']['location'] = tuple(player.position)
    user_data[str(random_uuid)]['player']['rotation'] = [
        -tuple(camera.rotation)[0],
        tuple(player.position)[1],
        tuple(player.position)[2]
    ]  # TODO: la rotation en multi marche super mal tout le corps bouge alors que c pas normal

    if (args.multiplayer):
        if (counter == 20):
            other_users, connected_users = asyncio.run(
                sendToServer(user_data, uri))
            counter = 0
        else:
            counter += 1
        placeOtherPlayers()


app.run()
