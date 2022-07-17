from math import floor
import pygame as pg
from player import Player
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

coins = 0
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

# Logo
logo = pg.image.load("assets/super_mario_farmer.png").convert()

# Sounds/Music
pg.mixer.music.load("assets/gameloop.wav")
pg.mixer.music.play(-1)

death_sound = pg.mixer.Sound("assets/death.wav")
coin_sound = pg.mixer.Sound("assets/coin.wav")
foonga_sound = pg.mixer.Sound("assets/foonga.wav")
powerup_sound = pg.mixer.Sound("assets/powerup.wav")
toad_sound = pg.mixer.Sound("assets/toad.wav")
jump_sound = pg.mixer.Sound("assets/jump.wav")
jump_tall_sound = pg.mixer.Sound("assets/jump_tall.wav")
pause_sound = pg.mixer.Sound("assets/pause.wav")
time_warn_sound = pg.mixer.Sound("assets/time_warn.wav")
stage_clear_sound = pg.mixer.Sound("assets/stage_clear.wav")
fireworks_sound = pg.mixer.Sound("assets/fireworks.wav")
powerup_appear_sound = pg.mixer.Sound("assets/powerup_appear.wav")
flagpole_sound = pg.mixer.Sound("assets/flagpole.wav")
sounds = (death_sound, coin_sound, foonga_sound, powerup_sound, toad_sound, jump_sound, jump_tall_sound, pause_sound, time_warn_sound, stage_clear_sound, fireworks_sound, powerup_appear_sound, flagpole_sound)

# Coin Animation
coin_img = pg.image.load("assets/coin.png").convert_alpha()
coin_left_img = pg.image.load("assets/coin_left.png").convert_alpha()
coin_right_img = pg.image.load("assets/coin_right.png").convert_alpha()
coin_img_list = [coin_img, coin_left_img, coin_img, coin_right_img]

coin_anims = [] # (pos, time)
used_blocks = []

def on_tile_collision(tile, side):
    if side == "bottom" and tile not in used_blocks:
        used_blocks.append(tile)

        if tile.id == "c":
            tile.id = "e"
            coin_sound.play()
            coin_anims.append([[tile.pos[0]*tile.SIZE+3, tile.pos[1]*tile.SIZE-12], 0])
            
            global coins
            coins += 1

        elif tile.id == "l":
            tile.id = "e"
            powerup_appear_sound.play()
            #toads.append(Toad(tile.pos[0]*tile.SIZE, (tile.pos[1]-1)*tile.SIZE)) pour plus tard

def die():
    global died
    died = FPS*2
    movement[0] = 0
    player.died_jump()
    pg.mixer.music.stop()
    death_sound.play()

while True:
    display.blit(background, (0,0))
    display.blit(player.image, (player.rect.x-scroll_x, player.rect.y))

    # Tiles
    for tile in tiles.values():
        display.blit(tile_imgs[tile.id], (tile.rect.x-scroll_x, tile.rect.y))

    # Foongas
    for foonga in foongas:
        display.blit(foonga.image, (foonga.rect.x-scroll_x, foonga.rect.y))

    # Coins anims
    for coin_anim in coin_anims:
        display.blit(coin_img, (coin_anim[0][0]-scroll_x, coin_anim[0][1]))

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
                if dx > 0:
                    dx = tile.rect.left-player.rect.right
                    on_tile_collision(tile, "right")
                
                elif dx < 0:
                    dx = tile.rect.right-player.rect.left
                    on_tile_collision(tile, "left")

            if tile.rect.colliderect(player.rect.x, player.rect.y+dy, player.rect.w, player.rect.h):
                if dy > 0:
                    dy = tile.rect.top-player.rect.bottom
                    on_tile_collision(tile, "top")
                
                elif dy < 0:
                    dy = tile.rect.bottom-player.rect.top
                    on_tile_collision(tile, "bottom")

    # Foongas
    to_delete = []
    for foonga in foongas:

        # player collision
        if not died and foonga.rect.colliderect(player.rect.x+dx, player.rect.y+dy, player.rect.w, player.rect.h):
            if player.rect.bottom<foonga.rect.top:
                to_delete.append(foonga)
                foonga_sound.play()

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

    # Coin animations
    to_delete = []
    for coin_anim in coin_anims:
        coin_img = coin_img_list[floor(coin_anim[1])]
        coin_img.set_alpha(256-64*floor(coin_anim[1]))
        coin_anim[0][1] -= 1
        coin_anim[1] += 0.2

        if coin_anim[1] >= 4:
            to_delete.append(coin_anim)

    coin_anims = [c for c in coin_anims if c not in to_delete]

    # timer de mort
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
            pg.mixer.music.play(-1)
    
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
                jump_sound.play()
                
        elif e.type == pg.KEYUP:
            if e.key == pg.K_q: movement[0] = 0
            if e.key == pg.K_d: movement[0] = 0
            if e.key == pg.K_LEFT: movement[0] = 0
            if e.key == pg.K_RIGHT: movement[0] = 0


    screen.blit(pg.transform.scale(display, (W, H)), (0,0))

    # Logo
    screen.blit(logo, (128-scroll_x*scale, 48))

    pg.display.flip()
    clock.tick(FPS)
