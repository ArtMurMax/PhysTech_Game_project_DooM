from random import randrange as rnd, choice
import pygame
import os


WIDTH = 480
HEIGHT = 600
FPS = 60

# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

font_name = pygame.font.match_font('arial')

LOCATIONS = dict()   # двухсторонний граф связей всех локаций, словарь вида
                # LOCATIONS = {
                #   локация: {
                #           название соседней локации: [вершины, задающие переход между локациями]
                #           }
                # }


class Object(pygame.sprite.Sprite):
    """Дефолтный класс внутриигрового объекта.
    Все прочие классы (игрока, врагов, вещей и проч.)
    наследуют его функции."""
    def __init__(
            self, *,
            coords=None,
            color=None,
            id=None,
            velocity=[0 ,0],
            position=[0, 0],
            location='surface',
            live='inf'
    ):
        self.location = location
        if id is not None:
            self.id = id
        elif coords is not None:
            self.coords = coords
            self.color = color if color is not None else choice(['red', 'blue', 'green', 'yellow'])
            self.id = canv.create_polygon(coords, fill=self.color)
        self.vel = velocity
        self.position = position
        self.live = live

    def walltest(self):
        """Проверка локации. Если surface (вне всех локаций),
        то объект удаляется, иначе меняется атрибут location у объекта."""
        if self.location == 'surface':
            self.__del__()
    
    def move(self):
        """Функция перемещения объекта.
        Скорость задаётся из вне
        или посредством редактирования данной функции
        в дочернем классе."""
        self.walltest()
        if self.live != 'inf':
            self.live -= dt
        self.x += self.vx
        self.y += self.vy
        canv.move(self.id, self.vx, self.vy)
    
    def __del__(self):
        """Функция даления (смерти) объекта."""
        canv.delete(self.id)


class Location:
    """Класс локации (комнаты).
    Это - сцена для объектов всей игры,
    вне локаций - зона уничтожения объектов."""
    def __init__(self, *, coords=None, color=None, id=None, max_velocity=[100, 100], owners=dict()):
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
        return False

    def is_connected(self, location):
        """Атрибут проверки того,
        что две локации соединены переходом."""
        return False


# class Player(Object):
#
    """Класс игрока.
    Объект, перемещением, атакой и действиями которого
    управляет игрок с клавиатуры и мыши."""


# class Enemy(Object):
#
    """Класс противников.
    Объект, поведение и атаки которого определяется 
    одним из наперёд заданных алгоритмов
    и прощитывается компьпьютером."""


# Создаем игру и окно
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

# # настройка папки ассетов
# game_folder = os.path.dirname(__file__)
# img_dir = os.path.join(game_folder, 'img')
# background = pygame.image.load(os.path.join(img_dir, 'background.png')).convert()
# background_rect = background.get_rect()
# player_img = pygame.image.load(os.path.join(img_dir, 'player.png')).convert()
# enemy_images = []
# enemy_list =[
#     # названия тукстур врагов
# ]
# for img in enemy_list:
#     enemy_images.append(pygame.image.load(os.path.join(img_dir, img)).convert())
# bullet_img = pygame.image.load(os.path.join(img_dir, "laserRed16.png")).convert()

# all_sprites = pygame.sprite.Group()
# mobs = pygame.sprite.Group()
# bullets = pygame.sprite.Group()
# player = Player()
# all_sprites.add(player)
# for i in range(8):
#     m = Mob()
#     all_sprites.add(m)
#     mobs.add(m)
# score = 0

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
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # player.shoot()
                pass

    # # Обновление
    # all_sprites.update()

    # # Проверка, не ударил ли моб игрока
    # hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)
    # if hits:
    #     running = False

    # hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    # for hit in hits:
    #     score += 50 - hit.radius
    #     m = Mob()
    #     all_sprites.add(m)
    #     mobs.add(m)

    # Отрисовка
    screen.fill(BLACK)
    # screen.blit(background, background_rect)
    # all_sprites.draw(screen)
    # draw_text(screen, str(score), 18, WIDTH / 2, 10)

    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()

pygame.quit()
