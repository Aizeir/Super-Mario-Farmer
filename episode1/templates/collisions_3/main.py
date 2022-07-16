import pygame as pg
from player import Player
from tile import Tile
pg.init()

W, H = 960, 540
scale = 3
FPS = 30

pg.display.set_caption("Mario")

screen = pg.display.set_mode((W, H))
display = pg.Surface((W//scale, H//scale))
clock = pg.time.Clock()

background = pg.image.load("assets/background.png").convert()

player = Player()
movement = [0, 0]

true_scroll_x = 0
scroll_x = 0

tile_imgs = {
    "f": pg.image.load("assets/floor.png").convert(),
    "b": pg.image.load("assets/brick.png").convert(),
    "l": pg.image.load("assets/lucky.png").convert(),
    "e": pg.image.load("assets/lucky_empty.png").convert(),
    "c": pg.image.load("assets/lucky.png").convert(),
    "t": pg.image.load("assets/tube.png").convert(),
    "T": pg.image.load("assets/tube_top.png").convert(),
    "a": pg.image.load("assets/cube.png").convert(),
    'db': pg.image.load("assets/flag_beam.png").convert(),
    'd': pg.image.load("assets/flag_top.png").convert(),
}

tiles = {}

def generate_tiles():
    map = open("assets/map.txt").read()

    for y, row in enumerate(map.split("\n")):
        for x, id in enumerate(row.split(",")):
            if id in tile_imgs:
                tiles[x, y] = Tile(x, y, id)

generate_tiles()

while True:
    display.blit(background, (0,0))
    display.blit(player.image, (player.rect.x-scroll_x, player.rect.y))

    for tile in tiles.values():
        display.blit(tile_imgs[tile.id], (tile.rect.x-scroll_x, tile.rect.y))

    # Scroll
    true_scroll_x += (player.rect.x+player.rect.w/2-true_scroll_x-W/scale/2) / 1
    scroll_x = max(scroll_x, int(true_scroll_x))
    
    # Mouvement
    dx, dy = movement
    
    # Collisions
    for pos, tile in tiles.items():

        if tile.rect.colliderect(player.rect.x+dx, player.rect.y, player.rect.w, player.rect.h):
            
            if dx > 0: dx = tile.rect.left-player.rect.right
            
            elif dx < 0: dx = tile.rect.right-player.rect.left

        if tile.rect.colliderect(player.rect.x, player.rect.y+dy, player.rect.w, player.rect.h):
            
            if dy > 0: dy = tile.rect.top-player.rect.bottom
            
            elif dy < 0: dy = tile.rect.bottom-player.rect.top
    
    # Appliquer le mouvement
    player.rect.x += dx
    player.rect.y += dy
    player.rect.x = max(player.rect.x, scroll_x) # pour ne pas retourner en arrière

    # Animation joueur
    if dx != 0:
        player.xdir = dx/abs(dx)

        if player.images_cooldown == 0:
            player.images_cooldown = FPS/2
            player.image_idx = (player.image_idx+1)%player.images_len
        else:
            player.images_cooldown -= 1

    if player.xdir < 0:
        player.image = player.images_right[player.image_idx]
    else: 
        player.image = player.images_left[player.image_idx]

    # Player.is_grounded
    player.is_grounded = dy == 0
    
    # Events
    for e in pg.event.get():
        if e.type == pg.QUIT:
            pg.quit()
            exit()

        elif e.type == pg.KEYDOWN:
            if e.key == pg.K_q or e.key == pg.K_LEFT:
                movement[0] = -player.speed
            if e.key == pg.K_d or e.key == pg.K_RIGHT:
                movement[0] = player.speed
                
        elif e.type == pg.KEYUP:
            if e.key == pg.K_q: movement[0] = 0
            if e.key == pg.K_d: movement[0] = 0
            if e.key == pg.K_LEFT: movement[0] = 0
            if e.key == pg.K_RIGHT: movement[0] = 0


    screen.blit(pg.transform.scale(display, (W, H)), (0,0))
    pg.display.flip()
    clock.tick(FPS)
