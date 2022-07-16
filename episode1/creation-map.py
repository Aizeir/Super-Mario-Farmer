import pygame as pg
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

    for tile in tiles.values():
        display.blit(tile_imgs[tile.id], (tile.rect.x, tile.rect.y))

    for e in pg.event.get():
        if e.type == pg.QUIT:
            pg.quit()
            exit()

    screen.blit(pg.transform.scale(display, (W, H)), (0,0))
    pg.display.flip()
    clock.tick(FPS)
