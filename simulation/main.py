import sys
import pygame
import random


##############################################################################
# Things that will go in config file  ########################################
##############################################################################
class Conf:
    SIZE = WIDTH, HEIGHT = 600, 400
    MOVE_VAL = 2
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    COLOR1 = (0, 255, 125)
    COLOR2 = (125, 125, 125)

    # CONSTANTS  #############################################################
    ACCEPT = 0
    UD_UPPER = 1
    UD_LOWER = 2
    LR_LEFT = 1
    LR_RIGHT = 2
# End config file ############################################################


def check_limit(pos, upper=0, lower=Conf.HEIGHT, left=0, right=Conf.WIDTH):
    return_list = [Conf.ACCEPT, Conf.ACCEPT]
    x_left = pos.x
    x_right = pos.x + pos.width
    y_top = pos.y
    y_bottom = pos.y + pos.height
    if y_top <= upper:
        return_list[0] = Conf.UD_UPPER
    elif y_bottom >= lower:
        return_list[0] = Conf.UD_LOWER
    if x_left <= left:
        return_list[1] = Conf.LR_LEFT
    elif x_right >= right:
        return_list[1] = Conf.LR_RIGHT
    return return_list



def main():
    pygame.init()
    screen = pygame.display.set_mode(Conf.SIZE)
    background = pygame.Surface(Conf.SIZE).convert()
    obj = pygame.Surface((50, 50), pygame.SRCALPHA)
    bounce_obj = pygame.Surface((15, 15))
    bounce_obj.fill(Conf.BLACK)
    background.fill(Conf.WHITE)
    pygame.draw.rect(obj, Conf.COLOR1, (0, 0, 50, 50), 2)
    pygame.draw.rect(background, Conf.COLOR2, (10, 20, 73, 26), 2)
    keys = {}
    pos = obj.get_rect(topleft=(30, 20))
    pos1 = bounce_obj.get_rect(topleft=(5, 5))
    screen.blit(background, (0, 0))
    screen.blit(obj, pos)
    pygame.display.update()
    counter = 0
    movement_ud = 1
    movement_lr = 1
    while True:
        counter += 1
        screen.blit(background, pos, pos)
        screen.blit(background, pos1, pos1)
        if counter % 50 == 0:
            movement_ud = int(3 * random.random())
            movement_lr = int(3 * random.random())
            if movement_ud == movement_lr == 0:
                if int(2 * random.random()) == 0:
                    movement_lr = 1
                else:
                    movement_ud = 1

        if movement_ud == 0:  # Neither up or down
            pos1 = pos1.move(0, 0)
        elif movement_ud == 1:  # up
            pos1 = pos1.move(0, -Conf.MOVE_VAL)
        elif movement_ud == 2:  # down
            pos1 = pos1.move(0, Conf.MOVE_VAL)

        if movement_lr == 0:  # Neither left or right
            pos1 = pos1.move(0, 0)
        elif movement_lr == 1:  # left
            pos1 = pos1.move(-Conf.MOVE_VAL, 0)
        elif movement_lr == 2:  # right
            pos1 = pos1.move(Conf.MOVE_VAL, 0)

        x_left = pos1.x
        x_right = pos1.x + pos1.width
        y_top = pos1.y
        y_bottom = pos1.y + pos1.height
        if x_left <= 0 and movement_lr == 1:
            movement_lr = 2
        elif x_right > Conf.WIDTH and movement_lr == 2:
            movement_lr = 1
        if y_top <= 0 and movement_ud == 1:
            movement_ud = 2
        elif y_bottom > Conf.HEIGHT and movement_ud == 2:
            movement_ud = 1

        if keys != {}:
            if pygame.K_UP in keys:
                pos = pos.move(0, -Conf.MOVE_VAL)
            if pygame.K_DOWN in keys:
                pos = pos.move(0, Conf.MOVE_VAL)
            if pygame.K_LEFT in keys:
                pos = pos.move(-Conf.MOVE_VAL, 0)
            if pygame.K_RIGHT in keys:
                pos = pos.move(Conf.MOVE_VAL, 0)
            up_down, left_right = check_limit(pos)
            if up_down == Conf.UD_UPPER:
                pos = pos.move(0, Conf.MOVE_VAL)
            elif up_down == Conf.UD_LOWER:
                pos = pos.move(0, -Conf.MOVE_VAL)
            if left_right == Conf.LR_LEFT:
                pos = pos.move(Conf.MOVE_VAL, 0)
            if left_right == Conf.LR_RIGHT:
                pos = pos.move(-Conf.MOVE_VAL, 0)
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
        screen.blit(bounce_obj, pos1)
        pygame.display.update()
        pygame.time.delay(10)


if __name__ == '__main__':
    main()





