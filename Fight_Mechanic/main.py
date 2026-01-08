# Name: Иван, Date: 08.01.2026, WhatYouDo: создал файл для реализации общей боёвки, определил структуру кода

import arcade

# Импортируем функции для запуска мини-игр
from Defender_Battle.main import setup_defender
from healFlySticksMechanic.healAct import setup_heal



# Примеры реализации объектов из других файлов
# <-------------------------------------------------------------------------------------------------------------------

# Окно для атаки
class AttackView(arcade.View):
    def __init__(self, main_scene_manager):
        super().__init__()
        self.main_scene_manager = main_scene_manager
        self.text = "Атака"

    def setup(self):
        ...

    def on_show(self):
        ...

    def on_update(self, delta_time):
        ...

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            self.text,
            self.center_x,
            self.center_y,
            arcade.color.WHITE,
            40
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.back_to_menu()

    def back_to_menu(self):
        self.main_scene_manager.next_scene()


# Функция для запуска атаки
def attack_setup(main_scene_manager, *settings):
    attack_view = AttackView(main_scene_manager)
    main_scene_manager.window.show_view(attack_view)



# Динамические объекты
# <-------------------------------------------------------------------------------------------------------------------

# Функция для переключения на меню
def menu_setup(scene_manager, *settings):
    scene_manager.window.show_view(scene_manager.fight_box.menu_view)


# Переключается меду сценами, окнами и мини-играми
class SceneManager:
    def __init__(self, fight_box):
        self.fight_box = fight_box
        self.window = fight_box.window

        # Добавляем сцены в очередь: каждая сцена - функция, которая запускает механику мини-битвы
        self.scenes = [menu_setup, attack_setup, setup_defender, setup_heal]
        self.curr_scene_index = 0 # Индекс текущей сцены в очереди

    def setup(self):
        self.curr_scene_index = 0
        self.next_scene()

    # Запускаем следующую сцену
    def next_scene(self, *args):
        func = self.scenes[self.curr_scene_index]
        if self.curr_scene_index != 0:
            self.curr_scene_index = 0  # Возвращаемся на меню после мини-боя
        func(self)  # Передаём себя, чтобы вернуться и запустить следующую сцену

    # Выходим из боёвки
    def back(self):
        ...


# Окно отрисовки меню
class MenuView(arcade.View):
    def __init__(self, fight_box):
        super().__init__()
        self.fight_box = fight_box
        self.text = "Меню"

    def setup(self):
        ...

    def on_show(self):
        ...

    def on_update(self, delta_time):
        ...

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            self.text,
            self.center_x,
            self.center_y,
            arcade.color.WHITE,
            40,
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.KEY_1:
            self.to_attack()
        elif key == arcade.key.KEY_2:
            self.to_defender()
        elif key == arcade.key.KEY_3:
            self.to_heal()

    def to_attack(self):
        self.scene_manager = self.fight_box.scene_manager
        self.scene_manager.curr_scene_index = 1
        self.scene_manager.next_scene()

    def to_defender(self):
        self.scene_manager = self.fight_box.scene_manager
        self.scene_manager.curr_scene_index = 2
        self.scene_manager.next_scene()

    def to_heal(self):
        self.scene_manager = self.fight_box.scene_manager
        self.scene_manager.curr_scene_index = 3
        self.scene_manager.next_scene()



# Статичные объекты и спрайты
# <-------------------------------------------------------------------------------------------------------------------

# Задний фон, анимация фона, персонажи, враги - только отрисовка
class Background:
    def __init__(self):
        ...

    # Для отрисовки фоновых объектов
    def draw(self):
        ...


# Интерфейс, кнопки выбора действия, аура - отрисовка и механика
class Interface:
    def __init__(self):
        ...

    # Для отрисовки интерфейса
    def draw(self):
        ...


# Реализация механики персонажей - здоровье, действие, предметы - только механика, отрисовка в Background
class HeroMechanic:
    def __init__(self):
        self.health = 100 # Здоровье
        self.is_in_fight = False # Участвует ли в мини-бое в данный момент
        self.attributes = [] # Предметы в инвенторе



# Главное для запуска битвы
# <-------------------------------------------------------------------------------------------------------------------

# Содержит все объекты
class FightBox:
    def __init__(self, main_scene_manager):
        self.main_scene_manager = main_scene_manager # Ссылка на предыдущий менеджер сцен
        self.window = main_scene_manager.window # Ссылка на окно

        self.scene_manager = SceneManager(self)  # Собственный менеджер сцен
        self.menu_view = MenuView(self)  # Окно отрисовки меню

        self.scene_manager.setup()


# Функция для запуска общей битвы
def setup_fight(main_scene_manager):
    FightBox(main_scene_manager)



# Описание
# <-------------------------------------------------------------------------------------------------------------------
"""
Если вы находитесь в меню, нажмите:
1 - чтобы перейти на атаку
2 - чтобы перейти на защиту
3 - чтобы перейти на лечение

Если вы играете мини-бой, нажмите:
пробел - чтобы вернуться на меню
"""
