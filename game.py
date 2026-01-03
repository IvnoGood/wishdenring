
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
from time import time as tm
from ursina.prefabs.health_bar import HealthBar
from ursina.shaders import lit_with_shadows_shader

app = Ursina(icon="./assets/icons/app.ico",
             title="WishDenRing")

parser = argparse.ArgumentParser(description='WishDenring config files')
parser.add_argument('-c', '--config', type=str,
                    help='Adds a config file')
parser.add_argument('-m', '--multiplayer', type=str,
                    help='Activate multiplayer mode')
parser.add_argument('-ip', '--ipaddr', type=str,
                    help='Specify ip address and port as parameter (default: ws://localhost:8080)')
args = parser.parse_args()

config = {"user": {"camera": {"sensi": 45, "renderDistance": 45},
                   "sounds": {"musics": 0.1, "ambientSounds": 1, "playerSounds": 0.5}}}

if (args.config):
    with open(args.config, "r") as f:
        jsonData = json.load(f)
        config = jsonData

sensibiliteVal = config["user"]["camera"]["sensi"]
renderDistance = config["user"]["camera"]["renderDistance"]

# musiques de fond, teleports
musicSoundsVolume = config["user"]["sounds"]["musics"]
# sons comme: dash, marche, shops, mort et combat
ambientSoundsVolume = config["user"]["sounds"]["ambientSounds"]
# sons comme: dash, mort et combat
playerSoundsVolume = config["user"]["sounds"]["playerSounds"]

portail3 = SpriteSheetAnimation(   # portail du premier boss
    texture='Dimensional_Portal.png',
    tileset_size=(3, 2),
    fps=8,
    animations={'pouet3': ((0, 0), (2, 1))})
portail3.play_animation('pouet3')
portail3.position = (1015.7, 989, 998.2)
portail3.scale = (8, 8)
portail3._double_sided = True
portail3.color = color.magenta


tp_grotte = {
    0: {"portal": portail3,
        "mobNmb": 1,
        "boss": Entity(),
        "isSpe": False,
        "sky": "./assets/textures/environement/chaos.jpg",
        "tpPos": (500, 2, 500)
        }
}


camera.clip_plane_far = renderDistance


boss_room = {
    1: Entity(model='plane', scale=60, texture='./assets/textures/concrete_0.png', collider='box', position=(500, -0.5, 500), texture_scale=(60, 60))
}

fontaine = Entity(
    model='/assets/models/fontaine.obj',
    scale=(0.85, 0.85, 0.85),
    position=(10, 0.7, -10),
    collider='mesh',
    color=color.light_gray,
    texture_scale=(10, 10),
    shader=lit_with_shadows_shader,
    texture="./assets/textures/concrete_0.png"
)

Eau = Entity(
    model='cube',
    scale=(8.75, 0.35, 8.75),
    position=(10, 0.75, -10),
    collider='box',
    texture="./assets/textures/tex_Water.jpg",
    color=color.rgba(1, 1, 1, 0.95),
    rotation=(0, 45, 0),
    texture_scale=(5, 5)
)

fondEau = Entity(
    model='cube',
    scale=(8.75, 0.35, 8.75),
    position=(10, 0.2, -10),
    collider='box',
    texture="./assets/textures/stone/stonecob.png",
    rotation=(0, 45, 0),
    texture_scale=(5, 5)
)


class Character(Entity):
    def __init__(self):
        super().__init__(
            model='sphere',
            color=color.red,
            position=(0, 3, 0),
            collider='sphere'
        )


class Players(Entity):
    def __init__(self, position=(0, 10, 0), rotation=(0, 0, 0), model="katana", **kwargs):
        # Initialize the parent entity at the networked position/rotation
        # gpt pr cette ligne utilisat de vecteurs pour faire le multijoueur
        super().__init__(position=Vec3(*position), ** kwargs)

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

        self.item = Entity(parent=self,
                           position=(1, 2.25, -0.5),
                           model=f"./assets/models/{model}.obj",
                           scale=0.5,
                           rotation=(0, 90, 0)
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
            scale=1,
            collider='box'
        )

        self.torso = Entity(
            parent=self,
            model='cube',
            color=color.blue,
            position=Vec3(0, 1.25, 0),
            scale=Vec3(1, 2, 1),
            collider='box'

        )

        self.head = Entity(
            parent=self,
            model='cube',
            texture='shrek_face.jpg',
            position=Vec3(0, 2.75, 0),
            scale=Vec3(1, 1, 1),
            collider='box',
            double_sided=True
        )


enemy = Enemies()

pv_enemy_boss = 25
pv_enemy_boss_max = 25

barre_de_vie_enemy = Entity(parent=enemy,
                            model='cube',
                            color=color.red,
                            position=(0, 3.85, 0),
                            scale=(2.5, 0.1, 0.1))

# log les info dans l'inventaire
inventaire = {
    0: {"model": "katana", "color": color.magenta},
    1: {},
    2: {},
    3: {},
    4: {},
    5: {},
    6: {},
    7: {},
    8: {}
}

slot_actuel = 0


class IventaireBas(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
        )
        self.invContent = []

        self.iventory = Entity(parent=self,
                               model='quad',
                               scale=(0.65, 0.08),
                               origin=(0, 0),
                               position=(0, -0.4),
                               texture='./assets/textures/slot.png',
                               texture_scale=(8, 1),
                               enable=True
                               )
        for key in inventaire:
            slot = inventaire[0]
            model = slot["model"]
            color = slot["color"]
            #! c full beugé donc pas d'affichage d'inv
            # newSlot = Entity(parent=self.iventory, model='quad', texture=f"./assets/textures/{model}.png", color=color, scale=1, origin=(0, 0), position=(0, 0), rotation=(45, 0, 0))
            # self.invContent.append(newSlot)


health_bar_1 = HealthBar(bar_color=color.lime.tint(-.25),
                         roundness=.2, max_value=100, value=100, scale=(0.32, 0.04), origin=(-0.5, 21))


class MoneyDisplay(Text):
    def __init__(self, value="123"):
        super().__init__(
            parent=camera.ui,
            text=value,
            origin=(0, 0),
            position=(0.6, -0.4),
            font='assets/fonts/BitcountPropSingle-Regular.ttf',
            scale=2,
            color=color.gold
        )

        self.coinme = Entity(parent=self,
                             model='quad',
                             scale=(0.05, 0.05),
                             origin=(0, 0),
                             position=(-0.05, 0),
                             texture='./assets/textures/coin.png',
                             enable=True
                             )

    def update_value(self, new_value):
        self.text = str(new_value)


player = Character()
player.rotation = (0, 35, 0)
player.position = (10, 10, 0)
speedFact = 5
degatEpee = 1
start_epee = time.time()


class HandItem(Entity):
    def __init__(self, id='', entColor=''):

        super().__init__(
            parent=player,
            model=f"./assets/models/{id}.obj",
            rotation=(0, 0, 0),
            position=(0.5, .5, 1),
            scale=0.25,
            color=entColor,
            collider="mesh",
            shader=lit_with_shadows_shader,
            double_sided=True,
        )

        self.origin = (0, -0.5, 0)
        self.rotation = (0, 0, 0)
        self.swinging = False

    def updItem(self, newVal):
        self.color = newVal[0]
        self.model = f"./assets/models/{newVal[1]}.obj"
        self.modelName = newVal[1]

    def update(self):
        global speedFact, degatEpee

        if (self.modelName == "katana"):
            if held_keys["left mouse"]:
                if held_keys["left mouse"] and self.swinging == False and pause == False:
                    self.swing()
                if (self.color == color.brown):
                    degatEpee = 2

                elif (self.color == color.gray):
                    degatEpee = 3

                elif (self.color == color.gold):
                    degatEpee = 4

                elif (self.color == color.magenta):
                    degatEpee = 5

        elif (self.modelName == "fiole"):
            if held_keys["right mouse"]:
                drinkSound = Audio('./assets/sounds/drink.ogg',
                                   autoplay=True)
                drinkSound.volume = playerSoundsVolume
                print("heal")
                if (self.color == color.red):
                    health_bar_1.value += 30

                elif (self.color == color.yellow):
                    speedFact = speedFact * 1.5

                elif (self.color == color.magenta):
                    degatEpee = degatEpee * 2
                    pass

                inventaire[slot_actuel] = {}
                time.sleep(0.125)

    def swing(self):
        global start_epee
        if time.time() - start_epee >= 1 and pause == False:
            start_epee = time.time()
            swingSound = Audio('./assets/sounds/swordswoosh.ogg',
                               autoplay=True)
            swingSound.volume = playerSoundsVolume
            self.swinging = True
            print('swing')
            self.animate_rotation(
                Vec3(90, -20, 0),
                duration=0.5,
                curve=curve.out_quad
            )
            if pause == False:
                invoke(self.reset_rotation, delay=0.5)

    def reset_rotation(self):
        self.animate_rotation(
            Vec3(0, 0, 0),
            duration=0.1,
            curve=curve.in_quad
        )
        self.swinging = False
        print('not swinging')


handItem = HandItem(id="fiole", entColor=color.yellow)


def controlHotbar():
    global slot_actuel, inventaire
    if held_keys["1"]:
        slot_actuel = 0
    elif held_keys["2"]:
        slot_actuel = 1
    elif held_keys["3"]:
        slot_actuel = 2
    elif held_keys["4"]:
        slot_actuel = 3
    elif held_keys["5"]:
        slot_actuel = 4
    elif held_keys["6"]:
        slot_actuel = 5
    elif held_keys["7"]:
        slot_actuel = 6
    elif held_keys["8"]:
        slot_actuel = 7
    slotData = inventaire[slot_actuel]
    if ("color" in slotData and "model" in slotData):
        handItem.enable()
        slotUpd = [slotData["color"], slotData["model"]]
        handItem.updItem(slotUpd)
    else:
        handItem.disable()


player.height = 1
player.cursor = Entity(parent=camera.ui, model='quad',
                       color=color.pink, scale=.008, rotation_z=45)

checkpoints = {
    0: Entity(model='cube', color=color.green, scale=(1, 0.001, 1), position=(10, 0.002, 0)),
}


platforme = Entity(model='cube', color=color.orange, scale=(
    1, 1, 1), position=(-1, -2, -7), collider='box')


# ------ TERRAIN ------
# structSol = Entity(model='./assets/models/ile2.obj', scale=(1, 1,1), color=color.gray,collider='mesh', origin_y=0,shader=lit_with_shadows_shader)

""" sol = Entity(model="plane", scale=(16, 1, 16), color=color.gray,
             collider='box', origin_y=0.5, texture_scale=(64, 64), double_sided=True, shader=lit_with_shadows_shader)
 """
Entity(model='plane', scale=64,
       shader=lit_with_shadows_shader, collider="box", texture="brick", texture_scale=(64, 64), color=color.rgba(0.8, 0.8, 0.8, 1))

# ------ END TERRAIN ------

vitesse_chute = 0
force_gravite = -1.0
last_checkpoint = player.position

player.mouse_sensitivity = Vec2(
    sensibiliteVal, sensibiliteVal)
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
PlayersMoving = {}

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


def set_PlayersMoving_false(id):
    global PlayersMoving
    PlayersMoving[id] = False


def placeOtherPlayers():
    global PlayersMoving
    for client in other_users:
        val = next(iter(client))
        if (val in connected_user_entities):
            connectedPlayer = connected_user_entities[val]
            loc = client[val]["player"]["location"]
            rot = client[val]["player"]["rotation"]

            if not PlayersMoving.get(val, False):
                PlayersMoving[val] = True
                duration = 0.01
                connectedPlayer.animate_position(
                    Vec3(loc[0], loc[1], loc[2]),
                    duration=duration,
                    curve=curve.linear
                )
                invoke(set_PlayersMoving_false, val, delay=duration)

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
sky_path = "./assets/textures/environement/sunset.jpg"
sky_image = load_texture(
    sky_path)
sky = Sky(color=color.white, texture=sky_image)
boss_battle = False
if boss_battle == False:
    sky.texture = sky_path

environementSounds = None
coins = 50

# ------ STRUCTURES ------

light = DirectionalLight(shadows=True, position=Vec3(5, 5, -20))
light_look_pos = Vec3(10., 0.5, 15)
""" pointer = Entity(model="cube", position=light_look_pos,
                 color=color.red, scale=1)

pointer = Entity(model="cube", position=light.position,
                 color=color.red, scale=1) """

light.look_at(light_look_pos)


light.shadow_resolution = 2048 * 20
light.shadow_bias = 0.005
(0.255, 0.125, 0.20)

light.color = color.hex("#eae0c1")


ThomasHut = Entity(
    model="./assets/models/hyundai_porter.obj",
    texture="./assets/textures/truck/h-porter-gray.jpg",
    scale=0.1,
    collider="box",
    position=(-7, 0, 15),
    rotation=(0, 315, 0),
    double_sided=True,
    shader=lit_with_shadows_shader
)

ThomasHut.cast_shadows = True
ThomasHut.receive_shadows = True

ThomasNpc = Entity(
    model="./assets/models/npc.obj",
    collider="box",
    scale=(1.125, 1.125, 1.125),
    texture="./assets/textures/hero_baseColor.png",
    double_sided=True,
    position=Vec3(-0.61932373, 0, 13.616727),
    rotation=(0, 145, 0),
    shader=lit_with_shadows_shader
)


ThomasNpc.cast_shadows = True
ThomasNpc.receive_shadows = True

ThomasNpcTag = Entity(
    model="plane",
    rotation=(270, 0, 25),
    texture="./assets/textures/thomas_affichage.png",
    double_sided=True,
    position=Vec3(-0.61932373, 2.5, 13.616727),
    scale=(2, 1, 1)
)

NpcThomasToolTip = Text("Appuie sur T pour discuter")
NpcThomasToolTip.disable()
coloor = (0.80, 0.80, 0.80, 1)
darken = color.rgba(coloor[0], coloor[1], coloor[2], coloor[3])
ThomasNpc.color = darken
ThomasHut.color = darken
ThomasNpcTag.color = darken


AlexaHut = Entity(
    model="./assets/models/hut.obj",
    scale=(2.5, 2.5, 2.5),
    collider="mesh",
    position=(13, 0, 12),
    rotation=(0, -315, 0),
    shader=lit_with_shadows_shader
)
AlexaNpc = Entity(
    model="./assets/models/MEDICAL_SISTER.obj",
    position=(16, 0, 12),
    collider="mesh",
    scale=0.01,
    ignore=True,
    origin_y=0,
    texture="./assets/textures/MEDICAL_SISTER_BaseColor.png",
    double_sided=True,
    rotation=(0, -145, 0),
    shader=lit_with_shadows_shader
)
AlexaNpcTag = Entity(
    model="plane",
    rotation=(270, 0, -25),
    texture="./assets/textures/alexa_affichage.png",
    double_sided=True,
    position=(16, 2.5, 12),
    scale=(2, 1, 1),
)
AlexaToolTip = Text("Appuie sur T pour discuter")
AlexaToolTip.disable()

AlexaNpc.color = darken
AlexaHut.color = darken
AlexaNpcTag.color = darken


class ShopButton(Button):
    def __init__(self, title="Lorem Ipsum", defcolor=color.azure, cost=0, model="./assets/models/fiole.obj", color=color.white, ** kwargs):
        super().__init__(text=title, color=defcolor)

        def takemymoney():
            buySound = Audio('./assets/sounds/shopPurchase.ogg',
                             autoplay=True)
            buySound.volume = ambientSoundsVolume
            global coins
            op = coins - cost
            if (op > 0):
                moneyDp.update_value(op)
                coins = op

            global found
            found = False
            for key in inventaire:
                if ("color" not in inventaire[key] and "model" not in inventaire[key]):
                    print("slot: ", key, " is empty !")
                    inventaire[key] = {"model": model, "color": color}
                    found = True
                    break
            if not found:
                print("no space left")
                moneyDp.update_value(coins + cost)
                coins = coins + cost

        self.on_click = takemymoney


class GUIExitBtn(Button):
    def __init__(self, gui=[], **kwargs):
        super().__init__(text="Exit", color=color.red)

        def closeGui():
            global pause
            player.position = (10, 2.5, 0)
            # Vec3(
            # player.position[0]+4, player.position[1], player.position[2]+2)
            pause = False
            mouse.locked = True

        self.on_click = closeGui


NpcThomasGUI = WindowPanel(
    title='Thomas - Forgeron',
    content=(
        ShopButton(title="Epée en bois - 16p", cost=16,
                   model="katana", color=color.brown),
        ShopButton(title="Epée en fer - 128p", cost=128,
                   model="katana", color=color.gray),
        ShopButton(title="Epée en or - 256p", cost=256,
                   model="katana", color=color.gold),
        ShopButton(title="Epée en améthyste - 500p", cost=500,
                   model="katana", color=color.magenta),
        GUIExitBtn()
    ),
    popup=False,
    Draggable=False
)
NpcThomasGUI.y = NpcThomasGUI.panel.scale_y / 2 * NpcThomasGUI.scale_y
NpcThomasGUI.layout()
NpcThomasGUI.disable()

NpcAlexaGUI = WindowPanel(
    title='Alexa - Forgeron',
    content=(
        ShopButton(title="Potion de régénération - 32p", cost=32,
                   model="fiole", color=color.red),
        ShopButton(title="Potion de céléritée - 32p", cost=32,
                   model="fiole", color=color.yellow),
        GUIExitBtn()
    ),
    popup=False,
    Draggable=False
)
NpcAlexaGUI.y = NpcAlexaGUI.panel.scale_y / 2 * NpcAlexaGUI.scale_y
NpcAlexaGUI.layout()
NpcAlexaGUI.disable()


def displayForNpc(pause):
    if (distance(player, ThomasNpc) < 3):
        NpcThomasToolTip.enable()
        if (held_keys["t"]):
            print("opened gui")
            openSoundTH = Audio('./assets/sounds/click.ogg',
                                autoplay=True)
            openSoundTH.volume = ambientSoundsVolume
            NpcThomasToolTip.disable()
            time.sleep(0.25)
            mouse.locked = False
            pause = True
            NpcThomasGUI.enable()
        return pause
    elif (distance(player, AlexaNpc) < 3):
        AlexaToolTip.enable()
        if (held_keys["t"]):
            print("opened gui")
            openSoundAL = Audio('./assets/sounds/click.ogg',
                                autoplay=True)
            openSoundAL.volume = ambientSoundsVolume
            AlexaToolTip.disable()
            time.sleep(0.25)
            mouse.locked = False
            pause = True
            NpcAlexaGUI.enable()
        return pause
    else:
        NpcThomasToolTip.disable()
        NpcThomasGUI.disable()
        AlexaToolTip.disable()
        NpcAlexaGUI.disable()
        return pause

# ------ STRUCTURES END ------

# ------ NPC DISSCUSSION ------


# ------ NPC DISSCUSSION END------


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


moneyDp = MoneyDisplay(value=str(coins))


class DroppedItem(Entity):
    def __init__(self, modelEnt="cube", scaleEnt=1, colorEnt=color.red,
                 textureEnt='', pos=(0, 0, 0), collider=None, coinValue=0, modelName="coin"):
        super().__init__(
            parent=scene,
            model=modelEnt,
            position=pos,
            scale=scaleEnt,
            color=colorEnt,
            texture=textureEnt,
            collider=collider
        )
        self.modelName = modelName
        self.picked_up = False
        self.coin_value = coinValue

    def update(self):
        self.rotation_y += 50 * time.dt
        global coins
        if self.picked_up:
            return
        if distance(player.position, self.position) < 2:
            print(self.modelName)
            if (self.modelName == "coin"):
                coins = self.coin_value + coins
                moneyDp.update_value(coins)
                print(coins)
                self.picked_up = True
                self.enabled = False
            else:
                global found
                found = False
                for key in inventaire:
                    if ("color" not in inventaire[key] and "model" not in inventaire[key]):
                        print("slot: ", key, " is empty !")
                        inventaire[key] = {
                            "model": self.modelName, "color": self.color}
                        found = True
                        self.picked_up = True
                        self.enabled = False
                        break


"""
coin = DroppedItem(modelEnt="./assets/models/coin.obj",
                   pos=(4, 0.125, 4),
                   scaleEnt=0.125,
                   colorEnt=color.yellow,
                   modelName="coin",
                   coinValue=20)

erlenR = DroppedItem(modelEnt="./assets/models/fiole.obj",
                     pos=(6, 0.5, 7),
                     scaleEnt=0.25,
                     colorEnt=color.red,
                     modelName="fiole") """
boss_dmg = 25
boss_win = False
tp_grotte_boss = Entity(model='cube',
                        scale=(2.5, 4, 2.5),
                        position=(0, 0, 0),
                        collider='box', texture='brick', color=color.black, texture_scale=(10, 10))
tp_grotte_boss.collider = None
tp_grotte_boss.visible = None


def degat():
    global pv_enemy_boss, pv_enemy_boss_max, delay, degatEpee, boss_win, boss_dmg
    # print("Point 3D sous la souris :", mouse.world_point)
    calc = pv_enemy_boss - degatEpee
    bossHitSound = Audio('./assets/sounds/hitsword.ogg',
                         autoplay=True)
    bossHitSound.volume = ambientSoundsVolume
    if (calc <= 0):
        pv_enemy_boss -= degatEpee
        barre_de_vie_enemy.scale = (
            2.50*(pv_enemy_boss/pv_enemy_boss_max), 0.1, 0.1)

#        enemy.visible = False
        enemy.visible = False
        enemy.collider = None
        location = enemy.position
        enemy.position = Vec3(500, -1000, 900)
        boss_battle = False
        boss_dmg = 0

        boss_win = True
        coin = DroppedItem(modelEnt="./assets/models/coin.obj",
                           pos=location,
                           scaleEnt=0.125,
                           colorEnt=color.yellow,
                           modelName="coin",
                           coinValue=randint(50, 75))
        tp_grotte_boss.visible = True
        tp_grotte_boss.collider = 'box'
        tp_grotte_boss.position = Vec3(520, 1, 500)
    else:
        pv_enemy_boss -= degatEpee
        barre_de_vie_enemy.scale = (
            2.50*(pv_enemy_boss/pv_enemy_boss_max), 0.1, 0.1)


delay = 1
start = time.time()

death = False
dash_cooldown = time.time()
boss_attacking = False
boss_timer = time.time()


clé_jump = False
clé_lab = False
# ------ AUDIO environement ------
print("Loading sound...")
environementSounds = Audio('./assets/sounds/ursina_audio_crestlands_part.ogg',
                           loop=True, autoplay=True)
environementSounds.volume = musicSoundsVolume
print("Loaded:", environementSounds)
# ------ END AUDIO environement ------


def update():
    global vitesse_chute, speedFact
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
    global coins
    global degat, delay, start
    global pv_enemy_boss, boss_win, health_bar_1
    global death, dash_cooldown, boss_attacking, boss_timer, boss_dmg
    global pv_enemy_boss
    global jump
    global clé_jump
    global clé_lab
    global lave_jump
    global pv_enemy_boss, boss_win, health_bar_1
    global death, dash_cooldown, boss_attacking, boss_timer, boss_dmg

    if (held_keys["l"]):
        print(player.position)
        print([portail.rotation, portail2.rotation, portail3.rotation,
              portail4.rotation, portail6.rotation])

    if held_keys['q'] and time.time()-dash_cooldown >= 1.5 and pause == False:
        print('dash')
        dashSound = Audio('./assets/sounds/dash.ogg',
                          autoplay=True)
        dashSound.volume = playerSoundsVolume
        dash_distance = 7
        if held_keys['a']:
            direction = -Vec3(camera.right.x, 0, camera.right.z).normalized()
        elif held_keys['d']:
            direction = Vec3(camera.right.x, 0, camera.right.z).normalized()
        elif held_keys['s']:
            direction = -Vec3(camera.forward.x, 0,
                              camera.forward.z).normalized()
        else:
            direction = Vec3(camera.forward.x, 0,
                             camera.forward.z).normalized()
        hit = raycast(
            player.world_position,
            direction,
            distance=dash_distance,
            ignore=(player,)
        )

        if hit.hit:
            target_pos = hit.world_point - direction * 0.6
        else:
            target_pos = player.world_position + direction * dash_distance

        player.animate(
            'position',
            target_pos,
            duration=0.35,
            curve=curve.out_quad
        )
        dash_cooldown = time.time()

    if distance(fontaine, player) <= 6:
        health_bar_1.value = 100
    if pause == False:
        if distance(enemy, player) <= 6:

            if boss_attacking == False:
                boss_attacking = True
                boss_timer = time.time()

            elif time.time() - boss_timer >= 1.65:
                print("hit")
                playerDamageSound = Audio('./assets/sounds/playerHit.ogg',
                                          autoplay=True)
                playerDamageSound.volume = playerSoundsVolume
                health_bar_1.value -= boss_dmg
                boss_timer = time.time()
        else:
            if boss_attacking == True and time.time() - boss_timer >= 2:
                boss_attacking = False

        if health_bar_1.value <= 0:
            death = True
            coins = 0

    if death == True:
        deathBossSound = Audio('./assets/sounds/death.ogg',
                               autoplay=True)
        deathBossSound.volume = playerSoundsVolume
        player.position = (last_checkpoint.x,
                           last_checkpoint.y+5, last_checkpoint.z)
        player.rotation = (0, 0, 0)
        health_bar_1.value = 100
        boss_battle = False
        sky.texture = sky_image
        death = False

    if held_keys['left mouse'] and distance(player, enemy) <= 9:
        if time.time() - start >= delay:
            start = time.time()
            degat()

    if (boss_win):
        # la partie reprise de combat ca marche pas trop prblm pv boss + tp qiu se dep
        tp_grotte_boss.collider = "box"
    if boss_win == False:
        tp_grotte_boss.position = (520, 100, 500)
    if boss_win == True:
        # la partie reprise de combat ca marche pas trop prblm pv boss + tp qiu se dep
        tp_grotte_boss.visible = True
        tp_grotte_boss.position = (
            enemy.position[0]+4, enemy.position[1], enemy.position[2])
        tp_grotte_boss.position = (520, 1, 500)

        if distance(tp_grotte_boss, player) < 3:
            player.position = (0, 1, 0)
            sky.texture = sky_path
            boss_battle = False
            enemy.visible = True
            pv_enemy_boss = 15
            tp_grotte_boss.collider = None
            tp_grotte_boss.visible = None
            player.rotation = (0, 0, 0)
            sky.texture = sky_path

    direction_x = player.x - enemy.x
    direction_z = player.z - enemy.z
    if enemy.hovered and distance(player, enemy) <= 9:
        enemy.color = color.gray
    else:
        enemy.color = color.white
    enemy.look_at(enemy.position + (direction_x, 0, direction_z))

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

    vitesse = speedFact * time.dt
    direction = Vec3(camera.forward.x, 0, camera.forward.z).normalized()

    move = Vec3(0, 0, 0)

    if pause == False:
        if held_keys['w']:
            move += direction * vitesse
            if (not bgmusicIsPlaying):
                """ environementSounds = Audio('./assets/sounds/footsteps.ogg', #! faites le sys de footsteps plz g full la flm
                                           autoplay=True)
                environementSounds.volume = 0.5 """
                bgmusicIsPlaying = True

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

    portailTpSound = Audio('./assets/sounds/teleport.ogg', autoplay=False)
    portailTpSound.volume = ambientSoundsVolume

    portail.rotation = Vec3(0, 0.56399536, 0)
    if distance(player, portail) < 4:
        player.position = (1000, 986, 1000)
        portailTpSound.play()

    portail2.rotation = Vec3(0, 52.433784, 0)
    if distance(player, portail2) < 4:
        player.position = (last_checkpoint.x,
                           last_checkpoint.y+5, last_checkpoint.z)
        portailTpSound.play()

    portail3.rotation = Vec3(0, 96.54034, 0)
    # PRIS PR LE BOSS DE VIK

    portail4.rotation = Vec3(0, 146.95483, 0)
    if distance(player, portail4) < 4:
        player.position = (3000, 1001.5, 3001.7)
        portailTpSound.play()
        jump = True
        if player.intersects(lave_jump):
            player.position = (last_checkpoint.x,
                               last_checkpoint.y+5, last_checkpoint.z)
            jump = False

    portail6.rotation = Vec3(0, 236.51391, 0)
    if distance(player, portail6) < 4:
        portailTpSound.play()
        player.position = Vec3(1957.1273, 1005, 2092.245)
        # player.position = (2057.5, 1045, 1941) WIN IS HERE

    portaillab.look_at(player)
    portaillab.rotation_y = portaillab.rotation_y + 180
    portaillab.rotation_x = 0
    portaillab.rotation_z = 0
    if distance(player, portaillab) < 4:
        player.position = (1000, 986, 1000)
        portailTpSound.play()

    portailjump.look_at(player)
    portailjump.rotation_y = portailjump.rotation_y + 180
    portailjump.rotation_x = 0
    portailjump.rotation_z = 0
    if player.intersects(portailjump):
        player.position = (1000, 986, 1000)
        portailTpSound.play()
        jump = False
    if player.intersects(lave_jump):
        player.position = (last_checkpoint.x,
                           last_checkpoint.y+5, last_checkpoint.z)
        health_bar_1.value = 100
        deathSound = Audio('./assets/sounds/death.ogg',
                           autoplay=True)
        deathSound.volume = playerSoundsVolume
        jump = False
    if jump == True:
        lave_jump.y += 0.25 * time.dt
    if jump == False:
        lave_jump.position = (3000, 980, 3000)

    if clé_jump.hovered and distance(player, clé_jump) <= 9:
        clé_jump.color = color.orange
    else:
        clé_jump.color = color.yellow
    if clé_lab.hovered and distance(player, clé_lab) <= 9:
        clé_lab.color = color.orange
    else:
        clé_lab.color = color.yellow

    """ grille_portail5.look_at(player)
    grille_portail5.rotation_y += 90
    grille_portail5.rotation_x = 0
    grille_portail5.rotation_z = 0 """

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
        vitesse_chute += force_gravite * time.dt*3.8
        player.y += vitesse_chute * time.dt

        if player.intersects().hit:
            player.y = old_y
            vitesse_chute = 0

        if held_keys['space'] and vitesse_chute == 0:
            vitesse_chute = 6

    if player.y <= -45:
        player.position = (last_checkpoint.x,
                           last_checkpoint.y + 2, last_checkpoint.z)

        # gravité
    if player.y <= -15:
        player.position = (last_checkpoint.x,
                           last_checkpoint.y + 2, last_checkpoint.z)
        boss_battle = False
        sky.texture = sky_path

    user_data[str(random_uuid)]['player']['location'] = tuple(player.position)
    user_data[str(random_uuid)]['player']['rotation'] = [
        -tuple(camera.rotation)[0],
        tuple(player.position)[1],
        tuple(player.position)[2]
    ]  # TODO: la rotation en multi marche super mal tout le corps bouge alors que c pas normal

    if (args.multiplayer):
        if (counter == 10):
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
        if distance(player.position, tp_grotte[i]["portal"].position) <= 3:
            portailTpSound = Audio('./assets/sounds/teleport.ogg',
                                   autoplay=True)
            portailTpSound.volume = ambientSoundsVolume
            print("Début combat de boss")
            bossStartSound = Audio('./assets/sounds/bossintro.ogg',
                                   autoplay=True)
            bossStartSound.volume = ambientSoundsVolume
            msg.enable()
            tp_grotte_boss.collider = None
            tp_grotte_boss.visible = None
            invoke(lambda: msg.animate('alpha', 0, duration=1), delay=2)
            boss_battle = True
            boss_win = False
            sky.texture = "./assets/textures/environement/chaos.jpg"
            enemy.position = (510, 3, 500)
            pv_enemy_boss = pv_enemy_boss_max
            enemy.collider = True
            enemy.visible = True
            barre_de_vie_enemy.scale = (2.5, 0.1, 0.1)
            player.position = (500, 2, 500)
            player.rotation = (0, 90, 0)
            boss_dmg = 25

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
        pause = displayForNpc(pause)
        controlHotbar()


clé_jumpe = False
clé_labe = False


def input(key):
    global clé_jump
    global clé_lab
    global clé_jumpe
    global clé_labe
    if key == 'left mouse down':
        print("Point 3D sous la souris :", mouse.world_point)
    if key == 'left mouse down' and clé_lab.hovered and distance(player, clé_lab) <= 9:
        clé_lab.visible = False
        clé_lab.collider = None
        clé_labe = True
    if key == 'left mouse down' and clé_jump.hovered and distance(player, clé_jump) <= 9:
        clé_jump.visible = False
        clé_jump.collider = None
        clé_jumpe = True


portail = SpriteSheetAnimation(    # portail du lobby
    texture='Dimensional_Portal.png',
    tileset_size=(3, 2),
    fps=8,
    animations={'pouet': ((0, 0), (2, 1))})

portail.play_animation('pouet')
portail.position = Vec3(10, 4, 20)
portail.scale = (8, 8)
portail._double_sided = True

portailAff = Entity(
    model="plane",
    rotation=(270, 0, 0),
    texture="./assets/textures/salleSign.png",
    double_sided=True,
    position=(10.25, 9, 20),
    scale=(4, 1, 2),
)

portail2 = SpriteSheetAnimation(     # portail pour aller au lobby
    texture='Dimensional_Portal.png',
    tileset_size=(3, 2),
    fps=8,
    animations={'pouet2': ((0, 0), (2, 1))})
portail2.play_animation('pouet2')
portail2.position = (1012, 989, 1009.23)
portail2.scale = (8, 8)
portail2._double_sided = True

portail2Aff = Entity(
    model="plane",
    rotation=(270, 52.433784, 0),
    texture="./assets/textures/retourSign.png",
    double_sided=True,
    position=(1012.25, 994, 1009.23),
    scale=(4, 1, 2),
)

portail3Aff = Entity(
    model="plane",
    rotation=(270,  96.54034, 0),
    texture="./assets/textures/shrekSign.png",
    double_sided=True,
    position=(1015.95, 994, 998.2),
    scale=(4, 1, 2),
)

portail4 = SpriteSheetAnimation(   # portail du jump avec lave
    texture='Dimensional_Portal.png',
    tileset_size=(3, 2),
    fps=8,
    animations={'pouet4': ((0, 0), (2, 1))})
portail4.play_animation('pouet4')
portail4.position = (1008.6, 989, 986.78)
portail4.scale = (8, 8)
portail4._double_sided = True
portail4.color = color.orange

portail4Aff = Entity(
    model="plane",
    rotation=(270, 146.95483, 0),
    texture="./assets/textures/jumpSign.png",
    double_sided=True,
    position=(1008.85, 994, 986.78),
    scale=(4, 1, 2),
)

""" portail5 = SpriteSheetAnimation(   # portail horde d'ennemis
    texture='Dimensional_Portal.png',
    tileset_size=(3, 2),
    fps=8,
    animations={'pouet3': ((0, 0), (2, 1))})
portail5.play_animation('pouet3')
portail5.position = (996.2, 989, 984.7)
portail5.scale = (8, 8)
portail._double_sided = True
portail5.color = color.yellow
 """

portail6 = SpriteSheetAnimation(   # portail labyrinthe
    texture='Dimensional_Portal.png',
    tileset_size=(3, 2),
    fps=8,
    animations={'pouet3': ((0, 0), (2, 1))})
portail6.play_animation('pouet3')
portail6.position = (987, 989, 991.4)
portail6.scale = (8, 8)
portail6._double_sided = True
portail6.color = color.blue

portail6Aff = Entity(
    model="plane",
    rotation=(270,  236.51391, 0),
    texture="./assets/textures/labSign.png",
    double_sided=True,
    position=(987.25, 994, 991.4),
    scale=(4, 1, 2),
)


""" portail7 = SpriteSheetAnimation(   # portail prof de NSI
    texture='Dimensional_Portal.png',
    tileset_size=(3, 2),
    fps=8,
    animations={'pouet3': ((0, 0), (2, 1))})
portail7.play_animation('pouet3')
portail7.position = (984.5, 989, 1003.6)
portail7.scale = (8, 8)
portail._double_sided = True
portail7.color = color.pink """


""" portail8 = SpriteSheetAnimation(   # portail dimension vide
    texture='Dimensional_Portal.png',
    tileset_size=(3, 2),
    fps=8,
    animations={'pouet3': ((0, 0), (2, 1))})
portail8.play_animation('pouet3')
portail8.position = (991.87, 989, 1013)
portail8.scale = (8, 8)
portail._double_sided = True
portail8.color = color.azure
 """

""" portail9 = SpriteSheetAnimation(   # portail boss final
    texture='Dimensional_Portal.png',
    tileset_size=(3, 2),
    fps=8,
    animations={'pouet3': ((0, 0), (2, 1))})
portail9.play_animation('pouet3')
portail9.position = (1002, 989, 1015.7)
portail9.scale = (8, 8)
portail._double_sided = True
portail9.color = color.red """

portaillab = SpriteSheetAnimation(   # portail du labyrinthe
    texture='Dimensional_Portal.png',
    tileset_size=(3, 2),
    fps=8,
    animations={'pouet3': ((0, 0), (2, 1))})
portaillab.play_animation('pouet3')
portaillab.position = (2057.5, 1002.5, 1939)
portaillab.scale = (5.5, 5.5)
portaillab.color = color.orange

portailjump = SpriteSheetAnimation(   # portail du labyrinthe
    texture='Dimensional_Portal.png',
    tileset_size=(3, 2),
    fps=8,
    animations={'pouet3': ((0, 0), (2, 1))})
portailjump.play_animation('pouet3')
portailjump.position = Vec3(3012.7204, 1040.232, 3035.33)
portailjump.scale = (5, 5)
portailjump.color = color.orange

dome_fermé = Entity(position=(1000, 1000, 1000),
                    model='./assets/models/domefermé.obj',
                    collider='mesh',
                    rotation=(0, 0, 0),
                    scale=(17, 17, 17),
                    texture='./assets/textures/stone/stonebricks0001.png',
                    color=color.white,
                    texture_scale=(10, 10),
                    double_sided=True)

sol_dome = Entity(position=(1000, 984.8989, 1000),
                  model='plane',
                  scale=(50, 50, 50),
                  color=color.rgba(0, 0, 0, 0),
                  texture_scale=(10, 10),
                  collider='box')

labyrinthe = Entity(model='./assets/models/labyrinthe.obj',
                    position=(2000, 1000, 2000),
                    scale=(100, 100, 100),
                    texture='./assets/textures/stone/stonebricks0001.png',
                    collider='mesh',
                    texture_scale=(100, 100),
                    double_sided=True)

sol_labyrinthe = Entity(model='plane',                     # car défaut de modèle
                        position=(2050, 999.9, 1940),
                        scale=(2000, 30, 2000),
                        texture='brick',
                        collider='box',
                        color=color.rgba(0, 0, 0, 5),
                        texture_scale=(5, 5))


clé_lab = Entity(model='./assets/models/clé.obj',
                 position=(2057.5, 1001, 1941),
                 color=color.yellow,
                 scale=(2, 2, 2),
                 collider='mesh',
                 rotation_x=90)

jump = Entity(model='./assets/models/jump22.obj',
              position=(3000, 1000, 3000),
              texture='brick',
              scale=(1, 1, 1),
              collider='mesh',
              texture_scale=(15, 15),
              double_sided=True,
              use_cache=False)
""" 
fin_jump = Entity(model='cube',
                  position=(2985.72, 1033, 3035.53),
                  scale=(7, 1, 7),
                  collider='mesh',
                  texture_scale=(15, 15),
                  texture='brick') """
clé_jump = Entity(model='./assets/models/clé.obj',
                  position=Vec3(3011.3547, 1036.232, 3035.4333),
                  scale=(1, 1, 1),
                  color=color.yellow,
                  rotation_x=90,
                  rotation_y=90)
lave_jump = Entity(model='plane',
                   position=(3000, 980, 3000),
                   texture='./assets/textures/lave.png',
                   scale=(1000, 1000, 1000),
                   texture_scale=(500, 500),
                   collider='box')

""" grille_portail5 = Entity(model='./assets/models/grille.obj',
                         color=color.gray,
                         position=(995.8, 986, 986),
                         rotation=portail5.rotation,
                         scale=(0.16, 0.16, 0.16),)
 """
app.run()
