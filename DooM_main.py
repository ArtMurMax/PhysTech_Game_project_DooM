import pygame
import random
import math
import os
from DooM_objects import *

WIDTH = 800
HEIGHT = 650
FPS = 60

def str(self, angle):
    self.angle = angle

# Создаем игру и окно
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()
player = Player(Vector(WIDTH/2, HEIGHT/2), player_img, 100)
mobs.append(player)
all_sprites.add(player)
mobs.append(Enemy(Vector(200, 200), player_img, 180 * math.pi / 180, player, 100, str))
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
            if event.key == pygame.K_SPACE:
                player.shoot()

    # Обновление
    all_sprites.update()

    # Рендеринг
    screen.fill(WHITE)
    all_sprites.draw(screen)
    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()