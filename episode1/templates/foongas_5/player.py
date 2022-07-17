import pygame as pg

class Player:
    DEFAULT_X = 128
    DEFAULT_Y = 128

    def __init__(self):
        self.images_left = [pg.image.load("assets/mario_0.png").convert_alpha(), 
                            pg.image.load("assets/mario_1.png").convert_alpha()]
        self.images_right = [pg.transform.flip(x, True, False) for x in self.images_left]
        
        self.image_left_jump = pg.image.load("assets/mario_jump.png").convert_alpha()
        self.image_right_jump = pg.transform.flip(self.image_left_jump, True, False)

        self.image_idx = 0
        self.images_len = len(self.images_left)
        self.images_cooldown = 0
        self.image = self.images_left[self.image_idx]

        self.rect = self.images_left[0].get_rect()
        self.rect.x = self.DEFAULT_X
        self.rect.y = self.DEFAULT_Y

        self.xdir = 1 # Direction du joueur (-1 = gauche, 1 = droite)
        self.speed = 1
        self.jump_height = 17
        self.jump_count = self.jump_height

        self.is_jumping = False
        self.is_grounded = False

    def jump(self):
        if self.is_grounded:
            self.is_jumping = True
            self.jump_count = self.jump_height

    def stop_jumping(self):
        self.is_jumping = False
        self.jump_count = self.jump_height
