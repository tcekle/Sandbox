import sandbox
import sys, random, os
import pygame
from pygame import *
from pygame.locals import *
from pygame.color import *
from pygame.compat import geterror
import pymunk

"""From moodle"""
try:
    main_dir = os.path.dirname(os.path.abspath(__file__))
except:
    main_dir = os.getcwd()
data_dir = os.path.join(main_dir, 'data')

"""From chimp example"""
def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    return image

""" Main function that runs the main menu of the game """
def main():

    # Variables that need to be initialized
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    clock = pygame.time.Clock()
    running = True
    selection = 1
    background_play = load_image("play.png")
    background_sandbox = load_image("sandbox.png")
    background_help = load_image("help.png")
    background_quit = load_image("quit.png")
    screen.blit(background_play, (0, 0))
    pymunk.init_pymunk()
    space = pymunk.Space()
    space.gravity = (0.0, -400.0)
    next_shape = 0
    display_help = False
    winner = False
    cur_help = 0
    score = 0
    font = pygame.font.Font(None, 60)

    """ Music by Rudy Vessup
        Song name : .:: jUsT dO it::.
        Downloaded from: http://www.flashkit.com/loops/Sales/Techno_breed/_jUsT-Rudy_Ves-8003/index.php"""
    music = sandbox.load_sound("main_menu.wav")
    music.play(-1)

    # Keep track of balls, triangles and boxes
    balls = []
    triangles = []
    boxes = []

    # Load the main menu help pictures
    help_menu = []
    for n in range(1, 9):
        img = load_image("help" + str(n) + ".png")
        help_menu.append(img)

    congrats = load_image("congrats.png")

    # Lines that correspond to the main menu for objects colliding with words
    sandbox.line(space, 193, 415, 337, 415)
    sandbox.line(space, 270, 320, 528, 320)
    sandbox.line(space, 442, 134, 582, 134)

    # Start the running loop
    while running:
        screen.fill(THECOLORS["white"])
        pygame.display.set_caption("Welcome to SandBox!")

        # Capture events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_UP:
                    selection -= 1
                if event.key == K_DOWN:
                    selection += 1
                if event.key == K_RIGHT:
                    if display_help:
                        cur_help += 1
                if event.key == K_LEFT:
                    if display_help:
                        cur_help -= 1
                    
            # Click or hit enter on selection to start it    
            if event.type == MOUSEBUTTONDOWN and  event.button == 1 or event.type == KEYDOWN and event.key == K_RETURN:
                if not display_help:
                    if not winner:
                        if selection == 1:
                            music.fadeout(1000)
                            score = sandbox.main()
                            winner = True
                            music.play(-1)
                        elif selection == 2:
                            music.fadeout(1000)
                            sandbox.sandbox()
                            music.play(-1)
                        elif selection == 3:
                            display_help = True
                        elif selection == 4:
                            running = False
                    else:
                        # Close score screen
                        winner = False
                        score = 0
            # Progress through the help menu
            if event.type == MOUSEBUTTONDOWN and  event.button == 1:
                if display_help:
                    x,y = pygame.mouse.get_pos()
                    if x > 115 and x < 180 and y > 465 and y < 500:
                        cur_help -= 1
                    elif x > 620 and x < 685 and y > 465 and y <500:
                        cur_help += 1
             
        if selection == 0:
            selection = 4
        elif selection == 5:
            selection = 1

        # Use mouse location to select menu items
        x,y = pygame.mouse.get_pos()
        if not winner:
            if x > 193 and x < 337 and y > 170 and y < 240:
                selection = 1
            if x > 270 and x < 528 and y > 262 and y < 343:
                selection = 2
            if x > 356 and x < 510 and y > 366 and y < 430:
                selection = 3
            if x > 442 and x <582 and y > 463 and y < 515:
                selection = 4

        # Start shapes falling, and add more when next_shape == 30
        if next_shape == 30:
            x = random.randint(100, 700)
            s = random.randint(10, 30)
            b = sandbox.add_ball(space, s, x, -100)
            balls.append(b)

            x = random.randint(100, 700)
            s = random.randint(10, 50)
            t = sandbox.add_triangle(space, s, x, -200)
            t.friction = 0.0
            triangles.append(t)
            
            x = random.randint(100, 700)
            s = random.randint(10, 50)
            s2 = random.randint(10, 50)
            r = sandbox.add_box(space, s, s2, x, -150)
            r.friction = 0.0
            boxes.append(r)
            next_shape = 0
        else:
            next_shape += 1

        # Remove the objects when they get to a certain point (y == -100), otherwise
        #  game slows to a crawl
        for ball in balls:
            if ball.body.position.y < -100:
                space.remove(ball, ball.body)
                balls.remove(ball)
            else:
                sandbox.draw_ball(screen, ball)
        for box in boxes:
            if box.body.position.y < -100:
                space.remove(box, box.body)
                boxes.remove(box)
            else:
                sandbox.draw_poly(screen, box, THECOLORS["red"])
        for tri in triangles:
            if tri.body.position.y < -100:
                space.remove(tri, tri.body)
                triangles.remove(tri)
            else:
                sandbox.draw_poly(screen, tri, THECOLORS["green"])

        # Show the correct picture for what is being selected
        if not winner:
            if selection == 1:
                screen.blit(background_play, (0, 0))
            elif selection == 2:
                screen.blit(background_sandbox, (0, 0))
            elif selection == 3:
                screen.blit(background_help, (0, 0))
            elif selection == 4:
                screen.blit(background_quit, (0, 0))

        # Show score after playing the game
        text = font.render(str(score), 20, THECOLORS["black"])
        if winner:
            screen.blit(congrats, (0,0))
            screen.blit(text, (400,300))

        # Show help menu
        if display_help == True:
            if cur_help >= 0 and cur_help <= 7:
                screen.blit(help_menu[cur_help], (0,0))
            else:
                display_help = False
                cur_help = 0


        
        space.step(1/60.0)

        clock.tick(60)
        pygame.display.flip()

    pygame.quit()
    
if __name__ == '__main__':
    main()
