from random import randrange as rnd, choice


root = tk.Tk()
fr = tk.Frame(root)
root.geometry('800x600')
canv = tk.Canvas(root, bg='white')
canv.pack(fill=tk.BOTH, expand=1)
dt = 0.03
LOCATIONS = dict()   # двухсторонний граф связей всех локаций, словарь вида
                # LOCATIONS = {
                #   локация: {
                #           название соседней локации: [вершины, задающие переход между локациями]
                #           }
                # }


class Object:
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
