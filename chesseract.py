# 4D Chess
# Myles Scholz

import pyglet
from pyglet.gl import *
from pyglet.window import key
import math
import numpy as np
import os
import pieces
from pieces import *

class Window(pyglet.window.Window):
    
    ref_axis = [1, 0, 0]
    translation = 0
    
    move_selector = [0, 0, 7, 0]
    
    pieces = []
    focus = 0
    
    def __init__(self, width, height, title=''):
        super(Window, self).__init__(width, height, title)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.setup_game()
        
    def on_draw(self):
        self.clear()
        
        glPushMatrix()
        
        glBegin(GL_QUADS)
        for g in range(0, 1536, 192):
            if ((g / 192) % 2 != 0):
                g_invert = True
            else:
                g_invert = False
            for h in range(-96, 96, 24):
                if ((h / 24) % 2 != 0):
                    h_invert = True
                else:
                    h_invert = False
                # White background to the board
                glColor4ub(255, 255, 255, 127)
                glVertex3f( 64, g + 64, h)
                glVertex3f(-64, g + 64, h)
                glVertex3f(-64, g - 64, h)
                glVertex3f( 64, g - 64, h)
                
                # Dark grey squares
                glColor4ub(32, 32, 32, 127)
                for i in range(8):
                    if (g_invert or h_invert) and not (g_invert and h_invert):
                        if i % 2 == 0:
                            start = 1
                        else:
                            start = 0
                    else:
                        if i % 2 == 0:
                            start = 0
                        else:
                            start = 1
                    
                    for j in range(start, 8, 2):
                        glVertex3f((16 * j - 64), g + (16 * i - 64), h + 0.1)
                        glVertex3f((16 * (j + 1) - 64), g + (16 * i - 64), h + 0.1)
                        glVertex3f((16 * (j + 1) - 64), g + (16 * (i + 1) - 64), h + 0.1)
                        glVertex3f((16 * j - 64), g + (16 * (i + 1) - 64), h + 0.1)
                
                # Dark grey underside of the board
                glColor4ub(32, 32, 32, 127)
                glVertex3f( 64, g + 64, h - 4)
                glVertex3f(-64, g + 64, h - 4)
                glVertex3f(-64, g - 64, h - 4)
                glVertex3f( 64, g - 64, h - 4)
                
                # Right
                glVertex3f(64, g + 64,  h)
                glVertex3f(64, g - 64,  h)
                glVertex3f(64, g - 64, h - 4)
                glVertex3f(64, g + 64, h - 4)
                
                # Left
                glVertex3f(-64, g - 64,  h)
                glVertex3f(-64, g + 64,  h)
                glVertex3f(-64, g + 64, h - 4)
                glVertex3f(-64, g - 64, h - 4)
                
                # Back
                glVertex3f(-64, g + 64,  h)
                glVertex3f( 64, g + 64,  h)
                glVertex3f( 64, g + 64, h - 4)
                glVertex3f(-64, g + 64, h - 4)
                
                # Front
                glVertex3f( 64, g - 64,  h)
                glVertex3f(-64, g - 64,  h)
                glVertex3f(-64, g - 64, h - 4)
                glVertex3f( 64, g - 64, h - 4)
        
        glEnd()
        
        # Selector
        
        glBegin(GL_QUADS)
        
        glColor4ub(255, 96, 96, 191)
        x = self.move_selector[0]*16 - 56
        y = self.move_selector[1]*16 + self.move_selector[3]*192 - 56
        z = self.move_selector[2]*24 - 96
        glVertex3f(x + 8, y + 8, z + 0.3)
        glVertex3f(x - 8, y + 8, z + 0.3)
        glVertex3f(x - 8, y - 8, z + 0.3)
        glVertex3f(x + 8, y - 8, z + 0.3)
        
        glEnd()
        
        # Pieces

        for piece in self.pieces:
            if piece == self.pieces[self.focus]:
                piece.focus()
                piece.get_moves()
                piece.elim_moves(self.pieces)
            else:
                piece.unfocus()
            
            piece.draw(16)
        
        glPopMatrix()
        
    def on_resize(self, width, height):
        aspect_ratio = width / height
        
        glViewport(0, 0, width, height)
        # +x right, +y up, +z back
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        gluPerspective(35, aspect_ratio, 1, 1000)
        
        # Move model back into view
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -400)
    
    def on_key_press(self, symbol, modifiers):
        
        # Camera Controls
        if symbol == key.W:
            glTranslatef(0, -192, 0)
            self.translation -= 192
        elif symbol == key.S:
            glTranslatef(0,  192, 0)
            self.translation += 192
        
        if symbol == key.LSHIFT:
            glTranslatef(0, 0, -8)
        elif symbol == key.LCTRL:
            glTranslatef(0, 0, 8)
        
        # Focus Controls
        if symbol == key.LEFT:
            self.focus -= 1
            
            if self.focus < 0:
                self.focus += len(self.pieces)
            
            if self.pieces[self.focus].captured:
                self.focus -= 1
        elif symbol == key.RIGHT:
            self.focus += 1
            
            if self.focus >= len(self.pieces):
                self.focus -= len(self.pieces)
            
            if self.pieces[self.focus].captured:
                self.focus += 1
        
        if self.focus >= len(self.pieces):
            self.focus -= len(self.pieces)
        elif self.focus < 0:
            self.focus += len(self.pieces)
        
        if symbol == key.LEFT or symbol == key.RIGHT:
            self.move_selector = list(self.pieces[self.focus].pos)
        
        # Piece Controls
        if symbol == key.NUM_4:
            if self.move_selector[0] > 0:
                self.move_selector[0] -= 1
        elif symbol == key.NUM_6:
            if self.move_selector[0] < 7:
                self.move_selector[0] += 1
        
        if symbol == key.NUM_8:
            if self.move_selector[1] < 7:
                self.move_selector[1] += 1
        elif symbol == key.NUM_5:
            if self.move_selector[1] > 0:
                self.move_selector[1] -= 1
        
        if symbol == key.NUM_7:
            if self.move_selector[2] < 7:
                self.move_selector[2] += 1
        elif symbol == key.NUM_9:
            if self.move_selector[2] > 0:
                self.move_selector[2] -= 1
        
        if symbol == key.NUM_1:
            if self.move_selector[3] < 7:
                self.move_selector[3] += 1
        elif symbol == key.NUM_3:
            if self.move_selector[3] > 0:
                self.move_selector[3] -= 1
            
        if symbol == key.SPACE:
            for piece in self.pieces:
                if piece == self.pieces[self.focus]:
                    piece.move(self.move_selector, self.pieces)
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if dx != 0:
            glTranslatef(0, -self.translation, 0)
            glRotatef(dx / 2, 0, 0, 1)
            self.rot_ref_axis(math.radians(dx / 2))
            glTranslatef(0, self.translation, 0)
        
        x = self.ref_axis[0]
        y = self.ref_axis[1]
        z = self.ref_axis[2]
        if dy != 0:
            glTranslatef(0, -self.translation, 0)
            glRotatef(-dy / 2, x, y, z)
            glTranslatef(0, self.translation, 0)
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        glMatrixMode(GL_PROJECTION)
        if scroll_y > 0:
            glTranslatef(0, 0, 10)
        else:
            glTranslatef(0, 0, -10)
        glMatrixMode(GL_MODELVIEW)
    
    def rot_ref_axis(self, theta):
        cos = math.cos(theta)
        sin = math.sin(theta)
        z_rot = np.array([[cos, -sin, 0], [sin, cos, 0], [0, 0, 1]])
        
        self.ref_axis = np.dot(self.ref_axis, z_rot)
    
    def setup_game(self):
        for h in range(2):
            for i in range(8):
                for j in range(8):
                    # Pawns
                    if h == 0:
                        piece = Pawn([i, 1, j, 0], "white")
                    else:
                        piece = Pawn([i, 6, j, 7], "black")
                    self.pieces.append(piece)
                    
                    # Bishops
                    if (i > 1 and i < 6) and (j == 0 or j == 7):
                        if h == 0:
                            piece = Bishop([i, 0, j, 0], "white")
                        else:
                            piece = Bishop([i, 7, j, 7], "black")
                        self.pieces.append(piece)
                    
                    # Knights
                    if (i == 0 or i == 7) and (j > 1 and j < 6):
                        if h == 0:
                            piece = Knight([i, 0, j, 0], "white")
                        else:
                            piece = Knight([i, 7, j, 7], "black")
                        self.pieces.append(piece)
                    
                    # Rooks
                    if ((i == 0 or i == 7) and (j < 2 or j > 5)) or ((i == 1 or i == 6) and (j == 0 or j == 7)):
                        if h == 0:
                            piece = Rook([i, 0, j, 0], "white")
                        else:
                            piece = Rook([i, 7, j, 7], "black")
                        self.pieces.append(piece)
                    
                    # Queens
                    if (i == 3 and j == 3) or (i == 4 and j == 4):
                        if h == 0:
                            piece = Queen([i, 0, j, 0], "white")
                        else:
                            piece = Queen([i, 7, j, 7], "black")
                        self.pieces.append(piece)
                    
                    # Kings
                    if h == 0:
                        piece = King([3, 0, 4, 0], "white")
                    else:
                        piece = King([4, 7, 3, 7], "black")
                    self.pieces.append(piece)
        
        for piece in self.pieces:
            piece.get_moves()
            piece.elim_moves(self.pieces)

def run():
    Window(1080, 720, "4D Chess")
    pyglet.app.run()

run()
