import arcade
import EasySprite
from EasyBlock import VisualBlock, TextureBlock

HERO_TYPE_ICON_PATH_DICT = {
    "attack" : "Fight_Mechanic/Static/Interface_Textures/attack_icon.png",
    "defense": "Fight_Mechanic/Static/Interface_Textures/defense_icon.png",
    "heal": "Fight_Mechanic/Static/Interface_Textures/heal_icon.png"
}


class MiniWindow:
    def __init__(self, mg_box):
        window = mg_box.fight_box.window

        # Параметры окна
        self.left = 150
        self.right = 150
        self.top = 50
        self.bottom = mg_box.interface.main_height + 50

        self.x = self.left
        self.y = self.bottom

        self.width = window.width - self.left - self.right
        self.height = window.height - self.top - self.bottom

        self.center_x = self.left + self.width // 2
        self.center_y = self.bottom + self.height // 2

        # Декоративная рамки окна
        self.frame = self.Frame(self)

    # Отрисовка декоративных элементов окна
    def draw(self):
        self.frame.draw()

    # Декоративная рамка окна
    class Frame:
        def __init__(self, mini_window):
            self.mini_window = mini_window

            self.base_color = arcade.color.WHITE
            self.base_border_width = 3

            self.curr_color = self.base_color
            self.curr_border_width = self.base_border_width

            self.rect = arcade.XYWH(
                mini_window.center_x,
                mini_window.center_y,
                mini_window.width,
                mini_window.height
            )

            # Настройка пульсации
            self.can_pulse = True
            self.is_pulse = False
            self.base_pulse_time = 0.2

        def draw(self):
            arcade.draw_rect_outline(self.rect, self.curr_color, self.curr_border_width)

        # Пульсация рамки - резкая кратковременная подсветка
        def start_pulse(self, color=None, border_width=None, time=None):
            if self.can_pulse:
                if not self.is_pulse:
                    self.is_pulse = True

                    if color is None:
                        color = self.base_color
                    if border_width is None:
                        border_width = self.base_border_width
                    if time is None:
                        time = self.base_pulse_time

                    self.curr_color = color
                    self.curr_border_width = border_width

                    arcade.schedule(self.stop_pulse, time)

        def stop_pulse(self, delta_time=0):
            arcade.unschedule(self.stop_pulse)

            self.is_pulse = False

            self.curr_color = self.base_color
            self.curr_border_width = self.base_border_width


class MiniGameInterface:
    def __init__(self, mg_box):
        self.window = mg_box.window

        self.main_height = 120 # Высота интерфейса (без учёта ауры)

        self.main_fon_plank = VisualBlock(
            0,
            0,
            self.window.width,
            self.main_height,
            show_fon=False,
            creation_type="LBWH"
        )

        self.hero_list = self.HeroList(self)

    def draw(self):
        self.main_fon_plank.draw()
        self.hero_list.draw()


    class HeroList:
        def __init__(self, interface):
            self.main_fon_plank = interface.main_fon_plank

            self.count_heros = 3

            self.indent = 20 # Отступ слева, справа, сверху, снизу и шаг между героями
            self.hero_width = (self.main_fon_plank.width - self.indent * (self.count_heros + 1)) // self.count_heros
            self.hero_height = self.main_fon_plank.height - self.indent * 2

            self.types_lst = ["attack", "defense", "heal"]
            self.heros_lst = []

            for i in range(0, self.count_heros):
                left = self.main_fon_plank.left + self.indent + i * (self.hero_width + self.indent)
                bottom = self.main_fon_plank.bottom + self.indent
                cords = (left, bottom, self.hero_width, self.hero_height)

                hero_type = self.types_lst[i]

                hero = self.Hero(i, hero_type, cords, interface)
                self.heros_lst.append(hero)

        def draw(self):
            for hero in self.heros_lst:
                hero.draw()

        class Hero:
            def __init__(self, number, hero_type, cords, interface):
                self.hero_fon_plank = VisualBlock(
                    *cords,
                    creation_type="LBWH",
                    show_fon=False
                )

                # Отступ слева и справа и шаг между иконкой и полоской здоровья
                self.indent = 20

                self.icon_path = HERO_TYPE_ICON_PATH_DICT[hero_type]
                self.icon_img = EasySprite.load_image(self.icon_path, scale=3)

                self.icon = TextureBlock(
                    self.hero_fon_plank.left + self.indent,
                    self.hero_fon_plank.bottom + (self.hero_fon_plank.height - self.icon_img.height) // 2,
                    self.icon_img,
                )

                self.health_bar = self.HealthBar(
                    self.icon.right + (self.hero_fon_plank.right - self.icon.right) // 2,
                    self.hero_fon_plank.center_y,
                    self,
                    width=self.hero_fon_plank.right - self.icon.right - self.indent * 2,
                    health_factor=0.7
                )

            def draw(self):
                self.hero_fon_plank.draw()
                self.icon.draw()
                self.health_bar.draw()

            class HeroNumber:
                ...

            class HeroText:
                ...

            class HealthBar:
                def __init__(
                        self,
                        center_x: int,
                        center_y: int,
                        hero,
                        width: int = 100,
                        height: int = 10,
                        health_factor: float = 1
                ):
                    self.hero = hero

                    self.health_factor = health_factor  # Доля здоровья

                    self.width = width
                    self.height = height
                    self.center_x = center_x
                    self.center_y = center_y

                    self.curr_health_color = arcade.color.GREEN
                    self.rest_health_color = arcade.color.RED

                def update(self, new_health_factor):
                    self.health_factor = new_health_factor

                def draw(self):
                    bottom = self.center_y - self.height // 2

                    # Текущее здоровье (зелёный)
                    curr_health_width = self.width * self.health_factor
                    curr_health_left = self.center_x - self.width // 2
                    arcade.draw_lbwh_rectangle_filled(
                        curr_health_left,
                        bottom,
                        curr_health_width,
                        self.height,
                        self.curr_health_color
                    )

                    # Остаток здоровья до максимума (красный)
                    rest_health_width = self.width - curr_health_width
                    rest_health_left = curr_health_left + curr_health_width
                    arcade.draw_lbwh_rectangle_filled(
                        rest_health_left,
                        bottom,
                        rest_health_width,
                        self.height,
                        self.rest_health_color
                    )


    class Aura:
        def __init__(self, interface):
            ...

        def draw(self):
            ...

        class AuraFonPlank:
            def __init__(self, aura):
                self.rect = ...
                self.frame = ...

            def draw(self):
                ...

        class AuraIcon:
            def __init__(self, aura):
                self.icon = ...

            def draw(self):
                ...

        class AuraBar:
            def __init__(self, aura):
                ...

            def draw(self):
                ...

            def update(self, new_aura_factor):
                ...

        class AuraScore:
            def __init__(self, aura):
                self.score_text = ...

            def draw(self):
                ...


class MiniGameCurtain:
    def __init__(self, mg_box):
        self.window = mg_box.window
        self.mini_window = mg_box.mini_window
        self.fon_color = arcade.color.BLACK

    def draw(self):
        window = self.window
        mini_window = self.mini_window

        # Левый
        arcade.draw_lbwh_rectangle_filled(0,0, mini_window.x, window.height, self.fon_color)

        # Правый
        arcade.draw_lbwh_rectangle_filled(
            mini_window.x + mini_window.width,
            0,
            window.width - mini_window.width - mini_window.x,
            window.height,
            self.fon_color
        )

        # Нижний
        arcade.draw_lbwh_rectangle_filled(mini_window.x, 0, mini_window.width, mini_window.y, self.fon_color)

        # Верхний
        arcade.draw_lbwh_rectangle_filled(
            mini_window.x,
            mini_window.y + mini_window.height,
            mini_window.width,
            window.height - mini_window.height - mini_window.y,
            self.fon_color)


class Persons:
    def __init__(self, mg_box):
        ...

    def draw(self):
        ...


class MiniGameDopBox:
    def __init__(self, fight_box):
        self.fight_box = fight_box
        self.window = fight_box.window

        self.interface = MiniGameInterface(self)
        self.mini_window = MiniWindow(self)
        self.curtain = MiniGameCurtain(self)
        self.persons = Persons(self)

    def draw(self):
        self.curtain.draw()
        self.mini_window.draw()
        self.interface.draw()
        self.persons.draw()
