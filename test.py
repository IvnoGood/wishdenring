import PIL.Image
from ursina.shaders import ssao_shader
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *
from perlin_noise import PerlinNoise
# from time import time

app = Ursina(title="Snake 3D", fullscreen=False)

""" moutains = Terrain(heightmap='./assets/map/heightmap.png', skip=10)

terrain = Entity(model=moutains, scale=(10, 2, 10),
                 texture="./assets/map/colormap.png", collider="mesh") """

""" 
noise = PerlinNoise(octaves=3, seed=0)
amp = 3
freq = 24
width = 10


# Source - https://stackoverflow.com/questions/70467860/need-help-in-perline-noise-ursina-to-make-an-a-plain-land
# Posted by Jan Wilamowski
# Retrieved 2025-12-06, License - CC BY-SA 4.0
start = time()
level_parent = Entity(model=Mesh(vertices=[], uvs=[]),
                      color=color.white, texture='./assets/textures/grass.png', texture_scale=(1, 1))

for x in range(1, width):
    for z in range(1, width):
        # add two triangles for each new point
        y00 = noise([x/freq, z/freq]) * amp
        y10 = noise([(x-1)/freq, z/freq]) * amp
        y11 = noise([(x-1)/freq, (z-1)/freq]) * amp
        y01 = noise([x/freq, (z-1)/freq]) * amp
        level_parent.model.vertices += (
            # first triangle
            (x, y00, z),
            (x-1, y10, z),
            (x-1, y11, z-1),
            # second triangle
            (x, y00, z),
            (x-1, y11, z-1),
            (x, y01, z-1)
        )

level_parent.model.generate()
level_parent.model.project_uvs()  # for texture
level_parent.model.generate_normals()  # for lighting
level_parent.collider = 'mesh'  # for collision

end = time()

print("took", end-start, "seconds to generate terrain")

app = Ursina()


player = Entity(model='sphere', color=color.azure, scale=.2, origin_y=-.5)


hv = level_parent.model.height_values


def update():
    direction = Vec3(held_keys['d'] - held_keys['a'],
                     0, held_keys['w'] - held_keys['s']).normalized()
    player.position += direction * time.dt * 4
    y = terraincast(player.world_position, level_parent, hv)
    if y is not None:
        player.y = y


EditorCamera()
camera.shader = ssao_shader
Sky()

app.run()
 """


class HeightmapTerrain(Entity):
    def __init__(self, path, scale=1, height=20, **kwargs):
        super().__init__(**kwargs)

        img = PIL.Image.open(path).convert('L')  # grayscale
        w, h = img.size

        # convert to array of [0..1]
        pixels = img.load()

        vertices = []
        triangles = []
        uvs = []

        for z in range(h):
            for x in range(w):
                y = pixels[x, z] / 255 * height   # NORMALIZED ✔
                vertices.append(Vec3(x*scale, y, z*scale))
                uvs.append((x / w, z / h))

        for z in range(h-1):
            for x in range(w-1):
                i = z*w + x
                triangles.extend([
                    i, i+1, i+w,
                    i+1, i+w+1, i+w
                ])

        self.model = Mesh(vertices=vertices,
                          triangles=triangles, uvs=uvs, mode='triangle')
        self.texture = Texture(path)
        self.collider = 'mesh'


terrain_entity = HeightmapTerrain(
    "./assets/map/heightmap.png", scale=1, height=15)
terrain_entity.double_sided = False

player = Entity(model='sphere', color=color.azure, scale=.2, origin_y=-.5)


hv = terrain_entity.model.height_values


def update():
    direction = Vec3(held_keys['d'] - held_keys['a'],
                     0, held_keys['w'] - held_keys['s']).normalized()
    player.position += direction * time.dt * 4
    y = terraincast(player.world_position, terrain_entity, hv)
    if y is not None:
        player.y = y


camera.shader = ssao_shader
Sky()
FirstPersonController()
app.run()
