import sys, random, os
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
from pygame import *
from pymunk import Vec2d
from math import sqrt

collisiontype_default = 0
COLLTYPE_MOUSE = 1

try:
    main_dir = os.path.dirname(os.path.abspath(__file__))
except:
    main_dir = os.getcwd()
data_dir = os.path.join(main_dir, 'data')

"""From Chimp example"""
def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound

""" Taken from joints pymunk demo, and altered slightly
        to allow different sizes and position"""
def add_ball(space, radius, x, y):
    mass = 1
    inertia = pymunk.moment_for_circle(mass, 0, radius) # 1
    body = pymunk.Body(mass, inertia) # 2
    body.position = to_pygame2(x,y) # 3
    shape = pymunk.Circle(body, radius) # 4
    shape.friction = 1.0
    shape.elasticity = 0.5
    space.add(body, shape) # 5
    return shape

""" Creates a rectangle of width and height at position x,y"""
def add_box(space, width, height, x, y):
    mass = 1
    size = width
    size2 = height
    pos = to_pygame2(x,y)
    box_points = map(Vec2d, [(-size, -size2), (-size, size2), (size,size2), (size, -size2)])
    shape = create_poly(box_points, space, mass = mass, pos = pos)
    shape.elasticity = 0.5
    return shape

""" Creates a triangle of size "size" at position x,y"""
def add_triangle(space, size, x, y):
    mass = 20
    pos = to_pygame2(x,y)
    points = map(Vec2d, [(-size/2, -size), (size, size/2), (-size, size)])
    shape = create_poly(points, space, mass = mass, pos = pos)
    return shape

""" Creating the body for triangles/rectangles """
def create_poly(points, space, mass = 5.0, pos = (0,0)):
    moment = pymunk.moment_for_poly(mass,points, Vec2d(0,0))    
    body = pymunk.Body(mass, moment)
    body.position = Vec2d(pos)
    shape = pymunk.Poly(body, points, Vec2d(0,0))
    shape.collision_type = collisiontype_default
    shape.friction = 1.0
    shape.elasticity = 0.5
    space.add(body, shape)
    return shape

""" Draw the ball to the screen. Taken from joints example"""
def draw_ball(screen, ball):
    p = int(ball.body.position.x), 600-int(ball.body.position.y)
    pygame.draw.circle(screen, THECOLORS["blue"], p, int(ball.radius), 2)

""" Draws poly's to the screen (triangles/rectangles) """
def draw_poly(screen, poly, color):
    body = poly.body
    ps = poly.get_points()
    ps.append(ps[0])
    ps = map(to_pygame, ps)
    pygame.draw.aalines(screen, color, False, ps, 5)

""" Make a static line that can't be moved starting at x1,y1 to x2,y2 """
def line(space, x1, y1, x2, y2):
    body = pymunk.Body(pymunk.inf, pymunk.inf)
    body.position = (0,0)
    body.friction = 1.0
    a = (x1, y1)
    b = (x2, y2)
    l = pymunk.Segment(body, a, b, 2.0)
    space.add_static(l)
    l.friction = 1.0
    l.elasticity = .9
    return l

""" Draw line to the screen """
def draw_line(screen, line):
    pygame.draw.aaline(screen, THECOLORS["black"], to_pygame(line.a), to_pygame(line.b), 5.0)

"""'Small hack to convert pymunk to pygame coordinates' -- From pymunk example"""
def to_pygame(p):
    return int(p.x), int(-p.y+600)

"""My version of to_pygame that takes 2 seperate values"""
def to_pygame2(x,y):
    return int(x), int(-y+600)

""" Calculates distance between two points """
def distance(point1, point2):
    x1,y1 = point1
    x2,y2 = point2

    return sqrt((x1-x2)**2+(y1-y2)**2)

""" Clear the lists for moving onto the next level """
def clear_lists(space, balls, boxes, triangles, lines, finishball):
    x = len(balls)
    for n in range(x-1, -1, -1):
        space.remove(balls[n], balls[n].body)
        balls.pop()
    x = len(finishball)
    for n in range(x-1, -1, -1):
        space.remove(finishball[n], finishball[n].body)
        finishball.pop()
    x = len(boxes)
    for n in range(x-1, -1, -1):
        space.remove(boxes[n], boxes[n].body)
        boxes.pop()
    x = len(triangles)
    for n in range(x-1, -1, -1):
        space.remove(triangles[n], triangles[n].body)
        triangles.pop()
    x = len(lines)
    for n in range(x-1, -1, -1):
        space.remove_static(lines[n])
        lines.pop()

""" Parse the txt file and build the level accordingly """
def load_level(level, space, balls, boxes, triangles, lines, finishball, t):
    # Check if playing the levels, or SandBox mode
    if t:
        test = os.path.join(data_dir, 'level' + str(level) + '.txt')
    else:
        test = os.path.join(data_dir, 'sandbox.txt')
    f = open(test)
    incoming = f.readlines()
    i = len(incoming)
    cur = 0
    while not (cur == i):
        if incoming[cur] == '#new line\n':
            x1 = int(incoming[cur+1])
            y1 = int(incoming[cur+2])
            x2 = int(incoming[cur+3])
            y2 = int(incoming[cur+4])
            cur += 4
            l = line(space, x1, y1, x2, y2)
            lines.append(l)
        if incoming[cur] == '#new triangle\n':
            size = int(incoming[cur+1])
            x = int(incoming[cur+2])
            y = int(incoming[cur+3])
            tri = add_triangle(space, size, x, y)
            triangles.append(tri)
            cur += 3
        if incoming[cur] == '#new rect\n':
            width = int(incoming[cur+1])
            height = int(incoming[cur+2])
            x = int(incoming[cur+3])
            y = int(incoming[cur+4])
            rect = add_box(space, width, height, x, y)
            boxes.append(rect)
            cur += 4
        if incoming[cur] == '#new ball\n':
            radius = int(incoming[cur+1])
            x = int(incoming[cur+2])
            y = int(incoming[cur+3])
            ball = add_ball(space, radius, x, y)
            balls.append(ball)
            cur += 3
        if incoming[cur] == '#finish ball\n':
            radius = 20
            x = int(incoming[cur+1])
            y = int(incoming[cur+2])
            ball = add_ball(space, radius, x, y)
            finishball.append(ball)
            cur += 2
        if incoming[cur] == '#finish\n':
            xfin = int(incoming[cur+1])
            yfin = int(incoming[cur+2])
            cur += 2
        else:
            cur += 1
    return int(xfin), int(yfin)

""" Start of the SandBox portion of the game """
def sandbox():

    # Variables that need to be initialized
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True
    pygame.key.set_repeat(400, 10)
    mouse_old = to_pygame2(0,0)
    mouse_new = to_pygame2(0,0)
    pymunk.init_pymunk()
    space = pymunk.Space()
    gravity_x = 0.0
    gravity_y = -400.0
    space.gravity = (0.0, -400.0)
    run_physics = True
    current_level = 1
    width = 20
    height = 20
    font = pygame.font.Font(None, 16)

    # Lists to keep track of all objects 
    balls = []
    balls_remove = []
    boxes = []
    boxes_remove = []
    triangles = []
    tri_remove = []
    lines = []
    outer_lines = []
    finishball = []

    # Keeps track of making new lines with mouse
    second = False

    """ Music by calpomatt (Author's name not given)
        Song name: Searching For Truth - Solo
        Downloaded from: http://www.flashkit.com/loops/Ambient/Ambient/SFT-calpomat-4638/index.php"""
    music = load_sound("sandbox.wav")
    music.play(-1)

    #Outer lines must be different than regular lines,
    # otherwise they can be deleted
    l = line(space, 0, 0, 800, 0)
    outer_lines.append(l)
    l = line(space, 0, 0, 0, 600)
    outer_lines.append(l)
    l = line(space, 0, 600, 800, 600)
    outer_lines.append(l)
    l = line(space, 800, 600, 800, 0)
    outer_lines.append(l)

    
    finish = load_level(1, space, balls, boxes, triangles, lines, finishball, False)
    
    # Start the main running loop
    while running:
        # Keep track of mouse vector for adding impulse to objects
        mouse_old = mouse_new
        xx,yy = pygame.mouse.get_pos()
        mouse_new = to_pygame2(xx, yy)
        pygame.display.set_caption("Welcome to the Sandbox! Have fun!")

        # Get keyboard and mouse comands
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                pygame.quit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == KEYDOWN and event.key == K_SPACE:
                run_physics = not run_physics
            elif event.type == KEYDOWN:
                if event.key == K_b:
                    ball = add_ball(space, width, xx, yy)
                    balls.append(ball)
                if event.key == K_r:
                    rect = add_box(space, width, height, xx, yy)
                    boxes.append(rect)
                if event.key == K_t:
                    tri = add_triangle(space, width, xx, yy)
                    triangles.append(tri)
                if event.key == K_UP:
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        height += 1
                    else:
                        gravity_y += 1
                        space.gravity = (gravity_x, gravity_y)
                if event.key == K_DOWN:
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        if height > 5:
                            height -= 1
                    else:
                        gravity_y -= 1
                        space.gravity = (gravity_x, gravity_y)
                if event.key == K_LEFT:
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        if width > 5:
                            width -= 1
                    else:
                        gravity_x -= 1
                        space.gravity = (gravity_x, gravity_y)
                if event.key == K_RIGHT:
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        width += 1
                    else:
                        gravity_x += 1
                        space.gravity = (gravity_x, gravity_y)
                if event.key == K_DELETE or event.key == K_d:
                    if pygame.key.get_mods() & KMOD_SHIFT:
                            width = 20
                            height = 20
                            gravity_x = 0.0
                            gravity_y = -400.0
                            space.gravity = (0.0, -400.0)
                    else:
                        fake_lines = []
                        clear_lists(space, balls, boxes, triangles, fake_lines, finishball)
            elif event.type == KEYDOWN and event.key == K_c:
                for box in boxes:
                    boxes.remove(box)
                    num_shapes -= 1
                for ball in balls_remove:
                    space.remove(ball, ball.body)
                    balls.remove(ball)
                    num_shapes -= 1
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if pygame.key.get_mods() & KMOD_SHIFT:
                    if not second:
                        x1,y1 = pygame.mouse.get_pos()
                        x1,y1 = to_pygame2(x1,y1)
                        second = True
                    else:
                        x2,y2 = pygame.mouse.get_pos()
                        x2,y2 = to_pygame2(x2,y2)
                        l = line(space, x1, y1, x2, y2)
                        lines.append(l)
                        second = False

        # Check if mouse is in an object, and if released after being picked up,
        #  apply a force in the mouse vector direction
        if pygame.mouse.get_pressed() [0]:
            t,y = pygame.mouse.get_pos()
            x = to_pygame2(t,y)
            test = (Vec2d(mouse_new)-Vec2d(mouse_old))
            for ball in balls:
                if ball.point_query(x):
                    none = False
                    ball.body.position = x
                    ball.body.velocity = Vec2d(0,0)
                    ball.body.apply_impulse(40*test)
            for ball in finishball:
                if ball.point_query(x):
                    none = False
                    ball.body.position = x
                    ball.body.velocity = Vec2d(0,0)
                    ball.body.apply_impulse(40*test)
            for box in boxes:
                if box.point_query(x):
                    none = False
                    box.body.position = x
                    box.body.velocity = Vec2d(0,0)
                    box.body.apply_impulse(40*test)
            for tri in triangles:
                if tri.point_query(x):
                    none = False
                    xx, yy = x
                    tri.body.position = (xx, yy-4)
                    tri.body.velocity = Vec2d(0,0)
                    tri.body.apply_impulse(100*test)

        # Delete items by right-clicking on them
        if pygame.mouse.get_pressed() [2]:
            x,y = pygame.mouse.get_pos()
            x = to_pygame2(x,y)
            test = (Vec2d(mouse_new)-Vec2d(mouse_old))
            for ball in balls:
                if ball.point_query(x):
                    space.remove(ball, ball.body)
                    balls.remove(ball)
            for box in boxes:
                if box.point_query(x):
                    space.remove(box, box.body)
                    boxes.remove(box)
            for tri in triangles:
                if tri.point_query(x):
                    space.remove(tri, tri.body)
                    triangles.remove(tri)
            for l_line in lines:
                if l_line.point_query(x):
                    space.remove_static(l_line)
                    lines.remove(l_line)

        screen.fill(THECOLORS["white"])


        # Draw objects to the screen
        for ball in balls:
            if ball.body.position.y < -100:
                balls_remove.append(ball)
            else:
                draw_ball(screen, ball)

        for box in boxes:
            if box.body.position.y < -100:
                boxes_remove.append(box)
            else:
                draw_poly(screen, box, THECOLORS["red"])

        for tri in triangles:
            draw_poly(screen, tri, THECOLORS["green"])

        for l in lines:
            draw_line(screen, l)

        # Draw the help text in the upper left
        text_left = ["LMB: Grab object"
                    ,"Shift + LMB: Click twice for new line"
                    ,"RMB: Delete object"
                    ,"Space: Change speed to slowmo"
                    ,"B,R,T: Spawn ball, rect, triangle"
                    ,"Del or D: Delete all objects from space (add shift to reset variables)"
                    ,"Up/Down arrow: Change Y gravity]"
                    ,"Left/Right arrow: Change X gravity"
                    ,"Shift + Up/Down arrow: Change height"
                    ,"Shift + Left/Right arrow: Change radius/width"
                    ,"ESC: Return to main menu"]

        y = 5
        for t_line in text_left:
            text = font.render(t_line, 20, THECOLORS["black"])
            screen.blit(text, (5,y))
            y += 10
            
        # Draw the variables in the uppper right
        text_right = ["Gravity: " + str(gravity_x) + "," + str(gravity_y)
                      ,"Radius/Width = " + str(width)
                      ,"Height = " + str(height)]

        y = 5
        for t_line in text_right:
            text = font.render(t_line, 5, THECOLORS["black"])
            screen.blit(text, (650,y))
            y += 10
        
        
        if run_physics:
            space.step(1/60.0) # regular speed           
        else:
            space.step(1/480.0) # slow motion

        clock.tick(60)
        pygame.display.flip()
    music.fadeout(1000)

# Start the levels part of the game
def main():
    # Variables that need initializing
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True
    pygame.key.set_repeat()
    mouse_old = to_pygame2(0,0)
    mouse_new = to_pygame2(0,0)
    pymunk.init_pymunk() #2
    space = pymunk.Space() #3
    space.gravity = (0.0, -400.0)
    run_physics = True
    current_level = 1
    windistance = 5
    max_level = 9
    font = pygame.font.Font(None, 40)
    time = 0
    tick_time = 0
    score = 0

    """ Music by calpomatt (Author's name not given)
        Song name: Searching For Truth
        Downloaded from: http://www.flashkit.com/loops/Ambient/Ambient/Searc-calpomat-4394/index.php"""
    music = load_sound("game.wav")
    music.play(-1)

    # Lists for objects
    balls = []
    boxes = []
    triangles = []
    lines = []
    finishball = []

    # Start the first level
    finish = load_level(1, space, balls, boxes, triangles, lines, finishball, True)

    # Start main running loop
    while running:
        # Mouse vector
        mouse_old = mouse_new
        xx,yy = pygame.mouse.get_pos()
        mouse_new = to_pygame2(xx, yy)
        pygame.display.set_caption("Level " + str(current_level))
        # Capturing mouse and keyboard events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                pygame.quit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == KEYDOWN and event.key == K_SPACE:
                run_physics = not run_physics
                if score > 0:
                    score -= 50
            elif event.type == KEYDOWN and event.key == K_PAGEUP:
                if current_level < max_level:
                    time_tick = 0
                    time = 0
                    current_level += 1
                    clear_lists(space, balls, boxes, triangles, lines, finishball)
                    finish = load_level(current_level, space, balls, boxes, triangles, lines, finishball, True)
            elif event.type == KEYDOWN and event.key == K_PAGEDOWN:
                if current_level > 1:
                    time_tick = 0
                    time = 0
                    current_level -= 1
                    clear_lists(space, balls, boxes, triangles, lines, finishball)
                    finish = load_level(current_level, space, balls, boxes, triangles, lines, finishball, True)
            elif event.type == KEYDOWN and event.key == K_d:
                clear_lists(space, balls, boxes, triangles, lines, finishball)
                finish = load_level(current_level, space, balls, boxes, triangles, lines, finishball, True)
            elif event.type == KEYDOWN and event.key == K_c:
                for box in boxes:
                    boxes.remove(box)
                    num_shapes -= 1
                for ball in balls_remove:
                    space.remove(ball, ball.body)
                    balls.remove(ball)
                    num_shapes -= 1

        # Check if mouse is in an object, and if released after being picked up,
        #  apply a force in the mouse vector direction
        if pygame.mouse.get_pressed() [0]:
            x,y = pygame.mouse.get_pos()
            x = to_pygame2(x,y)
            test = (Vec2d(mouse_new)-Vec2d(mouse_old))
            for ball in balls:
                if ball.point_query(x):
                    ball.body.position = x
                    ball.body.velocity = Vec2d(0,0)
                    ball.body.apply_impulse(40*test)
            for ball in finishball:
                if ball.point_query(x):
                    win = 0
                    ball.body.position = x
                    ball.body.velocity = Vec2d(0,0)
                    ball.body.apply_impulse(40*test)
            for box in boxes:
                if box.point_query(x):
                    box.body.position = x
                    box.body.velocity = Vec2d(0,0)
                    box.body.apply_impulse(40*test)
            for tri in triangles:
                if tri.point_query(x):
                    xx, yy = x
                    tri.body.position = (xx, yy-4)
                    tri.body.velocity = Vec2d(0,0)
                    tri.body.apply_impulse(100*test)

        screen.fill(THECOLORS["white"])

        # Draw the objects to the screen
        balls_remove = []
        for ball in balls:
            if ball.body.position.y < -100:
                balls_remove.append(ball)
            else:
                draw_ball(screen, ball)

        for ball in finishball:
            pos = int(ball.body.position.x), 600-int(ball.body.position.y)
            pygame.draw.circle(screen, THECOLORS["purple"], pos, int(ball.radius), 2)
            if distance(pos, finish) <= windistance:
                win += 1
            else:
                win = 0

        boxes_remove = []
        for box in boxes:
            if box.body.position.y < -100:
                boxes_remove.append(box)
            else:
                draw_poly(screen, box, THECOLORS["red"])


        tri_remove = []
        for tri in triangles:
            if tri.body.position.y < -100:
                tri_remove.append(box)
            else:
                draw_poly(screen, tri, THECOLORS["green"])

        pygame.draw.circle(screen, THECOLORS["black"], finish,
           20, 2)

        # Remove objects from the space if they happen to get loose
        for ball in balls_remove:
            space.remove(ball, ball.body)
            balls.remove(ball)

        for box in boxes_remove:
            boxes.remove(box)

        for tri in tri_remove:
            triangles.remove(tri)
            space.remove(tri, tri.body)

        for l in lines:
            draw_line(screen, l)


        if run_physics:
            space.step(1/60.0) # regular speed         
        else:
            space.step(1/480.0) # slow motion
            
        if tick_time == 65:
            time += 1
            tick_time = 0
        else:
            tick_time += 1

        # Update timer and score
        text_right = ["Time: " + str(time) + "s"
                     ,"Score: " + str(score)]

        y = 5
        for t_line in text_right:
            text = font.render(t_line, 20, THECOLORS["black"])
            screen.blit(text, (600,y))
            y += 40

        # If the ball is successfully balanced for enough time, you win the level
        if win == 60 and run_physics:
            score += int(10000/(time+1)) # time+1 just in case time is 0
            win = 0
            time = 0
            time_tick = 0
            # progress to next level, if not max level
            if current_level < max_level:
                current_level += 1
                clear_lists(space, balls, boxes, triangles, lines, finishball)
                finish = load_level(current_level, space, balls, boxes, triangles, lines, finishball, True)
            else:
                running = False
    
        
        clock.tick(60)
        pygame.display.flip()

    music.fadeout(1000)
    return score
        
if __name__ == '__main__':
    main()
