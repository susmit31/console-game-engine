##################################################
##################################################
# Package for turning the console into a canvas #
# / Console Game Engine #
##################################################
##################################################

##################################################
# Imports #
##################################################
import sys
import math
import threading
from colorain import *

##################################################
# Block Elements #
##################################################
BLOCK_FULL = chr(9608)
BLOCK_THREEQTR = chr(9619)
BLOCK_HALF = chr(9618)
BLOCK_QTR = chr(9617)

BLOCKS = [BLOCK_FULL, BLOCK_THREEQTR, BLOCK_HALF, BLOCK_QTR]

##################################################
# Move the cursor relative to current position #
##################################################
def move_cursor(line, col):
    base = "\033["

    linedir = "A" if line < 0 else "B"
    coldir = "C" if col > 0 else "D"
    
    linecode = f"{base}{abs(line)}{linedir}"
    colcode = f"{base}{abs(col)}{coldir}"
    sys.stdout.write(linecode)
    sys.stdout.write(colcode) 


##################################################
# Get a one-character input w/o echoing #
##################################################
def getChar():
    try:
        # for Windows-based systems
        import msvcrt # If successful, we are on Windows
        return msvcrt.getch()

    except ImportError:
        # for POSIX-based systems (with termios & tty support)
        import tty, termios  # raises ImportError if unsupported

        fd = sys.stdin.fileno()
        oldSettings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            answer = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)

        return answer

def run_input_thread(handle_input, argdict):
    inp_thread = threading.Thread(target = handle_input, args = (argdict,))
    inp_thread.start()

##################################################
# 2D coordinates and vectors #
##################################################
class Coord2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"{(self.x, self.y)}"
    
    def __add__(self, coord):
        return Coord2D(self.x + coord.x, self.y + coord.y)

    def __sub__(self, coord):
        return Coord2D(self.x - coord.x, self.y - coord.y)
    
    def __eq__(self, coord):
        return self.x == coord.x and self.y == coord.y
    
    def dot(self, coord):
        return self.x*coord.x + self.y*coord.y

    def rotate(self, angle, reference):
        rotn_mat = [Coord2D(math.cos(angle), -math.sin(angle)), \
            Coord2D(math.sin(angle), math.cos(angle))]
        newpt = Coord2D(rotn_mat[0].dot(self - reference), rotn_mat[1].dot(self - reference))
        self.x = newpt.x + reference.x
        self.y = newpt.y + reference.y

class Vector2D:
    def __init__(self, end):
        if isinstance(end, tuple):
            end = Coord2D(*end)
        self.end = end
        self.x = self.end.x
        self.y = self.end.y

    def __repr__(self):
        return f"{self.x}i + {self.y}j"
    
    def __add__(self, vector):
        sum_end = self.end + Coord2D(vector.x, vector.y)
        return Vector2D(sum_end)

    def dot(self, vector):
        return self.x*vector.x + self.y*vector.y

    def length(self):
        sqr_len = self.dot(self)
        print(f"{chr(int('221a',16))}{sqr_len}")
        return   math.sqrt(sqr_len)

    def rotate(self, angle):
        return Vector2D(self.start.rotate(angle), self.end.rotate(angle))

##################################################
# 2D scene (i.e., 2D canvas) #
##################################################
class Scene2D:
    def __init__(self, width, height, colour = None, sprites = None):
        self.width = width
        self.height = height
        self.scene = [[BLOCKS[0]][:]*2*self.width for i in range(self.height)]
        self.sprites = []
        self.grounds = []
    
    def render(self, reset=True):
        sys.stdout.write('\n'.join([''.join(ln) for ln in self.scene]))
        if reset:
            move_cursor(-self.height+1, -2*self.width)
        else: print()

    def edit_pixel(self, pixel_loc, newval):
        if isinstance(pixel_loc, Coord2D):
            x, y = pixel_loc.x, pixel_loc.y
        elif isinstance(pixel_loc, tuple):
            x, y = pixel_loc[0], pixel_loc[1]
        if y > self.height -1:
            y %= (self.height-1)
        x, y = math.floor(x), math.floor(y)
        self.scene[y][2*x] = newval
        self.scene[y][2*x+1] = newval
    
    def reset_pixel(self, pixel_loc):
        if isinstance(pixel_loc, tuple):
            pixel_loc = Coord2D(pixel_loc[0], pixel_loc[1])
        self.edit_pixel(pixel_loc, BLOCKS[0])
    
    def clear(self):
        for y in range(self.height):
            for x in range(self.width):
                self.reset_pixel((x,y))
    
    def restore_terminal(self):
        for y in range(self.height):
            for x in range(self.width):
                self.edit_pixel((x,y), ' ')
        self.render()

    def paint_pixel(self, pixel_loc, colour):
        if isinstance(pixel_loc, tuple):
            pixel_loc = Coord2D(pixel_loc[0], pixel_loc[1])
        self.edit_pixel(pixel_loc, Stx(f"<{fgtokens[colour]}>{BLOCKS[0]}</>").parsed)
    
    def add_sprite(self, sprite):
        self.sprites.append(sprite)
    
    def add_ground(self, ground):
        self.grounds.append(ground)
    
    def gravitate_and_collide(self):
        for sprite in self.sprites:
            on_ground = False
            sprite.lock['left'] = False
            sprite.lock['right'] = False
            min_y_dist = float('inf')
            closest_ground = None
            for ground in self.grounds:
                bouncy = 0
                coll_dir = sprite.detect_collision(ground)
                if coll_dir:
                    on_ground = coll_dir == 'bottom'
                    sideways_collision = coll_dir in ['left', 'right']
                    if on_ground or coll_dir=='top':
                        reflected_velocity = Vector2D((0, -sprite.velocity.y/10 if bouncy else 0))
                        sprite.velocity = reflected_velocity
                    elif sideways_collision: 
                        sprite.lock[coll_dir] = True
                        sprite.velocity = Vector2D((0,0))
                    break
                else:
                    y_dist = ground.min_y()-sprite.max_y()
                    x_overlap = ground.min_x() < sprite.max_x() <= ground.max_x() or\
                        sprite.min_x() < ground.max_x() <= sprite.max_x()
                    if 0 < y_dist < min_y_dist:
                        if x_overlap:
                            closest_ground = ground
                            min_y_dist = y_dist
            if not on_ground:
                if min_y_dist < sprite.velocity.y:
                    sprite.velocity = Vector2D((0, min_y_dist))
                elif sprite.velocity.y + sprite.max_y() < self.height:
                    sprite.velocity += Vector2D((0,1))       
                else:
                    sprite.velocity = Vector2D((0,self.height - sprite.max_y()))
            if sprite.max_x() == self.width:
                sprite.lock['right'] = True
            elif sprite.min_x() == 0:
                sprite.lock['left'] = True
            sprite.update()


##################################################
# Sprites #
##################################################
class Sprite:
    def __init__(self, scene, positions, gravity = False, rigid = True, color='red'):
        self.scene = scene
        self.positions = positions
        self.velocity = Vector2D((0,0))
        self.gravity = gravity
        self.rigid = rigid
        self.color = color
        self.lock = {'left':False, 'right':False, 'top': False, 'bottom': False}
        self.draw(self.color)

    def draw(self, color=None):
        if color is None:
            color = self.color
        for pos in self.positions:
            self.scene.paint_pixel(pos, color)
    
    def erase(self):
        for pos in self.positions:
            self.scene.reset_pixel(pos)

    def translate(self, x, y):
        self.erase()
        for pos in self.positions:
            pos.x += x
            pos.y += y
        self.draw()
    
    def rotate(self, angle, reference):
        self.erase()
        for pos in self.positions:
            pos.rotate(angle, reference)
            pos.x = math.floor(pos.x)
            pos.y = math.floor(pos.y)
        self.draw()
    
    def jump(self):
        if self.velocity.y == 0:
            self.velocity += Vector2D((0,-2))
            self.update()
    
    def move_right(self):
        if not self.lock['right']:
            prev_y_velocity = self.velocity.y
            self.velocity += Vector2D((1,-prev_y_velocity))
            self.update()
            self.velocity += Vector2D((-1,prev_y_velocity))
    
    def move_left(self):
        if not self.lock['left']:
            prev_y_velocity = self.velocity.y
            self.velocity += Vector2D((-1,-prev_y_velocity))
            self.update()
            self.velocity += Vector2D((1,prev_y_velocity))
    
    def toggle_gravity(self):
        self.gravity = not self.gravity

    def update(self):
        self.erase()
        for pos in self.positions:
            pos.y += self.velocity.y
            pos.x += self.velocity.x
        self.draw()
    
    def detect_collision(self, obj):
        if self.rigid:
            obj_min_x = obj.min_x()
            obj_max_x = obj.max_x()
            obj_min_y = obj.min_y()
            obj_max_y = obj.max_y()
            if self.max_x() == obj_min_x:
                if obj_min_y < self.max_y() <= obj_max_y:
                    return 'right'
                elif self.min_y() <= obj_max_y <= self.max_y():
                    return 'right'
            elif self.min_x() == obj_max_x:
                if obj_min_y < self.max_y() <= obj_max_y:
                    return 'left'
                elif self.min_y() <= obj_max_y <= self.max_y():
                    return 'left'
            elif self.max_y() == obj_min_y:
                if obj_min_x < self.max_x() <= obj_max_x:
                    return 'bottom'
                elif self.min_x() <= obj_max_x <= self.max_x():
                    return 'bottom'
            elif self.min_y() == obj_max_y:
                if obj_min_x < self.max_x() <= obj_max_x:
                    return 'top'
                elif self.min_x() < obj_max_x <= self.max_x():
                    return 'top'
            else:
                return False
        return False

    def max_x(self):
        return max([pos.x for pos in self.positions])+1

    def min_x(self):
        return min([pos.x for pos in self.positions])
    
    def max_y(self):
        return max([pos.y for pos in self.positions])+1
    
    def min_y(self):
        return min([pos.y for pos in self.positions])

    def width(self):
        min_x = self.min_x()
        max_x = self.max_x()
        return max_x - min_x
    
    def height(self):
        min_y = self.min_y()
        max_y = self.max_y()
        return max_y - min_y


##################################################
# Rectangular sprites #
##################################################
class Rect(Sprite):
    def __init__(self, scene, topleft, width, height, color='red'):
        positions = []
        if isinstance(topleft, tuple):
            topleft = Coord2D(* topleft)
        for i in range(width):
            for j in range(height):
                positions.append(topleft + Coord2D(i,j))
        super().__init__(scene, positions, color=color)
    
    def rotate(self, angle, reference = None):
        if reference is None:
            reference = self.positions[0]
        super().rotate(angle, reference)