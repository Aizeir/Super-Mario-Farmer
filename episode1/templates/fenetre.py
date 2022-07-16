import pygame as pg
pg.init()

pg.display.set_caption("Mario")

screen = pg.display.set_mode((960, 540))
clock = pg.time.Clock()

while True:
    for e in pg.event.get():
        if e.type == pg.QUIT:
            pg.quit()
            exit()

    pg.display.flip()
    clock.tick(30)
