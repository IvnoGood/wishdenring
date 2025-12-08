
from ursina import *
from random import randint
# import requests
import json
import uuid
import websockets
from websockets.sync.client import connect
import asyncio
from time import sleep
import argparse
from collections import deque
from perlin_noise import PerlinNoise
from time import time as tm
from ursina.shaders import ssao_shader

app = Ursina(icon="./assets/icons/app.ico", title="WishDenRing")

# ------ STRUCTURES ------

hut = Entity(model="./assets/models/hut.obj",
             scale=(2.5, 2.5, 2.5), collider="mesh", position=(0, 0, 10), rotation=(0, 315, 0))

ThoamsNpc = Entity(model="./assets/models/npc.obj", scale=(1.125, 1.125,
                                                           1.125), texture="./assets/textures/hero_baseColor.png", double_sided=True, position=Vec3(-0.61932373, 0, 13.616727), rotation=(0, 145, 0))
ThomasNpcTag = Entity(model="plane", rotation=(
    270, 0, 0), texture="./assets/textures/thomas_affichage.png", double_sided=True, position=Vec3(-0.61932373, 2.5, 13.616727), scale=(2, 1, 1))

# ------ STRUCTURES END ------


# ------ NATURES ------

# Flowers
for i in range(25):
    max = 200
    pos = (randint(-max, max), 0.5, randint(-max, max))
    flower1 = Entity(
        model="plane", texture="./assets/textures/plants/rose.png", position=pos, rotation=(270, 45, 0), double_sided=True)
    flower2 = Entity(
        model="plane", texture="./assets/textures/plants/rose.png", position=pos, rotation=(270, -45, 0), double_sided=True)

for i in range(150):
    max = 200
    pos = (randint(-max, max), 0.5, randint(-max, max))
    type = randint(1, 3)
    flower1 = Entity(
        model="plane", texture=f"./assets/textures/plants/Grass_0{type}.png", position=pos, rotation=(270, 45, 0), double_sided=True)
    flower2 = Entity(
        model="plane", texture=f"./assets/textures/plants/Grass_0{type}.png", position=pos, rotation=(270, -45, 0), double_sided=True)

""" # small grass
for i in range(50):
    max = 200
    pos = (randint(-max, max), 0.5, randint(-max, max))
    flower1 = Entity(
        model="plane", texture="./assets/textures/plants/short_grass.png", position=pos, rotation=(270, 45, 0), double_sided=True, color=color.green)
    flower2 = Entity(
        model="plane", texture="./assets/textures/plants/short_grass.png", position=pos, rotation=(270, -45, 0), double_sided=True, color=color.green)

# tall grass
for i in range(50):
    max = 200
    posBottom = (randint(-max, max), 0.5, randint(-max, max))
    posTop = (posBottom[0], posBottom[1]+1, posBottom[2])
    flower1Bottom = Entity(
        model="plane", texture="./assets/textures/plants/tall_grass_bottom.png", position=posBottom, rotation=(270, 45, 0), double_sided=True, color=color.green)
    flower1Top = Entity(
        model="plane", texture="./assets/textures/plants/tall_grass_top.png", position=posTop, rotation=(270, 45, 0), double_sided=True, color=color.green)
    flower2Bottom = Entity(
        model="plane", texture="./assets/textures/plants/tall_grass_bottom.png", position=posBottom, rotation=(270, -45, 0), double_sided=True, color=color.green)
    flower2Top = Entity(
        model="plane", texture="./assets/textures/plants/tall_grass_top.png", position=posTop, rotation=(270, -45, 0), double_sided=True, color=color.green)
 """

# ------ NATURES END ------


# ------ CLOUDS ------
clouds = []
for i in range(9):
    cloud = Entity(
        model='cube',
        scale=(randint(8, 14), randint(2, 5), randint(8, 14)),
        color=color.white33,
        position=(randint(-100, 100), randint(20, 30), randint(-100, 100)),
        rotation=(0, randint(0, 360), 0),
        alpha=0.8
    )
    clouds.append(cloud)


def moveClouds():
    for cloud in clouds:
        cloud.x += 1 * time.dt

# ------ CLOUDS END ------


class Character(Entity):
    def __init__(self, position=(0, 0.5, 0)):
        self.block = Entity()


structure_grotte = {
    0: Entity(model='cube', scale=(5, 5, 5), position=(10, 2, 20), collider='box', texture='brick', color=color.gray, texture_scale=(10, 10)),
    1: Entity(model='cube', scale=(3.5, 1.25, 3.5), position=(10, 4.5, 20), collider='box', texture='brick', color=color.gray, texture_scale=(10, 10)),
    2: Entity(model='cube', scale=(2.5, 4, 2.5), position=(10, 2, 23), collider='box', texture='brick', color=color.gray, texture_scale=(10, 10)),
}
tp_grotte = {
    0: Entity(model='cube', scale=(2.5, 4, 2.5), position=(10, 1, 18.748), collider='box', texture='brick', color=color.black, texture_scale=(10, 10))
}
camera.clip_plane_far = 75
boss_room = {
    1: Entity(model='plane', scale=60, texture='./assets/textures/concrete_0.png', collider='box', position=(500, -0.5, 500), texture_scale=(60, 60))
}


class Character(Entity):
    def __init__(self):
        super().__init__(
            model='sphere',
            color=color.red,
            position=(0, 3, 0),
            collider='sphere'
        )


""" class Sword(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.red,
            position=(0, 0, 0),
            collider='box',
            rotation=(0,45,45),
            parent=camera.ui
        ) 

sword = Sword()
 """


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


class Enemies(Entity):
    def __init__(self, position=(520, 10, 500), rotation=(0, 0, 0), **kwargs):
        # Initialize the parent entity at the networked position/rotation
        # gpt pr cette ligne utilisat de vecteurs pour faire le multijoueur
        super().__init__(position=Vec3(*position), **kwargs)

        # Create children using local coordinates and parent=self so moving this Entity moves them all
        self.sphere = Entity(
            parent=self,
            model='sphere',
            color=color.blue,
            position=Vec3(0, 0, 0),
            collider='mesh',
            scale=1
        )

        self.torso = Entity(
            parent=self,
            model='cube',
            color=color.blue,
            position=Vec3(0, 1.25, 0),
            scale=Vec3(1, 2, 1),
            collider='mesh'
        )

        self.head = Entity(
            parent=self,
            model='cube',
            texture='shrek_face.jpg',
            position=Vec3(0, 2.75, 0),
            scale=Vec3(1, 1, 1),
            collider='mesh',
        )


enemy = Enemies()


class BottomBar(Entity):
    def __init__(self):
        player.enabled = True
        super().__init__(
            parent=camera.ui,
        )

        self.iventory = Entity(parent=self,
                               model='quad',
                               scale=(0.65, 0.08),
                               origin=(0, 0),
                               position=(0, -0.4),
                               texture='./assets/textures/slot.png',
                               texture_scale=(8, 1),
                               enable=True
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

player.height = 1

player.cursor = Entity(parent=camera.ui, model='quad',
                       color=color.pink, scale=.008, rotation_z=45)

checkpoints = {
    0: Entity(model='cube', color=color.green, scale=(1, 0.001, 1), position=(0, 0.5, 0)),
    1: Entity(model='cube', color=color.green, scale=(1, 0.001, 1), position=(3, 0.5, 3))
}


platforme = Entity(model='cube', color=color.orange, scale=(
    1, 1, 1), position=(-1, -2, -7), collider='box')


# ------ TERRAIN ------
sol = Entity(model='plane', scale=200, texture='grass',
             collider='box', origin_y=0, texture_scale=(200, 200))

""" noise = PerlinNoise(octaves=3, seed=0)
amp = 2
freq = 24
width = 30


# Source - https://stackoverflow.com/questions/70467860/need-help-in-perline-noise-ursina-to-make-an-a-plain-land
# Posted by Jan Wilamowski
# Retrieved 2025-12-06, License - CC BY-SA 4.0
start = tm()
sol = Entity(model=Mesh(vertices=[], uvs=[]),
             color=color.white, texture='./assets/textures/grass.png', texture_scale=(1, 1))

for x in range(1, width):
    for z in range(1, width):
        # add two triangles for each new point
        y00 = noise([x/freq, z/freq]) * amp
        y10 = noise([(x-1)/freq, z/freq]) * amp
        y11 = noise([(x-1)/freq, (z-1)/freq]) * amp
        y01 = noise([x/freq, (z-1)/freq]) * amp
        sol.model.vertices += (
            # first triangle
            (x, y00, z),
            (x-1, y10, z),
            (x-1, y11, z-1),
            # second triangle
            (x, y00, z),
            (x-1, y11, z-1),
            (x, y01, z-1)
        )

sol.model.generate()
sol.model.project_uvs()  # for texture
sol.model.generate_normals()  # for lighting
sol.collider = 'mesh'  # for collision

end = tm()

print("took", end-start, "seconds to generate terrain")

 """
# ------ END TERRAIN ------

player.rotation_y = 180
vitesse_chute = 0
force_gravite = -1.5
last_checkpoint = player.position

player.mouse_sensitivity = Vec2(40, 40)
player.camera_pivot = Entity(parent=player, y=player.height)
# camera.shader = ssao_shader  # ! c'est juste moche
mouse.locked = True

pause = False
footstepsIsPlaying = False
bgmusicIsPlaying = False


# ------ MULTIPLAYER ------

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

# ------ MULTIPLAYER END ------


grid = {(x, z): True for x in range(450, 550) for z in range(450, 550)}

#  BFS Pathfinding


def bfs(start, goal):
    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()

        if current == goal:
            break

        x, z = current
        neighbors = [(x+1, z), (x-1, z), (x, z+1), (x, z-1)]

        for n in neighbors:
            if n in grid and grid[n] and n not in came_from:
                queue.append(n)
                came_from[n] = current

        # Reconstitution du chemin
    path = []
    c = goal
    while c != start:
        path.append(c)
        c = came_from.get(c)
        if c is None:   # Pas de chemin
            return []
    path.reverse()
    return path


path = []
moving = False   # variable globale qui indique si l'ennemi est en train d'animer un mouvement

# Fonction utilitaire pour arrêter le mouvement (appelée par invoke)


def set_moving_false():
    global moving
    moving = False


msg = Text(
    text='BOSS ROOM',
    font='assets/textures/font_boss.ttf',
    scale=8,
    color=color.red,
    origin=(0, -1.4)
)
msg.disable()
camera.fov = 90
camera.parent = player.camera_pivot   # <- essentiel pour FPS
camera.position = Vec3(0, 0, 0)
pause = False
sky_image = load_texture("./assets/textures/environement/sunset.jpg")
sky = Sky(color=color.white, texture=sky_image)
boss_battle = False
if boss_battle == False:
    sky.color = color.white

environementSounds = None


def update():
    vitesse = 4 * time.dt
    global vitesse_chute
    global last_checkpoint
    global sensitivity
    global pause
    global bgmusicIsPlaying
    global environementSounds
    global counter
    global connected_users
    global other_users
    global connected_user_entities
    global isInv
    global path, moving
    global boss_battle

    # ------ AUDIO environement ------
    if (not bgmusicIsPlaying):
        print("Loading sound...")
        environementSounds = Audio('./assets/sounds/env_1.mp3',
                                   loop=True, autoplay=True)
        environementSounds.volume = 5
        print("Loaded:", environementSounds)
        bgmusicIsPlaying = True
    # ------ END AUDIO environement ------

    for i in checkpoints:
        if distance(player.position, checkpoints[i].position) <= 1.5:
            last_checkpoint = checkpoints[i]
            checkpoints[i].color = color.yellow

    if pause == False:
        player.rotation_y += mouse.velocity[0] * player.mouse_sensitivity[0]

        player.camera_pivot.rotation_x -= mouse.velocity[1] * \
            player.mouse_sensitivity[1]
        player.camera_pivot.rotation_x = clamp(
            player.camera_pivot.rotation_x, -90, 90)

    vitesse = 4 * time.dt
    direction = Vec3(camera.forward.x, 0, camera.forward.z).normalized()

    move = Vec3(0, 0, 0)

    if pause == False:
        if held_keys['w']:
            move += direction * vitesse
            if held_keys['shift']:
                move += direction * vitesse

        if held_keys['s']:
            move -= direction * vitesse
        if held_keys['a']:
            move -= Vec3(camera.right.x, 0,
                         camera.right.z).normalized() * vitesse
        if held_keys['d']:
            move += Vec3(camera.right.x, 0,
                         camera.right.z).normalized() * vitesse

    # collisions X
    old_x = player.x
    player.x += move.x
    if player.intersects().hit:
        player.x = old_x

    # collisions Z
    old_z = player.z
    player.z += move.z
    if player.intersects().hit:
        player.z = old_z

    if pause != True:
        old_y = player.y
        vitesse_chute += force_gravite * 0.1
        player.y += vitesse_chute * time.dt

        if player.intersects().hit:
            player.y = old_y
            vitesse_chute = 0

        if held_keys['space'] and vitesse_chute == 0:
            vitesse_chute = 6

    if player.y <= -45:
        player.position = (last_checkpoint.x,
                           last_checkpoint.y + 2, last_checkpoint.z)

    # saut possible que si le perso est sur une surface plate où il ne chute pas
    if pause != True:
        if held_keys['space'] and vitesse_chute == 0:
            # met une vitesse de chute positive pour que le joueur "tombe" vers le haut puis il chute avec la
            vitesse_chute = 6
        # gravité
    if player.y <= -5:
        player.position = (last_checkpoint.x,
                           last_checkpoint.y + 2, last_checkpoint.z)
        boss_battle = False
        sky.color = color.white

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

    if held_keys['escape'] or held_keys['e']:
        sleep(0.25)
        pause = not pause   # ON <-> OFF

        if pause:
            mouse.locked = False
            pause_menu = True
        else:
            mouse.locked = True
            pause_menu = False

    for i in tp_grotte:
        if distance(player.position, tp_grotte[i].position) <= 2.5:
            print("Début combat de boss")
            msg.enable()
            invoke(lambda: msg.animate('alpha', 0, duration=1), delay=2)
            boss_battle = True
            sky.color = color.red
            player.position = (500, 2, 500)

    enemy_pos = (round(enemy.x), round(enemy.z))
    player_pos = (round(player.x), round(player.z))
    if pause != True:
        if distance(enemy.position, player.position) <= 4.5:
            path = []
            return
        # Recalcul du chemin si aucune étape restante et si l'ennemi ne bouge pas
        if not path and not moving:
            path = bfs(enemy_pos, player_pos)

        # Si on a un chemin et qu'on n'est pas en train de bouger :
        if path and not moving:
            next_step = path.pop(0)

            if not grid.get(next_step, False):
                path = []
                return

            # Lancer l'animation vers la prochaine case
            moving = True
            duration = 0.2
            enemy.animate_position(
                Vec3(next_step[0], 0, next_step[1]),
                duration=duration,
                curve=curve.linear
            )

            # Quand l'animation finit, on met moving = False
            invoke(set_moving_false, delay=duration)

        moveClouds()

        ThomasNpcTag.look_at(player, axis=Vec3.up)


app.run()
