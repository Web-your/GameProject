# Name: Иван, Date: 08.01.2026, WhatYouDo: создал файл для реализации общей боёвки, определил структуру кода
# Name: Иван и Макс, Date: 08.01.2026, WhatYouDo: добавили интерфейс

import arcade

# Импортируем функции для запуска мини-игр
from Defender_Battle.main import setup_defender
from healFlySticksMechanic.healAct import setup_heal
from FlyArrowsMehanic.FlyArrows import setup_attack

# Импортируем интерфейс для мини-боя
from Fight_Mechanic.MiniGameDopObjects import MiniGameDopBox



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



# Динамические объекты
# <-------------------------------------------------------------------------------------------------------------------

# Функция для переключения на меню
def menu_setup(scene_manager, *settings):
    fight_box = scene_manager.fight_box
    fight_box.mini_window.frame.setup()
    fight_box.window.show_view(fight_box.menu_view)


# Переключается меду сценами, окнами и мини-играми
class SceneManager:
    def __init__(self, fight_box):
        self.fight_box = fight_box
        self.window = fight_box.window

        # Добавляем сцены в очередь: каждая сцена - функция, которая запускает механику мини-битвы
        self.scenes = [menu_setup, setup_attack, setup_defender, setup_heal]
        self.curr_scene_index = 0 # Индекс текущей сцены в очереди

    def setup(self):
        self.curr_scene_index = 0
        self.next_scene()

    # Запускаем следующую сцену
    def next_scene(self, *args):
        func = self.scenes[self.curr_scene_index]
        self.change_curr_scene_index()
        func(self)  # Передаём себя, чтобы вернуться и запустить следующую сцену

    # Меняем индекс текущей сцены
    def change_curr_scene_index(self):
        # Возвращаемся на меню после мини-боя
        if self.curr_scene_index != 0:
            self.curr_scene_index = 0

    # Выходим из боёвки
    def back(self):
        stop_fight(self.fight_box)


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
        if key == arcade.key.KEY_1:
            self.to_attack()
        elif key == arcade.key.KEY_2:
            self.to_defender()
        elif key == arcade.key.KEY_3:
            self.to_heal()

    def on_mouse_motion(self, x, y, dx, dy):
        self.fight_box.interface.mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        self.fight_box.interface.mouse_press(x, y, button, modifiers)

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
    def __init__(self, fight_box):
        self.fight_box = fight_box
        self.window = fight_box.window

        self.panel_color = arcade.color.WHITE_SMOKE
        self.small_panel_color = arcade.color.LIGHT_GRAY

        self.main_panel_width = MAIN_PANEL_WIDTH
        self.main_panel_height = MAIN_PANEL_HEIGHT
        self.small_panel_width = 180
        self.small_panel_height = 40

        self.main_panel_x = fight_box.width // 2
        self.main_panel_y = MAIN_PANEL_HEIGHT // 2 + 50

        self.small_panel_x = self.main_panel_x - self.main_panel_width / 2 + self.small_panel_width / 2
        self.small_panel_y = self.main_panel_y + self.main_panel_height / 2 + self.small_panel_height / 2

        self.buttons_list = arcade.SpriteList()
        self.zones_list = arcade.SpriteList()
        self.icons_list = arcade.SpriteList()

        self.textures = {}
        self.load_textures()

        self.create_interface()

    def load_textures(self):
        texture_info = {
            'ATK_icon': {
                'normal': 'Fight_Mechanic/Static/Interface_Textures/ATK_icon.png',
                'active': 'Fight_Mechanic/Static/Interface_Textures/ATK_act_icon.png',
                'color': arcade.color.RED
            },
            'DEF_icon': {
                'normal': 'Fight_Mechanic/Static/Interface_Textures/DEF_icon.png',
                'active': 'Fight_Mechanic/Static/Interface_Textures/DEF_act_icon.png',
                'color': arcade.color.BLUE
            },
            'HEAL_icon': {
                'normal': 'Fight_Mechanic/Static/Interface_Textures/HEAL_icon.png',
                'active': 'Fight_Mechanic/Static/Interface_Textures/HEAL_act_icon.png',
                'color': arcade.color.GREEN
            },
            'ITEM_icon': {
                'normal': 'Fight_Mechanic/Static/Interface_Textures/ITEM_icon.png',
                'active': 'Fight_Mechanic/Static/Interface_Textures/ITEM_act_icon.png',
                'color': arcade.color.PURPLE
            },
            'something_icon': {
                'normal': 'Fight_Mechanic/Static/Interface_Textures/something_icon.png',
                'active': 'Fight_Mechanic/Static/Interface_Textures/something_act_icon.png',
                'color': arcade.color.ORANGE
            },
            'icon_circle': {
                'normal': None,
                'active': None,
                'color': arcade.color.DARK_BLUE
            }
        }

        for name, info in texture_info.items():
            try:
                if info['normal']:
                    self.textures[name] = arcade.load_texture(info['normal'])
                else:
                    self.textures[name] = None
            except:
                self.textures[name] = None
                print(f"Текстура {info['normal']} не загружена")

            try:
                if info['active']:
                    self.textures[name + '_active'] = arcade.load_texture(info['active'])
                else:
                    self.textures[name + '_active'] = None
            except:
                self.textures[name + '_active'] = None
                print(f"Активная текстура {info['active']} не загружена")

            self.textures[name + '_color'] = info['color']
            self.textures[name + '_color_active'] = (
                max(0, info['color'][0] - 50),
                max(0, info['color'][1] - 50),
                max(0, info['color'][2] - 50)
            )

    def create_button_sprite(self, x, y, texture_name, width, height):
        normal_texture = self.textures.get(texture_name)
        active_texture = self.textures.get(texture_name + '_active')
        normal_color = self.textures.get(texture_name + '_color', arcade.color.LIGHT_GRAY)
        active_color = self.textures.get(texture_name + '_color_active', arcade.color.GRAY)

        if normal_texture:
            sprite = arcade.Sprite()
            sprite.texture = normal_texture

            scale_x = width / sprite.width
            scale_y = height / sprite.height
            sprite.scale = min(scale_x, scale_y)

            sprite.normal_texture = normal_texture
            sprite.active_texture = active_texture
        else:
            sprite = arcade.SpriteSolidColor(width, height, normal_color)
            sprite.normal_texture = None
            sprite.active_texture = None

        sprite.center_x = x
        sprite.center_y = y

        sprite.texture_name = texture_name
        sprite.normal_color = normal_color
        sprite.active_color = active_color
        sprite.is_hovered = False

        return sprite

    def create_interface(self):
        zone_width = (self.main_panel_width - PANEL_MARGIN * 4) // 3 - 60
        zone_height = self.main_panel_height - 120

        for i in range(3):
            zone_x = (self.main_panel_x - self.main_panel_width / 2 + PANEL_MARGIN +
                      zone_width // 2 + i * (zone_width + PANEL_MARGIN) + 20 * i + 40)
            zone_y = self.main_panel_y - 15

            zone_color = None
            if i == 0:
                zone_color = arcade.color.LIGHT_BLUE
            elif i == 1:
                zone_color = arcade.color.LIGHT_YELLOW
            else:
                zone_color = arcade.color.LIGHT_GREEN

            zone_sprite = arcade.SpriteSolidColor(zone_width, zone_height, zone_color)
            zone_sprite.center_x = zone_x
            zone_sprite.center_y = zone_y
            zone_sprite.sprite_type = "zone"
            zone_sprite.zone_index = i
            self.zones_list.append(zone_sprite)

            icon_x = zone_x - zone_width / 2 + 25
            icon_y = zone_y

            icon_sprite = arcade.SpriteSolidColor(24, 24, arcade.color.DARK_BLUE)
            icon_sprite.center_x = icon_x
            icon_sprite.center_y = icon_y
            icon_sprite.sprite_type = "icon"
            icon_sprite.zone_index = i
            self.icons_list.append(icon_sprite)

            for j in range(3):
                button_x = icon_x + 35 + j * (BUTTON_WIDTH + ELEMENT_MARGIN) + BUTTON_WIDTH / 2
                button_y = zone_y

                texture_name = None

                if j == 0:
                    if i == 0:
                        texture_name = 'ATK_icon'
                    elif i == 1:
                        texture_name = 'DEF_icon'
                    elif i == 2:
                        texture_name = 'HEAL_icon'
                elif j == 1:
                    texture_name = 'ITEM_icon'
                elif j == 2:
                    texture_name = 'something_icon'

                # Создаем кнопку-спрайт
                button_sprite = self.create_button_sprite(
                    button_x,
                    button_y,
                    texture_name,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT
                )

                button_sprite.button_type = texture_name
                button_sprite.zone_index = i
                button_sprite.button_index = j

                self.buttons_list.append(button_sprite)

    def update_button_texture(self, button, is_hovered):
        if is_hovered != button.is_hovered:
            button.is_hovered = is_hovered

            if button.normal_texture:
                if is_hovered and button.active_texture:
                    button.texture = button.active_texture
                else:
                    button.texture = button.normal_texture
            else:
                if is_hovered:
                    button.color = button.active_color
                else:
                    button.color = button.normal_color

    def draw(self):
        main_panel_rect = arcade.LRBT(
            left=self.main_panel_x - self.main_panel_width / 2,
            right=self.main_panel_x + self.main_panel_width / 2,
            bottom=self.main_panel_y - self.main_panel_height / 2,
            top=self.main_panel_y + self.main_panel_height / 2
        )
        arcade.draw_rect_filled(main_panel_rect, self.panel_color)
        arcade.draw_rect_outline(main_panel_rect, arcade.color.BLACK, 2)

        small_panel_rect = arcade.LRBT(
            left=self.main_panel_x - self.main_panel_width / 2,
            right=self.main_panel_x - self.main_panel_width / 2 + self.small_panel_width,
            bottom=self.main_panel_y + self.main_panel_height / 2,
            top=self.main_panel_y + self.main_panel_height / 2 + self.small_panel_height
        )
        arcade.draw_rect_filled(small_panel_rect, self.small_panel_color)
        arcade.draw_rect_outline(small_panel_rect, arcade.color.BLACK, 2)

        connection_rect = arcade.LRBT(
            left=self.main_panel_x - self.main_panel_width / 2,
            right=self.main_panel_x - self.main_panel_width / 2 + self.small_panel_width,
            bottom=self.main_panel_y + self.main_panel_height / 2,
            top=self.main_panel_y + self.main_panel_height / 2 + 2
        )
        arcade.draw_rect_filled(connection_rect, arcade.color.DARK_GRAY)

        self.zones_list.draw()

        for zone in self.zones_list:
            arcade.draw_rect_outline(
                arcade.LRBT(
                    left=zone.center_x - zone.width / 2,
                    right=zone.center_x + zone.width / 2,
                    bottom=zone.center_y - zone.height / 2,
                    top=zone.center_y + zone.height / 2
                ),
                arcade.color.BLACK,
                1
            )

        self.icons_list.draw()

        for i, icon in enumerate(self.icons_list):
            arcade.draw_text(
                str(i + 1),
                icon.center_x,
                icon.center_y,
                arcade.color.WHITE,
                12,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )

        self.buttons_list.draw()

        for button in self.buttons_list:
            has_texture = button.normal_texture is not None

            if not has_texture:
                text = ""
                if button.button_index == 0:
                    if button.zone_index == 0:
                        text = "ATK"
                    elif button.zone_index == 1:
                        text = "DEF"
                    elif button.zone_index == 2:
                        text = "HEAL"
                elif button.button_index == 1:
                    text = "ITEM"
                elif button.button_index == 2:
                    text = "???"

                arcade.draw_text(
                    text,
                    button.center_x,
                    button.center_y,
                    arcade.color.BLACK,
                    10,
                    anchor_x="center",
                    anchor_y="center",
                    bold=True
                )

    def mouse_motion(self, x, y, dx, dy):
        for button in self.buttons_list:
            left = button.center_x - button.width / 2
            right = button.center_x + button.width / 2
            bottom = button.center_y - button.height / 2
            top = button.center_y + button.height / 2

            is_hovered = (left <= x <= right and bottom <= y <= top)

            self.update_button_texture(button, is_hovered)

    def mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for btn in self.buttons_list:
                left = btn.center_x - btn.width / 2
                right = btn.center_x + btn.width / 2
                bottom = btn.center_y - btn.height / 2
                top = btn.center_y + btn.height / 2

                if left <= x <= right and bottom <= y <= top:
                    zone_idx = btn.zone_index
                    btn_idx = btn.button_index
                    btn_type = btn.button_type

                    print(f"Нажата кнопка: Зона {zone_idx + 1}, Кнопка {btn_idx + 1} ({btn_type})")

                    return



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

        self.interface = Interface(self) # Интерфейс

        self.scene_manager = SceneManager(self)  # Собственный менеджер сцен
        self.menu_view = MenuView(self)  # Окно отрисовки меню

        self.scene_manager.setup()


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
