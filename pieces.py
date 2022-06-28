# Pieces
# Myles Scholz

import pyglet
from pyglet.gl import *
from pyglet.window import key
import math
import numpy as np
import os

class Piece:
    def __init__(self, position, color, value):
        self.pos = position
        self.color = color.lower()
        self.val = value
        self.highlight = 0
        self.captured = False
        self.check = 0
        self.dirs = []
        self.moves = []
        self.images = []
        for name in os.listdir("Pieces/"):
            image = pyglet.image.load("Pieces/" + name)
            self.images.append([image, image.get_texture(), image.get_data('RGBA', image.width * 4)])
    
    def get_dirs(self):
        pass
    
    def get_moves(self):
        self.moves = []
        for direction in self.dirs:
            to_pos = self.pos
            to_pos += direction
            while not any([(x > 7 or x < 0) for x in to_pos]):
                self.moves = np.append(self.moves, to_pos)
                to_pos += direction
                
        self.moves = np.reshape(self.moves, (-1, 4))
    
    def elim_moves(self, pieces):
        elims = []
        for direction in self.dirs:
            to_pos = self.pos
            to_pos += direction
            while not (any([all(to_pos == piece.pos) for piece in pieces]) or any([(x > 7 or x < 0) for x in to_pos])):
                to_pos += direction
            
            # Extend one further step if the piece is of the opposite color
            one_step = False
            for piece in pieces:
                    if all(to_pos == piece.pos) and piece.color != self.color and not one_step:
                        to_pos += direction
                        one_step = True
            
            while not any([(x > 7 or x < 0) for x in to_pos]):
                elims = np.append(elims, to_pos)
                to_pos += direction
                
        elims = np.reshape(elims, (-1, 4))
        
        for move in elims:
            elims_i = []
            for i in range(len(self.moves)):
                if all(move == self.moves[i]):
                    elims_i.append(i)
            
            for i in elims_i:
                self.moves = np.delete(self.moves, i, axis = 0)
    
    def move(self, to_pos, pieces):
        if any([all(to_pos == move) for move in self.moves]):
            for piece in pieces:
                if any([to_pos == piece.pos]):
                    piece.captured = True
            self.pos = list(to_pos)
            self.get_dirs()
            self.get_moves()
            self.elim_moves(pieces)
    
    def focus(self):
        self.highlight = 32
    
    def unfocus(self):
        self.highlight = 0
    
    def draw(self, image, sides=32):
        
        glBindTexture(image[1].target, image[1].id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image[0].width, image[0].height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image[2])
        
        if self.captured:
            self.pos[0] -= 8
        
        coords = [self.pos[0]*16 - 56, self.pos[1]*16 - 56, self.pos[2]*24 - 96, self.pos[3]*192]
        
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glBindTexture(image[1].target, image[1].id)
        
        glBegin(GL_POLYGON)
        glColor4ub(64 + self.highlight + self.check, 64 + self.highlight, 64 + self.highlight, 255)
        
        top_points = []
        bottom_points = []
        
        for i in range(sides):
            theta = (2*math.pi / sides)*i
            x = 8 * math.cos(theta) + coords[0]
            y = 8 * math.sin(theta) + coords[1] + coords[3]
            z = coords[2]
            glVertex3f(x, y, z)
            bottom_points.append([x, y, z])
            
        for i in range(sides):
            theta = (2*math.pi / sides)*i
            x = 8 * math.cos(theta) + coords[0]
            y = 8 * math.sin(theta) + coords[1] + coords[3]
            z = 2 + coords[2]
            glTexCoord2f(0.5 + 0.5*math.cos(theta), 0.5 + 0.5*math.sin(theta))
            glVertex3f(x, y, z)
            top_points.append([x, y, z])
        
        glEnd()
        glDisable(GL_TEXTURE_2D)
        
        glBegin(GL_QUADS)
    
        for i in range(len(top_points) - 1):
            glVertex3f(top_points[i][0], top_points[i][1], top_points[i][2])
            glVertex3f(bottom_points[i][0], bottom_points[i][1], bottom_points[i][2])
            glVertex3f(bottom_points[i + 1][0], bottom_points[i + 1][1], bottom_points[i + 1][2])
            glVertex3f(top_points[i + 1][0], top_points[i + 1][1], top_points[i + 1][2])
        
        glVertex3f(top_points[sides - 1][0], top_points[sides - 1][1], top_points[sides - 1][2])
        glVertex3f(bottom_points[sides - 1][0], bottom_points[sides - 1][1], bottom_points[sides - 1][2])
        glVertex3f(bottom_points[0][0], bottom_points[0][1], bottom_points[0][2])
        glVertex3f(top_points[0][0], top_points[0][1], top_points[0][2])
        
        glEnd()
        
        if self.highlight != 0:
            glBegin(GL_QUADS)
            glColor4ub(96, 255, 96, 127)
            for move in self.moves:
                to_coords = [move[0]*16 - 56, move[1]*16 - 56, move[2]*24 - 96, move[3]*192]
                glVertex3f(to_coords[0] + 8, to_coords[1] + to_coords[3] + 8, to_coords[2] + 0.2)
                glVertex3f(to_coords[0] - 8, to_coords[1] + to_coords[3] + 8, to_coords[2] + 0.2)
                glVertex3f(to_coords[0] - 8, to_coords[1] + to_coords[3] - 8, to_coords[2] + 0.2)
                glVertex3f(to_coords[0] + 8, to_coords[1] + to_coords[3] - 8, to_coords[2] + 0.2)
            glEnd()

class Pawn(Piece):
    first = True
    
    def __init__(self, position, color):
        super().__init__(position, color, 1)
        self.get_dirs()
        self.get_moves()
    
    def get_dirs(self):
        self.dirs = []
        forward = 0
        if self.color == "white":
            forward = 1
        elif self.color == "black":
            forward = -1
            
        self.dirs = np.append(self.dirs, [0, forward, 0, 0])
        if self.first:
            self.dirs = np.append(self.dirs, [0, 2*forward, 0, 0])
            
        for i in range(1, -2, -2):
            for j in range(0, 4):
                if j != 1:
                    final = [0, forward, 0, 0]
                    final[j] = i
                    self.dirs = np.append(self.dirs, final)
        
        self.dirs = np.reshape(self.dirs, (-1,4))
    
    def get_moves(self):
        self.moves = []
        for direction in self.dirs:
            to_pos = self.pos
            to_pos += direction
            if not any([(x > 7 or x < 0) for x in to_pos]):
                self.moves = np.append(self.moves, to_pos)
        
        self.moves = np.reshape(self.moves, (-1, 4))
    
    def elim_moves(self, pieces):
        elims = []
        for direction in self.dirs:
            to_pos = self.pos
            to_pos += direction
            
            # Remove out-of-bounds moves
            if any([(x > 7 or x < 0) for x in to_pos]):
                elims = np.append(elims, to_pos)
            
            for piece in pieces:
                # Remove moves into same-color pieces
                if all(to_pos == piece.pos) and piece.color == self.color:
                    elims = np.append(elims, to_pos)
                # Remove straight-ahead moves into pieces
                straights = [[0, 1, 0, 0], [0, -1, 0, 0], [0, 2, 0, 0], [0, -2, 0, 0]]
                if all(to_pos == piece.pos) and any(all(direction == straight) for straight in straights):
                    for straight in straights:
                        elims = np.append(elims, straight)
            
            # Remove diagonal moves not into pieces
            if not any(all(to_pos == piece.pos) for piece in pieces) and not any(all(direction == straight) for straight in [[0, 1, 0, 0], [0, -1, 0, 0], [0, 2, 0, 0], [0, -2, 0, 0]]):
                elims = np.append(elims, to_pos)
        
        elims = np.reshape(elims, (-1, 4))
        
        for move in elims:
            elims_i = []
            for i in range(len(self.moves)):
                if all(move == self.moves[i]):
                    elims_i.append(i)
            
            for i in elims_i:
                self.moves = np.delete(self.moves, i, axis = 0)
    
    def move(self, to_pos, pieces):
        if self.first:
            self.first = False
        super().move(to_pos, pieces)
    
    def draw(self, sides = 32):
        if self.color == "black":
            self.texture = self.images[3]
        elif self.color == "white":
            self.texture = self.images[9]
        super().draw(self.texture, sides)

class Bishop(Piece):
    def __init__(self, position, color):
        super().__init__(position, color, 3)
        self.get_dirs()
        self.get_moves()
        
    def get_dirs(self):
        self.dirs = []
        for h in range(1, -2, -2):
            for i in range(1, -2, -2):
                for j in range(3):
                    for k in range(j + 1, 4):
                        final = [0, 0, 0, 0]
                        final[j] = h
                        final[k] = i
                        self.dirs = np.append(self.dirs, final)
        
        self.dirs = np.reshape(self.dirs, (-1,4))
    
    def draw(self, sides = 32):
        if self.color == "black":
            self.texture = self.images[0]
        elif self.color == "white":
            self.texture = self.images[6]
        super().draw(self.texture, sides)

class Knight(Piece):
    def __init__(self, position, color):
        super().__init__(position, color, 3)
        self.get_dirs()
        self.get_moves()
        
    def get_dirs(self):
        for h in range(1, -2, -2):
            for i in range(1, -2, -2):
                for j in range(3):
                    for k in range(j + 1, 4):
                        final = [0, 0, 0, 0]
                        final[j] = 2*h
                        final[k] = i
                        self.dirs = np.append(self.dirs, final)
                        final[j] = h
                        final[k] = 2*i
                        self.dirs = np.append(self.dirs, final)
        
        self.dirs = np.reshape(self.dirs, (-1,4))
    
    def get_moves(self):
        self.moves = []
        for direction in self.dirs:
            to_pos = self.pos
            to_pos += direction
            if not any([(x > 7 or x < 0) for x in to_pos]):
                self.moves = np.append(self.moves, to_pos)
                
        self.moves = np.reshape(self.moves, (-1, 4))
    
    def draw(self, sides = 32):
        if self.color == "black":
            self.texture = self.images[2]
        elif self.color == "white":
            self.texture = self.images[8]
        super().draw(self.texture, sides)

class Rook(Piece):
    def __init__(self, position, color):
        super().__init__(position, color, 5)
        self.get_dirs()
        self.get_moves()
        
    def get_dirs(self):
        self.dirs = []
        for i in zip(np.identity(4, dtype=int),-np.identity(4, dtype=int)):
            self.dirs = np.append(self.dirs, np.array(i))

        self.dirs = np.reshape(self.dirs, (-1,4))
    
    def draw(self, sides = 32):
        if self.color == "black":
            self.texture = self.images[5]
        elif self.color == "white":
            self.texture = self.images[11]
        super().draw(self.texture, sides)

class Queen(Piece):
    def __init__(self, position, color):
        super().__init__(position, color, 9)
        self.get_dirs()
        self.get_moves()
        
    def get_dirs(self):
        self.dirs = []
        for i in zip(np.identity(4, dtype=int),-np.identity(4, dtype=int)):
            self.dirs = np.append(self.dirs, np.array(i))
        
        for h in range(1, -2, -2):
            for i in range(1, -2, -2):
                for j in range(3):
                    for k in range(j + 1, 4):
                        final = [0, 0, 0, 0]
                        final[j] = h
                        final[k] = i
                        self.dirs = np.append(self.dirs, final)

        self.dirs = np.reshape(self.dirs, (-1,4))
    
    def draw(self, sides = 32):
        if self.color == "black":
            self.texture = self.images[4]
        elif self.color == "white":
            self.texture = self.images[10]
        super().draw(self.texture, sides)
        
class King(Piece):
    def __init__(self, position, color):
        super().__init__(position, color, 10)
        self.get_dirs()
        self.get_moves()
    
    def get_dirs(self):
        self.dirs = []
        for i in zip(np.identity(4, dtype=int),-np.identity(4, dtype=int)):
            self.dirs = np.append(self.dirs, np.array(i))
        
        for h in range(1, -2, -2):
            for i in range(1, -2, -2):
                for j in range(3):
                    for k in range(j + 1, 4):
                        final = [0, 0, 0, 0]
                        final[j] = h
                        final[k] = i
                        self.dirs = np.append(self.dirs, final)
        
        self.dirs = np.reshape(self.dirs, (-1,4))
    
    def get_moves(self):
        self.moves = []
        for direction in self.dirs:
            to_pos = self.pos
            to_pos += direction
            if not any([(x > 7 or x < 0) for x in to_pos]):
                self.moves = np.append(self.moves, to_pos)
                
        self.moves = np.reshape(self.moves, (-1, 4))

    def elim_moves(self, pieces):
        elims = []
        for direction in self.dirs:
            to_pos = self.pos
            to_pos += direction
            
            # Remove out-of-bounds moves
            if any([(x > 7 or x < 0) for x in to_pos]):
                elims = np.append(elims, to_pos)
            
            for piece in pieces:
                # Remove moves into same-color pieces
                if all(to_pos == piece.pos) and piece.color == self.color:
                    elims = np.append(elims, to_pos)
                
                # Remove moves into check
                if piece.color != self.color and any(all(to_pos == move) for move in piece.moves):
                    elims = np.append(elims, to_pos)
        
        elims = np.reshape(elims, (-1, 4))
        
        for move in elims:
            elims_i = []
            for i in range(len(self.moves)):
                if all(move == self.moves[i]):
                    elims_i.append(i)
            
            for i in elims_i:
                self.moves = np.delete(self.moves, i, axis = 0)
        
        self.check_check(pieces)
    
    def check_check(self, pieces):
        if any((any(all(self.pos == move) for move in piece.moves) and piece.color != self.color) for piece in pieces):
            self.check = 128
        else:
            self.check = 0
    
    def draw(self, sides = 32):
        if self.color == "black":
            self.texture = self.images[1]
        elif self.color == "white":
            self.texture = self.images[7]
        super().draw(self.texture, sides)

