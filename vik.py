
from ursina import *
from random import randint
from time import sleep
app = Ursina()

class Character(Entity):
    def __init__(self):
        super().__init__(
            model='sphere',
            color=color.red,
            position=(0, 7, 0),
            collider='box'
        )

player = Character()

checkpoints = {
    
    0:Entity(model='cube', color=color.green, scale=(1, 0.001, 1), position=(0, 0.5, 0), collider ='box' ),
    1:Entity(model='cube', color=color.green, scale=(1, 0.001, 1), position=(3, 0.5, 3), collider ='box' )
    
}


user_data = {
    "player": {
        "location": (0,0,0),
        "rotation": (0,0,0)
    }
}


platforme = Entity(model='cube', color=color.orange, scale=(1, 1, 1), position=(-1, -2, -7), collider='box')

sol = Entity(model='cube', scale=(100, 1, 100), position=(0, 0, 0), collider='box',texture='grass')

player.rotation_y = 180
vitesse_chute=0
force_gravite=-1
last_chesckpoint=player.position

camera.rotation_x = 0
camera.rotation_y = 0
sensitivity = 40

pause = False

def update():
    vitesse = 4 * time.dt
    global vitesse_chute
    global last_checkpoint
    global sensitivity
    global pause
    
    camera.parent=player
    camera.position = Vec3(0, 2, 0) 
    
    
    for i in checkpoints:
        if distance(player.position,checkpoints[i].position) <= 1.5:
            last_checkpoint = checkpoints[i]
            checkpoints[i].color= color.yellow
    
    camera.rotation_x -= mouse.delta[1] * sensitivity
    camera.rotation_y += mouse.delta[0] * sensitivity
    # Limit vertical rotation
    camera.rotation_x = clamp(camera.rotation_x, -80, 80)

    
    v1= Vec3(0,0,0) #pour assigne le vecteur du déplacement
    
    direction = Vec3(camera.forward.x, 0, camera.forward.z).normalized()
    
    if held_keys['w']:
        v1 += direction * vitesse
    if held_keys['s']:
        v1 -= direction * vitesse
    if held_keys['a']:
        v1 -= Vec3(camera.right.x, 0, camera.right.z).normalized() * vitesse
    if held_keys['d']:
        v1 += Vec3(camera.right.x, 0, camera.right.z).normalized() * vitesse
        #Déplacement sur l'axe x
    old_x = player.x # assigne la vielle coordonné x en cas de collision
    player.x += v1.x # bouge le joueur
    if player.intersects().hit: # detecte les collisions
        player.x = old_x # si il y a une collision, revenir sur l'ancienne coordoné pour ne pas passer dans le mur

    # Déplacement sur l'axe z même fonctionnement que pour l'axe x
    old_z = player.z
    player.z += v1.z
    if player.intersects().hit:
        player.z = old_z

    old_y=player.y
    vitesse_chute += force_gravite*0.1 # défini la vitesse de chute pour avoir une chute qui n'est pas constante la vitesse peut être
                                       # changé pour avoir une gravité + forte mais peut faire des bugs (passer dans le sol)
    player.y += vitesse_chute*time.dt  #fait chuter les perso
    if player.intersects().hit:
        player.y=old_y                 #revenir sur le dessus de la plateforme car il y a eu une collision
        vitesse_chute=0                #fin de la chute
        
    if held_keys['space'] and vitesse_chute==0 : #saut possible que si le perso est sur une surface plate où il ne chute pas
        vitesse_chute=6                # met une vitesse de chute positive pour que le joueur "tombe" vers le haut puis il chute avec la
                                       # gravité
    if player.y <= -25:
        player.position = (last_checkpoint.x, last_checkpoint.y +2, last_checkpoint.z)

    if held_keys['e']:
        pause = True
        print("pause")
        mouse.locked = False
        mouse.visible = True

        
    if held_keys['r']==True:
        pause = False
    #pour la chute
    if pause == False:
        mouse.locked = True
        mouse.visible = False
    

    direction = Vec3(0, 0, 0).normalized()


app.run()