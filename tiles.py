'''contains the tile class, which dtermines the properties of eayh map tile

name, char, color <- all via type
blocked
blocks sight
explored

can be changed via change_type

'''

import libtcodpy as libtcod

class Tile:
    '''a tile of the map and its properties'''
    def __init__(self, blocked, block_sight = None, type='dummy', name='dummy' ):
        self.blocked = blocked

        #all tiles start unexplored
        self.explored = False

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
        
        self.name = name
        self.change_type(type)
            
    def change_type(self, type):    
        '''call to assign new type andd all corresponding properties'''
        self.type = type
        
        if type == 'empty': #empty tile
            self.name = 'empty'
            self.char_light = '.'
            self.char_dark = ' '
            self.color_light = 'grey'
            self.color_dark = 'white'
            self.blocked = False
            self.block_sight = False
            
        elif type == 'grass': #empty tile
            self.name = 'empty'
            self.char_light = '.'
            self.char_dark = ' '
            self.color_light = 'grey'
            self.color_dark = 'white'
            self.blocked = False
            self.block_sight = False
            
            i = libtcod.random_get_int(0,0,100)
            if i <= 30:
                self.color_light = 'dark green'
                self.char_light = "'"
            elif i <= 80:
                self.color_light = 'green'
                self.char_light = ','
            elif i <= 81:
                self.color_light = 'dark green'
                self.char_light = 'T'
        
        elif type == 'rock wall':
            self.name = 'wall'
            self.char_light = '#'
            self.char_dark = '#'
            self.color_light = 'grey'
            self.color_dark = 'dark grey'
            self.blocked = True
            self.block_sight = True
            
        elif type == 'beach':
            self.name = 'beach'
            self.char_light = '.'
            self.char_dark = chr(192)
            self.color_light = 'lighter yellow'
            self.color_dark = 'lighter yellow'
            self.blocked = False
            self.block_sight = False
   
        elif type == 'sky':
            self.name = 'empty'
            self.char_light = '='
            self.char_dark = '='
            self.color_light = 'sky'
            self.color_dark = 'dark bluee'
            self.blocked = False
            self.block_sight = False
            
            # i = libtcod.random_get_int(0,0,100)
            # if i <= 30:
                # self.color_light = 'sky'
                # self.char_light = '%'
            # elif i <= 80:
                # self.color_light = 'sky'
                # self.char_light = '#'
            # elif i <= 81:
                # self.color_light = 'light blue'
                # self.char_light = '-'
   
        elif type == 'water':
            self.name = 'water'
            #self.char_light = 'w'
            self.char_light = '[U+2248]'
            self.char_dark = 'w'
            self.color_light = 'blue'
            self.color_dark = 'blue'
            self.blocked = True
            self.block_sight = False
            
            i = libtcod.random_get_int(0,0,100)
            if i <= 30:
                self.color_light = 'light blue'
                #self.char_light = 'm'
   
        elif type == 'door':
            self.name = 'door'
            self.char_light = '+'
            self.char_dark = '+'
            self.color_light = 'darker orange'
            self.color_dark = 'darker orange'
            self.blocked = False
            self.block_sight = False
            
        elif type == 'lava':
            self.name = 'lava'
            self.char_light = '{'
            self.char_dark = '{'
            self.color_light = 'flame'
            self.color_dark = 'flame'
            self.blocked = False
            self.block_sight = False
        
        elif type == 'ice':
            self.name = 'ice'
            self.char_light = '/'
            self.char_dark = '/'
            self.color_light = 'white'
            self.color_dark = 'blue'
            self.blocked = True
            self.block_sight = False
