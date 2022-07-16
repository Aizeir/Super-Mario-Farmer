import pygame as pg

class Player:
    DEFAULT_X = 128

    def __init__(self):
        
        # les images/animations...
        self.images_left = [pg.image.load("assets/mario_0.png").convert_alpha(), pg.image.load("assets/mario_1.png").convert_alpha()]
        self.images_right = [pg.transform.flip(x, True, False) for x in self.images_left]
        self.image_left_jump = pg.image.load("assets/mario_jump.png").convert_alpha()
        self.image_right_jump = pg.transform.flip(self.image_left_jump, True, False)

        self.images_left_tall = [pg.image.load("assets/mario_tall_0.png").convert_alpha(), pg.image.load("assets/mario_tall_1.png").convert_alpha()]
        self.images_right_tall = [pg.transform.flip(x, True, False) for x in self.images_left_tall]
        self.image_left_jump_tall = pg.image.load("assets/mario_jump_tall.png").convert_alpha()
        self.image_right_jump_tall = pg.transform.flip(self.image_left_jump_tall, True, False)

        self.image_idx = 0
        self.images_len = len(self.images_left)
        self.images_cooldown = 0
        self.image = self.images_left[self.image_idx]
           
        # Rect
        self.rect = self.images_left[0].get_rect()
        self.rect.x = self.DEFAULT_X
        self.rect.y = self.DEFAULT_Y
            
        self.xdir = 1 # si le joueur va a droite ou a gauche: ca sert pas a grand-chose juste pour les animations
        self.speed = 2
        self.jump_height = 17
        self.jump_count = self.jump_height

        self.is_jumping = False
        self.is_grounded = False
        self.is_tall = False

        self.immune = 0 # timer immune

    def jump(self):
        if self.is_grounded:
            self.is_jumping = True
            self.jump_count = self.jump_height

    def died_jump(self): # le saut de quand il est mort: un peu moins haut
        self.jump()
        self.jump_count = 15

    def stop_jumping(self):
        self.is_jumping = False
        self.jump_count = self.jump_height

    def set_tall(self):
        self.is_tall = True
        self.rect.w = self.images_left_tall[0].get_width()
        self.rect.h = self.images_left_tall[0].get_height()
    
    def set_small(self):
        self.is_tall = False
        self.rect.w = self.images_left[0].get_width()
        self.rect.h = self.images_left[0].get_height()
        self.immune = 90
