import pygame as pg
from player1 import Player
from tile import Tile
from foonga import Foonga
pg.init()

W, H = 960, 540
scale = 3
FPS = 30

pg.display.set_caption("Mario")

screen = pg.display.set_mode((W, H))
display = pg.Surface((W//scale, H//scale))
clock = pg.time.Clock()

background = pg.image.load("assets/background.png").convert()

gravity = 4
MAX_LIVES = 3

player = Player()
movement = [0, gravity]

lives = MAX_LIVES
died = 0

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
foongas = []

def generate_tiles():
    map = open("assets/map.txt").read()

    for y, row in enumerate(map.split("\n")):
        for x, id in enumerate(row.split(",")):
            if id in tile_imgs:
                tiles[x, y] = Tile(x, y, id)

            elif id == "F":
                foongas.append(Foonga(x*Tile.SIZE, y*Tile.SIZE+2))

generate_tiles()

def die():
    global died
    died = FPS*2
    movement[0] = 0
    player.died_jump()
    #pg.mixer.music.stop() # si on met une musique

    
while True:
    display.blit(background, (0,0))
    display.blit(player.image, (player.rect.x-scroll_x, player.rect.y))

    # Tiles
    for tile in tiles.values():
        display.blit(tile_imgs[tile.id], (tile.rect.x-scroll_x, tile.rect.y))

    # Foongas
    for foonga in foongas:
        display.blit(foonga.image, (foonga.rect.x-scroll_x, foonga.rect.y))

    # Scroll
    true_scroll_x += (player.rect.x+player.rect.w/2-true_scroll_x-W/scale/2) / 1
    scroll_x = max(scroll_x, int(true_scroll_x))

    dx, dy = movement

    # Jump
    if player.is_jumping:
        if player.jump_count > 0:
            dy -= (player.jump_count * abs(player.jump_count)) * 0.05
            player.jump_count -= 1
        else: 
            player.stop_jumping()
    
    if not died:
        # Collisions
        for pos, tile in tiles.items():

            if tile.rect.colliderect(player.rect.x+dx, player.rect.y, player.rect.w, player.rect.h):
                
                if dx > 0: dx = tile.rect.left-player.rect.right
                
                elif dx < 0: dx = tile.rect.right-player.rect.left

            if tile.rect.colliderect(player.rect.x, player.rect.y+dy, player.rect.w, player.rect.h):
                
                if dy > 0: dy = tile.rect.top-player.rect.bottom
                
                elif dy < 0: dy = tile.rect.bottom-player.rect.top

    # Foongas
    to_delete = []
    for foonga in foongas:

        # player collision
        if not died and foonga.rect.colliderect(player.rect.x+dx, player.rect.y+dy, player.rect.w, player.rect.h):
            if player.rect.bottom<foonga.rect.top:
                to_delete.append(foonga)

            else: die()

        # movement / collisions
        foonga_dy = gravity

        for pos, tile in tiles.items():
            if tile.rect.colliderect(foonga.rect.x+foonga.move, foonga.rect.y, foonga.rect.w, foonga.rect.h):
                foonga.move = -foonga.move
            if tile.rect.colliderect(foonga.rect.x, foonga.rect.y+foonga_dy, foonga.rect.w, foonga.rect.h):
                foonga_dy = tile.rect.top - foonga.rect.bottom
        
        foonga.rect.x += foonga.move
        foonga.rect.y += foonga_dy

    foongas = [f for f in foongas if f not in to_delete]
    
    # Apply movement
    player.rect.x += dx
    player.rect.y += dy
    player.rect.x = max(player.rect.x, scroll_x)

    # Player.is_grounded
    player.is_grounded = dy == 0

    # Player Animation
    # increment image_idx
    if dx != 0:
        player.xdir = dx/abs(dx)

        if player.images_cooldown == 0:
            player.images_cooldown = FPS/2
            player.image_idx = (player.image_idx+1)%player.images_len
        else:
            player.images_cooldown -= 1
     
    # Select player image
    player_jumping = player.is_jumping and not player.is_grounded
    if player.xdir < 0:
        if player_jumping: 
            player.image = player.image_right_jump
        else: 
            player.image = player.images_right[player.image_idx]
    else: 
        if player_jumping: 
            player.image = player.image_left_jump
        else:
            player.image = player.images_left[player.image_idx]

    # Death state
    if died > 0:
        died -= 1
        if died == 0:

            lives -= 1
            if lives == 0:
                # GAMEOVER
                from gameover import gameover
                gameover(screen, clock, FPS)
                lives = MAX_LIVES

            # RESPAWN
            tiles = {}
            foongas = []
            scroll_x = 0
            player.rect.x = player.DEFAULT_X
            player.rect.y = player.DEFAULT_Y
            generate_tiles()
            #pg.mixer.music.play(-1)
    
    # Events
    for e in pg.event.get():
        if e.type == pg.QUIT:
            pg.quit()
            exit()

        elif e.type == pg.KEYDOWN and not died:
            if e.key == pg.K_q or e.key == pg.K_LEFT:
                movement[0] = -player.speed
            if e.key == pg.K_d or e.key == pg.K_RIGHT:
                movement[0] = player.speed

            if e.key == pg.K_SPACE:
                player.jump()
                
        elif e.type == pg.KEYUP:
            if e.key == pg.K_q: movement[0] = 0
            if e.key == pg.K_d: movement[0] = 0
            if e.key == pg.K_LEFT: movement[0] = 0
            if e.key == pg.K_RIGHT: movement[0] = 0


    screen.blit(pg.transform.scale(display, (W, H)), (0,0))
    pg.display.flip()
    clock.tick(FPS)
