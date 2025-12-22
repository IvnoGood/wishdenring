
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
#from ursina.shaders import lit_with_shadows_shader 

app = Ursina(icon="./assets/icons/app.ico", title="WishDenRing")


structure_grotte = {
    0: Entity(model='cube', scale=(5, 5, 5), position=(10, 2, 20), collider='box', texture='brick', color=color.gray, texture_scale=(10, 10)),
    1: Entity(model='cube', scale=(3.5, 1.25, 3.5), position=(10, 4.5, 20), collider='box', texture='brick', color=color.gray, texture_scale=(10, 10)),
    2: Entity(model='cube', scale=(2.5, 4, 2.5), position=(10, 2, 23), collider='box', texture='brick', color=color.gray, texture_scale=(10, 10)),
}
tp_grotte = {
    0: Entity(model='cube', scale=(2.5, 4, 2.5), position=(10, 1, 18.748), collider='box', texture='brick', color=color.black, texture_scale=(10, 10))
}
camera.clip_plane_far = 120
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
            scale=1,
            collider = 'box'
        )

        self.torso = Entity(
            parent=self,
            model='cube',
            color=color.blue,
            position=Vec3(0, 1.25, 0),
            scale=Vec3(1, 2, 1),
            collider = 'box'

        )

        self.head = Entity(
            parent=self,
            model='cube',
            texture='shrek_face.jpg',
            position=Vec3(0, 2.75, 0),
            scale=Vec3(1, 1, 1),
            collider = 'box'

        )



enemy = Enemies()

pv_enemy_boss = 25
pv_enemy_boss_max = 25

barre_de_vie_enemy = Entity(parent=enemy,
                            model='cube',
                            color=color.red,
                            position=(0, 3.85, 0),
                            scale=(2.5, 0.1, 0.1))

#log les info dans l'inventaire
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
                         roundness=.2, max_value=100, value=50, scale=(0.32, 0.04), origin=(-0.5, 21))


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
player.rotation = (0,35,0)
player.position = (10,6,0)
inv = IventaireBas()
speedFact = 4
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
            collider="mesh"
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
                if held_keys["left mouse"] and self.swinging == False:
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
        if time.time() - start_epee >= 1:
            start_epee = time.time()
            self.swinging = True
            print('swing')
            self.animate_rotation(
                Vec3(90, -20, 0),
                duration=0.5,
                curve=curve.out_quad
            )

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
    0: Entity(model='cube', color=color.green, scale=(1, 0.001, 1), position=(10, 0.5, 0)),
}


platforme = Entity(model='cube', color=color.orange, scale=(
    1, 1, 1), position=(-1, -2, -7), collider='box')


# ------ TERRAIN ------
#structSol = Entity(model='./assets/models/ile2.obj', scale=(1, 1,1), color=color.gray,collider='mesh', origin_y=0,shader=lit_with_shadows_shader)

sol = Entity(model="./assets/models/baseIle.obj", scale=(2, 1,2), texture='./assets/textures/bricks.png', collider='mesh', origin_y=0.5, texture_scale=(64, 64), double_sided=True)

#DirectionalLight(parent=scene, y=2, z=10, shadows=True, rotation=(45, -45, 45))
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
sky_image = load_texture("./assets/textures/environement/stars-at-night-sky.png")
sky = Sky(color=color.white, texture=sky_image)
boss_battle = False
if boss_battle == False:
    sky.texture = "./assets/textures/environement/stars-at-night-sky.png"

environementSounds = None
coins = 0


# ------ STRUCTURES ------

ThomasHut = Entity(model="./assets/models/hut.obj",
                   scale=(2.5, 2.5, 2.5), collider="mesh", position=(0, 0, 10), rotation=(0, 315, 0))

ThomasNpc = Entity(model="./assets/models/npc.obj", scale=(1.125, 1.125,
                                                           1.125), texture="./assets/textures/hero_baseColor.png", double_sided=True, position=Vec3(-0.61932373, 0, 13.616727), rotation=(0, 145, 0))
ThomasNpcTag = Entity(model="plane", rotation=(
    270, 0, 25), texture="./assets/textures/thomas_affichage.png", double_sided=True, position=Vec3(-0.61932373, 2.5, 13.616727),texture_scale=(1,1), scale=(2, 1, 1))

NpcThomasToolTip = Text("Appuie sur T pour discuter")
NpcThomasToolTip.disable()


AlexaHut = Entity(model="./assets/models/hut.obj",
                  scale=(2.5, 2.5, 2.5), collider="mesh", position=(13, 0, 12), rotation=(0, -315, 0))

AlexaNpc = Entity(model="./assets/models/MEDICAL_SISTER.obj", position=(16, 0, 12),
                  collider="box", scale=0.01, ignore=True, origin_y=0, texture="./assets/textures/MEDICAL_SISTER_BaseColor.png", double_sided=True, rotation=(0, -145, 0))
AlexaNpcTag = Entity(model="plane", rotation=(
    270, 0, -25), texture="./assets/textures/alexa_affichage.png", double_sided=True,  position=(16, 2.5, 12),texture_scale=(1,1), scale=(2, 1, 1))

AlexaToolTip = Text("Appuie sur T pour discuter")
AlexaToolTip.disable()


""" class ThomasGUI(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui
        )
        self.gui = Entity(
            parent=self,
            model='quad',
            scale=(1.5, 0.85),
            origin=(0, -0.09),
            position=(0, 0),
            texture='./assets/textures/guiThomas.png',
            enable=True)
         """


class ShopButton(Button):
    def __init__(self, title="Lorem Ipsum", defcolor=color.azure, cost=0, model="./assets/models/fiole.obj", color=color.white, ** kwargs):
        super().__init__(text=title, color=defcolor)

        def takemymoney():
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
            player.position = (10,2.5,0)
                            #Vec3(
                #player.position[0]+4, player.position[1], player.position[2]+2)
            pause = False
            mouse.locked = True

        self.on_click = closeGui


NpcThomasGUI = WindowPanel(
    title='Thomas - Forgeron',
    content=(
        ShopButton(title="Epée en bois - 16p", cost=16,
                   model="katana", color=color.gray),
        ShopButton(title="Epée en fer - 128p", cost=128,
                   model="katana", color=color.gray),
        ShopButton(title="Epée en or - 256p", cost=256,
                   model="katana", color=color.gold),
        ShopButton(title="Epée en améthyste - 500p", cost=500,
                   model="katana", color=color.gold),
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


# ------ NATURES ------

# Flowers
for i in range(0):
    max = 100
    pos = (randint(-max, max), 0.5, randint(-max, max))
    flower1 = Entity(
        model="plane", texture="./assets/textures/plants/rose.png", position=pos, rotation=(270, 45, 0), double_sided=True)
    flower2 = Entity(
        model="plane", texture="./assets/textures/plants/rose.png", position=pos, rotation=(270, -45, 0), double_sided=True)

for i in range(0):
    max = 100
    pos = (randint(-max, max), 0.5, randint(-max, max))
    type = randint(1, 3)
    flower1 = Entity(
        model="plane", texture=f"./assets/textures/plants/Grass_0{type}.png", position=pos, rotation=(270, 45, 0), double_sided=True)
    flower2 = Entity(
        model="plane", texture=f"./assets/textures/plants/Grass_0{type}.png", position=pos, rotation=(270, -45, 0), double_sided=True)

# ------ NATURES END ----


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
                        inventaire[key] = {"model": self.modelName, "color": self.color}
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
                     modelName="fiole")

erlenG = DroppedItem(modelEnt="./assets/models/fiole.obj",
                     pos=(6, 1.5, 7),
                     scaleEnt=0.25,
                     colorEnt=color.green,
                     modelName="fiole")

erlenP = DroppedItem(modelEnt="./assets/models/fiole.obj",
                     pos=(6, 2.5, 7),
                     scaleEnt=0.25,
                     colorEnt=color.magenta,
                     modelName="fiole") """

boss_win = False
tp_grotte_boss = Entity(model='cube', 
                scale=(2.5, 4, 2.5), 
                position=(0,0,0), 
                collider='box', texture='brick', color=color.black, texture_scale=(10, 10))
tp_grotte_boss.collider = None
tp_grotte_boss.visible = None

def degat():
    global pv_enemy_boss, pv_enemy_boss_max, delay, degatEpee, boss_win
    # print("Point 3D sous la souris :", mouse.world_point)
    calc = pv_enemy_boss - degatEpee
    if (calc <= 0):
        enemy.visible = False
        enemy.collider = None
        boss_win = True
        location = enemy.position
        coin = DroppedItem(modelEnt="./assets/models/coin.obj",
                   pos=location,
                   scaleEnt=0.125,
                   colorEnt=color.yellow,
                   modelName="coin",
                   coinValue=randint(50,75))
        enemy.position = (500,1000,900)
    else:
        pv_enemy_boss -= degatEpee
        barre_de_vie_enemy.scale = (
            2.50*(pv_enemy_boss/pv_enemy_boss_max), 0.1, 0.1)


delay = 1
start = time.time()


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
    global pv_enemy_boss, boss_win
    
        
        
    if held_keys['left mouse'] and distance(player, enemy) <= 9:
        if time.time() - start >= delay:
            start = time.time()
            degat()

    if (boss_win):
        #la partie reprise de combat ca marche pas trop prblm pv boss + tp qiu se dep
        tp_grotte_boss.visible = True
        tp_grotte_boss.position = (510,1,500)

        if distance(tp_grotte_boss, player) < 2:
            player.position = (10,5,0)
            sky.texture = "./assets/textures/environement/stars-at-night-sky.png"
            boss_battle = False
            enemy.visible = True
            pv_enemy_boss = 15
            tp_grotte_boss.collider = None
            tp_grotte_boss.visible = None
            player.rotation=(0,0,0)
    direction_x = player.x - enemy.x
    direction_z = player.z - enemy.z
    if enemy.hovered and distance(player, enemy) <= 9:
        enemy.color = color.gray
    else:
        enemy.color = color.white
    enemy.look_at(enemy.position + (direction_x, 0, direction_z))

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

    vitesse = speedFact * time.dt
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
        sky.texture = "./assets/textures/environement/stars-at-night-sky.png"

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
            tp_grotte_boss.collider = None
            tp_grotte_boss.visible = None
            invoke(lambda: msg.animate('alpha', 0, duration=1), delay=2)
            boss_battle = True
            boss_win = False
            enemy.position = (510,3,500)
            pv_enemy_boss=pv_enemy_boss_max
            enemy.collider= True
            enemy.visible = True
            barre_de_vie_enemy.scale=(2.5,0.1,0.1)
            sky.texture = "./assets/textures/environement/chaos.jpg"
            player.position = (500, 2, 500)
            player.rotation = (0,90,0)

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


app.run()
