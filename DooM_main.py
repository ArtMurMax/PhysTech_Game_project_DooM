from DooM_consts import *
import pygame
import random
import math
import os
from time import time
from DooM_objects import *

def str(self, angle):
    self.angle = angle

# Создаем игру и окно
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()
player = Player(Vector(WIDTH/2, HEIGHT/2), 100, gun_type='shotgun')
mobs.append(player)
all_sprites.add(player)
mobs.append(Enemy(Vector(200, 200), 180 * math.pi / 180, player, 100, str))
all_sprites.add(mobs[-1]) #Берем последний элемент



# Цикл игры
running = True
while running:
    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    for event in pygame.event.get():
        # проверка для закрытия окна
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and time() - player.last_shoot_time > player.reload_time:
                player.shoot()
                player.last_shoot_time = time()

    # Обновление
    all_sprites.update()

    # Рендеринг
    screen.fill(WHITE)
    all_sprites.draw(screen)
    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()