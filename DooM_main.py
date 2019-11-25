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
YELLOW = (255, 255, 0)

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
player_img = pygame.image.load(os.path.join(img_folder, 'player.png'))
bullet_img = pygame.image.load(os.path.join(img_folder, 'bullet.png'))

class Vector():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, point, angle):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.angle = angle
        self.image = pygame.transform.rotate(self.image, int(self.angle * 180 / math.pi))
        self.rect = self.image.get_rect()
        self.rect.centery = point.y
        self.rect.centerx = point.x
        self.speed = 10
        self.velocity = Vector(- self.speed * math.sin(angle), - self.speed * math.cos(angle))

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        # убить, если он заходит за верхнюю часть экрана
        if self.rect.bottom < 0:
            self.kill()

class Mob(pygame.sprite.Sprite):
    def __init__(self, point, image):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (point.x, point.y)
        self.angle = 0
        self.vector_gun_start = Vector(0, self.rect.top - self.rect.centery)
        self.point_gun = self.vector_gun_start + Vector(self.rect.centerx, self.rect.centery)

    def shoot(self):
        bullet = Bullet(self.point_gun, self.angle)
        all_sprites.add(bullet)
        bullets.add(bullet)

    def move(self):
        self.angle += self.w
        self.image = pygame.transform.rotate(self.original_image, int(self.angle * 180 / math.pi))
        self.rect = self.image.get_rect(center=self.rect.center)
        self.point_gun.x = self.vector_gun_start.x * math.cos(self.angle) + self.vector_gun_start.y * math.sin(self.angle) + self.rect.centerx
        self.point_gun.y = - self.vector_gun_start.x * math.sin(self.angle) + self.vector_gun_start.y * math.cos(self.angle) + self.rect.centery

        self.velocity = Vector(self.velocity_rel.x * math.cos(self.angle) + self.velocity_rel.y * math.sin(self.angle),
                      - self.velocity_rel.x * math.sin(self.angle) + self.velocity_rel.y * math.cos(self.angle))
        self.rect.x += self.velocity.x; self.rect.y += self.velocity.y

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0


class Enemy(Mob):
    def get_course(self, player_position):
        player_vector = Vector(player_position.x - self.rect.centerx, player_position.y - self.rect.centery)
        self.angle = math.atan(player_vector.y / player_vector.x);


class Player(Mob):
    def update(self):
        self.velocity_rel = Vector(0, 0)
        self.w = 0

        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.w = 5 * math.pi / 180
        if keystate[pygame.K_RIGHT]:
            self.w = -5 * math.pi / 180

        if keystate[pygame.K_a]:
            self.velocity_rel.x = -8
        if keystate[pygame.K_d]:
            self.velocity_rel.x = 8

        if keystate[pygame.K_w]:
            self.velocity_rel.y = -8
        if keystate[pygame.K_s]:
            self.velocity_rel.y = 8

        super().move()




# Создаем игру и окно
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
player = Player(Vector(WIDTH/2, HEIGHT/2), player_img)
all_sprites.add(player)
bullets = pygame.sprite.Group()

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