import pygame
import random
import math
import os

WIDTH = 800
HEIGHT = 650
FPS = 60

# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
player_img = pygame.image.load(os.path.join(img_folder, 'player.png'))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = player_img
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.fi = 0;

    def update(self):
        speed_rel_x = 0
        speed_rel_y = 0
        w = 0

        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            w = 5 * math.pi / 180
        if keystate[pygame.K_RIGHT]:
            w = -5 * math.pi / 180
        self.fi += w
        self.image = pygame.transform.rotate(self.original_image, int(self.fi * 180 / math.pi))
        self.rect = self.image.get_rect(center=self.rect.center)

        if keystate[pygame.K_a]:
            speed_rel_x = -8
        if keystate[pygame.K_d]:
            speed_rel_x = 8

        if keystate[pygame.K_w]:
            speed_rel_y = -8
        if keystate[pygame.K_s]:
            speed_rel_y = 8

        speed_x = speed_rel_x * math.cos(self.fi) + speed_rel_y * math.sin(self.fi)
        self.rect.x += speed_x
        speed_y = - speed_rel_x * math.sin(self.fi) + speed_rel_y * math.cos(self.fi)
        self.rect.y += speed_y

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0



# Создаем игру и окно
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# Цикл игры
running = True
while running:
    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False

    # Обновление
    all_sprites.update()

    # Рендеринг
    screen.fill(WHITE)
    all_sprites.draw(screen)
    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()