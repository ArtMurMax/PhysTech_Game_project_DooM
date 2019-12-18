from DooM_consts import *
import pygame
import random
import math
import os
from time import time
from DooM_objects import *


def str(self, angle):
    self.angle = angle

def str_zombie(self):
    vision, angle = self.check_vision()
    if (vision or abs(self.angle - angle) < 1E-2 and abs(self.player_vector) < self.r_of_vision) and abs(self.player_vector) > 25:
        self.angle = angle
        self.velocity_rel.x = 0.25
    elif 10 < abs(self.player_vector) <= 25:
        self.velocity_rel.x = 0.25
    elif abs(self.player_vector) <= 10:
        animation(self, self.img_attack, 1.5, True)
        self.player.hp -= self.damage
        if random.randint(0, 25) == 0:
            snd_zombie.play()
        self.velocity_rel.x = 0
    else:
        self.velocity_rel.x = 0

# Создаем игру и окно
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()
player = Player(Vector(WIDTH/2, HEIGHT/2), 100, 20, gun_type='shotgun')
mobs.append(player)
all_sprites.add(player)
mobs.append(Enemy('skeleton', Vector(200, 200), 180 * math.pi / 180, player, 100, str_zombie, 16, r_of_vision=300))
all_sprites.add(mobs[-1]) #Берем последний элемент

player.change_location(START, 0)

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
        if player.hp <= 0:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and time() - player.last_shoot_time > player.reload_time:
                player.shoot()
                player.last_shoot_time = time()

    # Обновление
    all_sprites.update()

    # Рендеринг
    screen.fill(BLACK)
    screen.blit(player.BACKGROUND, player.background_rect)
    all_sprites.draw(screen)
    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()