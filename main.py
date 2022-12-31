# Tyler Cobb
# ETGG 1803 Lab #10
# 04/27/2021
# Outside Sources: https://www.kenney.nl/assets/sci-fi-sounds for shot effect

import pygame
import level_manager

pygame.init()

ui_space = 100
win = pygame.display.set_mode((800, 700))
LM = level_manager.level_manager(win, ui_space)
clock = pygame.time.Clock()
done = False

while not done:
    delta_time = clock.tick() / 1000
    LM.update(delta_time)
    done = LM.input()
    LM.draw()
    pygame.display.flip()

pygame.quit()
