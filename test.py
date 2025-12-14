from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar
from ursina import *


app = Ursina()

health_bar_1 = HealthBar(bar_color=color.lime.tint(-.25),
                         roundness=.5, max_value=100, value=50, scale=(.5, .1))
print(health_bar_1.text_entity.enabled, health_bar_1.text_entity.text)

FirstPersonController()


def input(key):
    if key == '+' or key == '+ hold':
        health_bar_1.value += 10
    if key == '-' or key == '- hold':
        health_bar_1.value -= 10
        print('ow')


app.run()
