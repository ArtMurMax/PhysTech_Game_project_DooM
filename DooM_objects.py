from DooM_consts import *
import pygame
import os
import math
from time import time
import random

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
locations_folder = os.path.join(img_folder, 'room2')
mob_folder = os.path.join(img_folder, 'mob')
bullet_img = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, 'bullet.png')), (5, 16))
invisible_bullet_img = bullet_img #pygame.image.load(os.path.join(img_folder, 'invisible_bullet.png'))
locations_imgs = [pygame.image.load(os.path.join(locations_folder, 'room00%02i.png' % (i))) for i in range(16)]
pygame.mixer.init()
snd_dir = os.path.join(game_folder, 'snd')
snd_shoot = pygame.mixer.Sound(os.path.join(snd_dir, 'shotgun_shot.wav'))
snd_reload = pygame.mixer.Sound(os.path.join(snd_dir, 'shotgun_reload.wav'))
snd_zombie = pygame.mixer.Sound(os.path.join(snd_dir, 'zombie_attack.wav'))

global all_sprites, mobs, portals, BACKGROUND, background_rect

all_sprites = pygame.sprite.Group()
mobs = []
portals = []
PR_LOC = START

def str(self, angle):
    self.angle = angle

def str_zombie(self):
    vision, angle = self.check_vision()
    if (vision or abs(self.angle - angle) < 1E-2 and abs(self.player_vector) < self.r_of_vision) and abs(self.player_vector) > 25:
        self.angle = angle
        self.velocity_rel.x = 2
    elif 10 < abs(self.player_vector) <= 25:
        self.velocity_rel.x = 0.5
    elif abs(self.player_vector) <= 10:
        animation(self, self.img_attack, 1.5, True)
        self.player.hp -= self.damage
        if random.randint(0, 25) == 0:
            snd_zombie.play()
        self.velocity_rel.x = 0
    else:
        self.velocity_rel.x = 0

class Vector():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __abs__(self):
        return (self.x**2 + self.y**2)**0.5

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return self.x * other.x + self.y * other.y

def animation(obj, imgs, frame_time, cyclic, from_begin=False):
    '''Процедура анимирует объекты
    obj - объект
    imgs - список его изображений
    frame_time - раз в сколько кадров обновлять
    cycic - цикличная ли анимация
    from_begin - начать анимацию заново'''
    end = False;

    if from_begin:
        obj.img_number = 0
    if time() - obj.time_last_img_upd >= frame_time / FPS:
        obj.time_last_img_upd = time()
        obj.img_number += 1
        if obj.img_number >= len(imgs):
            if cyclic:
                obj.img_number = 0
            else:
                end = True;
        if obj.img_number < len(imgs):
            obj.original_image = imgs[obj.img_number]

    return end


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
        if self.rect.bottom > BOTTOM or self.rect.top < TOP or self.rect.right > RIGHT or self.rect.left < LEFT:
            self.kill()


class Mob(pygame.sprite.Sprite):
    '''
    Общий класс для всех мобов
    angle ∈ [0; 2*pi)
    '''
    def __init__(self, position, hp, image_number, *, gun_type='', location='surface', velocity=[0 ,0], reload_time=0.8):
        pygame.sprite.Sprite.__init__(self)
        self.position = position
        self.gun_type = gun_type
        if self.gun_type:
            self.gun_type += '_'
        if self.name == 'skeleton':
            self.img_idle = [pygame.transform.scale(pygame.image.load(os.path.join(mob_folder,
                                    '%s-idle_%s%i.png' % (self.name, self.gun_type, i))), (40, 40)) for i in range(image_number)]
        #Кривая графика зомби
            self.img_attack = [pygame.transform.scale(pygame.image.load(os.path.join(mob_folder,
                                    '%s-attack_%s%i.png' % (self.name, self.gun_type, i))), (51, 51)) for i in range(8)]
        else:
            self.img_idle = [pygame.transform.scale(pygame.image.load(os.path.join(mob_folder,
                                    '%s-idle_%s%i.png' % (self.name, self.gun_type, i))), (51, 51)) for i in range(image_number)]
        self.img_move = [pygame.transform.scale(pygame.image.load(os.path.join(mob_folder,
                                    '%s-move_%s%i.png' % (self.name, self.gun_type, i))), (51, 51)) for i in range(image_number)]
        if self.name == 'survivor':
            self.img_reload = [pygame.transform.scale(pygame.image.load(os.path.join(mob_folder,
                        '%s-reload_%s%i.png' % (self.name, self.gun_type, i))), (51, 51)) for i in range(20)]
        self.original_image = self.image = self.img_move[0]
        self.rect = self.image.get_rect()
        self.rect.center = (self.position.x, self.position.y)
        self.angle = 3/2*math.pi
        self.vector_gun_start = Vector((self.rect.right - self.rect.centerx), -(self.rect.top - self.rect.centery) * 5 / 10)
        self.velocity_rel = Vector(0, 0)
        self.gun_position = self.vector_gun_start + Vector(self.rect.centerx, self.rect.centery)
        self.w = 0
        self.hp = hp
        self.reload_time = reload_time
        self.last_shoot_time = time()
        self.time_last_img_upd = time()
        self.img_number = 0
        self.shooting = False
        self.shots = 0
        self.first_for_sound = True

    def shoot(self):
        self.shooting = True
        self.shots += 1
        bullet = Bullet(self.gun_position, self.angle, 40, bullet_img)
        all_sprites.add(bullet)
        self.__class__.bullets.add(bullet)
        snd_shoot.play()

    def check_bullet(self, bullets):
        hits = pygame.sprite.spritecollide(self, bullets, True)
        for hit in hits:
            self.hp -= hit.damage
        if self.hp <= 0:
            self.kill()

    def move(self):
        self.angle += self.w
        self.angle %= (2*math.pi)
        self.image = pygame.transform.rotate(self.original_image, int((-self.angle) * 180 / math.pi))
        self.rect = self.image.get_rect(center=self.rect.center)
        self.gun_position.x = self.vector_gun_start.x * math.cos(self.angle) - self.vector_gun_start.y * math.sin(self.angle) + self.rect.centerx
        self.gun_position.y = self.vector_gun_start.x * math.sin(self.angle) + self.vector_gun_start.y * math.cos(self.angle) + self.rect.centery

        if self.shooting and self.shots >= 5:
            if self.first_for_sound:
                snd_reload.play()
                self.first_for_sound = False
            is_end = animation(self, self.img_reload, self.reload_time * FPS / len(self.img_reload), False)
            if is_end:
                self.first_for_sound = True
                self.shots = 0
                self.shooting = False
                self.img_number = 0

        elif self.velocity_rel.x or self.velocity_rel.y:
            self.velocity = Vector(self.velocity_rel.x * math.cos(self.angle) - self.velocity_rel.y * math.sin(self.angle),
                          self.velocity_rel.x * math.sin(self.angle) + self.velocity_rel.y * math.cos(self.angle))
            self.position = self.position + self.velocity
            self.rect.centerx = self.position.x; self.rect.centery = self.position.y

            if self.rect.right > RIGHT:
                self.rect.right = RIGHT
            if self.rect.left < LEFT:
                self.rect.left = LEFT
            if self.rect.bottom > BOTTOM:
                self.rect.bottom = BOTTOM
            if self.rect.top < TOP:
                self.rect.top = TOP

            animation(self, self.img_move, 2, True)
            self.shooting = False
        else:
            animation(self, self.img_idle, 2, True)



class Enemy(Mob):
    bullets = pygame.sprite.Group()

    def __init__(self, name, point, angle_of_vision, player, hp, strategy, image_number, *, location='surface', r_of_vision=abs(Vector(WIDTH, HEIGHT)), damage=1):
        self.name = name
        self.r_of_vision = r_of_vision
        super().__init__(point, hp, image_number)
        self.angle_of_vision = angle_of_vision
        self.player_position = point
        self.player = player
        self.strategy = strategy
        self.damage = damage
        Enemy.invisible_bullets = pygame.sprite.Group()

    def check_vision(self):
        angle = math.atan2(self.player_vector.y, self.player_vector.x) % (2*math.pi)

        vision = False
        if (self.angle + self.angle_of_vision / 2) % (2*math.pi) > angle or (self.angle - self.angle_of_vision / 2) % (2*math.pi) < angle:
            if not self.invisible_bullets and abs(self.player_vector) < self.r_of_vision:
                invisible_bullet = Bullet(self.gun_position, angle, invisible_bullet_img)
                self.invisible_bullets.add(invisible_bullet)
                all_sprites.add(
                    invisible_bullet)  # Стоит вообще не передавать ее всем спрайтам, чтобы не отрисовывалась

            # Теперь проверим, достигла ли невидимая пуля игрока
            else:
                hits = pygame.sprite.spritecollide(self.player, self.invisible_bullets, True)
                if hits:
                    vision = True

        return vision, angle

    def update(self):
        self.player_vector = self.player.position - self.gun_position
        self.check_bullet(Player.bullets)
        self.strategy(self)
        self.move()


class Player(Mob):
    name = 'survivor'
    bullets = pygame.sprite.Group()
    BACKGROUND = locations_imgs[14]
    background_rect = BACKGROUND.get_rect()

    def check_portal(self):
        tps = pygame.sprite.spritecollide(self, portals, False)
        if tps:
            print(tps[0].pos)
            self.change_location(LOCATIONS[PR_LOC][tps[0].pos], tps[0].pos)

    def update(self):
        self.velocity_rel = Vector(0, 0)
        self.w = 0

        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.w = -2 * math.pi / 180
        if keystate[pygame.K_RIGHT]:
            self.w = 2 * math.pi / 180

        if keystate[pygame.K_a]:
            self.velocity_rel.y = -1
        if keystate[pygame.K_d]:
            self.velocity_rel.y = 1

        if keystate[pygame.K_w]:
            self.velocity_rel.x = 1
        if keystate[pygame.K_s]:
            self.velocity_rel.x = -1

        super().move()
        self.check_bullet(Enemy.bullets)
        self.check_portal()

    def change_location(self, new_loc, portal):
        '''Функция, осуществляющая смену локации.'''

        global PR_LOC, portals, all_sprites

        portals = []
        for sprt in all_sprites:
            if sprt != self:
                sprt.kill()

        if portal == 0:
            self.rect.centerx, self.rect.centery = self.rect.centerx, 500
            self.position.x, self.position.y = self.rect.centerx, 500
        elif portal == 1:
            self.rect.centerx, self.rect.centery = 130, self.rect.centery
            self.position.x, self.position.y = 130, self.rect.centery
        elif portal == 2:
            self.rect.centerx, self.rect.centery = self.rect.centerx, 100
            self.position.x, self.position.y =self.rect.centerx, 100
        else:
            self.rect.centerx, self.rect.centery = 670, self.rect.centery
            self.position.x, self.position.y = 670, self.rect.centery
        self.BACKGROUND = locations_imgs[new_loc[1]]
        self.background_rect = self.BACKGROUND.get_rect()
        PR_LOC = new_loc
        # TODO добавление объектов в локации new_loc
        for i in range(4):
            if LOCATIONS[new_loc][i] != -1:
                portals.append(Portal(i, LOCATIONS[new_loc][i]))
                all_sprites.add(portals[-1])
        for i in range(LOCATIONS[new_loc][-1]):
            mobs.append(Enemy('skeleton', Vector(random.randint(LEFT, RIGHT), random.randint(TOP, BOTTOM)), 180 * (random.random()) * math.pi / 180, self, 100, str_zombie, 16, r_of_vision=300))
            all_sprites.add(mobs[-1])


class Portal(pygame.sprite.Sprite):

    def __init__(self, pos, way, *, lenth=90, thickness=4):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        if pos == 0:
            self.image = pygame.Surface((lenth, thickness))
            self.rect = self.image.get_rect()
            self.rect.center = (400, 60)
        elif pos == 2:
            self.image = pygame.Surface((lenth, thickness))
            self.rect = self.image.get_rect()
            self.rect.center = (400, 540)
        elif pos == 1:
            self.image = pygame.Surface((thickness, lenth))
            self.rect = self.image.get_rect()
            self.rect.center = (710, 300)
        else:
            self.image = pygame.Surface((thickness, lenth))
            self.rect = self.image.get_rect()
            self.rect.center = (90, 300)
        #self.image.fill(YELLOW)
        self.way = way