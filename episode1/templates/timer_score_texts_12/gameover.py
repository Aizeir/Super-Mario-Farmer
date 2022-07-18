import pygame as pg

font = pg.font.Font("assets/font.ttf", 50)
gameover_sound = pg.mixer.Sound("assets/gameover.wav") # la musique de gameover

def gameover(screen, clock, fps):

    gameover_label = font.render("GAME OVER", True, (255,255,255))
    gameover_rect = gameover_label.get_rect(centerx=screen.get_width()/2, centery=screen.get_height()/2)
    gameover_sound.play()

    screen.fill((50, 50, 50))
    screen.blit(gameover_label, gameover_rect)
    
    for _ in range(fps*4): # fps*4 = 4 secondes = durée de l'écran gameover
        pg.display.flip()
        clock.tick(fps)

        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()
