from math import ceil, floor
import pygame as pg
from toad import Toad
from foonga import Foonga
from player import Player
from tile import Tile
pg.init()

pg.display.set_caption("Super Mario Farmer")

# Constantes
W, H = 960, 540
scale = 3
FPS = 30

# Scroll
true_scroll_x = 0
scroll_x = 0

# Screen
screen = pg.display.set_mode((W, H))
display = pg.Surface((W//scale, H//scale))
clock = pg.time.Clock()

# Background
background = pg.image.load("assets/background.png").convert()

# Joueur
player = Player()
MAX_LIVES = 3
TIMER = 400*FPS

# Dictionnaire ID: image
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

# Liste des tiles ou on peut passer à travers
not_solid_ids = ['db', 'd']

# Fonction pour inscrire les tiles
def generate_tiles():
    map = open("assets/map.txt").read()

    for y, row in enumerate(map.split("\n")):
        for x, id in enumerate(row.split(",")):
            if id in tile_imgs:
                tiles[x, y] = Tile(x, y, id)

                if id == 'd': # Drapeau (noter la position...)
                    global flag_pos, initial_flag_y
                    initial_flag_y = y*Tile.SIZE
                    flag_pos = [x*Tile.SIZE, initial_flag_y]

            elif id == "F": # Foongas (goombas)
                foongas.append(Foonga(x*Tile.SIZE, y*Tile.SIZE+2))

                
tiles = {} # Dictionnaire des Tiles
foongas = [] # Liste des foongas (goombas) me demandez pas pourquoi jai choisi ce nom
toads = [] # Liste des toads

# Infos sur le drapeau: position, image, position Y initiale
# drapeau = petit triangle qui descend quand tu gagnes
flag_pos = []
flag_img = pg.image.load("assets/flag.png").convert()
initial_flag_y = 0

# Bon je l'ai mis la mais mettez le ou vous voulez
generate_tiles()

gravity = 4 # Constante: gravité
movement = [0, gravity] # Mouvement du joueur (non affecte par les collisions)
died = 0 # timer de mort (0 = pas mort / autre chose=mort, reste x secondes avant d'être re en vie ou gameover)
paused = False
muted = False
cant_move = False # est ce que on freeze le joueur (quand il a gagné jai pas mis que le joueur entre dans le chateau je lai juste freeze)
timer = TIMER # timer du jeu (quelques minutes)

won = False # est-ce que le joueur a gagné
win_time = 0 # timer de victoire (pour passer d'une musique à l'autre) bon vous verrez a quoi ca sert

# Police d'écriture
font = pg.font.Font("assets/font.ttf", 20)

# Score/Coins/Vies
score = 0
coins = 0
lives = MAX_LIVES

# Logo SUPER AMRIO FARMER
logo = pg.image.load("assets/super_mario_farmer.png").convert()

# Sons/Music
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

coin_anims = [] # stocke les animations des coins sous la forme (pos, time)
used_blocks = [] # Lucky blocks utilisés

# Fonction pour interagir en cas de collision joueur-bloc (luckyblocks...)
def on_tile_collision(tile, side):
    if side == "bottom" and tile not in used_blocks:
        used_blocks.append(tile)

        global score

        if tile.id == "c": # Luckyblocks COIN
            tile.id = "e"
            coin_sound.play()
            coin_anims.append([[tile.pos[0]*tile.SIZE+3, tile.pos[1]*tile.SIZE-12], 0])
            
            global coins
            coins += 1
            score += 200

        elif tile.id == "l": # Luckyblocks TOAD
            tile.id = "e"
            powerup_appear_sound.play()
            toads.append(Toad(tile.pos[0]*tile.SIZE, (tile.pos[1]-1)*tile.SIZE))

            score += 1000
    
    global win_time, cant_move, won
    if tile.id == "db" and not won: # Si le joueur touche le pilier du drapeau
        win_time = 1*FPS
        pg.mixer.music.stop()
        pg.mixer.music.unload()
        flagpole_sound.play()
        cant_move = True
        won = True

# juste une fonction pour muter ou non tous les sons en meme temps
def set_sound_volume(vol):
    for s in sounds:
        s.set_volume(vol)

# tuer le joueur
def die():
    global died
    died = FPS*2
    movement[0] = 0
    player.died_jump()
    pg.mixer.music.stop()
    death_sound.play()

# DISPLAY
def display_world():
    display.blit(background, (0,0)) # background
    display.blit(player.image, (player.rect.x-scroll_x, player.rect.y)) # image joueur

    # Tiles
    for tile in tiles.values():
        display.blit(tile_imgs[tile.id], (tile.rect.x-scroll_x, tile.rect.y))
    display.blit(flag_img, (flag_pos[0]-scroll_x, flag_pos[1]))

    # Foongas
    for foonga in foongas:
        display.blit(foonga.image, (foonga.rect.x-scroll_x, foonga.rect.y))

    # Toads
    for toad in toads:
        display.blit(toad.image, (toad.rect.x-scroll_x, toad.rect.y))

    # Coins anims
    for coin_anim in coin_anims:
        display.blit(coin_img, (coin_anim[0][0]-scroll_x, coin_anim[0][1]))
    
    # Display
    screen.blit(pg.transform.scale(display, (W, H)), (0,0))

    # Logo
    screen.blit(logo, (128-scroll_x*scale, 48))

    # Texts
    screen.blit(font.render(f"Score {score}", True, (255, 255, 255)), (20,20))
    screen.blit(font.render(f"Coins {coins}", True, (255, 255, 255)), (220,20))
    screen.blit(font.render(f"Lives {lives}", True, (255, 255, 255)), (420,20))
    screen.blit(font.render(f"Timer {ceil(timer/FPS)}", True, (255, 255, 255)), (620,20))
    
    pg.display.flip()
    clock.tick(FPS)

# INPUTS / EVENTS
def inputs():
    for e in pg.event.get():
        # bon vous connaissez
        if e.type == pg.QUIT:
            pg.quit()
            exit()

        elif e.type == pg.KEYDOWN and not died:
            global paused, muted

            if not paused and not cant_move:
                # Mouvement
                if e.key == pg.K_q or e.key == pg.K_LEFT:
                    movement[0] = -player.speed
                if e.key == pg.K_d or e.key == pg.K_RIGHT:
                    movement[0] = player.speed
                    
                # Saut
                if e.key == pg.K_SPACE and player.is_grounded: 
                    player.jump()
                    if player.is_tall: jump_tall_sound.play()
                    else: jump_sound.play()
            
            # Pause (gérer les sons...)
            if e.key == pg.K_p: 
                paused = not paused
                if paused: 
                    pg.mixer.music.set_volume(0)
                    pause_sound.play()
                elif not muted:
                    set_sound_volume(1)
                    pg.mixer.music.set_volume(1)
             
            # Mute
            elif e.key == pg.K_m: 
                muted = not muted
                if muted:
                    set_sound_volume(0)
                    pg.mixer.music.set_volume(0)
                elif not paused:
                    set_sound_volume(1)
                    pg.mixer.music.set_volume(1)
                    
        # Key up (mouvement)
        elif e.type == pg.KEYUP and not died: 
            if e.key == pg.K_q: movement[0] = 0
            if e.key == pg.K_d: movement[0] = 0

# LOGIC
while True:
     
    # si le jeu est en pause on affiche juste
    if paused:
        inputs()
        display_world()
        continue

    # Scroll
    true_scroll_x += (player.rect.x+player.rect.w/2-true_scroll_x-W/scale/2) / 1
    scroll_x = max(scroll_x, int(true_scroll_x))

    # Immune (cad le joueur ne tue personne et n'est pas tué: c'est quand il vient de se faire boloss alors qi'il etait 'grand')
    if player.immune > 0:
        player.immune -= 1

    # Movement
    dx, dy = movement

    # Jump (calcul): https://www.techwithtim.net/tutorials/game-development-with-python/pygame-tutorial/jumping/
    if player.is_jumping:
        if player.jump_count >= -player.jump_height:
            dy -= (player.jump_count * abs(player.jump_count)) * 0.05
            player.jump_count -= 1
        else:
            player.stop_jumping()

    # Collisions
    if not died:
        for pos, tile in tiles.items():
            is_prop = tile.id in not_solid_ids # si le bloc est traversable
       
            if tile.rect.colliderect(player.rect.x+dx, player.rect.y, player.rect.w, player.rect.h):

                if dx > 0: 
                    if not is_prop: 
                        dx = tile.rect.left-player.rect.right
                    on_tile_collision(tile, "right")

                elif dx < 0:
                    if not is_prop: 
                        dx = tile.rect.right-player.rect.left
                    on_tile_collision(tile, "left")

            if tile.rect.colliderect(player.rect.x, player.rect.y+dy, player.rect.w, player.rect.h):
              
                if dy > 0: 
                    if not is_prop: 
                        dy = tile.rect.top-player.rect.bottom
                    on_tile_collision(tile, "top")

                elif dy < 0: 
                    if not is_prop: 
                        dy = tile.rect.bottom-player.rect.top
                    on_tile_collision(tile, "bottom")

        # Foongas (goombas au cas ou vous avez oublié)
        to_delete = [] # bon ca cest juste pour pouvoir supprimer les foongas pendant l'iteration
        for foonga in foongas:

            # collision joueur
            if foonga.rect.colliderect(player.rect.x+dx, player.rect.y+dy, player.rect.w, player.rect.h):
                # Si le joueur l'attaque par le haut (si le joueur est plus haut que le foonga) rappelez vous on a pas encore appliqué le mouvement au joueur !
                if player.rect.bottom<foonga.rect.top: 
                    to_delete.append(foonga)
                    score += 100
                    foonga_sound.play()

                elif player.immune == 0: # Sinon si il est pas 'immune'
                    if player.is_tall: # SET SMALL
                        player.set_small()

                    else: die() # PLAYER DIED

            # movement du foonga
            foonga_dy = gravity
            
            # collisions
            for pos, tile in tiles.items():
                if tile.rect.colliderect(foonga.rect.x+foonga.move, foonga.rect.y, foonga.rect.w, foonga.rect.h):
                    foonga.move = -foonga.move
                    
                if tile.rect.colliderect(foonga.rect.x, foonga.rect.y+foonga_dy, foonga.rect.w, foonga.rect.h):
                    foonga_dy = tile.rect.top - foonga.rect.bottom
            
            foonga.rect.x += foonga.move
            foonga.rect.y += foonga_dy
        
        foongas = [f for f in foongas if f not in to_delete] # on supprime ceux qui sont morte

        # Toads bon c'est a peu pres pareil que foonga
        to_delete = []

        for toad in toads:
            # player collision
            if toad.rect.colliderect(player.rect.x+dx, player.rect.y+dy, player.rect.w, player.rect.h):
                player.set_tall()
                powerup_sound.play()
                to_delete.append(toad)

            # movement
            toad_dy = gravity

            for pos, tile in tiles.items():
                if tile.rect.colliderect(toad.rect.x+toad.move, toad.rect.y, toad.rect.w, toad.rect.h):
                    toad.move = -toad.move
                if tile.rect.colliderect(toad.rect.x, toad.rect.y+toad_dy, toad.rect.w, toad.rect.h):
                    toad_dy = tile.rect.top - toad.rect.bottom
            
            toad.rect.x += toad.move
            toad.rect.y += toad_dy
        
        toads = [t for t in toads if t not in to_delete]

    # Applquer le Movement
    player.rect.x += dx
    player.rect.y += dy
    player.rect.x = max(player.rect.x, scroll_x)

    # Player Animation
    # la c pour les animations de marche, regler le cooldown entre chaque frame (player.images_cooldow) et l'index de l'image actuelle (player.image_idx)
    if dx != 0:
        player.xdir = dx/abs(dx)

        if player.images_cooldown == 0:
            player.images_cooldown = FPS/2
            player.image_idx = (player.image_idx+1)%player.images_len
        else: player.images_cooldown -= 1
    
    player_jumping = player.is_jumping and not player.is_grounded
    # bon la c pour connaitre quelle image le joueur doit avoir (si il saute/est grand...)
    if player.xdir < 0:
        if player.is_tall and player_jumping:
            player.image = player.image_right_jump_tall
        elif player_jumping: 
            player.image = player.image_right_jump
        elif player.is_tall: 
            player.image = player.images_right_tall[player.image_idx]
        else: 
            player.image = player.images_right[player.image_idx]
    else: 
        if player.is_tall and player_jumping: 
            player.image = player.image_left_jump_tall
        elif player_jumping: 
            player.image = player.image_left_jump
        elif player.is_tall: 
            player.image = player.images_left_tall[player.image_idx]
        else: 
            player.image = player.images_left[player.image_idx]

    # Player.is_grounded: savoir si il est par terre (jump)
    player.is_grounded = dy == 0

    # Coin animations (pos, time)
    to_delete = []
    for coin_anim in coin_anims:
        coin_img = coin_img_list[floor(coin_anim[1])]
        coin_img.set_alpha(256-64*floor(coin_anim[1]))
        coin_anim[0][1] -= 1
        coin_anim[1] += 0.2

        if coin_anim[1] >= 4:
            to_delete.append(coin_anim)

    coin_anims = [c for c in coin_anims if c not in to_delete]

    # quand le joueur meurt
    if died > 0:
        died -= 1
        if died == 0:

            lives -= 1
            if lives == 0:
                # GAMEOVER
                from gameover import gameover
                gameover(screen, clock, FPS)
                lives = MAX_LIVES
                coins = 0

            # RESPAWN
            timer = TIMER
            tiles = {}
            foongas = []
            toads = []
            score = 0
            scroll_x = 0
            player.rect.x = player.DEFAULT_X
            player.rect.y = 0
            generate_tiles()
            pg.mixer.music.play(-1)
    
    # Timer du jeu
    if timer > 0 and not died and not won:
        timer -= 1
        if timer == 0: die()
  
    # une alerte quand il reste 10 secondes (je sais pas c omment dans le jeu mais pg)
    if timer == 10*FPS and not died and not won:
        time_warn_sound.play()

    # quand le joueur gagne
    if win_time > 0 and not died:
        win_time -= 1
        flag_pos[1] = min(initial_flag_y+Tile.SIZE*6, flag_pos[1]+3)

        if win_time == 0:
            stage_clear_sound.play()

    inputs()
    display_world()
