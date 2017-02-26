import datetime
import pygame
import random
import pickle
import sys
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# TODO:
# 0. MAKE LIKE GEM TD
# 1. Implement high score and stuff
# 2. Fix the mazing glitch/bug
# 3. Make upgrades possible
# 5. Add new types of towers (electricity, plant, etc.)
# 6. Add support for actual levels not just programatic
# 7. Balance hecka (range, creep speed, initial money, creep worth, etc.)
# 9. Make code not absolutely terrible (repetition, functions, classes, etc.)
# 10. variables out the wazoo, fix, consoledate etc.
# 11. Add bosses (with level design)
# 12. Make third/fourth node in middle
# 13. Make bullets rather than just stupid lines
# 14. Make sell-worth full if same turn

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
s_x = s_y = 50


# Loads in the images for the creeps
c_basic = pygame.transform.scale(pygame.image.load('kiwi.png'), (creep_size, creep_size))
# Loads in the images for the towers
t_water = pygame.transform.scale(pygame.image.load('water.png'), (tower_size, tower_size))
t_fire = pygame.transform.scale(pygame.image.load('fire.png'), (tower_size, tower_size))
t_brick = pygame.transform.scale(pygame.image.load('brick.png'), (tower_size, tower_size))
t_elec = pygame.transform.scale(pygame.image.load('elec.png'), (tower_size, tower_size))
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


matrix = []
for ro in range(20):
    row = []
    for col in range(20):
        row.append(0)
    matrix.append(row)

def init():
    SPEED = 16
    tower_counter = 0
    creep_counter = 0
    touching = False
    money = 35
    held = False
    lives = 10  # Total person lives
    i = 0  # Counter for spawn times
    insert = True  # Is the player allowed to place a tower
    unabstructed = True
    wave_count = 0
    creep_death_bin = []
    path = False
    tower_dict.clear()
    creep_dict.clear()
    message = ''
    message_counter = 0
    selling = False
    fd = open('test.data')
    score_data = pickle.load(fd)
    print score_data


def main():  # This is the main function that needs to be broken up but im lazy
    init()
    SPEED = 16
    tower_counter = 0
    creep_counter = 0
    touching = False
    money = 35
    held = False
    lives = 10  # Total person lives
    i = 0  # Counter for spawn times
    insert = True  # Is the player allowed to place a tower
    unabstructed = True
    water_range = 100  # Range of the water tower
    fire_range = 200  # Fire range
    elec_range = 80
    wave_count = 0
    creep_death_bin = []
    path = False
    tower_dict.clear()
    creep_dict.clear()
    message = ''
    message_counter = 0
    selling = False
    fd = open('test.data')
    score_data = pickle.load(fd)
    print score_data
    while True:
        clicked = False
        screen.fill((255, 255, 255))  # Draws a white screen

        if path:
            for coord in path:
                pygame.draw.rect(screen, (152,251,152), (coord[0]*40, coord[1]*40, 40, 40))

        # Creep Spawner
        # print i, creep_counter, creep_dict

        pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pressed[pygame.K_BACKSPACE]:
                return 'quit'
            # elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # m_x, m_y = event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # If you click the mouse
                m_x, m_y = event.pos
                clicked = True

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
        if pressed[pygame.K_s]:
            selling = True
        if pressed[pygame.K_b]:
            held = True
            r_t_type = 't_brick'
            req_m = 2
        if pressed[pygame.K_e]:
            held = True
            r_t_type = 't_elec'
            req_m = 5

        # Next wave
        if clicked and 40 < m_x < 180 and 680 < m_y < 760:  # Implement some actual form of levels
            if creep_dict:
                message = 'There are ' + str(creep_counter) + ' creep(s) left!'
            else:
                wave_count += 1
                for i in range(wave_count):  # Spawns a creep every 40 ticks?
                    CREEP_LIVES = 130*wave_count  # This sets how many lives a given creep has
                    creep_dict[creep_counter] = {
                        'type': 'c_basic',
                        'x': 80-i*40,  # x coordinate
                        'y': 80-i*40,  # y coord
                        'del_x': 1,  # change in x
                        'del_y': 1,  # change in y
                        'lives': CREEP_LIVES,
                        'worth': round(.5+random.random()*wave_count*.7),
                        'node_counter': 0,
                        'node': 0
                    }
                    creep_counter += 1

        # Places towers
        elif clicked and held and money >= req_m:
            if creep_dict:
                message = 'You can\'t place towers while creeps are roaming, kill ' + str(creep_counter) + ' creep(s) first!'
            else:
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
                        'y': y-20,
                        'worth': 10
                    }
                    # PATH FINDING OH BOY OH BOY
                    # --------------------------
                    if path:
                        for node in path:
                            print node[0]*40, node[1]*40, x, y
                    matrix[m_y/40].pop(m_x/40)
                    matrix[m_y/40].insert(m_x/40, 1)
                    grid = Grid(matrix=matrix)
                    start = grid.node(2, 2)
                    end = grid.node(18, 18)
                    finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
                    path, runs = finder.find_path(start, end, grid)
                    # print('operations:', runs, 'path length:', len(path))
                    # print path  # [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (8, 9), (9, 10), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19)]
                    # print(grid.grid_str(path=path, start=start, end=end))
                    # --------------------------

        if clicked and selling:
            x, y = closest(m_x, m_y)
            for index, tower in tower_dict.items():
                if tower_counter > 0 and tower['x'] == x-20 and tower['y'] == y-20:
                    money += tower['worth']
                    tower_dict.pop(index)
                    selling = False
                    break

        # Draws the Grid
        for row in range(20):
            pygame.draw.line(screen, (211, 211, 211), (row*40, 0), (row*40, 800))
            pygame.draw.line(screen, (211, 211, 211), (0, row*40), (800, row*40))

        # Draws the Creeps
        for key, creep in creep_dict.items():
            c_x, c_y = center(creep['x'], creep['y'], creep_size)
            touching = False
            if creep['type'] == 'c_basic':
                if c_x > 700 and c_y > 700:  # Is the Creep in the house?
                    touching = True
                    lives -= 1  # Removes a life
                    creep_dict.pop(key)  # Destroys the creep
                    creep_counter -= 1
                    break
                if not touching:
                    # creep['node_counter'] += 1
                    print creep['node']
                    print path[creep['node']], (creep['x'], creep['y'])
                    if path[creep['node']] == (creep['x']/40, creep['y']/40):
                        creep['node'] += 1
                        print 'node up'
                    # print path[creep['node']]
                    if creep['node'] > 0:
                        creep['x'] += (path[creep['node']][0]*40 - path[creep['node']-1][0]*40)/SPEED
                        creep['y'] += (path[creep['node']][1]*40 - path[creep['node']-1][1]*40)/SPEED
                        print (path[creep['node']][0]*40 - path[creep['node']-1][0]*40)/SPEED
                        print (path[creep['node']][1]*40 - path[creep['node']-1][1]*40)/SPEED
                    else:
                        print 'starting up'
                        creep['x'] += 1
                        creep['y'] += 1
                    screen.blit(c_basic, (creep['x']+10, creep['y']+10))

        # Draws the Towers and shoots the creeps
        for key, val in tower_dict.items():  # For each tower
            shooting = 0
            t_x, t_y = center(val['x'], val['y'], tower_size)
            if val['type'] == 't_fire':  # This is only for the fire tower
                val['worth'] = 25
                screen.blit(t_fire, (val['x'], val['y']))  # Draw the tower
                for k, v in creep_dict.items():  # For each creep
                    c_x, c_y = center(v['x'], v['y'], creep_size)
                    # If the creep is within range of the tower
                    if shooting == 0 and abs(t_x - c_x) < fire_range and abs(t_y - c_y) < fire_range:  # RANGE OF TOWER HERE
                        pygame.draw.line(screen, (255, 0, 0), (t_x, t_y), (c_x, c_y))  # SHOOT!!!
                        v['lives'] -= 5  # Creep gets less life
                        shooting = 5
            elif val['type'] == 't_water':
                val['worth'] = 5
                screen.blit(t_water, (val['x'], val['y']))
                for k, v in creep_dict.items():
                    c_x, c_y = center(v['x'], v['y'], creep_size)
                    if shooting < 3 and abs(t_x - c_x) < water_range and abs(t_y - c_y) < water_range:  # RANGE OF TOWER HERE
                        pygame.draw.line(screen, (0, 0, 255), (t_x, t_y), (c_x, c_y))
                        v['lives'] -= 2
                        shooting += 1
            elif val['type'] == 't_brick':
                val['worth'] = 1
                screen.blit(t_brick, (val['x'], val['y']))
            elif val['type'] == 't_elec':
                val['worth'] = 3
                screen.blit(t_elec, (val['x'], val['y']))
                for k, v in creep_dict.items():
                    c_x, c_y = center(v['x'], v['y'], creep_size)
                    if shooting < 1 and abs(t_x - c_x) < elec_range and abs(t_y - c_y) < elec_range:  # RANGE OF TOWER HERE
                        pygame.draw.line(screen, (255, 255, 0), (t_x, t_y), (c_x, c_y))
                        v['lives'] -= 2
                        shooting += 1


        # If at any time a creep has no life left, it dies
        for in1, creep in creep_dict.items():
            if creep['lives'] < 0:
                creep_counter -= 1
                creep_death = {}
                money += creep['worth']
                creep_death['x'], creep_death['y'], creep_death['worth'] = creep['x'], creep['y'], creep['worth']
                creep_death['time'] = 30
                creep_death_bin.append(creep_death)
                creep_dict.pop(in1)

        for death in creep_death_bin:
            death['time'] -= 1
            if death['time'] > 0:
                screen.blit(myfont.render(str(death['worth']), 1, (255, 0, 0)), (death['x'], death['y']))

        if lives < 1:
            message = 'You lost on wave: ' + str(wave_count)
            score_data.append([raw_input('Score Name: '), wave_count])
            outputFile = 'test.data'
            fw = open(outputFile, 'w')
            pickle.dump(score_data, fw)
            fw.close()
            init()

        if pressed[pygame.K_RETURN]:
            init()

        # Draws the Spawner
        screen.blit(s_pineapple, (s_x, s_y))
        # Draws the house
        screen.blit(house, (700, 700))
        # Draws the menu tag
        screen.blit(myfont.render(('Menu'), 1, (0, 0, 0)), (350, 15))
        # Draws the money label
        screen.blit(myfont.render(('Money: ' + str(money)), 1, (0, 0, 0)), (420, 15))
        # Draws the lives
        screen.blit(heart, (550, 15))
        screen.blit(myfont.render(('= ' + str(lives)), 1, (0, 0, 0)), (580, 15))
        # Draws the next wave button
        pygame.draw.rect(screen, (50, 50, 50), (40, 680, 120, 80))
        screen.blit(myfont.render(('Next Wave'), 4, (255, 0, 0)), (60, 710))
        screen.blit(myfont.render(('Current Wave: ' + str(wave_count)), 1, (255, 0, 0)), (40, 15))

        #Draws the menu
        all_tower = ["Water", "Fire", "Brick", "Zap"]
        all_cost = {
            "Water": 10,
            "Fire": 50,
            "Brick": 2,
            "Zap": 5
        }

        for i, tower in enumerate (all_tower):
            menuWidth = 4
            menuHeight = 40
            menuItem = str(tower) + " Tower: " + str(all_cost[tower])
            textIndent = (menuWidth * 40 - (len(menuItem) * 9))/2
            menuPlaceX = 650
            menuPlaceY = (i + menuWidth) * 40
            topPadding = 10
            pygame.draw.rect(screen, (0, 30 * i + 60, 0), (menuPlaceX, menuPlaceY, menuWidth * 40, menuHeight))
            screen.blit(myfont.render((str(menuItem)), 4, (255, 255, 255)), (menuPlaceX + textIndent, menuPlaceY + topPadding))
            pygame.draw.rect(screen, (0, 0, 0), (menuPlaceX, (menuWidth - 1) * 40, menuWidth * 40, menuHeight))
            screen.blit(myfont.render(("BUY TOWERS"), 4, (255, 255, 255)), (menuPlaceX + menuWidth * 5, (menuWidth - 1) * 40 + topPadding))
            print textIndent

        '''for ind, tower in tower_dict.items():
            if tower["type"] not in all_tower:
                all_tower.append(tower["type"])
                print all_tower'''
        #Displays a message is applicable
        if message:
            message_counter += 1
            screen.blit(myfont.render((message), 1, (255, 0, 0)), (200, 380))
            if message_counter > 40:
                message = ''
                message_counter = 0

        # This is how the pygame thingy actually draws all this stuff
        pygame.display.flip()
        # Clock?
        clock.tick(30)


main()
