#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# libtcod python tutorial
#

import libtcodpy as libtcod
import PyBearLibTerminal as T
import math
import textwrap
import shelve
import time
import random
import re

#my modules
import monsters
import constellations
import tiles
import timer

#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 24

#size of the map portion shown on-screen
CAMERA_WIDTH = 25
CAMERA_HEIGHT = 13

#size of the map portion shown on treasure map view
MAP_CAMERA_WIDTH = 80
MAP_CAMERA_HEIGHT = 23

#size of the map
MAP_WIDTH = 500
MAP_HEIGHT = 500

#size of the sky portion on the screen
SKYCAM_WIDTH = 50
SKYCAM_HEIGHT = 10

#size of the map
SKY_WIDTH = 100
SKY_HEIGHT = 100

SKY_FACTOR_X = MAP_WIDTH / SKY_WIDTH
SKY_FACTOR_Y = MAP_HEIGHT / SKY_HEIGHT

#position of the boat window in the game screen
BOAT_WINDOW_X = 27
BOAT_WINDOW_Y = 10

#position of the sky window in the game screen
SKY_WINDOW_X = 15
SKY_WINDOW_Y = 0


#sizes and coordinates relevant for the GUI
PANEL_HEIGHT = 23#SCREEN_HEIGHT - CAMERA_HEIGHT
PANEL_WIDTH = SCREEN_WIDTH-SKYCAM_WIDTH
PANEL_Y = 0 #SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = SKYCAM_WIDTH+1
MSG_WIDTH = 30
MSG_HEIGHT = PANEL_HEIGHT - 2

INVENTORY_WIDTH = 50

#GUI column on the right
COLUMN_HEIGHT = 30
COLUMN_WIDTH = 10
COLUMN_Y = 0
COLUMN_X = 40

#parameters for dungeon generator
ROOM_MAX_SIZE = 40
ROOM_MIN_SIZE = 20
MAX_ROOMS = 22

PLAYER_NAME = 'You'

FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True  #light walls or not

LIMIT_FPS = 20  #20 frames-per-second maximum

FONT_SIZE = 24

SCALE = 2

MAP_HOTKEY_1 = None
MAP_HOTKEY_2 = None
MAP_HOTKEY_3 = None
MAP_HOTKEY_4 = None
MAP_HOTKEY_5 = None

key_set = {
        'up': '8',
        'down': '2',
        'left': '4',
        'right': '6',
        'upleft': '7',
        'upright': '9',
        'downleft': '1',
        'downright': '3',
        'hold': '5'
        }
rain = 0    
    
#---------------------------------------------------------------------------------------------------------
#A* STAR PATHFINDING!!!

class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def astar(maze, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1] # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]].type != 'water':
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)


# def main():

    # maze = [[0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            # [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            # [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            # [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            # [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            # [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            # [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            # [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    # start = (0, 0)
    # end = (7, 6)

    # path = astar(maze, start, end)
    # print(path) 
   
    
#---------------------------------------------------------------------------------------------------------

class Island:
    #a rectangle on the map incl map data for island. used to characterize an island.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.w = w
        self.h = h
        
        self.smallmap = None
        self.bigmap = None 
 
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)
 
    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Object:
    '''this is a generic object the player, a monster, an item, the stairs
    it's always represented by a character on screen.'''
    def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, index=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.always_visible = always_visible
        self.index = index
        self.fighter = fighter
        if self.fighter:  #let the fighter component know who owns it
            self.fighter.owner = self

        self.ai = ai
        if self.ai:  #let the AI component know who owns it
            self.ai.owner = self

    def move(self, dx, dy):
        '''moves the object if not blocked'''
        #check if leaving the map
        if self.x + dx < 0 or self.x + dx >= MAP_WIDTH or self.y + dy < 0 or self.y + dy >= MAP_HEIGHT:
            return
        #move by the given amount, if the destination is not blocked
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            
    def move_towards(self, target_x, target_y):
        '''calculates the movement of a smart object and calls move then'''
        # #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        # distance = math.sqrt(dx ** 2 + dy ** 2)

        ddx = 0 
        ddy = 0
        if dx > 0:
            ddx = 1
        elif dx < 0:
            ddx = -1
        if dy > 0:
            ddy = 1
        elif dy < 0:
            ddy = -1
        if not is_blocked(self.x + ddx, self.y + ddy):
            self.move(ddx, ddy)
        else:
            if ddx != 0:
                if not is_blocked(self.x + ddx, self.y):
                    self.move(ddx, 0)
                    return
            if ddy != 0:
                if not is_blocked(self.x, self.y + ddy):
                    self.move(0, ddy)
                    return
    
    def distance_to(self, other):
        '''returns the distance of object to another object'''
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        '''returns the distance of object to some coordinates'''
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def send_to_back(self):
        '''make this object be drawn first, so all others appear above it if they're in the same tile.'''
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def draw(self):
        '''draws the object to console "con", only called by render_all'''
        #only show if it's visible to the player; or it's set to "always visible" and on an explored tile
        
        mod_x = BOAT_WINDOW_X
        mod_y = BOAT_WINDOW_Y
        
        (x, y) = camera.to_camera_coordinates(self.x, self.y)
        if x is not None:
            #set the color and then draw the character that represents this object at its position
            if self.char == 'B':
                T.color('#8B4513')
                T.print_(x+mod_x, y+mod_y, '_')
                T.layer(3)
                T.color(self.color)
                T.print_(x+mod_x, y+mod_y, self.char)
                T.layer(0)
            else:
                T.color(self.color)
                T.print_(x+mod_x, y+mod_y, self.char)
                
                
    # def clear(self):
        # '''erase the character that represents this object, BUGGY and NOT needed cause render_all'''
        # (x, y) = camera.to_camera_coordinates(self.x, self.y)
        # if x is not None:
            # #libtcod.console_put_char_ex(con, self.x, self.y, '.', libtcod.grey, libtcod.black)
            # T.color('grey')
            # T.print_(self.x, self.y, '.')
            
    # def delete(self):
        # '''triggers easy removal of object and clears the char'''
        # for obj in objects:
            # if self in objects:
                # objects.remove(self)
        # self.clear()


def distance(x1,y1, x2, y2):
    '''returns the distance of object to some coordinates'''
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        
class Fighter:
    '''component of object to make it attacking and attackable contains
    combat-related properties and methods (monster, player, NPC).'''
    def __init__(self, hp, damage, inventory=[],death_function=None):

        self.base_hp = hp
        self.hp = hp  
        self.inventory = inventory
        self.base_damage = damage
        self.death_function = death_function

    @property
    def max_hp(self):
        '''the maximum possible hp of a fighter'''
        return self.base_hp
        
    @property
    def damage(self):
        '''return actual damage, by summing up the bonuses from all equipped items. Unmodified in TPB'''
        return self.base_damage
    
    def attack(self, target):
        '''call take_damage on target'''
        target.fighter.take_damage(self.damage)
         
    def take_damage(self, damage):
        '''is called by attacker and checks status of owner and deals damage. triggers fighter.death_function upon hp <= 0'''
        #apply damage if possible    
        if damage > 0:
            self.hp -= damage
            if self.owner == player:
                message('You get ' + str(damage) + ' damage.', libtcod.red)
     
        #check for death. if there's a death function, call it
        if self.hp <= 0:
            self.hp = 0
            function = self.death_function
            if function is not None:
                function(self.owner)

class Feature:
    def __init__(self, x, y, type):
        self.x = x #coordinates of the X
        self.y = y
        self.type = type #generated name to show in inventory

    def draw(self):
        x= self.x
        y= self.y
        
        T.layer(0)
        
        if self.type == 'stain_3':
            T.bkcolor("#CD853F")
            T.print_(x-1,y, ' ')
            T.print_(x+1,y, ' ')
            T.print_(x,y-1, ' ')
            T.print_(x,y+1, ' ')
            T.print_(x,y, ' ')
        elif self.type == 'stain_5':
            T.bkcolor("#CD853F")
            T.print_(x-1,y, ' ')
            T.print_(x+1,y, ' ')
            T.print_(x,y-1, ' ')
            T.print_(x,y+1, ' ')
            T.print_(x,y, ' ')
            T.print_(x-2,y, ' ')
            T.print_(x+2,y, ' ')
            T.print_(x,y-2, ' ')
            T.print_(x,y+2, ' ')
            T.print_(x-1,y-1, ' ')
            T.print_(x+1,y+1, ' ')
            T.print_(x-1,y+1, ' ')
            T.print_(x+1,y-1, ' ')
        
        T.layer(2)
        
        if self.type == 'anchor':
            T.print_(x,y  , '[color=black]  o')
            T.print_(x,y+1, '[color=black] _|_')
            T.print_(x,y+2, '[color=black]  | ')
            T.print_(x,y+3, '[color=black]\_|_/')
        elif self.type == 'skull_l':
            T.print_(x,y  , '[color=black] __')
            T.print_(x,y+1, '[color=black]|oo|')
            T.print_(x,y+2, '[color=black]|m|')
        elif self.type == 'skull_r':
            T.print_(x,y  , '[color=black] __')
            T.print_(x,y+1, '[color=black]|oo|')
            T.print_(x,y+2, '[color=black] |m|')
        elif self.type == 'chest_l':
            #T.print_(x,y  , '[color=black]Hallo')
            T.print_(x,y  , '[color=black]  ____')
            T.print_(x,y+1, '[color=black] _)___)')
            T.print_(x,y+2, '[color=black]|_+_|_|')
        elif self.type == 'chest_r':
            T.print_(x,y  , '[color=black] ____')
            T.print_(x,y+1, '[color=black](___(_')
            T.print_(x,y+2, '[color=black]|_|_+_|')
        elif self.type == 'fish_l':
            T.print_(x,y  , '[color=black]<)))><')
        elif self.type == 'fish_r':
            T.print_(x,y  , '[color=black]><(((>')
        
        T.layer(0)
        
class Treasure:
    def __init__(self, x, y, name, map, owner_x=0, owner_y=0, char='X', color='red'):
        self.x = x #coordinates of the X
        self.y = y
        self.name = name #generated name to show in inventory
        self.map = map #stores the full map info, centers around island
        self.owner_x = owner_x
        self.owner_y = owner_y
        self.char = char
        self.color = color
        
        self.map_owned = False #needed to check successful find. Can only find treasures with maps in inventory
        self.found = False
        self.features = []
        self.stains = []
        
        feature = ['anchor', 'skull_l', 'skull_r', 'chest_l', 'chest_r', 'fish_l', 'fish_r']
        random.shuffle(feature)
        positions = [(3,3), (10,18), (70,4), (70,10)]
        random.shuffle(positions)
        
        for i in range(libtcod.random_get_int(0,1,4)):
            type = feature.pop(0)
            position = positions.pop(0)
            obj = Feature(position[0], position[1], type)
            self.features.append(obj)
        
        
        for i in range(libtcod.random_get_int(0,7,20)):
            if libtcod.random_get_int(0,0,1) == 0:
                obj = Feature(libtcod.random_get_int(0,2,SCREEN_WIDTH-2), libtcod.random_get_int(0,2,SCREEN_HEIGHT-2), 'stain_3')
                self.features.append(obj)
            else:
                obj = Feature(libtcod.random_get_int(0,3,SCREEN_WIDTH-3), libtcod.random_get_int(0,3,SCREEN_HEIGHT-3), 'stain_5')
                self.features.append(obj)
                
                
    def draw(self):
        '''draws the object to console "con", only called by render_all'''
        #only show if it's visible to the player; or it's set to "always visible" and on an explored tile
        
        mod_x = BOAT_WINDOW_X
        mod_y = BOAT_WINDOW_Y
           
        (x, y) = camera.to_camera_coordinates(self.x, self.y)
        if x is not None:
            #set the color and then draw the character that represents this object at its position
            T.color(self.color)
            T.print_(x+mod_x, y+mod_y, self.char)

class Star:
    def __init__(self, x, y, char='O', color='yellow', brightness=5):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.brightness = brightness
        
    def distance(self, x, y):
        '''returns the distance of object to some coordinates'''
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        
    def draw(self):
        '''draws the object, only called by render_all'''
        
        #only show if it's within camera frame
        (x, y) = sky_cam.to_camera_coordinates(self.x, self.y)
        
        
        if clock[0] == 12 and not self.brightness == 10:
            return
        elif (clock[0] == 13 or clock[0] == 11) and not self.brightness >= 9:
            return
        elif (clock[0] == 14 or clock[0] == 10) and not self.brightness >= 8:
            return
        elif (clock[0] == 15 or clock[0] == 9) and not self.brightness >= 7:
            return
        elif (clock[0] == 16 or clock[0] == 8) and not self.brightness >= 6:
            return
        elif (clock[0] == 17 or clock[0] == 7) and not self.brightness >= 5:
            return
        elif (clock[0] == 18 or clock[0] == 6) and not self.brightness >= 4:
            return
        elif (clock[0] == 19 or clock[0] == 5) and not self.brightness >= 3:
            return
        elif (clock[0] == 20 or clock[0] == 4) and not self.brightness >= 2:
            return
        elif (clock[0] == 21 or clock[0] == 3) and not self.brightness >= 1:
            return
        
        
        if x is not None:
        #set the color and then draw the character that represents this object at its position
            T.color(self.color)
            T.print_(x+SKY_WINDOW_X, y+SKY_WINDOW_Y, self.char)

class Cloud:
    def __init__(self, x, y, char='[U+2248]', color='white', speed=1, color_dawn='#333333', color_dusk='white'):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.speed = speed
        self.color_dawn = color_dawn
        self.color_dusk = color_dusk
        self.color_night = '#333333'
        
        self.color_rain = 'dark grey'
        if libtcod.random_get_int(0,0,100) < 20:
            self.color_rain = 'darker grey'
        
        
    def move(self):
        a = self.x + (wind[0] * self.speed)
        b = self.y + (wind[1] * self.speed)
        
        if a < 0:
            a += SKY_WIDTH
        elif a >= SKY_WIDTH:
            a -= SKY_WIDTH
        if b < 0:
            b += SKY_HEIGHT
        elif b >= SKY_HEIGHT:
            b -= SKY_HEIGHT
            
        self.x = a
        self.y = b
        
    def draw(self):
        '''draws the object, only called by render_all'''
        
        #only show if it's within camera frame
        (x, y) = sky_cam.to_camera_coordinates(self.x, self.y)
        
       
        if x is not None:
        #set the color and then draw the character that represents this object at its position
            color = self.color
            
            if clock[0] >= 4 and clock[0] <= 6:
                color = self.color_dawn
                
            if clock[0] >= 18 and clock[0] <= 19:
                color = self.color_dusk
            
            if rain > 0:
                color = self.color_rain 
                
            if (clock[0] >= 20 or clock[0] <= 5) and not (clock[0] >= 4 and clock[0] <= 6):
                color = self.color_night 
            
            T.print_(x+SKY_WINDOW_X, y+SKY_WINDOW_Y,'[color=' + color + ']' + self.char)
            
class Bird:
    def __init__(self, x, y, char='v', color='red', ai=None):
        self.x = x
        self.y = y
        self.char = 'v'
        if libtcod.random_get_int(0,0,1) == 0:
            self.char = '[U+028C]'
        self.color = color
        self.target_x = libtcod.random_get_int(0,1, SKY_WIDTH-1)
        self.target_y = libtcod.random_get_int(0,1, SKY_HEIGHT-1)
        self.char_toggle = 3
        self.ai = ai
        if self.ai:  #let the AI component know who owns it
            self.ai.owner = self

    def move(self, dx, dy):
        a = self.x + dx
        b = self.y + dy
        
        if a < 0:
            a += SKY_WIDTH
        elif a >= SKY_WIDTH:
            a -= SKY_WIDTH
        if b < 0:
            b += SKY_HEIGHT
        elif b >= SKY_HEIGHT:
            b -= SKY_HEIGHT
            
        self.x = a
        self.y = b
    
    def move_towards(self, target_x, target_y):
        #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
 
        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)
 
    def distance_to(self, other):
        #return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
 
    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)    
    
    def draw(self):
        '''draws the object, only called by render_all'''
        
        #only show if it's within camera frame
        (x, y) = sky_cam.to_camera_coordinates(self.x, self.y)
            
        if x is not None:
        #set the color and then draw the character that represents this object at its position
            color = 'white'
            
            if self.char_toggle > 0:
                self.char_toggle -= 1
            elif self.char_toggle == 0:
                self.char_toggle = 3
                if self.char == '[U+028C]':
                    self.char = 'v'
                else:
                    self.char = '[U+028C]'
            
            T.print_(x+SKY_WINDOW_X, y+SKY_WINDOW_Y,'[color=' + color + ']' + self.char)
 
class BirdAI:
    def __init__(self, ticker, speed):
        self.ticker = ticker
        self.speed = speed
        self.ticker.schedule_turn(self.speed, self)
        
    def take_turn(self):
    
        action_speed = self.speed
        
        if game_state == 'dead' or game_state == 'exit':
            return self.ticker.schedule_turn(action_speed, self)
        
        if self.owner.target_x == self.owner.x and self.owner.target_y == self.owner.y:
            self.owner.target_x = libtcod.random_get_int(0,1, SKY_WIDTH-1)
            self.owner.target_y = libtcod.random_get_int(0,1, SKY_HEIGHT-1)
        
        self.owner.move_towards(self.owner.target_x,self.owner.target_y)
            
        self.ticker.schedule_turn(action_speed, self)
        
        
 
def scale(constellation, factor):
    scaled_constellation = []
    for i in range(len(constellation)):
        line = ""
        for j in range(len(constellation[i])):
            line = line + constellation[i][j] + ('-' * (factor-1))
                        
        scaled_constellation.append(line)
        empty_line = ('-' * 7 * factor)
        for k in range(factor-1):
            scaled_constellation.append(empty_line)
            
    return scaled_constellation
    
def mount_constellation(constellation, x, y, factor=10):
    global sky_objects
    
    scaled_constellation = scale(constellation, factor)
    
    for i in range(len(scaled_constellation)):
        for j in range(len(scaled_constellation[i])):
            if not scaled_constellation[i][j] == '-':
                a = x + j
                b = y + i
                
                if a >= SKY_WIDTH:
                    a -= SKY_WIDTH
                elif a < 0:
                    a += SKY_WIDTH
                    
                if b >= SKY_HEIGHT:
                    b -= SKY_HEIGHT
                elif b < 0:
                    b += SKY_HEIGHT
                    
                star = Star(a, b, char=scaled_constellation[i][j], brightness=libtcod.random_get_int(0,6,10))
                sky_objects.append(star)
                
class EnemyShip:
    def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.always_visible = always_visible
        self.home_x = x
        self.home_y = y
        self.pursuit = True
        self.ai = ai
        if self.ai:  #let the AI component know who owns it
            self.ai.owner = self
        
        self.path_home = None
        self.path_step = 1

    def move(self, dx, dy):
        '''moves the object if not blocked'''
        a = self.x + dx
        b = self.y + dy
        
        if a < 0:
            a += MAP_WIDTH
        elif a >= MAP_WIDTH:
            a -= MAP_WIDTH
    
        if b < 0:
            b += MAP_HEIGHT
        elif b >= MAP_HEIGHT:
            b -= MAP_HEIGHT
        
        if player.x == a and player.y == b:
            if player.food > 0:
                message('The pirates steal your food!', 'red')
                player.decrease_food()
                self.pursuit = False
                self.path_home = None
                self.path_step = 1
            return
        
        for obj in objects:
            if obj.name == 'Boat' and a == obj.x and b == obj.y:
                if player.food > 0:
                    message('The pirates steal your food!', 'red')
                    player.decrease_food()
                    self.pursuit = False
                    self.path_home = None
                    self.path_step = 1
                return
    
        if self.x == self.home_x and self.y == self.home_y:
            self.pursuit = True
        
        #move by the given amount, if the destination is not blocked
        if map[a][b].type == 'water':
            self.x = a
            self.y = b            
            
    def move_towards(self, target_x, target_y):
        '''calculates the movement of a smart object and calls move then'''
        # #vector from this object to the target, and distance
        
        #'manual' short distance pursuit at the edges
        if self.pursuit and ( self.x < 25 or self.x > MAP_WIDTH-25 or self.y < 25 or self.y > MAP_HEIGHT-25):
            dx = target_x - self.x
            dy = target_y - self.y
            test_1 = math.sqrt( (target_x - self.x) ** 2 + (target_y - self.y) ** 2)
            test_2 = math.sqrt( (target_x - MAP_WIDTH - self.x) ** 2 + (target_y - self.y) ** 2)
            test_3 = math.sqrt( (target_x - self.x) ** 2 + (target_y - MAP_HEIGHT - self.y) ** 2)
            test_4 = math.sqrt( (target_x - MAP_WIDTH - self.x) ** 2 + (target_y - MAP_HEIGHT - self.y) ** 2)
            test_5 = math.sqrt( (target_x + MAP_WIDTH - self.x) ** 2 + (target_y - self.y) ** 2)
            test_6 = math.sqrt( (target_x - self.x) ** 2 + (target_y + MAP_HEIGHT - self.y) ** 2)
            test_7 = math.sqrt( (target_x + MAP_WIDTH - self.x) ** 2 + (target_y + MAP_HEIGHT - self.y) ** 2) 
            test_8 = math.sqrt( (target_x - MAP_WIDTH - self.x) ** 2 + (target_y + MAP_HEIGHT - self.y) ** 2) 
            test_9 = math.sqrt( (target_x + MAP_WIDTH - self.x) ** 2 + (target_y - MAP_HEIGHT - self.y) ** 2) 
            
            shortest_distance = test_1
            if test_2 < shortest_distance:
                shortest_distance = test_2
            if test_3 < shortest_distance:
                shortest_distance = test_3
            if test_4 < shortest_distance:
                shortest_distance = test_4
            if test_5 < shortest_distance:
                shortest_distance = test_5
            if test_6 < shortest_distance:
                shortest_distance = test_6
            if test_7 < shortest_distance:
                shortest_distance = test_7
            if test_8 < shortest_distance:
                shortest_distance = test_8
            if test_9 < shortest_distance:
                shortest_distance = test_9
            
            if shortest_distance == test_1:
                dx = target_x - self.x
                dy = target_y - self.y
            elif shortest_distance == test_2:
                dx = target_x - self.x - MAP_WIDTH
                dy = target_y - self.y
            elif shortest_distance == test_3:
                dx = target_x - self.x 
                dy = target_y - self.y - MAP_HEIGHT
            elif shortest_distance == test_4:
                dx = target_x - self.x - MAP_WIDTH
                dy = target_y - self.y - MAP_HEIGHT
            elif shortest_distance == test_5:
                dx = target_x - self.x + MAP_WIDTH
                dy = target_y - self.y
            elif shortest_distance == test_6:
                dx = target_x - self.x 
                dy = target_y - self.y + MAP_HEIGHT
            elif shortest_distance == test_7:
                dx = target_x - self.x + MAP_WIDTH
                dy = target_y - self.y + MAP_HEIGHT
            elif shortest_distance == test_8:
                dx = target_x - self.x - MAP_WIDTH
                dy = target_y - self.y + MAP_HEIGHT
            elif shortest_distance == test_9:
                dx = target_x - self.x + MAP_WIDTH
                dy = target_y - self.y - MAP_HEIGHT
                
            ddx = 0 
            ddy = 0
            if dx > 0:
                ddx = 1
            elif dx < 0:
                ddx = -1
            if dy > 0:
                ddy = 1
            elif dy < 0:
                ddy = -1
            
            a = self.x + ddx
            b = self.y + ddy
            
            if a < 0:
                a += MAP_WIDTH
            elif a >= MAP_WIDTH:
                a -= MAP_WIDTH
        
            if b < 0:
                b += MAP_HEIGHT
            elif b >= MAP_HEIGHT:
                b -= MAP_HEIGHT
            
            if map[a][b].type == 'water': #not is_blocked(self.x + ddx, self.y + ddy):
                self.move(ddx, ddy)
            else:
                if ddx != 0:
                    if map[a][self.y].type == 'water': #not is_blocked(self.x + ddx, self.y):
                        self.move(ddx, 0)
                        return
                if ddy != 0:
                    if map[self.x][b].type == 'water': #not is_blocked(self.x, self.y + ddy):
                        self.move(0, ddy)
                        return
        #pursuit far away from map edges -> full A*
        elif self.pursuit and ( self.x >= 25 or self.x <= MAP_WIDTH-25 or self.y >= 25 or self.y <= MAP_HEIGHT-25):
            path = astar(map, (self.x,self.y), (target_x,target_y))
            self.move(path[1][0]-self.x, path[1][1]-self.y)
            
        #move home
        elif not self.pursuit and not self.path_home:
            #in case it is far away store the way once
            self.path_home = astar(map, (self.x,self.y), (target_x,target_y))
            self.move(self.path_home[self.path_step][0]-self.x, self.path_home[self.path_step][1]-self.y)
            self.path_step += 1
        elif not self.pursuit and self.path_home:
            # print self.path_home
            # print 'step', self.path_step
            # #print 'target ', self.path_home[self.path_step][0]-self.x, self.path_home[self.path_step][1]-self.y
            # print self.x, self.y
            # print self.home_x, self.home_y
            
            if self.path_step >= len(self.path_home):
                self.path_step = len(self.path_home)-1
            # print 'step', self.path_step
            self.move(self.path_home[self.path_step][0]-self.x, self.path_home[self.path_step][1]-self.y)
            self.path_step += 1
        else:
            path = astar(map, (self.x,self.y), (target_x,target_y))
            self.move(path[1][0]-self.x, path[1][1]-self.y)
            
    def distance_to(self, other):
        '''returns the distance of object to another object'''
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        '''returns the distance of object to some coordinates'''
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def send_to_back(self):
        '''make this object be drawn first, so all others appear above it if they're in the same tile.'''
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def draw(self):
        '''draws the object to console "con", only called by render_all'''
        #only show if it's visible to the player; or it's set to "always visible" and on an explored tile
        
        mod_x = BOAT_WINDOW_X
        mod_y = BOAT_WINDOW_Y
        
        (x, y) = camera.to_camera_coordinates(self.x, self.y)
        if x is not None:
            #set the color and then draw the character that represents this object at its position
            if self.char == 'B':
                T.color('#8B4513')
                T.print_(x+mod_x, y+mod_y, '_')
                T.layer(3)
                T.color(self.color)
                T.print_(x+mod_x, y+mod_y, self.char)
                T.layer(0)
            else:
                T.color(self.color)
                T.print_(x+mod_x, y+mod_y, self.char)
                
                
    # def clear(self):
        # '''erase the character that represents this object, BUGGY and NOT needed cause render_all'''
        # (x, y) = camera.to_camera_coordinates(self.x, self.y)
        # if x is not None:
            # #libtcod.console_put_char_ex(con, self.x, self.y, '.', libtcod.grey, libtcod.black)
            # T.color('grey')
            # T.print_(self.x, self.y, '.')
            
    # def delete(self):
        # '''triggers easy removal of object and clears the char'''
        # for obj in objects:
            # if self in objects:
                # objects.remove(self)
        # self.clear()

               
class PirateAI:
    def __init__(self, ticker, speed):
        self.ticker = ticker
        self.speed = speed
        self.ticker.schedule_turn(self.speed, self)
        
    def take_turn(self):
    
        action_speed = self.speed
        
        if game_state == 'dead' or game_state == 'exit':
            return self.ticker.schedule_turn(action_speed, self)
        
        
        if player.boat and self.owner.pursuit:
            target_x = player.x
            target_y = player.y
        elif not player.boat and self.owner.pursuit:
            for obj in objects:
                if obj.name == 'Boat':
                    target_x = obj.x
                    target_y = obj.y
        else:
            target_x = self.owner.home_x
            target_y = self.owner.home_y
                    
        x = self.owner.x
        y = self.owner.y
        test_1 = math.sqrt( (target_x - x) ** 2 + (target_y - y) ** 2)
        test_2 = math.sqrt( (target_x - MAP_WIDTH - x) ** 2 + (target_y - y) ** 2)
        test_3 = math.sqrt( (target_x - x) ** 2 + (target_y - MAP_HEIGHT - y) ** 2)
        test_4 = math.sqrt( (target_x - MAP_WIDTH - x) ** 2 + (target_y - MAP_HEIGHT - y) ** 2)
        test_5 = math.sqrt( (target_x + MAP_WIDTH - x) ** 2 + (target_y - y) ** 2)
        test_6 = math.sqrt( (target_x - x) ** 2 + (target_y + MAP_HEIGHT - y) ** 2)
        test_7 = math.sqrt( (target_x + MAP_WIDTH - x) ** 2 + (target_y + MAP_HEIGHT - y) ** 2) 
        test_8 = math.sqrt( (target_x - MAP_WIDTH - x) ** 2 + (target_y + MAP_HEIGHT - y) ** 2) 
        test_9 = math.sqrt( (target_x + MAP_WIDTH - x) ** 2 + (target_y - MAP_HEIGHT - y) ** 2) 
        
        shortest_distance = test_1
        if test_2 < shortest_distance:
            shortest_distance = test_2
        if test_3 < shortest_distance:
            shortest_distance = test_3
        if test_4 < shortest_distance:
            shortest_distance = test_4
        if test_5 < shortest_distance:
            shortest_distance = test_5
        if test_6 < shortest_distance:
            shortest_distance = test_6
        if test_7 < shortest_distance:
            shortest_distance = test_7
        if test_8 < shortest_distance:
            shortest_distance = test_8
        if test_9 < shortest_distance:
            shortest_distance = test_9
        
        if self.owner.pursuit:
            if shortest_distance < 25:
                self.owner.move_towards(target_x, target_y)
        else:
            self.owner.move_towards(target_x, target_y)
            
        self.ticker.schedule_turn(action_speed, self)
        
        
class Player:
    def __init__(self, x, y, char_p, char_b, name, color, blocks=False, always_visible=False, fighter=None, ai=None):
        self._x = x
        self._y = y
        self._char_p = char_p
        self._char_b = char_b
        self.boat = True
        
        self.speed = 1
        self.last_direction = [0,1]
        
        self.old_x = x
        self.old_y = y
        
        self.food = 7
        
        self.name = name
        self.color = color
        self.blocks = blocks
        
        self.always_visible = always_visible
        self.fighter = fighter
        if self.fighter:  #let the fighter component know who owns it
            self.fighter.owner = self

        self.ai = ai
        if self.ai:  #let the AI component know who owns it
            self.ai.owner = self
    
    def increase_speed(self):
        self.speed += 1
        if self.speed > 3:
            self.speed = 3
    def decrease_speed(self):
        self.speed -= 1
        if self.speed < 1:
            self.speed = 1
    
    def decrease_food(self):
        self.food -= 1
            
        
    @property
    def char(self):
        if self.boat:
            return self._char_b
        else:
            return self._char_p
            
    def move(self, dx, dy):
        '''moves the object if not blocked'''
        
        a = self.x + dx
        b = self.y + dy
        
        if a < 0:
            a += MAP_WIDTH
        elif a >= MAP_WIDTH:
            a -= MAP_WIDTH
    
        if b < 0:
            b += MAP_HEIGHT
        elif b >= MAP_HEIGHT:
            b -= MAP_HEIGHT
    
        #move by the given amount, if the destination is not blocked
        if not self.boat and not is_blocked(a,b):
            self.x = a
            self.y = b
                       
        elif self.boat:
            self.x = a
            self.y = b
            
    def distance_to(self, other):
        '''returns the distance of object to another object'''
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        '''returns the distance of object to some coordinates'''
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def send_to_back(self):
        '''make this object be drawn first, so all others appear above it if they're in the same tile.'''
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def draw(self):
        '''draws the object, only called by render_all'''
        
        mod_x = BOAT_WINDOW_X
        mod_y = BOAT_WINDOW_Y
            
        #only show if it's visible to the player; or it's set to "always visible" and on an explored tile
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            #print
            (x, y) = camera.to_camera_coordinates(self.x, self.y)
            if x is not None:
                #set the color and then draw the character that represents this object at its position
                #libtcod.console_set_default_foreground(console, self.color)
                #libtcod.console_put_char(console, x, y, self.char, libtcod.BKGND_NONE)
                if self.boat:
                    T.color('#8B4513')
                    T.print_(x+mod_x, y+mod_y, '_')
                    T.layer(3)
                    T.color(self.color)
                    T.print_(x+mod_x, y+mod_y, self.char)
                    T.layer(0)
                else:
                    T.color(self.color)
                    T.print_(x+mod_x, y+mod_y, self.char)
              
                
class PlayerAI:
    '''Is actually the one who plays TPB. Needed to be scheduled. Takes keyboard input and calls handle_keys
    Renders screen and exits game, kind of the actual main loop together with play_game.
    '''
    def __init__(self, ticker, speed):
        self.ticker = ticker
        self.speed = speed
        self.ticker.schedule_turn(self.speed, self)
        
    def take_turn(self):
        '''called by scheduler on the players turn, contains the quasi main loop'''
        global key, mouse, fov_recompute, rain
        action_speed = self.speed
        
        while True:
            #libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
            #render the screen
            render_all()
            T.refresh()
            key = T.read()
            #libtcod.console_flush()
            
            player_action = handle_keys()
            
            if player_action == 'exit' or game_state == 'exit':
                break
                main_menu()
            
            if player_action != 'didnt-take-turn':
                fov_recompute = True
                break
        
        
        if self.owner.boat: 
            for obj in sky_objects:
                if obj.color == 'white':
                    obj.move()
            
            check_rain()
            
            if clock[1] == 0 and rain > 0:
                rain -= 1
                
            if libtcod.random_get_int(0,0,100) == 1:
                change_wind()
        
            advance_clock()
                                        
            if clock == [12,0]:
                player.decrease_food()
                if player.food < 0:
                    player_death('starvation')
                else:
                    message('Lunchtime! You eat a ration.')
                
            if clock == [20,0] and libtcod.random_get_int(0,0,100) < 40:
                change_wind()
                
        if not moves:
            player_death('being stranded')
        
        
        self.ticker.schedule_turn(action_speed, self)
        
def check_rain():
    global rain
    
    if rain == 0:
        if libtcod.random_get_int(0,0,100) == 2:
            rain = libtcod.random_get_int(0,4,8)
            message('It started to rain.', 'blue')
    
                        
class BasicMonster:
    '''AI for a basic monster. Schedules the turn depending on speed and decides whether to move or attack.
    Owned by all monsters apart from bosses.
    '''
    def __init__(self, ticker, speed):
        self.ticker = ticker
        self.speed = speed
        self.ticker.schedule_turn(self.speed, self)
    
    def take_turn(self):
        '''checks whether monster and player are still alive, decides on move or attack'''
        #a basic monster takes its turn.
        monster = self.owner
        
        if not monster.fighter: #most likely because monster is dead
            return
        #stop when the player is already dead
        if game_state == 'dead':
            return
        
        #move towards player if far away
        if monster.distance_to(player) >= 2:
            (x,y) = monster.x, monster.y
            monster.move_towards(player.x, player.y)
            if monster.x == x and monster.y == y: #not moved?
                monster.move(libtcod.random_get_int(0,-1,1), libtcod.random_get_int(0,-1,1)) #try again randomly
            
        #close enough, attack! (if the player is still alive.)
        elif player.fighter.hp > 0:
            monster.fighter.attack(player)
        
        #schedule next turn
        self.ticker.schedule_turn(self.speed, self)            
            
                   
class DayNighTime:
    '''Timer object which runs in highscore mode only controling monster difficulty by turns passed, by increasing dungeon level'''
    def __init__(self, ticker, speed=1000): #every approx 150 turns the dungeon level is increased
        self.ticker = ticker
        self.speed = speed
        self.ticker.schedule_turn(self.speed, self)
        
    def take_turn(self):
        global dungeon_level
        
        #influences the GeneratorAIEnd for monster spaw decision
        dungeon_level += 1

        self.ticker.schedule_turn(self.speed, self)            
      

def random_choice_index(chances):  
    '''choose one option from list of chances, returning its index
    the dice will land on some number between 1 and the sum of the chances'''
    dice = libtcod.random_get_int(0, 1, sum(chances))

    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1

def random_choice(chances_dict):
    '''choose one option from dictionary of chances, returning its key'''
    chances = chances_dict.values()
    strings = chances_dict.keys()

    return strings[random_choice_index(chances)]

def from_dungeon_level(table):
    '''returns a value that depends on level. the table specifies what value occurs after each level, default is 0.'''
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0
   
class Camera:
    def __init__(self, x, y, width, height, map_width, map_height):
        self.x = x
        self.y = y
        self.x_buffer = 0
        self.y_buffer = 0
        self.width = width#CAMERA_WIDTH
        self.height = height#CAMERA_HEIGHT
        self.map_width = map_width#MAP_WIDTH
        self.map_height = map_height#MAP_HEIGHT
        self.global_ = True
        self.focus_island = None
        
    def switch_to_land(self, x, y, width, height):
        #store ships position
        self.x_buffer = self.x
        self.y_buffer = self.y
        #set new position
        self.x = x
        self.y = y
        self.width = 10
        self.height = 10
        #set new map
        self.map_width = width
        self.map_height = height
        self.global_ = False
        
    def switch_to_globe(self):
        #restore buffer
        if self.x_buffer:
            self.x = self.x_buffer
            self.y = self.y_buffer
        #set global map
        self.width = CAMERA_WIDTH
        self.height = CAMERA_HEIGHT
        self.map_width = MAP_WIDTH
        self.map_height = MAP_HEIGHT
        self.global_ = True
        
    def move_camera(self, target_x, target_y):
        global fov_recompute
     
        #new camera coordinates (top-left corner of the screen relative to the map)
        x = target_x - self.width / 2  #coordinates so that the target is at the center of the screen
        y = target_y - self.height / 2
     
        #make sure the camera doesn't see outside the map
        # if x < 0: x = self.map_width - x #0
        # if y < 0: y = self.map_width - y #0
        # # #if x > self.map_width - self.width - 1: x = self.map_width - self.width - 1
        # #if y > self.map_height - self.height - 1: y = self.map_height - self.height - 1
    
        # if x > self.map_width - self.width - 1: x -= self.map_width
        # if y > self.map_height - self.height - 1: y -= self.map_height
     
        if x != self.x or y != self.y: fov_recompute = True
        
        (self.x, self.y) = (x, y)
        
    def to_camera_coordinates(self, x, y):
        #convert coordinates on the map to coordinates on the screen
        (x, y) = (x - self.x, y - self.y)
        
        
        if x < 0: 
            x = self.map_width + x
        elif x > self.map_width-1:
            x = x - self.map_width
        if y < 0: 
            y = self.map_height + y
        elif y > self.map_height-1:
            y = y - self.map_height
        
        if (x < 0 or y < 0 or x >= self.width or y >= self.height):
            return (None, None)  #if it's outside the view, return nothing
        
        return (x, y) 
        
            
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def make_map(var):
    '''selects which map to make depending on dungeon level. var is doing nothing. 
    Highscore mode is executed on dungeon levels > 4'''
    global dungeon_level
    global map, sky, sky_objects, ISLANDS, TREASURE_INDEX
    
    '''make sky'''
    
    sky = [[ tiles.Tile(True, type = 'sky')
             for y in range(SKY_HEIGHT) ]
           for x in range(SKY_WIDTH) ]
    
    # #test
    # sky[0][0].change_type('grass')
    # sky[SKY_WIDTH-1][SKY_HEIGHT-1].change_type('grass')
    
    for j in range(100):
        star = Star(libtcod.random_get_int(0, 0, SKY_WIDTH), libtcod.random_get_int(0, 0, SKY_HEIGHT), char='.', brightness=libtcod.random_get_int(0,1,3))
        sky_objects.append(star)
    for j in range(100):
        star = Star(libtcod.random_get_int(0, 0, SKY_WIDTH), libtcod.random_get_int(0, 0, SKY_HEIGHT), char='*', brightness=libtcod.random_get_int(0,4,7))
        sky_objects.append(star)
        
    
    alphabet = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    random.shuffle(alphabet)
    
    # #four corners
    # mount_constellation(constellations.cons[alphabet.pop()], 0, 0, 7)
    # mount_constellation(constellations.cons[alphabet.pop()], 50, 50, 7)
    # mount_constellation(constellations.cons[alphabet.pop()], 50, 0, 7)
    # mount_constellation(constellations.cons[alphabet.pop()], 0, 50, 7)
    
    #middle
    mount_constellation(constellations.cons[alphabet.pop()], 15, 15, 10)
    
    #5 random
    for i in range(10):
        mount_constellation(constellations.cons[alphabet.pop()], libtcod.random_get_int(0, 0, SKY_WIDTH), libtcod.random_get_int(0, 0, SKY_HEIGHT), libtcod.random_get_int(0, 5, 11))
    
    make_clouds()
    
    '''make ocean'''
    make_ocean()
    
    player.x = 2
    player.y = 2
    
    #create one treasure on each island
    for island in ISLANDS:
        create_treasure(island)
    
    #create an index for each treasure
    TREASURE_INDEX = []
    for number in range(len(ISLANDS)):
        TREASURE_INDEX.append(number)
    random.shuffle(TREASURE_INDEX)
        
    #create a village and elder per island and assign one index each
    for island in ISLANDS:
        create_village(island)
    
def is_blocked(x, y):
    '''called to check if coordinates are blocked by
    -blocked tile
    returns boolean
    '''
    
    #first test the map tile
    if not player.boat:
        if map[x][y].blocked:
            return True
        #now check for any blocking objects
        for object in objects:
            if object.blocks and object.x == x and object.y == y:
                return True        
    return False

def make_clouds():
    global sky_objects
    
    for i in range(80):
        speed = 1
        if libtcod.random_get_int(0, 0, 100) <= 10:
            speed = 2
            
        x = libtcod.random_get_int(0, 10, SKY_WIDTH-10)
        y = libtcod.random_get_int(0, 10, SKY_HEIGHT-10)
        
        #cumulus, cirrus and nebula
        chance = libtcod.random_get_int(0, 0, 100)
        if chance < 30:
            #cumulus
            for j in range(2):
                cloud = Cloud(x-2+j, y-1, char='#',speed=speed)
                sky_objects.append(cloud)
            for j in range(8):
                cloud = Cloud(x-3+j, y, char='#',speed=speed)
                sky_objects.append(cloud)
            for j in range(12):
                cloud = Cloud(x-4+j, y+1, char='#',speed=speed, color_dawn='light orange', color_dusk='light red')
                sky_objects.append(cloud)
                
        elif chance >= 30 and chance < 60:
            #cirrus
            for j in range(6):
                cloud = Cloud(x-4+j, y-1, char='[U+2248]',speed=speed, color_dawn='light orange', color_dusk='light red')
                sky_objects.append(cloud)
            for j in range(7):
                cloud = Cloud(x-1+j, y, char='[U+2248]',speed=speed,color_dawn='light orange', color_dusk='light red')
                sky_objects.append(cloud)

#------------------------------------------------------------------------------------------
   
def find_island(x,y):
    #find closest enemy, up to a maximum range, and in the player's FOV
    closest_island = None
    closest_dist = 200  #start with big range

    for island in ISLANDS:
        (a,b) = island.center()
        #calculate distance between this object and the player
        dist = distance(x,y,a,b)
        if dist < closest_dist:  #it's closer, so remember it
            closest_island = island
            closest_dist = dist
    return closest_island
   
   
def make_ocean():
    global map, ISLANDS
    #fill map with "blocked wall" tiles
    map = [[ tiles.Tile(True, type = 'water')
             for y in range(MAP_HEIGHT) ]
           for x in range(MAP_WIDTH) ]
           
    #testing
    #map[0][0].change_type('grass')
    #map[MAP_WIDTH-1][MAP_HEIGHT-1].change_type('grass')
    
    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        #"Island" class makes rectangles easier to work with
        new_room = Island(x, y, w, h)

        #run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed: #THIS??????
        
            #this means there are no intersections, so this room is valid

            #"paint" it to the map's tiles
            create_island(new_room)
            
            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()

            rooms.append(new_room)
            
            num_rooms += 1
        
        else:
            pass
                 
    # for i in rooms:
        # (a,b) = i.center()
        # sky[a/SKY_FACTOR_X][b/SKY_FACTOR_Y].char_light = 'X'
        # sky[a/SKY_FACTOR_X][b/SKY_FACTOR_Y].color_light = 'yellow'
            
def create_island(room):
    global map, ISLANDS
    
    island = [[ tiles.Tile(True, type = 'water')
             for y in range(room.h) ]
           for x in range(room.w) ]
            
    points = []
    
    # from 40 to 80
    r = (room.w + room.h)/8 #5 to 10 points
    
    for p in range(r):
        x = random.randint(7,room.w-7)
        y = random.randint(7,room.h-7)
        points.append((x,y))
        
    for i in points:
        for y2 in range(room.h):
            for x2 in range(room.w):
                if distance(i[0],i[1],x2,y2) <= 4:
                    if libtcod.random_get_int(0,0,100) <= 60:
                        island[x2][y2].change_type('grass')
           
    island = cellular_iteration(island, room.w, room.h)
    
    # from c_iteration. one tiles remains land, manually change
    island[1][1].change_type('water')
    
    island = create_beach(island, room.w, room.h)
    
    #store it for later
    room.smallmap = island
    ISLANDS.append(room)
    
    #print it to the map
    for l in range(room.w):
        for m in range(room.h):
            map[room.x1+l][room.y1+m].change_type(island[l][m].type)
            
def create_beach(island, w, h):
    island_c = island[:]
    
    for x in range(w):
        for y in range(h):
            if island[x][y].type == 'grass':
                list = tile_neighbors(x, y, island, w, h)
                for i in list:
                    if i.type == 'water' and libtcod.random_get_int(0,0,10) < 8:
                        island_c[x][y].change_type('beach')
    return island_c
   
def create_treasure(island):
    
    #create a treasure
    while True:
        a = libtcod.random_get_int(0, 1, island.w-1)
        b = libtcod.random_get_int(0, 1, island.h-1)
        
        if map[a+island.x1][b+island.y1].type == 'water':
            pass
            
        else:
            map1 = 'K'
            name = make_map_name()
            treasure = Treasure(island.x1+a, island.y1+b, name, map1)
            TREASURES.append(treasure)
            random.shuffle(TREASURES)
            break
    
   
def create_village(island):
    global TREASURE_INDEX
    #create a village and elder
    while True:
        a = libtcod.random_get_int(0, 1, island.w-1)
        b = libtcod.random_get_int(0, 1, island.h-1)
        
        fail = False
        for i in range(-1,2):
            for j in range (-1,2):
                if map[a+island.x1+i][b+island.y1+j].type == 'water':
                    fail = True
            
        if not fail:
            while True:
                
                k = [libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1)]
                l = [libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1)]
                m = [libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1)]
                
                overlap = False
                for treasure in TREASURES:
                    if a+island.x1+k[0] == treasure.x and b+island.y1+k[1] == treasure.y:
                        overlap = True
                
                if not k == l and not k == m and not m == l and not overlap:
                    break
                
            number = TREASURE_INDEX.pop()
            obj = Object(a+island.x1+k[0], b+island.y1+k[1], '@', 'Elder', 'magenta', index=number)
            objects.append(obj)
            obj = Object(a+island.x1+l[0], b+island.y1+l[1], '[U+03A0]', 'Oracle', 'grey')
            objects.append(obj)
            obj = Object(a+island.x1+m[0], b+island.y1+m[1], '[U+0394]', 'Building', 'grey')
            objects.append(obj)
            break

def make_map_name():
    treasure = ['Coins', 'Gold', 'Silver', 'Brass', 'Bars', 'Assets', 'Treasure']
    random.shuffle(treasure)
    owner = ['Rodney', 'Ringo', 'Ratham', 'Roger', 'Robert', 'Rakham', 'Redbeard', 'Redhat', 'Rorey', 'Randy']
    random.shuffle(owner)
    attribute = ['red', 'angry', 'hairy one', 'mad', 'ruthless', 'lame', 'furious']
    random.shuffle(attribute)
    return treasure[0] + ' of ' + owner[0] + ' the ' + attribute[0]
   
def make_cave():
    '''starting function to make cellular automaton for cave level'''
    global map
    #fill map with "blocked wall" tiles
    map = [[ tiles.Tile(True, type = 'empty')
             for y in range(MAP_HEIGHT) ]
           for x in range(MAP_WIDTH) ]
    
    #randomly blank 55 % of the tiles
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if libtcod.random_get_int(0,0,100) <= 40:
                map[x][y].change_type('ice')

    #5 iterations ;)
    map = cellular_iteration(map)
    map = cellular_iteration(map)
    map = cellular_iteration(map)
    map = cellular_iteration(map)
    map = cellular_iteration(map)
     
def cellular_iteration(map, w, h):
    '''the iteration function over the random map. 4-5 rule chooses depending on neighbors''' 
    map_c = map[:]
    for x in range(1,w-1):
        for y in range(1,h-1):
            if map[x][y].type == 'water':
                neighbors = tile_neighbors(x,y,map, w, h)
                if count_empty(neighbors) < 4:
                    map_c[x][y].change_type('grass')
            
            elif map[x][y].type == 'grass':
                neighbors = tile_neighbors(x,y,map, w, h)
                if count_empty(neighbors) >= 5:
                    map_c[x][y].change_type('water')
    return map_c
    
def tile_neighbors(x, y, map, w, h):
    '''returns all neighbors of a tile x,y in map. part of cellular automaton'''
    neighbors = []
    for i in range(-1,2):
        for j in range(-1,2):
            if i == 0 and j == 0:
                continue
            if x+i > 0 and x+i < w and y+j > 0 and y+j < h:
                neighbors.append(map[x+i][y+j]) 
    return neighbors
    
def count_empty(list_of_neighbors):
    '''returns number of empy tiles in list of neighbors. part of cellular automaton'''
    empty = 0
    for i in list_of_neighbors:
        if i.name == 'water':
            empty += 1
    return empty
   
def place_cave_objects():
    '''places the generators and players in the cave. has to check for non blocked spots around the starting area'''
    global objects
    
    generators = ['g','g','g','i','i','i','i','i']
    random.shuffle(generators)
    
    coordinates = [ [4,4], [25,4], [46,4],
                    [4,19,], [46,19],
                    [4,36], [25,36], [46,36]
                    ]
    random.shuffle(coordinates)
    
    while generators:
        i = generators.pop()
        j = coordinates.pop()
        if i == 'g':
            (x,y) = j
            if is_blocked(j[0],j[1]):
                (x,y) = find_non_blocked(j[0],j[1])
            
            objects.append(create_object('cleft', x, y))
    
    if not is_blocked(25,20):
        player.x = 25
        player.y = 20
    else:
        (x,y) = find_non_blocked(25,20)
        player.x = x
        player.y = y
    
    
def find_non_blocked(x, y):
    '''checks a 10x10 square for starting area, whether a free spot can be found to set player/generator'''
    #gather all spots
    set = []
    for i in range(-7,7):
        for j in range(-7,7):
            set.append([i,j])
    
    while True:
        d = set.pop() #check all spots
        if not is_blocked(x+d[0],y+d[1]):
            return x+d[0],y+d[1]
            break
        if not d:
            return 0,0
            break
  
#--------------------------------------------------------------------------------------------   

def get_map_char(location_name, x, y):
    '''helper function to check maps.py for list with location_name checks coordinates and returns char
    e.g. maps.temple and would give maps.temple[y][x] == "+"'''
    i = getattr(maps, location_name)
    return i[y][x]
   
def make_preset_map(location_name):
    '''fills map with tiles according to layout in maps.py using get_map_char and maps.type_to_char'''
    global map
    map = []
    
    #fill map with tiles according to preset maps.py (objects kept blank)
    map = [[ tiles.Tile(True, type = maps.char_to_type( get_map_char(location_name, x, y ) ) )
             for y in range(MAP_HEIGHT) ]
           for x in range(MAP_WIDTH) ]  
    
def make_lavapools(map):
    '''make heightmap of 3 height levels and put it on map as three levels depp of lava'''
    test = libtcod.heightmap_new(MAP_WIDTH, MAP_HEIGHT)
    test2 = libtcod.heightmap_new(MAP_WIDTH, MAP_HEIGHT)
    test3 = libtcod.heightmap_new(MAP_WIDTH, MAP_HEIGHT)
    
    noise = libtcod.noise_new(2)
    
    libtcod.heightmap_add_fbm(test2, noise, 1, 1, 0.0, 0.0, 10, 0.0, 1.0)
    libtcod.heightmap_add_fbm(test3, noise, 2, 2, 0.0, 0.0,  5, 0.0, 1.0)
    
    libtcod.heightmap_multiply_hm(test2, test3, test)
    libtcod.heightmap_normalize(test, mi=0, ma=1)
    
    #assign different levels 0-4 to hightmap floats
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if libtcod.heightmap_get_value(test, x, y) < 0.2:
                libtcod.heightmap_set_value(test, x, y, 0)
            elif libtcod.heightmap_get_value(test, x, y) >= 0.2 and libtcod.heightmap_get_value(test, x, y) < 0.4:
                libtcod.heightmap_set_value(test, x, y, 1)
            elif libtcod.heightmap_get_value(test, x, y) >= 0.4 and libtcod.heightmap_get_value(test, x, y) < 0.6:
                libtcod.heightmap_set_value(test, x, y, 2)
            elif libtcod.heightmap_get_value(test, x, y) >= 0.6 and libtcod.heightmap_get_value(test, x, y) < 0.8:
                libtcod.heightmap_set_value(test, x, y, 3)
            elif libtcod.heightmap_get_value(test, x, y) >= 0.8:
                libtcod.heightmap_set_value(test, x, y, 4)
    
    #create a differnet color darkness to lava levels
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            for z in range(int(int(libtcod.heightmap_get_value(test, x, y))-1)):
                map[x][y].change_type('lava')
                if z < 1:
                    map[x][y].color_light = 'flame'
                elif z < 2:
                    map[x][y].color_light = 'darker_flame'
                elif z < 3:
                    map[x][y].color_light = 'darkest_flame'
    
    #clean up and return map
    libtcod.heightmap_delete(test)
    return map

def place_preset_objects(location_name):
    '''checks maps.py and generates objects from the respective character. Such as generators and player startin position'''
    global objects
    
    #the list of objects with just the player
    objects = [player]
    
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            i = get_map_char(location_name, x, y)
            
            if i == 'r': #not used for testing only
                create_monster('rat', x, y)
            
            elif i == 'p':
                player.x = x
                player.y = y

                
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def create_monster(type, x, y):
    '''function to easily create a monster of a type at coordinates x,y
    Translates the parameters of monsters.py and puts components ai, fighter,death_function, stats together
    '''
    # storage of data from monsters.py
    a = getattr(monsters, type)
 
    # creating fighter component
    fighter_component = Fighter(hp=a['hp'], damage=a['damage'], death_function=DEATH_DICT[a['death_function']])                
    
    #creating ai needs more info because of arguments
    if a['ai'] == 'BasicMonster':
        ai_component = BasicMonster(ticker, speed=a['speed'])
    elif a['ai'] == 'NoisyMonster':
        ai_component = NoisyMonster(ticker, speed=a['speed'])

    #create the monster    
    monster = Object(x, y, a['char'], a['name'], getattr(libtcod, a['color']), blocks=True, fighter=fighter_component, ai=ai_component)
    objects.append(monster)
      
def create_object(type, x=0, y=0):
    '''function to easily create an object of a type at coordinates x,y
    Translates the parameters of monsters.py and puts components together
    '''
    a = getattr(monsters, type)
    
    ai_component = None
    
    if 'ai' in a:
        if a['ai'] == 'GeneratorAI':
            ai_component = GeneratorAI(ticker)
        if a['ai'] == 'GeneratorAIEnd':
            ai_component = GeneratorAIEnd(ticker)
    
    obj = Object(x, y, a['char'], a['name'], getattr(libtcod, a['color']), ai=ai_component )
   
    if 'blocks' in a:
        obj.blocks = a['blocks']
        
    #is returned and needs to be appended to objects
    return obj

#-----------------------------------------------------------------------------------------------------------------            
            
def get_names_under_mouse():
    '''returns a string with the names of all objects under the mouse plus their stats if fighters'''
    (x, y) = (T.state(T.TK_MOUSE_X), T.state(T.TK_MOUSE_Y))
   
    (x, y) = (camera.x + x - BOAT_WINDOW_X, camera.y + y - BOAT_WINDOW_Y)  #from screen to map coordinates
   
    
    # if x < 0: 
        # x = MAP_WIDTH + x
    # elif x > MAP_WIDTH-1:
        # x = x - MAP_WIDTH
    # if y < 0: 
        # y = MAP_HEIGHT + y
    # elif y > MAP_HEIGHT-1:
        # y = y - MAP_HEIGHT
    
    #print 'cam',x,y
    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in reversed(objects)
             if obj.x == x and obj.y == y ]
    
    # #get terrain type unter mouse (terrain, walls, etc..)
    # if libtcod.map_is_in_fov(fov_map, x, y):
        # if not map[x][y].name == 'empty':
            # names.append(map[x][y].name)
    if names:
        pile = names
        i = 0
        for thing in pile:    
            pos = x+1+BOAT_WINDOW_X+10
            #if x >= 60:
            if x + len(thing) >= SCREEN_WIDTH:
                pos = x-len(thing)
            T.print_(pos, y+i+1+BOAT_WINDOW_Y+5, thing)
            i += 1
    #names = ', '.join(names)  #join the names, separated by commas
    #return names#.capitalize()
    
def render_all():
    '''main render function for consoles con (map), panel (messages), column (keys, directoins) plus mouseover console
    draws all objects and tiles in FOV
    '''
    global fov_map, fov_recompute, mouse, dungeon_level, clock, rain
    
    T.layer(0)
    
    vision = 15
    if clock[0] > 19 or clock[0] <= 5:
        vision = 13
    
    libtcod.map_compute_fov(fov_map, player.x, player.y, vision, FOV_LIGHT_WALLS, FOV_ALGO)
    T.clear()
    
    camera.move_camera(player.x, player.y)
    
   
    if fov_recompute:
       
        for y in range(camera.height):
            for x in range(camera.width):
                (map_x, map_y) = (camera.x + x, camera.y + y)
                
                
                #if libtcod.map_is_in_fov(fov_map, map_x, map_y):
                
                if player.distance(map_x,map_y) < vision:
                #it's visible
                    if map_x > MAP_WIDTH-1: 
                        map_x -= MAP_WIDTH
                    elif map_x < 0:
                        map_x += MAP_WIDTH
                        
                    if map_y > MAP_HEIGHT-1: 
                        map_y -= MAP_HEIGHT
                    elif map_y < 0:
                        map_y += MAP_HEIGHT
                    
                    #print 'map',map_x,map_y
                    
                    color_a = map[map_x][map_y].color_light
                    T.print_(x+BOAT_WINDOW_X, y+BOAT_WINDOW_Y, '[color=' + color_a + ']' + map[map_x][map_y].char_light)
                    map[map_x][map_y].explored = True
                    
#draw all objects in the list, except the player. we want it to
#always appear over all other objects! so it's drawn later.
    
    
    
    
        # for treasure in TREASURES:
            # treasure.draw()
               
#------------------------------------------------------------------------------------------ 
    sky_cam.move_camera(player.x/SKY_FACTOR_X, player.y/SKY_FACTOR_Y)
   
    for y in range(SKYCAM_HEIGHT):
        for x in range(SKYCAM_WIDTH):
            (map_x, map_y) = ((sky_cam.x) + x, (sky_cam.y) + y)
            
            if map_x > SKY_WIDTH-1: 
                map_x -= SKY_WIDTH
            elif map_x < 0:
                map_x += SKY_WIDTH
                
            if map_y > SKY_HEIGHT-1: 
                map_y -= SKY_HEIGHT
            elif map_y < 0:
                map_y += SKY_HEIGHT
            
            #if map_x < SKY_WIDTH and map_y < SKY_HEIGHT:
            color_a = sky_color(map_x,map_y)#sky[map_x][map_y].color_light
            T.print_(x+SKY_WINDOW_X, y+SKY_WINDOW_Y, '[color=' + color_a + ']' + sky[map_x][map_y].char_light)
        # libtcod.console_blit(sky_one, 0, 0, 30, 10, 0, 1, 0)    
    for object in sky_objects:
        object.draw()
    
    if rain > 0:
        char = '|'
        if wind[0] == -1:
            char = '/'
        elif wind[0] == 1:
            char = '\\'
        for i in range(50):
            T.print_(libtcod.random_get_int(0,15,65), libtcod.random_get_int(0,0,SCREEN_HEIGHT), '[color=blue]' + char)
    
#------------------------------------------------------------------------------------------ 
    
    if player.boat:
        (x, y) = camera.to_camera_coordinates(player.x, player.y)
            
        for move in moves:
            if move[4] == 'land':
                T.color('green')
            else:
                T.color('blue')
            T.print_(x+BOAT_WINDOW_X+move[0], y+BOAT_WINDOW_Y+move[1], move[3])
    
        #show ships trail in water 
        (a, b) = camera.to_camera_coordinates(player.old_x, player.old_y)
        libtcod.line_init(x+BOAT_WINDOW_X, y+BOAT_WINDOW_Y, a+BOAT_WINDOW_X, b+BOAT_WINDOW_Y)
        while True:
            (a, b) = libtcod.line_step()
            if not a: 
                break
            T.print_(a, b, '[color=light blue]=')
            
    
            
#------------------------------------------------------------------------------------------ 
    
    draw_windrose(1)
     
    draw_clock()
    
    #T.print_(0, 0, '[color=white]' + str(player.x) + ',' + str(player.y))
    
    color = 'white'
    if player.food <= 2:
        color = 'red'
    
    T.print_(60, 18, '[color=' +color + ']Food: ' + str(player.food) + '/7')
    
    speed = ''
    if player.boat:
        for i in range(player.speed):
            speed += '> '
    T.print_(10, 18, '[color=white]Speed: ' + speed)
    
    inventory = 0
    found = 0
    for t in TREASURES:
        if t.map_owned:
            inventory += 1
        if t.found:
            found += 1
    T.print_(10, 20, '[color=white]Maps: ' + str(inventory) + '/' + str(len(TREASURES)))
    T.print_(60, 20, '[color=white]Treasures: '+ str(found) + '/' + str(len(TREASURES))) 
    
   
#------------------------------------------------------------------------------------------ 
   
    list_to_print = []
    temp = ''
    reversed = game_msgs[::-1]
    
    if reversed:    
        for msg in reversed:
            temp += msg[0] + ' '
            if len(temp) <= SCREEN_WIDTH:
                list_to_print.insert(0, msg)
            else:
                remains = msg[0][:len(temp)-SCREEN_WIDTH:-1]
                list_to_print.insert(0, (remains[::-1], msg[1]))
                break
        x = 0
        for (line, color) in list_to_print:
            T.color(color)
            T.print_(x, 23, line)
            x += len(line)+1

#-------------------------------------------------------------------------------------------
    for object in objects:
        if object != player:
            object.draw()
    player.draw()
    
#-------------------------------------------------------------------------------------------
   
def get_number_for_move(move):
    
    if (move[0] == 1 and move[1] == 0) or (move[0] == 2 and move[1] == 0) or (move[0] == 3 and move[1] == 0):
        return '6'
    elif (move[0] == 1 and move[1] == 1) or (move[0] == 2 and move[1] == 2) or (move[0] == 3 and move[1] == 3):
        return '3'
    elif (move[0] == 1 and move[1] == -1) or (move[0] == 2 and move[1] == -2) or (move[0] == 3 and move[1] == -3):
        return '9'
    elif (move[0] == -1 and move[1] == -1) or (move[0] == -2 and move[1] == -2) or (move[0] == -3 and move[1] == -3):
        return '7'
    elif (move[0] == -1 and move[1] == 0) or (move[0] == -2 and move[1] == 0) or (move[0] == -3 and move[1] == 0):
        return '4'
    elif (move[0] == -1 and move[1] == 1) or (move[0] == -2 and move[1] == 2) or (move[0] == -3 and move[1] == 3):
        return '1'
    elif (move[0] == 0 and move[1] == 1) or (move[0] == 0 and move[1] == 2) or (move[0] == 0 and move[1] == 3):
        return '2'
    elif (move[0] == 0 and move[1] == -1) or (move[0] == 0 and move[1] == -2) or (move[0] == 0 and move[1] == -3):
        return '8'
    else:
        return 'f'

def sky_color(map_x,map_y):
    global clock
    color = sky[map_x][map_y].color_light
    
    
    if clock[0] == 19:
        color = 'red'
    elif clock[0] > 19 or clock[0] <= 5:
        color = 'black'
    elif clock[0] == 6:
        color = 'orange'
    
    if rain > 0 and clock[0] <= 19 and clock[0] > 5:
        color = 'light grey'
    
    return color

def make_GUI_frame(console, x, y, dx, dy):
    '''creates a white frame line around the console of dimensions x,y,dx,dy'''
    #sides
    for i in range(dx-1):
        libtcod.console_print_ex(console, i, 0, libtcod.BKGND_NONE, libtcod.LEFT, chr(196))
    for i in range(dx-1):
        libtcod.console_print_ex(console, i, dy-1, libtcod.BKGND_NONE, libtcod.LEFT, chr(196))
    for i in range(dy-1):
        libtcod.console_print_ex(console, 0, i, libtcod.BKGND_NONE, libtcod.LEFT, chr(179))
    for i in range(dy-1):
        libtcod.console_print_ex(console, dx-1, i, libtcod.BKGND_NONE, libtcod.LEFT, chr(179))

    #corners
    libtcod.console_print_ex(console, 0, 0, libtcod.BKGND_NONE, libtcod.LEFT, chr(218))
    libtcod.console_print_ex(console, dx-1, 0, libtcod.BKGND_NONE, libtcod.LEFT, chr(191))
    libtcod.console_print_ex(console, 0, dy-1, libtcod.BKGND_NONE, libtcod.LEFT, chr(192))
    libtcod.console_print_ex(console, dx-1, dy-1, libtcod.BKGND_NONE, libtcod.LEFT, chr(217))

# def message(new_msg, color = 'white'):
    # '''creates a message in the panel console of text ad color'''
    # #split the message if necessary, among multiple lines
    # new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    # for line in new_msg_lines:
    
        # #if the buffer is full, remove the first line to make room for the new one
        # if len(game_msgs) == MSG_HEIGHT:
            # del game_msgs[0]

        # #add the new line as a tuple, with the text and the color
        # game_msgs.append( (line, color) )

def message(new_msg, color = 'white'):
    '''creates a message in the panel console of text ad color'''
    
    game_msgs.append( (new_msg, color) )
        
def get_directions_from_last_move():
    
    out = []
    if player.last_direction == [1,0]:
        out = [[1,-1],[1,0],[1,1]]
    elif player.last_direction == [1,1]:
        out = [[1,0],[1,1],[0,1]]
    elif player.last_direction == [1,-1]:
        out = [[0,-1],[1,-1],[1,0]]
    
    elif player.last_direction == [-1,0]:
        out = [[-1,-1],[-1,0],[-1,1]]
    elif player.last_direction == [-1,-1]:
        out = [[-1,-1],[-1,0],[0,-1]]
    elif player.last_direction == [-1,1]:
        out = [[-1,0],[-1,1],[0,1]]
    
    elif player.last_direction == [0,1]:
        out = [[-1,1],[0,1],[1,1]]
    
    elif player.last_direction == [0,-1]:
        out = [[-1,-1],[0,-1],[1,-1]]
    
    # elif player.last_direction == [0,0]:
        # out = [[-1,-1],[0,-1],[1,-1]]
    
    return out
   
   
def sort_moves(speed, wind):
        
    move_map = []
    
    moves = get_directions_from_last_move()
    
    for i in range(1,speed+1):
        for j in moves:
            u = i * j[0]
            v = i * j[1]
            move_map.append([u,v]) #contains 3 to 6 moves with two parameters x,y and implicitly speed by abs()
    
    for move in move_map[:]:
        
        if wind == [1,0,1]:
            if speed == 1:        
                if move == [1,0]:
                    move.append('a')
                    move.append(key_set['right'])
                elif move == [1,-1]:
                    move.append('a')
                    move.append(key_set['upright'])
                elif move == [1,1]:
                    move.append('a')
                    move.append(key_set['downright'])
                    
                elif move == [0,1]:
                    move.append('k')
                    move.append(key_set['down'])
                elif move == [0,-1]:
                    move.append('k')
                    move.append(key_set['up'])
                elif move == [-1,-1]:
                    move.append('k')
                    move.append(key_set['upleft'])
                elif move == [-1,1]:
                    move.append('k')
                    move.append(key_set['downleft'])
                elif move == [-1,0]:
                    move.append('d')
                    move.append(key_set['left'])
            
            
            if speed == 2:
                if move == [1,0]:
                    move.append('k')
                    move.append(key_set['left'])
                elif move == [1,-1]:
                    move.append('k')
                    move.append(key_set['downleft'])
                elif move == [1,1]:
                    move.append('k')
                    move.append(key_set['upleft'])
                    
                elif move == [0,1]:
                    move.append('d')
                    move.append(key_set['up'])
                elif move == [0,-1]:
                    move.append('d')
                    move.append(key_set['down'])
                elif move == [-1,-1]:
                    move.append('d')
                    move.append(key_set['upleft'])
                elif move == [-1,1]:
                    move.append('d')
                    move.append(key_set['downleft'])
            
                elif move == [2,0]:
                    move.append('a')
                    move.append(key_set['right'])
                elif move == [2,-2]:
                    move.append('a')
                    move.append(key_set['upright'])
                elif move == [2,2]:
                    move.append('a')
                    move.append(key_set['downright'])
                    
                elif move == [0,2]:
                    move.append('k')
                    move.append(key_set['down'])
                elif move == [0,-2]:
                    move.append('k')
                    move.append(key_set['up'])
                
                        
            if speed == 3:
                if move == [2,0]:
                    move.append('d')
                    move.append(key_set['left'])
                elif move == [2,-2]:
                    move.append('d')
                    move.append(key_set['downleft'])
                elif move == [2,2]:
                    move.append('d')
                    move.append(key_set['upleft'])
                    
                elif move == [0,2]:
                    move.append('d')
                    move.append(key_set['up'])
                elif move == [0,-2]:
                    move.append('d')
                    move.append(key_set['down'])
                elif move == [-2,-2]:
                    move.append('d')
                    move.append(key_set['upleft'])
                elif move == [-2,2]:
                    move.append('d')
                    move.append(key_set['downleft'])
            
                elif move == [3,0]:
                    move.append('k')
                    move.append(key_set['right'])
                elif move == [3,-3]:
                    move.append('k')
                    move.append(key_set['upright'])
                elif move == [3,3]:
                    move.append('k')
                    move.append(key_set['downright'])
                    
                elif move == [0,3]:
                    move.append('k')
                    move.append(key_set['down'])
                elif move == [0,-3]:
                    move.append('k')
                    move.append(key_set['up'])
            
            if len(move) < 3:
                move_map.remove(move)
        
        elif wind == [-1,0,1]:
            if speed == 1:        
                if move == [1,0]:
                    move.append('d')
                    move.append(key_set['right'])
                elif move == [1,-1]:
                    move.append('d')
                    move.append(key_set['upright'])
                elif move == [1,1]:
                    move.append('d')
                    move.append(key_set['downright'])
                    
                elif move == [0,1]:
                    move.append('k')
                    move.append(key_set['down'])
                elif move == [0,-1]:
                    move.append('k')
                    move.append(key_set['up'])
                elif move == [-1,-1]:
                    move.append('a')
                    move.append(key_set['upleft'])
                elif move == [-1,1]:
                    move.append('a')
                    move.append(key_set['downleft'])
                elif move == [-1,0]:
                    move.append('a')
                    move.append(key_set['left'])
            
            if speed == 2:
                
                if move == [1,-1]:
                    move.append('d')
                    move.append(key_set['upright'])
                elif move == [1,1]:
                    move.append('d')
                    move.append(key_set['downright'])
                    
                elif move == [0,1]:
                    move.append('d')
                    move.append(key_set['up'])
                elif move == [-1,0]:
                    move.append('k')
                    move.append(key_set['right'])
                elif move == [0,-1]:
                    move.append('d')
                    move.append(key_set['down'])
                elif move == [-1,-1]:
                    move.append('k')
                    move.append(key_set['downright'])
                elif move == [-1,1]:
                    move.append('k')
                    move.append(key_set['upright'])
            
                elif move == [-2,0]:
                    move.append('a')
                    move.append(key_set['left'])
                elif move == [-2,-2]:
                    move.append('a')
                    move.append(key_set['upleft'])
                elif move == [-2,2]:
                    move.append('a')
                    move.append(key_set['downleft'])
                    
                elif move == [0,2]:
                    move.append('k')
                    move.append(key_set['down'])
                elif move == [0,-2]:
                    move.append('k')
                    move.append(key_set['up'])
                
            if speed == 3:
                if move == [-2,0]:
                    move.append('d')
                    move.append(key_set['right'])
                elif move == [2,-2]:
                    move.append('d')
                    move.append(key_set['upright'])
                elif move == [2,2]:
                    move.append('d')
                    move.append(key_set['downright'])
                    
                elif move == [0,2]:
                    move.append('d')
                    move.append(key_set['up'])
                elif move == [0,-2]:
                    move.append('d')
                    move.append(key_set['down'])
                elif move == [-2,-2]:
                    move.append('d')
                    move.append(key_set['downright'])
                elif move == [-2,2]:
                    move.append('d')
                    move.append(key_set['upright'])
            
                elif move == [-3,0]:
                    move.append('k')
                    move.append(key_set['left'])
                elif move == [-3,-3]:
                    move.append('k')
                    move.append(key_set['upleft'])
                elif move == [-3,3]:
                    move.append('k')
                    move.append(key_set['downleft'])
                    
                elif move == [0,3]:
                    move.append('k')
                    move.append(key_set['down'])
                elif move == [0,-3]:
                    move.append('k')
                    move.append(key_set['up'])
            
            if len(move) < 3:
                move_map.remove(move)
        
        elif wind == [0,1,1]:
            if speed == 1:        
                if move == [1,0]:
                    move.append('k')
                    move.append(key_set['right'])
                elif move == [1,-1]:
                    move.append('k')
                    move.append(key_set['upright'])
                elif move == [1,1]:
                    move.append('a')
                    move.append(key_set['downright'])
                    
                elif move == [0,1]:
                    move.append('a')
                    move.append(key_set['down'])
                elif move == [0,-1]:
                    move.append('k')
                    move.append(key_set['up'])
                elif move == [-1,-1]:
                    move.append('d')
                    move.append(key_set['upleft'])
                elif move == [-1,1]:
                    move.append('a')
                    move.append(key_set['downleft'])
                elif move == [-1,0]:
                    move.append('k')
                    move.append(key_set['left'])
            
            if speed == 2:
                if move == [1,-1]:
                    move.append('d')
                    move.append(key_set['upright'])
                elif move == [1,1]:
                    move.append('k')
                    move.append(key_set['upleft'])
                    
                elif move == [0,1]:
                    move.append('k')
                    move.append(key_set['up'])
                elif move == [-1,0]:
                    move.append('d')
                    move.append(key_set['right'])
                    
                elif move == [1,0]:
                    move.append('d')
                    move.append(key_set['left'])
                
                elif move == [-1,-1]:
                    move.append('d')
                    move.append(key_set['upleft'])
                elif move == [-1,1]:
                    move.append('k')
                    move.append(key_set['upright'])
            
                elif move == [-2,0]:
                    move.append('k')
                    move.append(key_set['left'])
                elif move == [2,0]:
                    move.append('k')
                    move.append(key_set['right'])
               
                elif move == [-2,2]:
                    move.append('a')
                    move.append(key_set['downleft'])
                    
                elif move == [2,2]:
                    move.append('a')
                    move.append(key_set['downright'])
                    
                elif move == [0,2]:
                    move.append('a')
                    move.append(key_set['down'])
                
            if speed == 3:
                if move == [-2,0]:
                    move.append('d')
                    move.append(key_set['right'])
                elif move == [2,-2]:
                    move.append('d')
                    move.append(key_set['upright'])
                elif move == [2,2]:
                    move.append('d')
                    move.append(key_set['upleft'])
                    
                elif move == [0,2]:
                    move.append('d')
                    move.append(key_set['up'])
                elif move == [-2,-2]:
                    move.append('d')
                    move.append(key_set['upleft'])
                elif move == [-2,2]:
                    move.append('d')
                    move.append(key_set['upright'])
                elif move == [2,0]:
                    move.append('d')
                    move.append(key_set['left'])
            
                elif move == [-3,0]:
                    move.append('k')
                    move.append(key_set['left'])
                
                elif move == [3,0]:
                    move.append('k')
                    move.append(key_set['right'])
                
                elif move == [-3,3]:
                    move.append('k')
                    move.append(key_set['downleft'])
                
                elif move == [3,3]:
                    move.append('k')
                    move.append(key_set['downright'])
                                
                elif move == [0,3]:
                    move.append('k')
                    move.append(key_set['down'])
                
            if len(move) < 3:
                move_map.remove(move)
        
    
        elif wind == [0,-1,1]:
            if speed == 1:        
                if move == [1,0]:
                    move.append('k')
                    move.append(key_set['right'])
                elif move == [1,-1]:
                    move.append('a')
                    move.append(key_set['upright'])
                elif move == [1,1]:
                    move.append('k')
                    move.append(key_set['downright'])
                    
                elif move == [0,1]:
                    move.append('k')
                    move.append(key_set['down'])
             
                elif move == [0,-1]:
                    move.append('a')
                    move.append(key_set['up'])
                elif move == [-1,-1]:
                    move.append('a')
                    move.append(key_set['upleft'])
                elif move == [-1,1]:
                    move.append('k')
                    move.append(key_set['downleft'])
                elif move == [-1,0]:
                    move.append('k')
                    move.append(key_set['left'])
            
            if speed == 2:
                if move == [1,-1]:
                    move.append('k')
                    move.append(key_set['downleft'])
                elif move == [1,1]:
                    move.append('d')
                    move.append(key_set['downright'])
                elif move == [0,-1]:
                    move.append('k')
                    move.append(key_set['down'])
                
                elif move == [-1,0]:
                    move.append('d')
                    move.append(key_set['right'])
                    
                elif move == [1,0]:
                    move.append('d')
                    move.append(key_set['left'])
                
                elif move == [-1,-1]:
                    move.append('k')
                    move.append(key_set['downright'])
                elif move == [-1,1]:
                    move.append('d')
                    move.append(key_set['downleft'])
            
                elif move == [-2,0]:
                    move.append('k')
                    move.append(key_set['left'])
                elif move == [2,0]:
                    move.append('k')
                    move.append(key_set['right'])
                              
                elif move == [-2,-2]:
                    move.append('a')
                    move.append(key_set['upleft'])
                    
                elif move == [2,-2]:
                    move.append('a')
                    move.append(key_set['upright'])
                    
                elif move == [0,-2]:
                    move.append('a')
                    move.append(key_set['up'])
                
            if speed == 3:
                if move == [-2,0]:
                    move.append('d')
                    move.append(key_set['right'])
                elif move == [2,-2]:
                    move.append('d')
                    move.append(key_set['downleft'])
                elif move == [2,2]:
                    move.append('d')
                    move.append(key_set['downright'])
                    
                elif move == [0,-2]:
                    move.append('d')
                    move.append(key_set['down'])
                elif move == [-2,-2]:
                    move.append('d')
                    move.append(key_set['downright'])
                elif move == [-2,2]:
                    move.append('d')
                    move.append(key_set['downleft'])
                elif move == [2,0]:
                    move.append('d')
                    move.append(key_set['left'])
            
                elif move == [-3,0]:
                    move.append('k')
                    move.append(key_set['left'])
                
                elif move == [3,0]:
                    move.append('k')
                    move.append(key_set['right'])
                elif move == [-3,-3]:
                    move.append('a')
                    move.append(key_set['upleft'])
                    
                elif move == [3,-3]:
                    move.append('a')
                    move.append(key_set['upright'])
                                
                elif move == [0,-3]:
                    move.append('k')
                    move.append(key_set['up'])
                
            if len(move) < 3:
                move_map.remove(move)
        
    
    for move in move_map:
        move.append('w')
    
    return move_map
   
def convert_dxdy_to_key(dx,dy):
    if dx == 0 and dy == 1:
        return key_set['down']
    elif dx == 0 and dy == -1:
        return key_set['up']
    elif dx == 1 and dy == 0:
        return key_set['right']
    elif dx == -1 and dy == 0:
        return key_set['left']
    elif dx == 1 and dy == 1:
        return key_set['downright']
    elif dx == -1 and dy == 1:
        return key_set['downleft']
    elif dx == -1 and dy == -1:
        return key_set['upleft']
    elif dx == 1 and dy == -1:
        return key_set['upright']
   
def move_to_last_dir(move):
    
    if move[0] == 0 and move[1] == 1:
        return [0,1]
    elif move[0] == 0 and move[1] == 2:
        return [0,1]
    elif move[0] == 0 and move[1] == 3:
        return [0,1]
    
    if move[0] == 1 and move[1] == 0:
        return [1,0]
    elif move[0] == 2 and move[1] == 0:
        return [1,0]
    elif move[0] == 3 and move[1] == 0:
        return [1,0]
    
    if move[0] == 1 and move[1] == 1:
        return [1,1]
    elif move[0] == 2 and move[1] == 2:
        return [1,1]
    elif move[0] == 3 and move[1] == 3:
        return [1,1]
    
    if move[0] == -1 and move[1] == -1:
        return [-1,-1]
    elif move[0] == -2 and move[1] == -2:
        return [-1,-1]
    elif move[0] == -3 and move[1] == -3:
        return [-1,-1]
    
    if move[0] == 0 and move[1] == -1:
        return [0,-1]
    elif move[0] == 0 and move[1] == -2:
        return [0,-1]
    elif move[0] == 0 and move[1] == -3:
        return [0,-1]
    
    if move[0] == -1 and move[1] == 0:
        return [-1,0]
    elif move[0] == -2 and move[1] == 0:
        return [-1,0]
    elif move[0] == -3 and move[1] == 0:
        return [-1,0]
    
    if move[0] == 1 and move[1] == -1:
        return [1,-1]
    elif move[0] == 2 and move[1] == -2:
        return [1,-1]
    elif move[0] == 3 and move[1] == -3:
        return [1,-1]
    
    if move[0] == -1 and move[1] == 1:
        return [-1,1]
    elif move[0] == -2 and move[1] == 2:
        return [-1,1]
    elif move[0] == -3 and move[1] == 3:
        return [-1,1]
    
def set_key_help(toggle):
    global key_set
    
    if toggle:
        key_set = {
        'up': 'w',
        'down': 'x',
        'left': 'a',
        'right': 'd',
        'upleft': 'q',
        'upright': 'e',
        'downleft': 'y',
        'downright': 'c',
        'hold': 's'
        }
    else:
        key_set = {
       'up': '8',
        'down': '2',
        'left': '4',
        'right': '6',
        'upleft': '7',
        'upright': '9',
        'downleft': '1',
        'downright': '3',
        'hold': '5'
        }
   
def update_move_help():
    global moves
    moves = sort_moves(player.speed,wind)
        
    for move in moves[:]:
        x = player.x+move[0]
        y = player.y+move[1]
        
        if x < 0:
            x += MAP_WIDTH
        elif x >= MAP_WIDTH:
            x -= MAP_WIDTH 
        if y < 0:
            y += MAP_HEIGHT
        elif y >= MAP_HEIGHT:
            y -= MAP_HEIGHT
                
        if map[x][y].type != 'water':
            if player.distance(x,y) < 2:
                move[4] = 'land'
            else:
                moves.remove(move)
   
def check_move_to(dx, dy, toggle_keys):
    #the direction the player wants to moving to
    #global decc_moves, keep_moves, acc_moves, wind
    global moves
    
    player.old_x = player.x
    player.old_y = player.y
    
    set_key_help(toggle_keys)
    
    if player.boat:
        
        input = convert_dxdy_to_key(dx,dy)
        
        update_move_help()
        
        for move in moves:
            if move[3] == input:
                #print 'before ', move, player.last_direction
                player.last_direction = move_to_last_dir(move)
                #print 'after ', move, player.last_direction
            
                if move[4] == 'land':
                    player.boat = False
                    player.speed = 1
                    player.last_direction = [-1*move[0],-1*move[1]]
                    obj = Object(player.x, player.y, 'B', 'Boat', 'white')
                    objects.append(obj)
                    player.move(move[0], move[1])
                    message('You set foot in the sand.')
                    fov_recompute = True
                    update_move_help()
                    return 0
                    
                else:
                    if move[2] == 'd':
                        player.decrease_speed()
                    elif move[2] == 'a':
                        player.increase_speed()
                    
                    if move[0] == -wind[0] and move[1] == -wind[1]:
                        message("You dont't move against the wind.", 'sky')
                        update_move_help()  
                        return 'didnt-take-turn'
                    else:
                        player_move(move[0],move[1])
                        update_move_help()  
                        return 0
                    
                    
        update_move_help() 
        return 'didnt-take-turn'
        
    else:
        player_move(dx, dy)
        return 0
        
    
    
def player_move(dx, dy):
    '''called on keypress, decides whether player can move or attackes if monster on that tile'''
    global fov_recompute
    
   
    x = player.x + dx
    y = player.y + dy
    
    if x < 0:
        x += MAP_WIDTH
    elif x >= MAP_WIDTH:
        x -= MAP_WIDTH 
    
    if y < 0:
        y += MAP_HEIGHT
    elif y >= MAP_HEIGHT:
        y -= MAP_HEIGHT
   
    
    if not player.boat:
        for obj in objects:
            if obj.name == 'Boat' and player.x +dx == obj.x and player.y +dy == obj.y:
                player.boat = True
                objects.remove(obj)
                player.move(dx, dy)
                fov_recompute = True
                message('You set sails!', 'white')
                player.last_direction = [dx,dy]
                player.old_x = player.x
                player.old_y = player.y
                update_move_help()
                return
            elif obj.name == 'Elder' and player.x +dx == obj.x and player.y +dy == obj.y:
                if not TREASURES[obj.index].map_owned:
                    TREASURES[obj.index].map_owned = True
                    message('I have this treasure map for you! Safe travel.', 'magenta')
                    #message("Press 'I' for inventory.")
                player.food = 7
                message('Please let me give you supplies.', 'green')
                    
                return
    
    # #try to find an attackable object there
    # target = None
    # for object in objects:
        # if object.fighter and object.x == x and object.y == y:
            # target = object
            # break
            
    # #attack if target found, move otherwise
    # if target is not None:
        # player.fighter.attack(target)
        # fov_recompute = True
    # else:
    
    player.move(dx, dy)
    
    moves = sort_moves(player.speed,wind)

    fov_recompute = True

        
def menu(header, options, width, back=None, x1=-1, y1=-1):
    '''generic function to create a selection menu, is used for msg_box and name_menu'''
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
    
    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(0, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height + 2

    if x1 == -1 and y1 == -1:
        x = SCREEN_WIDTH / 2 - width / 2
        y = SCREEN_HEIGHT / 2 - height / 2
    else:
        x = x1
        y = y1
        
    T.layer(2)
    
    #make_GUI_frame(x, y, width, height)
    
    #cursors position
    c_pos = 0
    
    output = None
    
    while True:
        T.layer(2)
        T.clear_area(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
        
        #create an off-screen console that represents the menu's window
        if back:
            T.composition(T.TK_ON)
            for i in range(width):
                for j in range(height):
                    T.print_(i+x,j+y, '[color=' + back + ']' + '[U+2588]')
        
        T.print_(x+1,y, '[color=white]' + header)
        
        #print all the options
        h = header_height
        letter_index = ord('a')
        run = 0
        for option_text in options:
            text = option_text
            
            if run == c_pos:
                T.print_(x+1,h+y+1, '[color=yellow]> ' + text)
                
            else:    
                T.print_(x+1,h+y+1, '[color=white] ' + text)
            h += 1
            letter_index += 1
            run += 1
            
        #present the root console to the player and wait for a key-press
        T.refresh()
        
        key = T.read()
        if key == T.TK_ESCAPE:
            break
        elif key == T.TK_UP or key == T.TK_KP_8:
            c_pos -= 1
            if c_pos < 0:
                c_pos = len(options)-1
                
        elif key == T.TK_DOWN or key == T.TK_KP_2:
            c_pos += 1
            if c_pos == len(options):
                c_pos = 0
        
        elif key == T.TK_ENTER:               
            #convert the ASCII code to an index; if it corresponds to an option, return it
            index = c_pos
            #if index >= 0 and index < len(options): 
            output = index
            break
            
    T.clear_area(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)
    T.composition(T.TK_OFF)
    T.layer(0)
    return output
        
def msgbox(text, width=30):
    '''use menu() as a sort of "message box"'''
    menu(text, [], width)  

    
def name_menu():
    '''allowes player to enter his name for highscore, called upon death in highscore mode'''
    global PLAYER_NAME
    
    img = libtcod.image_load('story2.png')
    
    for i in range(1):
            time.sleep(0.2)
    
    while not libtcod.console_is_window_closed():
        for i in range(1):
            time.sleep(0.2)
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)
        #show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-6, libtcod.BKGND_NONE, libtcod.CENTER, 'Enter your name for highscore:')
        #show options and wait for the player's choice
        PLAYER_NAME = enter_text_menu('', 25, 16)
        
        #write score and player name to txt
        f = open('Highscores.txt', 'a')
        f.write('\n' + PLAYER_NAME + ' ' + str(score)) 
        f.close()
        break
        
    highscore_screen()
  
def enter_text_menu(header, width, max_length): #many thanks to Aukustus and forums for poviding this code. 
    '''used in name_menue as loop for entering characters'''
    # the 80 should be the width of the game window, in my game it's 80
    con = libtcod.console_new(80, 3)

    libtcod.console_set_default_foreground(con, libtcod.white)

    libtcod.console_print_rect(con, 5, 0, width, 3, header)
    libtcod.console_print_ex(con, 5, 1, libtcod.BKGND_NONE, libtcod.LEFT, 'Name:')
    timer = 0
    input = ''
    x = 11
    cx = 15
    cy = SCREEN_HEIGHT/2 - 3

    while True:
        key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)

        timer += 1
        if timer % (LIMIT_FPS // 4) == 0:
            if timer % (LIMIT_FPS // 2) == 0:
                timer = 0
                libtcod.console_print_ex(con, x, 1, libtcod.BKGND_NONE, libtcod.LEFT, ' ')
            else:
                libtcod.console_print_ex(con, x, 1, libtcod.BKGND_NONE, libtcod.LEFT, '_')
        if key.vk == libtcod.KEY_BACKSPACE:
            if len(input) > 0:
                libtcod.console_print_ex(con, x, 1, libtcod.BKGND_NONE, libtcod.LEFT, ' ')
                input = input[:-1]
                x -= 1

        elif key.vk == libtcod.KEY_ENTER or key.vk == libtcod.KEY_KPENTER:
            break

        elif key.c > 0 and len(input) < max_length:
            letter = chr(key.c)
            if re.match("^[A-Za-z0-9-']*$", str(letter)) or str(letter) == ' ':
                libtcod.console_print_ex(con, x, 1, libtcod.BKGND_NONE, libtcod.LEFT, letter)
                input += letter
                x += 1

        libtcod.console_blit(con, 5, 0, width, 3, 0, cx, cy, 1.0, 1.0)
        libtcod.console_flush()
        
    return input  
  
   
def handle_keys():
    '''constantly called in PlayerAI to check player keyboard input and act or return "didnt-take-turn"'''
    global key, colorblind, mouse, game_state, FONT_SIZE

    if key == T.TK_ESCAPE:
        choice = menu('Do you want to quit?', ['Yes', 'No'], 24,'black', SCREEN_WIDTH / 2 - 12, 7 )
        if choice == 0:                
            game_state = 'exit' #<- lead to crash WHY ??
            return 'exit' #exit game
        else:
            return 'didnt-take-turn'

    # elif key.vk == libtcod.KEY_ESCAPE:
        # choice = menu('Do you want to quit?', ['Yes', 'No'], 24)
        # if choice == 0:                
            # game_state = 'exit'
            # return 'exit' #exit game
        # else:
            # return 'didnt-take-turn'
          
    if game_state == 'playing':
        #movement keys
        
        if key == T.TK_UP or key == T.TK_KP_8:
            return check_move_to(0, -1, False)
        elif key == T.TK_DOWN or key == T.TK_KP_2:
            return check_move_to(0, 1, False)            
        elif key == T.TK_LEFT or key == T.TK_KP_4:
            return check_move_to(-1, 0, False)
        elif key == T.TK_RIGHT or key == T.TK_KP_6:
            return check_move_to(1, 0, False)
        elif key == T.TK_HOME or key == T.TK_KP_7:
            return check_move_to(-1, -1, False)
        elif key == T.TK_PAGEUP or key == T.TK_KP_9:
            return check_move_to(1, -1, False)
        elif key == T.TK_END or key == T.TK_KP_1:
            return check_move_to(-1, 1, False)
        elif key == T.TK_PAGEDOWN or key == T.TK_KP_3:
            return check_move_to(1, 1, False)
        elif key == T.TK_KP_5:
            pass #return check_move_to(0, 0)
            
        elif key == T.TK_W:
            return check_move_to(0, -1, True)
        elif key == T.TK_X:
            return check_move_to(0, 1, True)
        elif key == T.TK_A:
            return check_move_to(-1, 0, True)
        elif key == T.TK_D:
            return check_move_to(1, 0, True)
        elif key == T.TK_Q:
            return check_move_to(-1, -1, True)
        elif key == T.TK_E:
            return check_move_to(1, -1, True)
        elif key == T.TK_Y or key == T.TK_Z:
            return check_move_to(-1, 1, True)
        elif key == T.TK_C:
            return check_move_to(1, 1, True)
        
        else:
            
            if key == T.TK_O:
                FONT_SIZE += 1
                T.set("font: courbd.ttf, size=" + str(FONT_SIZE))
            
            if key == T.TK_P:
                FONT_SIZE -= 1
                T.set("font: courbd.ttf, size=" + str(FONT_SIZE))
            
            if key == T.TK_I:
            #show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Choose item from your inventory or ESC to cancel.\n')
                if chosen_item is not None:
                    #show map
                    show_map(chosen_item)
                    pass
                    
                return 'didnt-take-turn'
                
            if key == T.TK_G:
                for treasure in TREASURES:
                    if treasure.x == player.x and treasure.y == player.y and treasure.map_owned and not treasure.found:
                        treasure.found = True
                        message('Digging here, you found the treasure!', 'green')
                        message('It is the ' + treasure.name + '.', 'white')
                        treasure.name += ' (found)'
                        treasure.char = 'O'
                        treasure.color = 'green'
                        map[player.x][player.y].char_light = '[U+2588]'
                        map[player.x][player.y].color_light = '#F4A460'
                        
                        number = 0
                        for treasure in TREASURES:
                            if treasure.found:
                                number += 1
                                if number >= 7:
                                    return win()
                        
                        return
                return 'didnt-take-turn'
            
            # if key == T.TK_J:
                # path = astar(map, (player.x,player.y), (250,250))
                # #print path
                # for point in path:
                    # map[point[0]][point[1]].color_light = 'red'
                            
            if key == T.TK_H:
                help_screen()
                return 'didnt-take-turn'
                # f=open("output.txt", "w")
                # list = ''
                # # for y in range(SKY_HEIGHT):
                    # # for x in range(SKY_WIDTH):
                        # # char = ' '
                        # # for obj in sky_objects:
                            # # if obj.x == x and obj.y == y and obj.color == 'yellow':
                                # # char = obj.char
                        # # list += char
                        # # if x == SKY_WIDTH-1:
                            # # list += '|'
                # for y in range(MAP_HEIGHT):
                    # for x in range(MAP_WIDTH):
                        # list += map[x][y].char_light
                        # if x == MAP_WIDTH-1:
                            # list += '|'
                
                # print >> f,list
                # f.close()
            
            if key == T.TK_T:
                update_move_help()
                
            if key == T.TK_1:
                show_map(MAP_HOTKEY_1)
                
            if key == T.TK_2:
                show_map(MAP_HOTKEY_2)
            if key == T.TK_3:
                show_map(MAP_HOTKEY_3)
            if key == T.TK_4:
                show_map(MAP_HOTKEY_4)
            if key == T.TK_5:
                show_map(MAP_HOTKEY_5)
            
            if key == T.TK_MOUSE_SCROLL:
                direction = T.state(T.TK_MOUSE_WHEEL)
                if direction < 0:
                    FONT_SIZE += 1
                elif direction > 0:
                    FONT_SIZE -= 1
                T.set("font: courbd.ttf, size=" + str(FONT_SIZE))
                    
            return 'didnt-take-turn'
            
def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    inventory = []
    for treasure in TREASURES:
        if treasure.map_owned:
            inventory.append(treasure)
    
    if not inventory:
        options = ['Inventory is empty.']
    else:
        options = []
        for map in inventory:
            text = map.name
            #show additional information, in case it's equipped
            options.append(text)

    index = menu(header, options, INVENTORY_WIDTH, 'black', 0, 0)

    #if an item was chosen, return it
    if index is None or inventory == []: return None
    return inventory[index]

#------------------------------------------------------------------------------------------             
def show_map(item):
   
    global fov_map, fov_recompute, MAP_HOTKEY_1, MAP_HOTKEY_2, MAP_HOTKEY_3, MAP_HOTKEY_4, MAP_HOTKEY_5
    
    if not item:
        return 'didnt-take-turn'
    
    T.layer(0)
    
    libtcod.map_compute_fov(fov_map, item.x, item.y, 100, FOV_LIGHT_WALLS, FOV_ALGO)
    T.clear()
    
    for i in range(SCREEN_WIDTH):
        for j in range(SCREEN_HEIGHT):
            #T.bkcolor("#CD853F")
            T.bkcolor("#F4A460")
            #T.bkcolor("#DEB887")
            #c = libtcod.random_get_int(0,0,100)
            # if c < 20:
                # T.bkcolor("D2B48C")
            T.print_(i,j, '[color=white] ')
            
    for feature in item.features:
        feature.draw()
    
    T.bkcolor('black')
    for i in range(SCREEN_HEIGHT):
        if libtcod.random_get_int(0,0,100) < 75:
            T.print_(0,i, '[color=white] ')
            
    for i in range(SCREEN_HEIGHT):
        if libtcod.random_get_int(0,0,100) < 75:
            T.print_(79,i, '[color=white] ')
    
    for i in range(SCREEN_WIDTH):
        if libtcod.random_get_int(0,0,100) < 75:
            T.print_(i,23, '[color=white] ')
            
    for i in range(15):
        if libtcod.random_get_int(0,0,100) < 75:
            T.print_(i,0, '[color=white] ')
            
    for i in range(65,SCREEN_WIDTH-1):
        if libtcod.random_get_int(0,0,100) < 75:
            T.print_(i,0, '[color=white] ')
    
    T.layer(2)
    
    camera.move_camera(item.x, item.y)
    
    for y in range(camera.height):
        for x in range(camera.width):
            (map_x, map_y) = (camera.x + x, camera.y + y)
            
            if map_x > MAP_WIDTH-1: 
                map_x -= MAP_WIDTH
            elif map_x < 0:
                map_x += MAP_WIDTH
                
            if map_y > MAP_HEIGHT-1: 
                map_y -= MAP_HEIGHT
            elif map_y < 0:
                map_y += MAP_HEIGHT
            
            color_a = 'black' #map[map_x][map_y].color_light
            if not map[map_x][map_y].type == 'water':
                T.print_(x+BOAT_WINDOW_X, y+BOAT_WINDOW_Y, '[color=' + color_a + ']' + map[map_x][map_y].char_light)
            
            
    for treasure in TREASURES:
        treasure.draw()
               
    sky_cam.move_camera(item.x/SKY_FACTOR_X, item.y/SKY_FACTOR_Y)
   
    for object in sky_objects:
        #object.draw()
        
        if object.color == 'yellow':
            #only show if it's within camera frame
            (x, y) = sky_cam.to_camera_coordinates(object.x, object.y)
            
            if x is not None:
            #set the color and then draw the character that represents this object at its position
                T.color(object.color)
                T.print_(x+SKY_WINDOW_X, y+SKY_WINDOW_Y, '[color=black]' + object.char)

    draw_windrose(0)
    T.print_(51, 19, '[color=black]Press 1,2,3,4,5 (non-keypad)')
    T.print_(51, 20, '[color=black]to put this map on a hotkey.')
    #T.print_(52, 19, '[color=black]')
    T.print_(43, 22, '[color=black]Press ENTER, ESC or SPACE to return.')
    
    T.refresh()
    
    while True:
        key = T.read()
        if key == T.TK_ESCAPE:
            break
        if key == T.TK_SPACE:
            break
        if key == T.TK_RETURN:
            break
        if key == T.TK_1:
            MAP_HOTKEY_1 = item
            break
        if key == T.TK_2:
            MAP_HOTKEY_2 = item
            break
        if key == T.TK_3:
            MAP_HOTKEY_3 = item
            break
        if key == T.TK_4:
            MAP_HOTKEY_4 = item
            break
        if key == T.TK_5:
            MAP_HOTKEY_5 = item
            break
        
    T.bkcolor('black')
    T.layer(0)
    
    
#------------------------------------------------------------------------------------------ 
def help_screen():
   
    T.layer(0)
    T.clear()
    
    for i in range(SCREEN_WIDTH):
        for j in range(SCREEN_HEIGHT):
            T.print_(i,j, '[color=white] ')
            
    T.print_(0,0, '[color=white]Help screen')
    
    T.print_(1,2, '[color=yellow]Controls:')
    
    T.print_(1,4, '[color=white]Key Pad or Keys')
    T.print_(1,5, '[color=white]7 8 9')
    T.print_(1,6, '[color=white] \|/ ')
    T.print_(1,7, '[color=white]4- -6')
    T.print_(1,8, '[color=white] /|\ ')
    T.print_(1,9, '[color=white]1 2 3')
    
    #T.print_(10,4, '[color=white]Keys')
    T.print_(10,5, '[color=white]q w e')
    T.print_(10,6, '[color=white] \|/ ')
    T.print_(10,7, '[color=white]a- -d')
    T.print_(10,8, '[color=white] /|\ ')
    T.print_(10,9, '[color=white]z x c')
    
    T.print_(1,11, '[color=white]i: open inventory')
    T.print_(1,13, '[color=white]g: dig for treasure')
    T.print_(1,15, '[color=white]h: help screen')
    T.print_(1,17, '[color=white]1,2,3,4,5: hotkeys for maps')
    T.print_(2,18, '[color=white](non-Key Pad)')
    T.print_(1,20, '[color=white]o, p, mousewheel: ')
    T.print_(6,21, '[color=white]change screen size')
    
    
    T.print_(30,2, '[color=yellow]Sailing:')
    T.print_(30,4, '[color=white]The boat has momentum and speed.')
    T.print_(30,5, '[color=white]You can only sail to the points indicated')
    T.print_(30,6, '[color=white]by the numbers/keys.')
    T.print_(30,7, '[color=white]Pressing the respective key moves the boat to')
    T.print_(30,8, '[color=white]that position.')
    T.print_(30,9, '[color=white]Moving with the wind accelerates you,')
    T.print_(30,10, '[color=white]against the wind slows you down.')
    
    T.print_(30,12, '[color=yellow]Hints:')
    T.print_(30,14, '[color=white]You start with a map, try to find the island!')
    T.print_(30,15, "[color=white]Stars form constellations, 'A's form a giant A.")
    T.print_(30,16, '[color=white]On every island is an Elder with a map and food.')
    T.print_(30,17, '[color=white]You see more stars at night.')
    T.print_(30,18, '[color=white]Weather obstructs your vision.')
    T.print_(30,19, '[color=white]You cannot fight pirates, sail away fast instead.')
    T.print_(30,20, '[color=white]Find 7 treasures to win.')
    
    T.print_(42, 23, '[color=white]Press ENTER, ESC or SPACE to return.')
    T.refresh()
    while True:
        key = T.read()
        if key == T.TK_ESCAPE:
            break
        if key == T.TK_SPACE:
            break
        if key == T.TK_RETURN:
            break
      
    T.bkcolor('black')
    
def story_screen():
   
    T.layer(0)
    T.clear()
    
    for i in range(SCREEN_WIDTH):
        for j in range(SCREEN_HEIGHT):
            T.print_(i,j, '[color=white] ')

    T.print_(0,0, '[color=yellow]' +
'''            
                                                                            .  
                  *             .                                           
                                 .                                          
  *                                                     *       .   *       
                 *                                                          
                                                   .                        

              *             *               *    *                    *     
            *          *                                                    
                     *             *                                        
     .                                                                      
                                  .                                    *    
''')
    
    
    T.print_(7,7, '[color=white]The night is quiet and the boat is shaking in the wind')
    
    T.print_(7,9, '[color=white]In this ocean, every island holds a treasure')
    
    T.print_(7,11, '[color=white]And a map')
    
    T.print_(7,13, '[color=white]With no compass or landmarks, the only guidance are the stars')
    
    T.print_(42, 23, '[color=white]Press ENTER, ESC or SPACE to advance.')
    T.refresh()
    while True:
        key = T.read()
        if key == T.TK_ESCAPE:
            break
        if key == T.TK_SPACE:
            break
        if key == T.TK_RETURN:
            break
      
    T.bkcolor('black')
            
def win_screen():
   
    T.layer(0)
    T.clear()
    T.bkcolor('black')
    
    for i in range(SCREEN_WIDTH):
        for j in range(SCREEN_HEIGHT):
            T.print_(i,j, '[color=white] ')
    
    T.print_(0,0, '[color=yellow]' +
'''            
                                                                            .  
                  *             .                                           
                                 .                                          
  *                                                     *       .   *       
                 *                                                          
                                                   .                        

              *             *               *    *                    *     
            *          *                                                    
                     *             *                                        
     .                                                                      
                                  .                                    *    
''')   
         
    T.print_(10,10, '[color=yellow]You won the game!')
    
    T.print_(12,12, '[color=yellow]Thank you for playing!')
    
    T.print_(42, 23, '[color=white]Press ENTER, ESC or SPACE to return.')
    T.refresh()
    while True:
        key = T.read()
        if key == T.TK_ESCAPE:
            break
        if key == T.TK_SPACE:
            break
        if key == T.TK_RETURN:
            break
            
def advance_clock(hour=None, minute=None):
    global clock
    
    if hour:
        clock = [hour,minute]
    else:
        clock[1] = clock[1] + 15
        
    if clock[1] > 45:
        clock[1] = 0
        clock[0] += 1
    if clock[0] > 23:
        clock[0] = 0
        
    if clock == [6,0]:
        message('Dawn is coming.', 'orange')
    elif clock == [19,0]:
        message('Dusk is setting.', 'red')
        
def draw_clock():
    global clock
    
    T.layer(0)
    T.print_(64, 11, '[color=white].')
    T.print_(65, 11, '[color=white][U+00BD]')
    T.print_(66, 11, '[color=white].')
    
    T.print_(63, 12, '[color=white].')
    T.print_(64, 12, '[color=black] ')
    T.print_(65, 12, '[color=black] ')
    T.print_(66, 12, '[color=black] ')
    T.print_(67, 12, '[color=white][U+02D9]')
    
    T.print_(63, 13, '[color=white]9')
    T.print_(64, 13, '[color=black] ')
    T.print_(65, 13, '[color=white]o')
    T.print_(66, 13, '[color=black] ')
    T.print_(67, 13, '[color=white]3')
    
    T.print_(63, 14, '[color=white].')
    T.print_(64, 14, '[color=black] ')
    T.print_(65, 14, '[color=black] ')
    T.print_(66, 14, '[color=black] ')
    T.print_(67, 14, '[color=white].')
    
    T.print_(64, 15, '[color=white].')
    T.print_(65, 15, '[color=white]6')
    T.print_(66, 15, '[color=white].')
    
    if clock[1] == 0:
        T.print_(65, 12, '[color=yellow]|')
        T.print_(65, 11, '[color=yellow]|')
    elif clock[1] == 15:
        T.print_(66, 13, '[color=yellow]-')
        T.print_(67, 13, '[color=yellow]-')
    elif clock[1] == 30:
        T.print_(65, 14, '[color=yellow]|')
        T.print_(65, 15, '[color=yellow]|')
    elif clock[1] == 45:
        T.print_(64, 13, '[color=yellow]-')
        T.print_(63, 13, '[color=yellow]-')
    
    if clock[0] == 12 or clock[0] == 0:
        #T.print_(6, 18, '[color=red]|')
        T.print_(65, 11, '[color=red]o')
    elif clock[0] == 1 or clock[0] == 13:
        #T.print_(6, 18, '[color=red]/')
        T.print_(66, 11, '[color=red]o')
    elif clock[0] == 2 or clock[0] == 14:
        #T.print_(7, 18, '[color=red][U+2044]o')
        T.print_(67, 12, '[color=red]o')
    elif clock[0] == 3 or clock[0] == 15:
        #T.print_(7, 19, '[color=red]-')
        T.print_(67, 13, '[color=red]o')
    elif clock[0] == 4 or clock[0] == 16:
        #T.print_(7, 19, '[color=red]_')
        T.print_(67, 14, '[color=red]o')
    elif clock[0] == 5 or clock[0] == 17:
        #T.print_(7, 20, '[color=red]\\')
        T.print_(66, 15, '[color=red]o')
    elif clock[0] == 6 or clock[0] == 18:
        #T.print_(6, 20, '[color=red]|')
        T.print_(65, 15, '[color=red]o')
    elif clock[0] == 7 or clock[0] == 19:
        #T.print_(5, 20, '[color=red]/')
        T.print_(64, 15, '[color=red]o')
    elif clock[0] == 8 or clock[0] == 20:
        #T.print_(5, 20, '[color=red][U+0337]')
        T.print_(63, 14, '[color=red]o')
    elif clock[0] == 9 or clock[0] == 21:
        #T.print_(5, 19, '[color=red]-')
        T.print_(63, 13, '[color=red]o')
    elif clock[0] == 10 or clock[0] == 22:
        #T.print_(5, 18, '[color=red]_')
        T.print_(63, 12, '[color=red]o')
    elif clock[0] == 11 or clock[0] == 23:
        #T.print_(5, 18, '[color=red]\\')
        T.print_(64, 11, '[color=red]o')
            
def change_wind():
    global wind, moves
    
    prev = wind
    
    while True:
        wind = [libtcod.random_get_int(0,-1,1),libtcod.random_get_int(0,-1,1),1]
        if wind[0] == 0 and wind[1] == 0:
            continue
        elif wind[0] == 1 and wind[1] == 1:
            continue
        elif wind[0] == -1 and wind[1] == -1:
            continue
        elif wind[0] == 1 and wind[1] == -1:
            continue
        elif wind[0] == -1 and wind[1] == 1:
            continue
        elif wind == prev:
            continue
        else:
            break
    
    message('The wind changes.', 'sky')
    player.decrease_speed()
    moves = sort_moves(player.speed,wind)
    
            
def draw_windrose(normal=0):
    global wind
    
    color = 'black'
    if normal:
        color = 'white'
    
    T.print_(13, 11, '[color=' + color + '].')
    T.print_(14, 11, '[color=' + color + ']N')
    T.print_(15, 11, '[color=' + color + '].')
    
    T.print_(12, 12,'[color=' + color + '].')
    T.print_(13, 12, '[color=black] ')
    T.print_(14, 12, '[color=' + color + ']|')
    T.print_(15, 12, '[color=black] ')
    T.print_(16, 12, '[color=' + color + '].')
    
    T.print_(12, 13, '[color=' + color + ']-')
    T.print_(13, 13, '[color=' + color + ']-')
    T.print_(14, 13, '[color=' + color + ']o')
    T.print_(15, 13, '[color=' + color + ']-')
    T.print_(16, 13, '[color=' + color + ']-')
    
    T.print_(12, 14, '[color=' + color + '].')
    T.print_(13, 14, '[color=black] ')
    T.print_(14, 14, '[color=' + color + ']|')
    T.print_(15, 14, '[color=black] ')
    T.print_(16, 14, '[color=' + color + '].')
    
    T.print_(13, 15, '[color=' + color + '].')
    T.print_(14, 15, '[color=' + color + ']|')
    T.print_(15, 15, '[color=' + color + '].')
    
    if normal:
        
        if wind[2] == 0:
            return
        elif wind[0] == 1 and wind[1] == 0:
            for i in range(3):
                color = 'light blue'
                if libtcod.random_get_int(0,0,1) == 1:
                    color = 'sky'
                T.print_(15+i, 13, '[color=' + color + '][U+02C3]')
        elif wind[0] == 0 and wind[1] == 1:
            for i in range(3):
                color = 'light blue'
                if libtcod.random_get_int(0,0,1) == 1:
                    color = 'sky'
                T.print_(14, 14+i, '[color=' + color + '][U+02C5]')
        elif wind[0] == -1 and wind[1] == 0:
            for i in range(3):
                color = 'light blue'
                if libtcod.random_get_int(0,0,1) == 1:
                    color = 'sky'
                T.print_(13-i, 13, '[color=' + color + '][U+02C2]')
        elif wind[0] == 0 and wind[1] == -1:
            for i in range(3):
                color = 'light blue'
                if libtcod.random_get_int(0,0,1) == 1:
                    color = 'sky'
                T.print_(14, 12-i, '[color=' + color + '][U+02C4]')
        

def player_death(cause):
    '''called on player death hp < 0. sets game_state to dead, breaking all loops'''
    #the game ended!
    global game_state
    #in case it gets called on many events happening the same loop
    if game_state == 'dead':
        return

    game_state = 'dead'

    #for added effect, transform the player into a corpse!
    player.boat = False
    player.char = '%'        
    player.color = '#8B4513'
    #create corpse that can be found and used in bone files 
    player.blocks = False
    
    message('--You died from ' + cause + '!', 'red')
    message('Press ENTER, ESC or SPACE to return.', 'red')
    render_all()
    T.refresh()
    while True:
        key = T.read()
        if key == T.TK_ESCAPE:
            break
        if key == T.TK_SPACE:
            break
        if key == T.TK_RETURN:
            break
            
def win():
    '''called on player death hp < 0. sets game_state to dead, breaking all loops'''
    #the game ended, you won!
    global game_state
    #in case it gets called on many events happening the same loop
    
    game_state = 'exit'

    message('You win the game with 7 treasures!', 'green')
    message('Press ENTER, ESC or SPACE to return.', 'green')
    render_all()
    T.refresh()
    while True:
        key = T.read()
        if key == T.TK_ESCAPE:
            break
        if key == T.TK_SPACE:
            break
        if key == T.TK_RETURN:
            break
    win_screen()
    
    
def monster_death(monster):
    '''calles upon death of normal monsters tranforming them to corpses'''
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
       
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    
    #gain points on monster defeated
    put_on_score(monster.fighter.base_hp)
    
    monster.fighter = None
    monster.ai = Corpse(ticker, monster)
    monster.name = 'remains of ' + monster.name
    
    try:
        monster.send_to_back()    
    except:
        pass

DEATH_DICT = {
    'monster_death': monster_death
    }

def create_player():
    '''create the player and set him as global item'''
    global player, objects
    #create object representing the player
    fighter_component = Fighter(hp=PLAYER_STATS['hp'], 
                                damage=PLAYER_STATS['damage'], 
                                death_function=player_death)
    ai_component = PlayerAI(ticker, 6)
    player = Player(0, 0, '@', 'B', PLAYER_NAME, 'white', blocks=True, fighter=fighter_component, ai=ai_component)
    objects.append(player)
    
    
def create_pirates():
    for i in range(7):
        while True:
            x = libtcod.random_get_int(0,1,MAP_WIDTH-1)
            y = libtcod.random_get_int(0,1,MAP_HEIGHT-1)
            if map[x][y].type == 'water':
                break
        #print x,y
        ai_component = PirateAI(ticker, 6)
        pirate = EnemyShip(x, y, 'B', 'ship', 'darker red', blocks=True, ai=ai_component)
        objects.append(pirate)
        
def create_birds():
    for i in range(35):
    #    while True:
        x = libtcod.random_get_int(0,2,SKY_WIDTH-2)
        y = libtcod.random_get_int(0,2,SKY_HEIGHT-2)
            
        ai_component = BirdAI(ticker, 24)
        bird = Bird(x, y, ai=ai_component)
        sky_objects.append(bird)      
         
def new_game():
    '''create a new game, set everything to start, call make_map. called for every stage and used for endless mode with level > 4'''
    global game_msgs, game_state, dungeon_level
    global PLAYER_STATS, objects, sky_objects, ticker, ISLANDS, TREASURES
    
    PLAYER_STATS = {'hp': 10,
                'damage': 1
                }
    
    objects = []    
    
    sky_objects = []
    
    ISLANDS = []
    TREASURES = []
    ticker = timer.Ticker()
    
    create_player()
    
    make_map('var')
    
    create_pirates()
    
    create_birds()
    
    initialize_fov()
    game_state = 'playing'
    
    #player start
    random.shuffle(ISLANDS)
    while True:
        x = libtcod.random_get_int(0,0,ISLANDS[0].w)
        y = libtcod.random_get_int(0,0,ISLANDS[0].h)
        if map[ISLANDS[0].x1 + x][ISLANDS[0].y1 + y].type != 'water':
            player.boat = False
            player.x = ISLANDS[0].x1 + x
            player.y = ISLANDS[0].y1 + y
            player.old_x = player.x
            player.old_y = player.y
            
            shortest_distance = [ISLANDS[0].x1, ISLANDS[0].y1]
            closest_point = []
            for i in range(ISLANDS[0].h):
                for j in range(ISLANDS[0].w):
                    if map[ISLANDS[0].x1 + j][ISLANDS[0].y1 + i].type == 'water':
                        if player.distance(ISLANDS[0].x1+j,ISLANDS[0].y1+i) < shortest_distance:
                            shortest_distance = player.distance(ISLANDS[0].x1+j, ISLANDS[0].y1+i)
                            closest_point = [ISLANDS[0].x1+j, ISLANDS[0].y1+i]
            
            obj = Object(closest_point[0], closest_point[1], 'B', 'Boat', 'white')
            objects.append(obj)
            player.old_x = obj.x
            player.old_y = obj.y        
            
            break
    
    
    #create the list of game messages and their colors, starts empty
    game_msgs = []

    #a warm welcoming message!
    message('Welcome! Press h for help.', 'white')        

    
def initialize_fov():
    '''refreshes the FOV of player and allows new rendering by render_all'''
    global fov_recompute, fov_map
    fov_recompute = True

    #create the FOV map, according to the generated map
    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)
            
    #libtcod.console_clear(con)  #unexplored areas start black (which is the default background color)

def play_game():
    '''called on game start from main_menu, containes the loop controlling the scheduler, checks game states'''
    global key, mouse, camera, sky_cam, clock, wind, map_cam, moves
    
    player_action = None
    camera = Camera(0,0,CAMERA_WIDTH,CAMERA_HEIGHT,MAP_WIDTH,MAP_HEIGHT)
    sky_cam = Camera(0,0,SKYCAM_WIDTH,SKYCAM_HEIGHT,SKY_WIDTH,SKY_HEIGHT)
    map_cam = Camera(0,0,MAP_CAMERA_WIDTH,MAP_CAMERA_HEIGHT,MAP_WIDTH,MAP_HEIGHT)
    
    clock = 0
    advance_clock(20,0)
    wind = [0,1,1] #[x,y,strength] from left, westwind, strength 1
    moves = sort_moves(player.speed,wind)
    TREASURES[0].map_owned = True
    
    #main loop
    while True:
        # libtcod.console_flush()
        if game_state == 'dead' or game_state == 'exit':
            break
       
        ticker.ticks += 1
        #print ticker.ticks
        if not game_state == 'dead':
            ticker.next_turn()    
       
        
def main_menu():
    '''the title screen and main menu'''
        
    while True:
        #show the background image, at twice the regular console resolution
        T.layer(0)
        T.clear()
        
        T.print_(0,0, '[color=yellow]' +
'''            
                                                                            .  
                  *             .                                           
                                 .                                          
  *                                                     *       .   *       
                 *                                                          
                                                   .                        

              *             *               *    *                    *     
            *          *                                                    
                     *             *                                        
     .                                                                      
                                  .                                    *    
''')
        for i in range(SCREEN_WIDTH):
            T.print_(0+i,23, '[color=blue][U+2248]')
            
        
        T.color('#8B4513')
        T.print_(4, 22, '_')
        T.layer(3)
        T.color('white')
        T.print_(4, 22, 'B')
        
        T.print_(9,8, '[color=white][U+028C]')
        T.print_(5,6, '[color=white]v')
        
        T.layer(0)
        
                #show the game's title, and some credits!
        T.color('yellow')
        T.print_(SCREEN_WIDTH/2, SCREEN_HEIGHT/2-3, '[align=center]Starcharted Islands')
        T.print_(SCREEN_WIDTH/2, SCREEN_HEIGHT-2, '[align=center][color=green]#[color=white]IOLx3[color=yellow] Game by Jan | v1.0')
        
        options = ['Play a new game', 'Quit']
        
        #show options and wait for the player's choice
        choice = menu('', options, 10, 'black', SCREEN_WIDTH/2-10, SCREEN_HEIGHT/2 - 2)
        
        if choice == 0:  #new game
            story_screen()
            help_screen()
            new_game()
            play_game()
        # elif choice == 1:  #load last game
            # try:
                # load_game()
            # except:
                # msgbox('\n No saved game to load.\n', 24)
                # continue
            # play_game()
        elif choice == 1:  #quit
            break
    
  
T.open()
T.set("window: size=" + str(SCREEN_WIDTH) + "x" + str(SCREEN_HEIGHT) + ', title=Starcharted Islands')
T.set("font: courbd.ttf, size=" + str(FONT_SIZE))
 

main_menu()
