import sys
import pygame


##############################################################################
# Things that will go in config file  ########################################
##############################################################################
class Conf:
    SIZE = WIDTH, HEIGHT = 400, 500
# End config file ############################################################


def main():
    pygame.init()
    screen = pygame.display.set_mode(Conf.SIZE)
    color = [255, 255, 255]
    screen.fill(color)
    pygame.draw.rect(screen, [0, 0, 0], [50, 10, 30, 55])
    pygame.draw.circle(screen,[0, 0, 0], [250, 250], 12, 2, draw_top_right=True)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


if __name__ == '__main__':
    main()





