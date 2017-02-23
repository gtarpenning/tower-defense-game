import datetime
import pygame

pygame.init()
screen_x = screen_y = 800
creep_size = 20
boss_size = 40
tower_size = 40
spawner_size = 80

# This is going to hold the info for every tower
tower_dict = {}
# Ditto for creeps
creep_dict = {}

# initializes mouse coordinates
m_y = m_x = 0
# initializes spawn coordinates
s_x = s_y = 100


# Loads in the images for the creeps
c_basic = pygame.transform.scale(pygame.image.load('kiwi.png'), (creep_size, creep_size))
# Loads in the images for the towers
t_water = pygame.transform.scale(pygame.image.load('water.png'), (tower_size, tower_size))
t_fire = pygame.transform.scale(pygame.image.load('fire.png'), (tower_size, tower_size))
# Loads in the spawner
s_pineapple = pygame.transform.scale(pygame.image.load('pineapple.png'), (spawner_size, spawner_size))
# Loads in the heart
heart = pygame.transform.scale(pygame.image.load('heart.png'), (20, 20))
# Loads in the house
house = pygame.transform.scale(pygame.image.load('house.png'), (spawner_size, spawner_size))

# Loads the font
myfont = pygame.font.SysFont("monospace", 25)
# Makes the screen object
screen = pygame.display.set_mode((screen_x, screen_y))
# Some clock thing for pygame
clock = pygame.time.Clock()


def closest(x, y):  # This is a function that rounds coordinates to a grid (for the towers)
    x_r = x / 40
    y_r = y / 40
    x = round(x_r, 0)*40
    y = round(y_r, 0)*40

    return x+20, y+20


def center(x, y, size):  # This is a function that finds the center of an object
    center_x = x+(size/2)
    center_y = y+(size/2)
    return center_x, center_y


def main():
    tower_counter = 0
    creep_counter = 0
    touching = False
    money = 200
    held = False
    lives = 10
    i = 0
    insert = True
    unabstructed = True
    water_range = 50
    fire_range = 100
    while True:
        clicked = False
        screen.fill((255, 255, 255))

        # Creep Spawner
        print i, creep_counter, creep_dict
        if i >= 40:
            CREEP_LIVES = 200
            creep_dict[creep_counter] = {
                'type': 'c_basic',
                'x': 100,
                'y': 100,
                'del_x': 1,
                'del_y': 1,
                'lives': CREEP_LIVES
            }
            i = 0
            creep_counter += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            # elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # m_x, m_y = event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                m_x, m_y = event.pos
                clicked = True

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_BACKSPACE]:
            return 'quit'

        # GAMEPLAY
        # Hold W or F to place water or fire towers
        if pressed[pygame.K_w]:
            held = True
            r_t_type = 't_water'
            req_m = 10
        if pressed[pygame.K_f]:
            held = True
            r_t_type = 't_fire'
            req_m = 50

        # Places towers
        if clicked and held and money >= req_m:
            insert = True
            x, y = closest(m_x, m_y)
            for it, t in tower_dict.items():
                if tower_counter > 0 and t['x'] == x-20 and t['y'] == y-20:
                    insert = False
                    break
            if insert:
                money -= req_m
                tower_counter += 1
                tower_dict[tower_counter] = {
                    'type': r_t_type,
                    'x': x-20,
                    'y': y-20
                }

        # RENDERING
        # Draws the Grid
        for row in range(20):
            pygame.draw.line(screen, (211, 211, 211), (row*40, 0), (row*40, 800))
            pygame.draw.line(screen, (211, 211, 211), (0, row*40), (800, row*40))

        # Draws the Creeps
        for key, val in creep_dict.items():
            c_x, c_y = center(val['x'], val['y'], creep_size)
            touching = False
            if val['type'] == 'c_basic':
                if c_x > 700 and c_y > 700:  # Is the Creep in the house?
                    touching = True
                    lives -= 1  # Removes a life
                    creep_dict.pop(key)  # Destroys the creep
                    creep_counter -= 1
                    break
                if not touching:
                    for it, v in tower_dict.items():
                        unabstructed = True
                        t_x, t_y = center(v['x'], v['y'], tower_size)
                        # print 'tower: ' + str(t_x) + ' ' + str(t_y) + ' creep ' + str(c_x) + ' ' + str(c_y)
                        if abs(t_x - c_x) < 30 and abs(t_y - c_y) < 30:
                            print 'touching a wall!'
                            unabstructed = False
                    if unabstructed:
                        r_x = (700 - c_x)
                        r_y = (700 - c_y)
                        r_x_tot = r_x / (r_x + r_y)
                        del_x = r_x_tot*1.41
                        del_y = 1.41-del_x
                        val['x'] += del_x
                        val['y'] += del_y
                        screen.blit(c_basic, (val['x'], val['y']))
                    else:
                        val['x'] += (val['del_x'] * -1)
                        val['y'] += val['del_y']
                        screen.blit(c_basic, (val['x'], val['y']))

        # Draws the Towers
        for key, val in tower_dict.items():
            t_x, t_y = center(val['x'], val['y'], tower_size)
            if val['type'] == 't_fire':
                screen.blit(t_fire, (val['x'], val['y']))
                for k, v in creep_dict.items():
                    c_x, c_y = center(v['x'], v['y'], creep_size)
                    if abs(t_x - c_x) < fire_range and abs(t_y - c_y) < fire_range:  # RANGE OF TOWER HERE
                        pygame.draw.line(screen, (255, 0, 0), (t_x, t_y), (c_x, c_y))
                        v['lives'] -= 5
            elif val['type'] == 't_water':
                screen.blit(t_water, (val['x'], val['y']))
                for k, v in creep_dict.items():
                    c_x, c_y = center(v['x'], v['y'], creep_size)
                    if abs(t_x - c_x) < water_range and abs(t_y - c_y) < water_range:  # RANGE OF TOWER HERE
                        pygame.draw.line(screen, (0, 0, 255), (t_x, t_y), (c_x, c_y))
                        v['lives'] -= 1

        for in1, creep in creep_dict.items():
            if creep['lives'] < 0:
                creep_dict.pop(in1)

        # Draw the Spawner
        screen.blit(s_pineapple, (s_x, s_y))
        screen.blit(house, (700, 700))

        screen.blit(myfont.render(('Menu'), 1, (0, 0, 0)), (350, 15))
        screen.blit(myfont.render(('Money: ' + str(money)), 1, (0, 0, 0)), (450, 15))
        screen.blit(heart, (550, 15))
        screen.blit(myfont.render(('= ' + str(lives)), 1, (0, 0, 0)), (580, 15))

        pygame.display.flip()
        clock.tick(60)
        i += 1


main()
