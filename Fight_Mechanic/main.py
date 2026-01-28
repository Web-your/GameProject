# Name: Иван, Date: 08.01.2026, WhatYouDo: создал файл для реализации общей боёвки, определил структуру кода
# Name: Иван и Макс, Date: 08.01.2026, WhatYouDo: добавили интерфейс

import arcade
import random

# Импортируем функции для запуска мини-игр
from Defender_Battle.main import setup_defender
from healFlySticksMechanic.healAct import setup_heal
from FlyArrowsMehanic.FlyArrows import setup_attack

# Импортируем интерфейс для мини-боя
from Fight_Mechanic.MiniGameDopObjects import MiniGameDopBox
from Fight_Mechanic.Interface import Interface


# Константы для интерфейса
MAIN_PANEL_WIDTH = 960
MAIN_PANEL_HEIGHT = 200
BUTTON_WIDTH = 50
BUTTON_HEIGHT = 50
PANEL_MARGIN = 10
ELEMENT_MARGIN = 3

# Константы для окошка мини-игр
MINI_WINDOW_WIDTH = 700
MINI_WINDOW_HEIGHT = 650
MINI_WINDOW_CENTER_X = 500
MINI_WINDOW_CENTER_Y = 420

TYPE_INDEX_DICT = {"menu": 0, "attack": 1, "defense": 2, "heal": 3}
INDEX_TYPE_LIST = ["menu", "attack", "defense", "heal"]

# API выбора
""""
{
    "hero_type" - str (attack, defense, heal):
    {
        "action_type": str (main, support, item, mana),
        "action_data": 
        {
            "count_mana": int,
            "support_hero": str,
            "attack_enemies": int,
            "heal_hero": str,
            "item": int,
            "item_hero": str
        }
    } 
    or None
}
"""

# Динамические объекты
# <-------------------------------------------------------------------------------------------------------------------

# Функция для переключения на меню
def menu_setup(scene_manager, *settings):
    fight_box = scene_manager.fb
    fight_box.mini_window.frame.setup()
    fight_box.window.show_view(fight_box.menu_view)


# Переключается меду сценами, окнами и мини-играми
class PhaseManager:
    def __init__(self, fb):
        self.fb = fb
        self.game_que = ["attack", "heal", "defense"]
        self.mini_games_list = []

        self.curr_hero = None

    def data_handler(self, data):
        for h_type, h_data in data.items():
            a_type, a_data = h_data.values()

            if a_type == "mana":
                self.fb.count_mana += a_data["count_mana"]

            elif a_type == "main":
                self.mini_games_list.append(TYPE_INDEX_DICT[h_type])
                if h_type == "attack":
                    self.fb.attack_hero.curr_enemies = a_data["attack_enemies"]
                elif h_type == "heal":
                    self.fb.heal_hero.curr_heal_hero = a_data["heal_hero"]

            elif a_type == "support":
                self.fb.hero_dict[a_data["support_hero"]].add_support()

            elif a_type == "item":
                # item = self.fb.item_list[a_data["item"]]
                item = self.fb.item_list[0]
                item_hero = a_data["item_hero"]
                item.use(item_hero)

        if len(self.mini_games_list) != 0:
            self.fb.scene_manager.next_scene_index = 0
            self.fb.scene_manager.curr_scene_index = self.mini_games_list[0]
            self.fb.scene_manager.next_scene()

        else:
            self.update()

    def update(self):
        for hero in self.fb.hero_list:
            hero.stop_support()
        self.curr_hero = None
        self.mini_games_list = []

    def temporary_updates(self):
        next_scene_index = self.fb.scene_manager.curr_scene_index
        self.curr_hero = self.fb.hero_dict[INDEX_TYPE_LIST[next_scene_index]]


class SceneManager:
    def __init__(self, fight_box):
        self.fb = fight_box
        self.window = fight_box.window

        # Добавляем сцены в очередь: каждая сцена - функция, которая запускает механику мини-битвы
        self.scenes = [menu_setup, setup_attack, setup_defender, setup_heal]
        self.curr_scene_index = 0 # Индекс текущей сцены в очереди
        self.next_scene_index = 0

    def setup(self):
        self.curr_scene_index = 0
        self.next_scene_index = 0
        self.next_scene()

    # Запускаем следующую сцену
    def next_scene(self, *args):
        func = self.scenes[self.curr_scene_index]
        self.change_curr_scene_index()
        func(self)  # Передаём себя, чтобы вернуться и запустить следующую сцену

    # Меняем индекс текущей сцены
    def change_curr_scene_index(self):
        if self.curr_scene_index == 0:
            self.fb.phase_manager.update()
        else:
            phase_scenes = self.fb.phase_manager.mini_games_list
            self.next_scene_index += 1
            if self.next_scene_index >= len(phase_scenes):
                self.next_scene_index = 0
                self.curr_scene_index = 0
            else:
                self.curr_scene_index = phase_scenes[self.next_scene_index]
                self.fb.phase_manager.temporary_updates()

    # Выходим из боёвки
    def back(self):
        stop_fight(self.fb)


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
        fb = self.fight_box

        arcade.draw_text(
            self.text,
            self.center_x,
            self.center_y,
            arcade.color.WHITE,
            40,
        )

        fb.interface.draw()

    def on_key_press(self, key, modifiers):
        self.fight_box.interface.on_key_press(key, modifiers)

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


class HealEffect:
    def __init__(self, fb):
        self.fb = fb
        self.type = "heal"
        self.heal_boost = 0.1

    def use(self, h_type):
        hero = self.fb.hero_dict[h_type]
        hero.get_health(self.heal_boost)


# Типы эффектов: +-attack, +-health, health_all
class Item:
    def __init__(self, fb, name="item", description="Предмет", effects=None):
        self.fb = fb

        self.name = name
        self.description = description

        if effects is None:
            self.effects = []
        else:
            self.effects = effects

    def use(self, h_type):
        for effect in self.effects:
            effect.use(h_type)


class Enemies:
    def __init__(self, fb, *settings):
        self.fb = fb
        self.health = 1

    def lose_health(self, main_lose_health):
        self.health -= main_lose_health
        if self.health < 0:
            self.health = 0



# Персонажи
# <-------------------------------------------------------------------------------------------------------------------

# Герой
class Hero:
    def __init__(self, fb, h_type):
        self.fb = fb
        self.mg_hero_dict = self.fb.mg_box.interface.hero_list.hero_dict

        self.type = h_type
        self.health = 1

    def lose_health(self, main_lose_health):
        self.health -= main_lose_health
        if self.health < 0:
            self.health = 0
        mg_hero = self.mg_hero_dict[self.type]
        mg_hero.health_bar.update(self.health)
        mg_hero.hero_fon_plank.pulse_frame(color=arcade.color.RED, width=7)

    def get_health(self, main_heal_health):
        self.health += main_heal_health
        if self.health > 1:
            self.health = 1
        mg_hero = self.mg_hero_dict[self.type]
        mg_hero.health_bar.update(self.health)
        mg_hero.hero_fon_plank.pulse_frame(arcade.color.GREEN)

    def add_support(self):
        pass

    def stop_support(self):
        pass


class AttackHero(Hero):
    def __init__(self, fb):
        super().__init__(fb, "attack")

        self.curr_enemies = None
        self.damage_boost = 0

    def hit_damage(self, main_damage):
        damage = main_damage + self.damage_boost
        self.curr_enemies.lose_health(damage)

    def add_support(self):
        self.damage_boost += 0.05

    def stop_support(self):
        self.damage_boost = 0


class DefenseHero(Hero):
    def __init__(self, fb):
        super().__init__(fb, "defense")
        self.lose_health_boost = 0

    def special_lose_health(self, main_lose_health):
        lose_health = main_lose_health + self.lose_health_boost
        if lose_health < 0:
            lose_health = 0

        hero = random.choice(self.fb.hero_list)
        hero.lose_health(lose_health)

    def raise_mana(self, main_raise_mana):
        self.fb.count_mana += main_raise_mana

    def add_support(self):
        self.lose_health_boost -= 0.05

    def stop_support(self):
        self.lose_health_boost = 0


class HealHero(Hero):
    def __init__(self, fb):
        super().__init__(fb, "heal")

        self.heal_hero = None
        self.heal_boost = 0

    def heal(self, main_heal_health):
        heal_health = main_heal_health + self.heal_boost
        self.heal_hero.get_health(heal_health)

    def add_support(self):
        self.heal_boost += 0.05

    def stop_support(self):
        self.heal_boost = 0



# Главное для запуска битвы
# <-------------------------------------------------------------------------------------------------------------------

# Содержит все объекты
class FightBox:
    def __init__(self, main_scene_manager, *settings):
        self.main_scene_manager = main_scene_manager # Ссылка на предыдущий менеджер сцен
        self.window = main_scene_manager.window # Ссылка на окно

        self.mg_box = MiniGameDopBox(self) # Доп объекты для мини-игры
        self.mini_window = self.mg_box.mini_window

        # Параметры окна
        self.width = self.window.width
        self.height = self.window.height
        self.center_x = self.window.center_x
        self.center_y = self.window.center_y

        self.count_mana = 10

        # Создание системных персонажей
        self.attack_hero = AttackHero(self)
        self.defense_hero = DefenseHero(self)
        self.heal_hero = HealHero(self)

        self.hero_dict = {
            "attack": self.attack_hero,
            "defense": self.defense_hero,
            "heal": self.heal_hero
        }
        self.hero_list = list(self.hero_dict.values())

        self.enemies_list = [Enemies(self), Enemies(self)]
        self.item_list = [Item(self, name="heal_item", effects=[HealEffect(self)])]

        self.interface = Interface(self)  # Интерфейс

        self.scene_manager = SceneManager(self)  # Собственный менеджер сцен
        self.phase_manager = PhaseManager(self) # Менеджер фаз
        self.menu_view = MenuView(self)  # Окно отрисовки меню

        self.scene_manager.setup()

    def lose_health(self, main_health_lose):
        self.phase_manager.curr_hero.lose_health(main_health_lose)

    def attack_enemies(self, main_damage):
        # self.phase_manager.curr_hero
        ...

    def heal(self, health_heal):
        if self.phase_manager.curr_support == 3:
            health_heal *= 5/4

        heal_hero = self.hero_dict[self.phase_manager.curr_heal_hero]
        health_heal.health += health_heal

        if health_heal.health > 1:
            heal_hero.health = 1


# Функция для запуска общей битвы
def setup_fight(main_scene_manager, *settings):
    FightBox(main_scene_manager, *settings)


# Функция для остановки общей битвы
def stop_fight(fight_box):
    main_scene_manager = fight_box.main_scene_manager
    # Вносим изменения в main_scene_manager ...
    del fight_box
    main_scene_manager.next_scene()



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
