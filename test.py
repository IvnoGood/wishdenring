from ursina import *
from ursina import Ursina, dedent, window
app = Ursina()
descr = dedent('''
      <red>Rainstorm<default> <red>Rainstorm<default>
      Summon a rain storm to deal 5 <blue>water<default> damage to everyone, test including yourself.
      1234 1234 1234 1234 1234 1234 2134 1234 1234 1234 1234 1234 2134 2134 1234 1234 1234 1234
      Lasts for 4 rounds.''').strip()

Text.default_resolution = 1080 * Text.size
test = Text(text=descr, wordwrap=30)

test.background = color.black


def input(key):
    if key == 'a':
        print('a')
        test.text = '<default><image:file_icon> <red><image:file_icon> test '
        print('by', test.text)
    if key == 'c':
        test.text = ''
window.fps_counter.enabled = False
print('....', Text.get_width('yolo'))
app.run()

