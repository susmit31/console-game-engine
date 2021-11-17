from cge import *
import sys

WIDTH = int(sys.argv[1])
HEIGHT = int(sys.argv[2])

sc = Scene2D(WIDTH, HEIGHT)

def rungame(input_handler, argdict, FPS=5):
    run_input_thread(input_handler, argdict)
    while 1:
        if argdict['quitGame']:
            sc.restore_terminal()
            break
        sc.render()
        sc.gravitate()
        time.sleep(1/FPS)

def handle_input(argdict):
    while 1:
        ch = getChar()
        if ch == 'a':
            argdict['b'].move_left()
        elif ch=='d':
            argdict['b'].move_right()
        elif ch=='w':
            argdict['b'].jump()
        elif ch=='q':
            argdict['quitGame'] = True
            return

r1 = Rect(sc, (3,3), WIDTH//3, 2)
r2 = Rect(sc, (r1.max_x()-5, r1.max_y()+5), WIDTH//2, 2)
r3 = Rect(sc, (r2.max_x()-5, r2.max_y()+5), WIDTH//3, 2)
# r4 = Rect(sc, (r3.max_x()-8, r3.min_y()-6), 4, 6)
r5 = Rect(sc, (sc.width-7, sc.height-2), 4, 2)
for r in (r1, r2, r3, r5):
    sc.add_ground(r)

box = Rect(sc, (r1.min_x() + 1, r1.min_y() -2), 2, 2, 'cyan')
# box = Rect(sc, (15, sc.height-3), 2, 2, 'cyan')
sc.add_sprite(box)
box.toggle_gravity()

rungame(handle_input, {'b':box, 'quitGame': False}, FPS=32)