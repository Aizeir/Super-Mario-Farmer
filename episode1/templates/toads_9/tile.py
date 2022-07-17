import pygame as pg

class Tile:
    SIZE = 16

    def __init__(self, x, y, id):
        self.pos = (x, y)
        self.rect = pg.Rect(x*self.SIZE, y*self.SIZE, self.SIZE, self.SIZE)
        self.id = id
