import sys
import pygame


##############################################################################
# Things that will go in config file  ########################################
##############################################################################
class Conf:
    SIZE = WIDTH, HEIGHT = 1000, 1000
    MOVE_VAL = 2
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    COLOR1 = (0, 255, 125)
    COLOR2 = (125, 125, 125)
# End config file ############################################################


def main():
    pygame.init()
    screen = pygame.display.set_mode(Conf.SIZE)
    background = pygame.Surface((1000, 1000)).convert()
    obj = pygame.Surface((50, 50), pygame.SRCALPHA)
    background.fill(Conf.WHITE)
    pygame.draw.rect(obj, Conf.COLOR1, (0, 0, 50, 50), 2)
    pygame.draw.rect(background, Conf.COLOR2, (20, 50, 530, 510), 2)
    keys = {}
    pos = obj.get_rect(topleft=(10, 520))
    screen.blit(background, (0, 0))
    screen.blit(obj, pos)
    pygame.display.update()
    while True:
        screen.blit(background, pos, pos)
        if keys != {}:
            if pygame.K_UP in keys:
                pos = pos.move(0, -Conf.MOVE_VAL)
            if pygame.K_DOWN in keys:
                pos = pos.move(0, Conf.MOVE_VAL)
            if pygame.K_LEFT in keys:
                pos = pos.move(-Conf.MOVE_VAL, 0)
            if pygame.K_RIGHT in keys:
                pos = pos.move(Conf.MOVE_VAL, 0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    keys[event.key] = event.key
                elif event.key == pygame.K_DOWN:
                    keys[event.key] = event.key
                elif event.key == pygame.K_LEFT:
                    keys[event.key] = event.key
                elif event.key == pygame.K_RIGHT:
                    keys[event.key] = event.key
                elif event.key == pygame.K_k:
                    print("k has been pressed")
                elif event.key == pygame.K_0:
                    print("0 has been pressed")
                elif event.key == pygame.K_ESCAPE:
                    sys.exit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    del keys[event.key]
                elif event.key == pygame.K_DOWN:
                    del keys[event.key]
                elif event.key == pygame.K_LEFT:
                    del keys[event.key]
                elif event.key == pygame.K_RIGHT:
                    del keys[event.key]
        screen.blit(obj, pos)
        pygame.display.update()
        pygame.time.delay(10)


if __name__ == '__main__':
    main()





