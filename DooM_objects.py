import pygame
import os
import math
from time import time

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
locations_folder = os.path.join(img_folder, 'room2')
player_img = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, 'player_s.png')), (51, 78))
bullet_img = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, 'bullet.png')), (5, 16))
invisible_bullet_img = bullet_img #pygame.image.load(os.path.join(img_folder, 'invisible_bullet.png'))
locations_imgs = [pygame.image.load(os.path.join(locations_folder, 'room00%02i.png' % (i))) for i in range(16)]

all_sprites = pygame.sprite.Group()
mobs = []

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

    def __init__(self, center, image, list_active_acts=[], list_passive_act=[], *, location='surface'):
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

    def __init__(self, point, angle, damage, image=bullet_img, *, location='surface'):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.angle = angle
        self.image = pygame.transform.rotate(self.image, int((-self.angle - math.pi/2) * 180 / math.pi))
        self.rect = self.image.get_rect()
        self.rect.centery = point.y
        self.rect.centerx = point.x
        self.speed = 10
        self.velocity = Vector(self.speed * math.cos(angle), self.speed * math.sin(angle))
        self.damage = damage

    def update(self):
        self.rect.centerx += self.velocity.x
        self.rect.centery += self.velocity.y
        # убить, если он заходит за границу экрана
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()


class Mob(pygame.sprite.Sprite):
    '''
    Общий класс для всех мобов
    angle ∈ [0; 2*pi)
    '''
    def __init__(self, position, image, hp, *, location='surface', velocity=[0 ,0], reload_time=0.4):
        pygame.sprite.Sprite.__init__(self)
        self.position = position
        self.original_image = self.image = image
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (self.position.x, self.position.y)
        self.angle = 3/2*math.pi
        self.vector_gun_start = Vector((self.rect.right - self.rect.centerx), -(self.rect.top - self.rect.centery) * 3 / 10)
        self.velocity_rel = Vector(0, 0)
        self.gun_position = self.vector_gun_start + Vector(self.rect.centerx, self.rect.centery)
        self.w = 0
        self.hp = hp
        self.reload_time = reload_time
        self.last_shoot_time = time()

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
        self.angle %= (2*math.pi)
        self.image = pygame.transform.rotate(self.original_image, int((-self.angle - math.pi/2) * 180 / math.pi))
        self.rect = self.image.get_rect(center=self.rect.center)
        self.gun_position.x = self.vector_gun_start.x * math.cos(self.angle) - self.vector_gun_start.y * math.sin(self.angle) + self.rect.centerx
        self.gun_position.y = self.vector_gun_start.x * math.sin(self.angle) + self.vector_gun_start.y * math.cos(self.angle) + self.rect.centery

        self.velocity = Vector(self.velocity_rel.x * math.cos(self.angle) - self.velocity_rel.y * math.sin(self.angle),
                      self.velocity_rel.x * math.sin(self.angle) + self.velocity_rel.y * math.cos(self.angle))
        self.position = self.position + self.velocity
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
    bullets = pygame.sprite.Group()

    def __init__(self, point, image, angle_of_vision, player, hp, strategy, *, location='surface'):
        super().__init__(point, image, hp)
        self.angle_of_vision = angle_of_vision
        self.player_position = point
        self.player = player
        self.strategy = strategy
        Enemy.invisible_bullets = pygame.sprite.Group()

    def check_vision(self):
        player_vector = self.player.position - self.gun_position
        angle = math.atan2(player_vector.y, player_vector.x) % (2*math.pi)

        vision = False
        if self.angle - angle < 1E-4:
            vision = True
        elif (self.angle + self.angle_of_vision / 2) % (2*math.pi) > angle or (self.angle - self.angle_of_vision / 2) % (2*math.pi) < angle:
            if not Enemy.invisible_bullets:
                invisible_bullet = Bullet(self.gun_position, angle, invisible_bullet_img)
                Enemy.invisible_bullets.add(invisible_bullet)
                all_sprites.add(
                    invisible_bullet)  # Стоит вообще не передавать ее всем спрайтам, чтобы не отрисовывалась

            # Теперь проверим, достигла ли невидимая пуля игрока
            else:
                hits = pygame.sprite.spritecollide(self.player, Enemy.invisible_bullets, True)
                if hits:
                    vision = True

        return vision, angle

    def update(self):
        self.check_bullet(Player.bullets)
        vision, angle = self.check_vision()
        if vision:
            self.strategy(self, angle)
        self.move()


class Player(Mob):
    bullets = pygame.sprite.Group()


    def update(self):
        self.velocity_rel = Vector(0, 0)
        self.w = 0

        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.w = -5 * math.pi / 180
        if keystate[pygame.K_RIGHT]:
            self.w = 5 * math.pi / 180

        if keystate[pygame.K_a]:
            self.velocity_rel.y = -2
        if keystate[pygame.K_d]:
            self.velocity_rel.y = 2

        if keystate[pygame.K_w]:
            self.velocity_rel.x = 2
        if keystate[pygame.K_s]:
            self.velocity_rel.x = -2

        super().move()
        self.check_bullet(Enemy.bullets)


class Portal(pygame.sprite.Sprite):

    def __init__(self, points, *, thickness=2, location='surface'):
        pygame.sprite.Sprite.__init__(self)
        if points[0][0] == points[1][0]:
            self.image = pygame.Surface((thickness, abs(points[0][1] - points[1][1]) // 2))
            self.rect = self.image.get_rect()
            self.rect.center = (center.x, center.y)
        else:
            self.image = pygame.Surface((abs(points[0][0] - points[1][0]) // 2, thickness))
            self.rect = self.image.get_rect()
            self.rect.center = (abs(points[0][0] + points[1][0]) // 2, abs(points[0][1] + points[1][1]) // 2)


class Location:
    """Класс локации (комнаты).
            Это - сцена для объектов всей игры,
            вне локаций - зона уничтожения объектов."""

    LOCATIONS = dict()  # двухсторонний граф связей всех локаций, словарь вида
    # LOCATIONS = {
    #   локация: {
    #           название соседней локации: [вершины, задающие переход между локациями]
    #           }
    # }


    def __init__(self, *, coords=None, color=None, image=None, max_velocity=[100, 100], owners=dict()):
        if coords is None:
            raise TypeError
        self.coords = coords
        if id is not None:
            self.id = id
        else:
            self.color = color if color is not None else choice(['grey', 'white', 'orange', 'brown'])
            self.id = canv.create_polygon(coords, fill=self.color)
        self.max_vel = max_velocity
        LOCATIONS[self] = owners
        for loc in owners:
            LOCATIONS[loc][self] = owners[loc]
        # self.walls =
        # self.doors =
        # self.guests =

    def is_included(self, object):
        """Артибут проверки того,
        что локация содержит данный объект."""
        return False

    def was_changed(self, object):
        """Атрибут проверки того,
        что данный объект изменил свою локацию после движения."""
        return object.l

    def is_connected(self, location):
        """Атрибут проверки того,
        что две локации соединены переходом."""
        return False