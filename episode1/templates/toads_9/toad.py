import pygame as pg

class Toad:
    def __init__(self, x, y):
        self.image = pg.image.load("assets/toad.png").convert_alpha()
        self.rect = pg.Rect(x, y, self.image.get_width(), self.image.get_height())

        self.move = 1
