from cge import *
import sys

WIDTH = int(sys.argv[1])
HEIGHT = int(sys.argv[2])

sc = Scene2D(WIDTH, HEIGHT)

def rungame(input_handler, argdict, FPS=10):
    run_input_thread(input_handler, argdict)
    while 1:
        if argdict['quitGame']:
            break
        sc.render()
        sc.gravitate()
        b.update()
        time.sleep(1/FPS)

def handle_input(argdict):
    while 1:
        ch = getChar()
        if ch == 'a':
            argdict['b'].translate(-1,0)
        elif ch=='d':
            argdict['b'].translate(1,0)
        elif ch=='q':
            argdict['quitGame'] = True
            return

r1 = Rect(sc, (3,3), 10, 2)
r2 = Rect(sc, (r1.max_x()-3, r1.max_y()+5), 14, 2)
r3 = Rect(sc, (r2.max_x()-3, r2.max_y()+5), 10, 2)
for r in (r1, r2, r3):
    sc.add_ground(r)

box = Rect(sc, (r1.min_x() + 2, r1.min_y() -2), 2, 2, 'cyan')
sc.add_sprite(box)
box.toggle_gravity()

rungame(handle_input, {'b':box, 'quitGame': False}, FPS=32)