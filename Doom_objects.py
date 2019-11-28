import pygame
import os
import math

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
invisible_bullet_img = bullet_img #pygame.image.load(os.path.join(img_folder, 'invisible_bullet.png'))

all_sprites = pygame.sprite.Group()

class Vector():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return self.x * other.x + self.y * other.y

class Object(pygame.sprite.Sprite):
    def __init__(self, center, image, list_active_acts=[], list_passive_act=[]):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (center.x, center.y)
        self.list_active_acts = list_active_acts
        self.list_passive_acts = list_passive_act

    def passive_act(self):
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_f]:
            for func in self.list_passive_acts:
                func()

    def active_act(self):
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_f]:
            for func in self.list_active_acts:
                func()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, point, angle, damage, image=bullet_img):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.angle = angle
        self.image = pygame.transform.rotate(self.image, int(self.angle * 180 / math.pi))
        self.rect = self.image.get_rect()
        self.rect.centery = point.y
        self.rect.centerx = point.x
        self.speed = 10
        self.velocity = Vector(- self.speed * math.sin(angle), - self.speed * math.cos(angle))
        self.damage = damage

    def update(self):
        self.rect.centerx += self.velocity.x
        self.rect.centery += self.velocity.y
        # убить, если он заходит за границу экрана
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()


class Mob(pygame.sprite.Sprite):
    bullets = pygame.sprite.Group()

    def __init__(self, position, image, hp):
        pygame.sprite.Sprite.__init__(self)
        self.position = position
        self.original_image = image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (self.position.x, self.position.y)
        self.angle = 0
        self.vector_gun_start = Vector(0, self.rect.top - self.rect.centery)
        self.velocity_rel = Vector(0, 0)
        self.gun_position = self.vector_gun_start + Vector(self.rect.centerx, self.rect.centery)
        self.w = 0
        self.hp = hp

    def shoot(self):
        bullet = Bullet(self.gun_position, self.angle, 50, bullet_img)
        all_sprites.add(bullet)
        self.__class__.bullets.add(bullet)

    def check_bullet(self, bullets):
        hits = pygame.sprite.spritecollide(self, bullets, True)
        for hit in hits:
            self.hp -= hit.damage
        if self.hp <= 0:
            self.kill()

    def move(self):
        self.angle += self.w
        self.angle %= 2 * math.pi
        self.image = pygame.transform.rotate(self.original_image, int(self.angle * 180 / math.pi))
        self.rect = self.image.get_rect(center=self.rect.center)
        self.position.x = self.rect.centerx; self.position.y = self.rect.centery
        self.gun_position.x = self.vector_gun_start.x * math.cos(self.angle) + self.vector_gun_start.y * math.sin(self.angle) + self.rect.centerx
        self.gun_position.y = - self.vector_gun_start.x * math.sin(self.angle) + self.vector_gun_start.y * math.cos(self.angle) + self.rect.centery

        self.velocity = Vector(self.velocity_rel.x * math.cos(self.angle) + self.velocity_rel.y * math.sin(self.angle),
                      - self.velocity_rel.x * math.sin(self.angle) + self.velocity_rel.y * math.cos(self.angle))
        self.position += self.velocity
        self.rect.centerx = self.position.x; self.rect.centery = self.position.y

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0


class Enemy(Mob):
    def __init__(self, point, image, angle_of_vision, player, hp):
        super().__init__(point, image, hp )
        self.angle_of_vision = angle_of_vision
        self.player_position = point
        self.player = player
        Enemy.invisible_bullets = pygame.sprite.Group()


    def get_course(self, player_position):
        player_vector = player_position - self.gun_position
        if player_vector.y < 0:
            angle = math.atan(player_vector.x / player_vector.y)
        elif player_vector.y == 0 and player_vector.x > 0:
            angle = -math.pi / 2
        elif player_vector.y == 0 and player_vector.x < 0:
            angle = math.pi / 2
        else:
            angle = math.pi + math.atan(player_vector.x / player_vector.y)

        angle %= 2 * math.pi

        if 0 < abs(angle - self.angle): # < self.angle_of_vision / 2: #Ограничение по углу так и не работает
            ret = False
            if not Enemy.invisible_bullets:
                invisible_bullet = Bullet(self.gun_position, angle, invisible_bullet_img)
                Enemy.invisible_bullets.add(invisible_bullet)
                all_sprites.add(invisible_bullet) #Стоит вообще не передавать ее всем спрайтам, чтобы не отрисовывалась

            #Теперь проверим, достигла ли невидимая пуля игрока
            else:
                hits = pygame.sprite.spritecollide(self.player, Enemy.invisible_bullets, True)
                if hits:
                    self.angle = angle
                    ret = True

            return ret

    def update(self):
        self.move()
        self.check_bullet(Player.bullets)


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
        # self.check_bullet(Enemy.bullets)