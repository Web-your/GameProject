""" Name: Максим | Date: 26.01.2026 | WhatYouDo: Заставил шкалу ауры работать, добавил иконки к основным действиям и поменял выделение у выбранных зон """
import arcade
import os
import matplotlib.font_manager as fm
import pyglet

from EasySprite_Lib.EasySprite import EasySprite

# Константы
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 400
MAIN_PANEL_WIDTH = 960
MAIN_PANEL_HEIGHT = 140
BUTTON_WIDTH = 50
BUTTON_HEIGHT = 50
PANEL_MARGIN = 10
ELEMENT_MARGIN = 10

# Состояния интерфейса
STATE_NORMAL = "normal"  # Обычный режим
STATE_SELECTION = "selection"  # Режим выбора целей/предметов
STATE_ALL_SELECTED = "all_selected"  # Все зоны выбраны
STATE_ZONE_SELECTION = "zone_selection"  # Режим выбора зоны для предмета

# Количество спрайтов для каждого уровня ауры
AURA_POINT_COUNTS = {
    0: 0,
    1: 21,
    2: 41,
    3: 62,
    4: 82,
    5: 102,
    6: 123,
    7: 143,
    8: 164,
    9: 184,
    10: 204
}

# API выбора 2
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

class Interface:
    def __init__(self, fb):
        self.fb = fb

        self.selected_data = {}
        self.hero_type_list = ["attack", "defense", "heal"]
        self.curr_hero = None
        self.curr_choice = {}
        self.curr_selection_type = None

        # Цвета интерфейса
        self.background_color = arcade.color.BLACK
        self.panel_color = arcade.color.BLACK
        self.small_panel_color = arcade.color.DIM_GRAY

        # Размеры и позиции панелей
        self.main_panel_width = MAIN_PANEL_WIDTH
        self.main_panel_height = MAIN_PANEL_HEIGHT + 100

        self.main_panel_x = SCREEN_WIDTH // 2
        self.main_panel_y = MAIN_PANEL_HEIGHT // 2 + 50

        self.small_panel_width = 180
        self.small_panel_height = 40
        self.small_panel_x = self.main_panel_x - self.main_panel_width / 2 + self.small_panel_width / 2
        self.small_panel_y = self.main_panel_y + self.main_panel_height / 2 + self.small_panel_height / 2

        # Списки графических элементов
        self.buttons_list = arcade.SpriteList()  # Список кнопок действий
        self.zones_list = arcade.SpriteList()  # Список зон (3 зоны)
        self.icons_list = arcade.SpriteList()  # Список иконок зон
        self.selection_buttons_list = arcade.SpriteList()  # Список кнопок выбора целей
        self.selection_icons_list = arcade.SpriteList()  # Список иконок для кнопок выбора

        # Переменные для режима выбора
        self.selection_zone = None  # Окно выбора целей
        self.selection_items = []  # Элементы для выбора
        self.selection_columns = []  # Колонки элементов
        self.selection_indicator = None  # Индикатор текущего выбора
        self.selected_item_index = 0  # Индекс выбранного элемента
        self.selected_column = 0  # Индекс выбранной колонки
        self.active_zone_index = None  # Индекс активной зоны (0-2)

        # Состояния интерфейса
        self.current_selection_type = None  # Тип текущего выбора
        self.ui_state = STATE_NORMAL  # Текущее состояние

        # Аура
        self.aura = 10  # Текущее значение ауры
        self.max_aura = 10  # Максимальное значение ауры

        # Данные о выборах
        self.confirmed_selections = {}  # Подтверждённые выборы по зонам
        self.selected_zones = []  # Индексы выбранных зон
        self.selected_buttons = {}  # Выбранные кнопки по зонам

        # Навигация по кнопкам
        self.selected_button_zone = 0  # Выбранная зона для кнопки
        self.selected_button_index = 0  # Выбранная кнопка в зоне
        self.button_indicator = None  # Индикатор текущей кнопки

        # Текстуры и спрайты
        self.textures = {}  # Загруженные текстуры
        self.button_sprites = {}  # Спрайты кнопок
        self.zone_texture = None  # Текстура зоны
        self.selection_button_texture = None  # Текстура кнопок выбора
        self.item_subwindow_texture = None  # Текстура подокна предметов
        self.aura_bar_texture = None  # Текстура шкалы ауры
        self.aura_bar_point_texture_1 = None  # Текстура первой точки шкалы ауры
        self.aura_bar_point_texture_2 = None  # Текстура средней точки шкалы ауры
        self.aura_bar_point_texture_3 = None  # Текстура последней точки шкалы ауры (только для 10 уровня)
        self.aura_bar_point_sprites = arcade.SpriteList()  # Список спрайтов точек шкалы ауры
        self.selection_icon_textures = {}  # Текстуры иконок для кнопок выбора

        # Шрифт
        self.font_name = None
        self.load_font()

        # Загрузка текстур после инициализации шрифта
        self.load_textures()

        # Подокно для предметов
        self.item_subwindow = None

        # Для режима выбора зоны предмета
        self.selected_item_for_zone = None  # Выбранный предмет для применения к зоне
        self.temp_selected_item = None  # Временное хранение выбранного предмета
        self.temp_selected_item_index = None  # Временное хранение индекса выбранного предмета
        self.temp_selected_column = None  # Временное хранение колонки выбранного предмета
        self.original_zone_index = None  # Сохраняем оригинальную зону, в которой был начат выбор
        self.target_zone_index = None  # Зона, к которой будет применен предмет

        # Создание интерфейса
        self.create_interface()
        self.update_button_indicator()

        # Инициализация спрайтов точек ауры
        self.init_aura_point_sprites()

    """Инициализирует спрайты точек ауры в соответствии с текущим уровнем ауры"""

    def init_aura_point_sprites(self):
        self.update_aura_point_sprites()

    """Обновляет спрайты точек ауры в соответствии с текущим уровнем ауры"""

    def update_aura_point_sprites(self):
        # Очищаем старые спрайты
        self.aura_bar_point_sprites.clear()

        # Получаем количество спрайтов для текущего уровня ауры
        point_count = AURA_POINT_COUNTS.get(self.aura, 0)

        if point_count == 0:
            return

        # Загружаем текстуры
        textures_available = all([
            self.aura_bar_point_texture_1,
            self.aura_bar_point_texture_2
        ])

        # Создаем спрайты
        for i in range(point_count):
            # Если это максимальный уровень маны (10) и предпоследняя точка - пропускаем её (создаём пробел)
            if self.aura == 10 and i == point_count - 2:
                continue  # Пропускаем создание предпоследнего спрайта - это будет пробел

            sprite = arcade.Sprite()

            # ВАЖНО: текстура 3 только для ауры 10 И последней точки
            is_last_point = (i == point_count - 1)
            is_max_aura = (self.aura == 10)

            # Выбираем текстуру в зависимости от позиции и уровня ауры
            if i == 0:  # Первая точка
                if self.aura_bar_point_texture_1:
                    sprite.texture = self.aura_bar_point_texture_1
                elif textures_available:
                    sprite.texture = self.aura_bar_point_texture_1
                else:
                    continue
            elif is_last_point and is_max_aura:  # Последняя точка при ауре 10
                if self.aura_bar_point_texture_3:
                    sprite.texture = self.aura_bar_point_texture_3
                elif self.aura_bar_point_texture_2:
                    sprite.texture = self.aura_bar_point_texture_2
                else:
                    continue
            else:  # Остальные средние точки
                if self.aura_bar_point_texture_2:
                    sprite.texture = self.aura_bar_point_texture_2
                elif textures_available:
                    sprite.texture = self.aura_bar_point_texture_2
                else:
                    continue

            # Настраиваем масштаб
            target_width = 40  # Обычная ширина
            target_height = 30  # Обычная высота

            scale_x = target_width / sprite.width
            scale_y = target_height / sprite.height
            sprite.scale = min(scale_x, scale_y)

            # Позиция будет установлена при отрисовке
            self.aura_bar_point_sprites.append(sprite)

    """Загружает кастомный шрифт"""

    def load_font(self):
        font_filename = "Fight_Mechanic/Static/Interface/web_ibm_mda.ttf"

        # Загружаю шрифт
        try:
            # Проверяем, существует ли файл
            if os.path.exists(font_filename):
                # Регистрируем шрифт в pyglet
                pyglet.font.add_file(font_filename)

                # Получаем имя шрифта через matplotlib.font_manager(использовалось для проверки)
                font_prop = fm.FontProperties(fname=font_filename)
                self.font_name = font_prop.get_name()
                return
            else:
                print(f"Файл шрифта не найден в текущей директории: {font_filename}")
        except Exception as e:
            print(f"Ошибка при загрузке шрифта: {e}")

        # План Б
        font_paths = [
            font_filename,
            os.path.join(".", font_filename),
            os.path.join("fonts", font_filename),
        ]

        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    # Регистрируем шрифт в pyglet
                    pyglet.font.add_file(font_path)

                    # Получаем имя шрифта через matplotlib.font_manager(использовалось для проверки)
                    font_prop = fm.FontProperties(fname=font_path)
                    self.font_name = font_prop.get_name()
                    return
            except Exception as e:
                print(f"Ошибка при загрузке шрифта из {font_path}: {e}")
                continue

        # Если ничего не помогло, используем стандартный шрифт
        print("Шрифт web_ibm_mda.ttf не найден. Используется стандартный шрифт.")
        self.font_name = "Arial"

    """Загружает все текстуры для интерфейса"""

    def load_textures(self):
        try:
            self.zone_texture = EasySprite.upscale_image(
                "Fight_Mechanic/Static/Interface/Field.png", 2)
        except Exception as e:
            print(f"Ошибка при загрузке текстуры Field.png: {e}")
            self.zone_texture = None

        try:
            self.selection_button_texture = EasySprite.upscale_image(
                "Fight_Mechanic/Static/Interface/SelectionLine.png", 4)
        except Exception as e:
            print(f"Ошибка при загрузке текстуры SelectionLine.png: {e}")
            self.selection_button_texture = None

        try:
            self.item_subwindow_texture = EasySprite.upscale_image(
                "Fight_Mechanic/Static/Interface/Field.png", 2)
        except Exception as e:
            print(f"Ошибка при загрузке текстуры Field.png: {e}")
            self.item_subwindow_texture = None

        try:
            # Загружаем текстуру ауры
            self.aura_bar_texture = EasySprite.upscale_image(
                "Fight_Mechanic/Static/Interface/AuraBar.png", 2)
        except Exception as e:
            print(f"Ошибка при загрузке текстуры AuraBar.png: {e}")
            self.aura_bar_texture = None

        # Загружаем текстуры точек шкалы ауры
        try:
            # Первая точка
            self.aura_bar_point_texture_1 = EasySprite.upscale_image(
                "Fight_Mechanic/Static/Interface/AuraBarPoint1.png", 2)
        except Exception as e:
            print(f"✗ Ошибка при загрузке текстуры AuraBarPoint1.png: {e}")
            self.aura_bar_point_texture_1 = None

        try:
            # Средняя точка
            self.aura_bar_point_texture_2 = EasySprite.upscale_image(
                "Fight_Mechanic/Static/Interface/AuraBarPoint2.png", 2)
        except Exception as e:
            print(f"Ошибка при загрузке текстуры AuraBarPoint2.png: {e}")
            self.aura_bar_point_texture_2 = None

        try:
            # Последняя точка (только для ауры 10)
            self.aura_bar_point_texture_3 = EasySprite.upscale_image(
                "Fight_Mechanic/Static/Interface/AuraBarPoint3.png", 2)
        except Exception as e:
            print(f"Ошибка при загрузке текстуры AuraBarPoint3.png: {e}")
            self.aura_bar_point_texture_3 = None

        # Если не удалось загрузить специальные текстуры, пробуем загрузить старую
        if not (self.aura_bar_point_texture_1 and self.aura_bar_point_texture_2):
            try:
                fallback_texture = EasySprite.upscale_image("AuraBarPoint.png", 2)
                self.aura_bar_point_texture_1 = fallback_texture
                self.aura_bar_point_texture_2 = fallback_texture
                print("Используется универсальная текстура AuraBarPoint.png")
            except Exception as e:
                print(f"Ошибка при загрузке универсальной текстуры AuraBarPoint.png: {e}")

        # Файлы текстур для кнопок действий
        texture_files = {
            'actionIcon_1': 'Fight_Mechanic/Static/Interface/actionIcon_1.png',
            'actionIcon_2': 'Fight_Mechanic/Static/Interface/actionIcon_2.png',
            'actionIcon_3': 'Fight_Mechanic/Static/Interface/actionIcon_3.png',
            'itemIcon': 'Fight_Mechanic/Static/Interface/itemIcon.png',
            'auroDopIcon': 'Fight_Mechanic/Static/Interface/auroDopIcon.png',
        }

        # Цвета для кнопок (если текстуры не загружены)
        texture_colors = {
            'actionIcon_1': arcade.color.RED,
            'actionIcon_2': arcade.color.BLUE,
            'actionIcon_3': arcade.color.GREEN,
            'itemIcon': arcade.color.PURPLE,
            'auroDopIcon': arcade.color.ORANGE,
        }

        # Загрузка текстур из файлов
        for name, filename in texture_files.items():
            try:
                upscaled_texture = EasySprite.upscale_image(filename, 4)
                self.textures[name] = upscaled_texture

                sprite = arcade.Sprite()
                sprite.texture = upscaled_texture

                # Масштабирование под размер кнопки
                scale_x = BUTTON_WIDTH / sprite.width
                scale_y = BUTTON_HEIGHT / sprite.height
                sprite.scale = min(scale_x, scale_y)

                self.button_sprites[name] = sprite

            except Exception as e:
                print(f"Ошибка при загрузке текстуры {filename}: {e}")
                self.textures[name] = None
                self.button_sprites[name] = None

        # Создание цветов для состояний кнопок
        for name, color in texture_colors.items():
            self.textures[name + '_color'] = color
            self.textures[name + '_color_active'] = (
                max(0, color[0] - 30),
                max(0, color[1] - 30),
                max(0, color[2] - 30)
            )

        # Загрузка текстур иконок для кнопок выбора
        selection_icon_files = {
            # Для 1 зоны
            'zone1_col1': 'Fight_Mechanic/Static/Interface/actionIcon_forText1_0.png',
            'zone1_col2_1': 'Fight_Mechanic/Static/Interface/actionIcon_forText1_1.png',
            'zone1_col2_2': 'Fight_Mechanic/Static/Interface/actionIcon_forText1_2.png',
            # Для 2 зоны
            'zone2_col1': 'Fight_Mechanic/Static/Interface/actionIcon_forText2_0.png',
            'zone2_col2_1': 'Fight_Mechanic/Static/Interface/actionIcon_forText2_1.png',
            'zone2_col2_2': 'Fight_Mechanic/Static/Interface/actionIcon_forText2_2.png',
            # Для 3 зоны
            'zone3_col1': 'Fight_Mechanic/Static/Interface/actionIcon_forText3_0.png',
            'zone3_col2_1': 'Fight_Mechanic/Static/Interface/actionIcon_forText3_1.png',
            'zone3_col2_2': 'Fight_Mechanic/Static/Interface/actionIcon_forText3_2.png',
        }

        for name, filename in selection_icon_files.items():
            try:
                upscaled_texture = EasySprite.upscale_image(filename, 4)
                self.selection_icon_textures[name] = upscaled_texture
            except Exception as e:
                print(f"Ошибка при загрузке текстуры {filename}: {e}")
                self.selection_icon_textures[name] = None

    """Создаёт спрайт кнопки с текстурой или цветом"""

    def create_button_sprite(self, x, y, texture_name, width, height, is_dropdown=False, is_first_button=False):
        normal_color = self.textures.get(texture_name + '_color', arcade.color.DARK_GRAY)
        active_color = self.textures.get(texture_name + '_color_active', arcade.color.GRAY)

        if is_first_button and texture_name in self.button_sprites and self.button_sprites[texture_name] is not None:
            sprite = arcade.Sprite()
            sprite.texture = self.button_sprites[texture_name].texture
            sprite.scale = self.button_sprites[texture_name].scale

            sprite.center_x = x
            sprite.center_y = y
            sprite.width = width
            sprite.height = height

            sprite.normal_texture = sprite.texture
            sprite.active_texture = None
            sprite.texture_name = texture_name
            sprite.normal_color = normal_color
            sprite.active_color = active_color
            sprite.is_hovered = False
            sprite.is_dropdown = is_dropdown

        elif texture_name in self.button_sprites and self.button_sprites[texture_name] is not None:
            sprite = arcade.Sprite()
            sprite.texture = self.button_sprites[texture_name].texture
            sprite.scale = self.button_sprites[texture_name].scale

            sprite.center_x = x
            sprite.center_y = y
            sprite.width = width
            sprite.height = height

            sprite.normal_texture = sprite.texture
            sprite.active_texture = None
            sprite.texture_name = texture_name
            sprite.normal_color = normal_color
            sprite.active_color = active_color
            sprite.is_hovered = False
            sprite.is_dropdown = is_dropdown

        else:
            sprite = arcade.SpriteSolidColor(width, height, normal_color)
            sprite.center_x = x
            sprite.center_y = y
            sprite.normal_texture = None
            sprite.active_texture = None
            sprite.texture_name = texture_name
            sprite.normal_color = normal_color
            sprite.active_color = active_color
            sprite.is_hovered = False
            sprite.is_dropdown = is_dropdown

        return sprite

    """Создаёт спрайт зоны с текстурой или цветом"""

    def create_zone_sprite(self, x, y, width, height, zone_index):
        if self.zone_texture:
            sprite = arcade.Sprite()
            sprite.texture = self.zone_texture
            sprite.center_x = x
            sprite.center_y = y

            scale_x = width / sprite.width
            scale_y = height / sprite.height
            sprite.scale = min(scale_x, scale_y)

            sprite.width = width
            sprite.height = height
        else:
            sprite = arcade.SpriteSolidColor(width, height, arcade.color.DARK_GRAY)
            sprite.center_x = x
            sprite.center_y = y

        sprite.sprite_type = "zone"
        sprite.zone_index = zone_index
        return sprite

    """Создаёт спрайт кнопки выбора целей"""

    def create_selection_button_sprite(self, x, y, width, height, text, has_icon=False, icon_texture=None):
        if self.selection_button_texture:
            sprite = arcade.Sprite()
            sprite.texture = self.selection_button_texture
            sprite.center_x = x
            sprite.center_y = y

            scale_x = width / sprite.width
            scale_y = height / sprite.height
            sprite.scale = min(scale_x, scale_y)

            sprite.width = width
            sprite.height = height
        else:
            sprite = arcade.SpriteSolidColor(width, height, arcade.color.DARK_GRAY)
            sprite.center_x = x
            sprite.center_y = y

        sprite.button_text = text
        sprite.has_icon = has_icon
        sprite.icon_texture = icon_texture
        return sprite

    """Создаёт спрайт иконки для кнопки выбора"""

    def create_selection_icon_sprite(self, x, y, texture_name):
        if texture_name in self.selection_icon_textures and self.selection_icon_textures[texture_name] is not None:
            sprite = arcade.Sprite()
            sprite.texture = self.selection_icon_textures[texture_name]
            sprite.center_x = x
            sprite.center_y = y

            # Масштабируем иконку
            target_width = 30
            target_height = 30
            scale_x = target_width / sprite.width
            scale_y = target_height / sprite.height
            sprite.scale = min(scale_x, scale_y)

            sprite.texture_name = texture_name
            return sprite
        return None

    """Создаёт все элементы интерфейса: зоны, иконки и кнопки"""

    def create_interface(self):
        zone_width = (self.main_panel_width - PANEL_MARGIN * 4) // 3 - 60
        zone_height = 80

        # Создание 3 зон
        for i in range(3):
            zone_x = (self.main_panel_x - self.main_panel_width / 2 + PANEL_MARGIN +
                      zone_width // 2 + i * (zone_width + PANEL_MARGIN) + 20 * i + 40)
            zone_y = self.main_panel_y + 60

            zone_sprite = self.create_zone_sprite(zone_x, zone_y, zone_width, zone_height, i)
            self.zones_list.append(zone_sprite)

            icon_x = zone_x - zone_width / 2 + 25
            icon_y = zone_y

            icon_sprite = arcade.SpriteSolidColor(20, 20, arcade.color.GRAY)
            icon_sprite.center_x = icon_x
            icon_sprite.center_y = icon_y
            icon_sprite.sprite_type = "icon"
            icon_sprite.zone_index = i
            self.icons_list.append(icon_sprite)

            # Создание 3 кнопок в каждой зоне
            for j in range(3):
                button_x = icon_x + 30 + j * (BUTTON_WIDTH + ELEMENT_MARGIN) + BUTTON_WIDTH / 2
                button_y = zone_y

                texture_name = None
                if j == 0:
                    if i == 0:
                        texture_name = 'actionIcon_1'
                    elif i == 1:
                        texture_name = 'actionIcon_2'
                    elif i == 2:
                        texture_name = 'actionIcon_3'
                elif j == 1:
                    texture_name = 'itemIcon'
                elif j == 2:
                    texture_name = 'auroDopIcon'

                is_first_button = (j == 0)

                button_sprite = self.create_button_sprite(
                    button_x,
                    button_y,
                    texture_name,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT,
                    is_first_button=is_first_button
                )

                button_sprite.button_type = texture_name
                button_sprite.zone_index = i
                button_sprite.button_index = j
                button_sprite.is_main_button = (j == 0)
                button_sprite.is_confirmed = False

                self.buttons_list.append(button_sprite)

    """Обновляет позицию индикатора выбранной кнопки"""

    def update_button_indicator(self):
        for button in self.buttons_list:
            if (button.zone_index == self.selected_button_zone and
                    button.button_index == self.selected_button_index):
                self.button_indicator = {
                    'x': button.center_x,
                    'y': button.center_y,
                    'width': button.width,
                    'height': button.height,
                    'zone_index': button.zone_index
                }
                break

    """Перемещает выбор зон (для режима выбора зоны предмета)"""

    def move_zone_selection(self, direction):
        if direction == 'left':
            if self.selected_button_zone > 0:
                self.selected_button_zone -= 1
        elif direction == 'right':
            if self.selected_button_zone < 2:
                self.selected_button_zone += 1
        elif direction == 'up':
            if self.selected_button_zone > 0:
                self.selected_button_zone -= 1
        elif direction == 'down':
            if self.selected_button_zone < 2:
                self.selected_button_zone += 1

        # Обновляем индикатор зоны (без привязки к кнопке)
        zone = None
        for z in self.zones_list:
            if z.zone_index == self.selected_button_zone:
                zone = z
                break

        if zone:
            self.button_indicator = {
                'x': zone.center_x,
                'y': zone.center_y,
                'width': zone.width,
                'height': zone.height,
                'zone_index': zone.zone_index
            }

        # Сохраняем выбранную зону как целевую
        self.target_zone_index = self.selected_button_zone

    """Перемещает выбор кнопок в обычном режиме"""

    def move_button_selection(self, direction):
        if self.ui_state != STATE_NORMAL:
            return

        total_buttons = 9
        current_flat_index = self.selected_button_zone * 3 + self.selected_button_index

        if direction == 'left':
            if self.selected_button_index > 0:
                self.selected_button_index -= 1
            elif self.selected_button_zone > 0:
                self.selected_button_zone -= 1
                self.selected_button_index = 2

        elif direction == 'right':
            if self.selected_button_index < 2:
                self.selected_button_index += 1
            elif self.selected_button_zone < 2:
                self.selected_button_zone += 1
                self.selected_button_index = 0

        elif direction == 'up':
            new_flat_index = (current_flat_index - 3) % total_buttons
            self.selected_button_zone = new_flat_index // 3
            self.selected_button_index = new_flat_index % 3

        elif direction == 'down':
            new_flat_index = (current_flat_index + 3) % total_buttons
            self.selected_button_zone = new_flat_index // 3
            self.selected_button_index = new_flat_index % 3

        self.update_button_indicator()

    """Подтверждает выбор кнопки в обычном режиме"""

    def confirm_button_selection(self):
        if self.ui_state != STATE_NORMAL:
            return

        selected_button = None
        for button in self.buttons_list:
            if (button.zone_index == self.selected_button_zone and
                    button.button_index == self.selected_button_index):
                selected_button = button
                break

        if not selected_button:
            return

        print(
            f"Выбрана кнопка: Зона {selected_button.zone_index + 1}, Кнопка {selected_button.button_index + 1} ({selected_button.button_type})")

        if selected_button.button_type == 'auroDopIcon':
            # Кнопка ауры - мгновенный выбор
            self.curr_choice = {"action_type": "mana", "action_data": {"count_mana": 1}}
            self.curr_hero = self.hero_type_list[selected_button.zone_index]
            self.selected_data[self.curr_hero] = self.curr_choice
            print(self.selected_data)

            self.immediate_auro_dop_selection(selected_button.zone_index)
            self.move_to_next_zone()
        else:
            # Остальные кнопки - переход в режим выбора
            self.start_selection_mode(selected_button.button_type, selected_button.zone_index)

    """Переходит к следующей незаполненной зоне"""

    def move_to_next_zone(self):
        for zone_idx in range(3):
            next_zone = (self.selected_button_zone + zone_idx + 1) % 3
            if next_zone not in self.selected_zones:
                self.selected_button_zone = next_zone
                self.selected_button_index = 0
                self.update_button_indicator()
                return

    """Создаёт окно выбора целей или предметов"""

    def create_selection_zone(self, selection_type, zone_index):
        if self.ui_state == STATE_ALL_SELECTED:
            return

        self.current_selection_type = selection_type
        self.active_zone_index = zone_index
        self.original_zone_index = zone_index  # Сохраняем оригинальную зону

        self.selection_buttons_list.clear()
        self.selection_icons_list.clear()
        self.item_subwindow = None

        # Настройки для разных типов выбора
        if selection_type == 'actionIcon_1':
            title = "Выбор цели для атаки"
            item_prefix = "Враг"
            column2_items = ["Персонаж 1", "Персонаж 2"]
            show_subwindow = False
            show_icons = True
        elif selection_type == 'actionIcon_2':
            title = "Выбор цели для защиты"
            item_prefix = "Союзник"
            column2_items = ["Персонаж 1", "Персонаж 2"]
            show_subwindow = False
            show_icons = True
        elif selection_type == 'actionIcon_3':
            title = "Выбор цели для лечения"
            item_prefix = "Пациент"
            column2_items = ["Персонаж 1", "Персонаж 2"]
            show_subwindow = False
            show_icons = True
        elif selection_type == 'itemIcon':
            title = None
            item_prefix = "Предмет"
            column2_items = ["Предмет 1", "Предмет 2", "Предмет 3"]
            show_subwindow = True
            show_icons = False

        selection_height = 140
        selection_y = 70

        self.selection_zone = {
            'x': SCREEN_WIDTH // 2,
            'y': selection_y,
            'width': SCREEN_WIDTH - 40,
            'height': selection_height,
            'color': arcade.color.BLACK,
            'title': title,
            'show_subwindow': show_subwindow,
            'show_icons': show_icons
        }

        if show_subwindow:
            self.item_subwindow = {
                'x': SCREEN_WIDTH - 260,
                'y': selection_y,
                'width': 460,
                'height': selection_height - 10,
                'texture': self.item_subwindow_texture,
                'title': "Описание",
                'description': "TBA"
            }

        self.selection_columns = []
        self.selection_items = []

        item_width = 125
        item_height = 35

        if selection_type in ['actionIcon_1', 'actionIcon_2', 'actionIcon_3']:
            column_count = 2
            column_spacing = 165
        else:
            column_count = 3
            column_spacing = 140

        for col in range(column_count):
            column_x = 90 + col * column_spacing
            column_items = []

            if selection_type in ['actionIcon_1', 'actionIcon_2', 'actionIcon_3']:
                if col == 0:
                    current_items_count = 3
                else:
                    current_items_count = 2
            else:
                current_items_count = 3

            for row in range(current_items_count):
                item_y = selection_y + 45 - row * (item_height + 12)

                if selection_type in ['actionIcon_1', 'actionIcon_2', 'actionIcon_3']:
                    if col == 0:
                        item_text = f"{item_prefix} {row + 1}"
                    else:
                        item_text = column2_items[row] if row < len(column2_items) else f"{item_prefix} {row + 4}"
                else:
                    item_num = col * 3 + row + 1
                    item_text = f"{item_prefix} {item_num}"

                # Определяем иконку для кнопки, если нужно
                icon_texture = None
                has_icon = False

                if show_icons and selection_type in ['actionIcon_1', 'actionIcon_2', 'actionIcon_3']:
                    has_icon = True
                    if self.active_zone_index == 0:  # Зона 1
                        if col == 0:
                            icon_texture = 'zone1_col1'
                        elif col == 1:
                            if row == 0:
                                icon_texture = 'zone1_col2_1'
                            elif row == 1:
                                icon_texture = 'zone1_col2_2'
                    elif self.active_zone_index == 1:  # Зона 2
                        if col == 0:
                            icon_texture = 'zone2_col1'
                        elif col == 1:
                            if row == 0:
                                icon_texture = 'zone2_col2_1'
                            elif row == 1:
                                icon_texture = 'zone2_col2_2'
                    elif self.active_zone_index == 2:  # Зона 3
                        if col == 0:
                            icon_texture = 'zone3_col1'
                        elif col == 1:
                            if row == 0:
                                icon_texture = 'zone3_col2_1'
                            elif row == 1:
                                icon_texture = 'zone3_col2_2'

                button_sprite = self.create_selection_button_sprite(
                    column_x,
                    item_y,
                    item_width,
                    item_height,
                    item_text,
                    has_icon=has_icon,
                    icon_texture=icon_texture
                )

                self.selection_buttons_list.append(button_sprite)

                # Создаем спрайт иконки, если есть
                if has_icon and icon_texture:
                    icon_sprite = self.create_selection_icon_sprite(
                        column_x - item_width / 2 + 15,
                        item_y,
                        icon_texture
                    )
                    if icon_sprite:
                        self.selection_icons_list.append(icon_sprite)

                item = {
                    'x': column_x,
                    'y': item_y,
                    'width': item_width,
                    'height': item_height,
                    'text': item_text,
                    'column': col,
                    'row': row,
                    'selected': False,
                    'item_num': row + 1 if col == 0 else row + 4,
                    'has_icon': has_icon,
                    'icon_texture': icon_texture
                }
                column_items.append(item)
                self.selection_items.append(item)

            self.selection_columns.append(column_items)

        if selection_type in ['actionIcon_1', 'actionIcon_2', 'actionIcon_3']:
            self.divider_x = 70 + 0.7 * column_spacing
            self.divider_visible = True
        else:
            self.divider_x = None
            self.divider_visible = False

        self.update_selection_indicator()

    """Обновляет индикатор выбора в окне выбора"""

    def update_selection_indicator(self):
        if not self.selection_items:
            return

        first_item = self.selection_columns[0][0]
        self.selection_indicator = {
            'x': first_item['x'],
            'y': first_item['y'],
            'width': first_item['width'],
            'height': first_item['height']
        }

        self.selected_column = 0
        self.selected_item_index = 0

    """Запускает режим выбора целей/предметов"""

    def start_selection_mode(self, selection_type, zone_index):
        if self.ui_state == STATE_ALL_SELECTED:
            return

        self.ui_state = STATE_SELECTION
        self.create_selection_zone(selection_type, zone_index)
        print(f"Режим выбора: {selection_type} (Зона {zone_index + 1})")

    """Сбрасывает текущий режим выбора"""

    def reset_selection(self):
        self.ui_state = STATE_NORMAL
        self.selection_zone = None
        self.selection_items = []
        self.selection_columns = []
        self.selection_indicator = None
        self.current_selection_type = None
        self.active_zone_index = None
        self.item_subwindow = None
        self.selection_buttons_list.clear()
        self.selection_icons_list.clear()
        self.selected_item_for_zone = None
        self.temp_selected_item = None
        self.temp_selected_item_index = None
        self.temp_selected_column = None
        self.original_zone_index = None
        self.target_zone_index = None
        print("Текущий выбор сброшен.")

    """Перемещает выбор в окне выбора"""

    def move_selection(self, direction):
        if not self.selection_items:
            return

        current_col = self.selected_column
        current_row = self.selected_item_index

        current_column_items = len(self.selection_columns[current_col])

        if direction == 'up':
            new_row = (current_row - 1) % current_column_items
            self.selected_item_index = new_row
        elif direction == 'down':
            new_row = (current_row + 1) % current_column_items
            self.selected_item_index = new_row
        elif direction == 'left':
            new_col = (current_col - 1) % len(self.selection_columns)
            if self.selected_item_index >= len(self.selection_columns[new_col]):
                self.selected_item_index = len(self.selection_columns[new_col]) - 1
            self.selected_column = new_col
        elif direction == 'right':
            new_col = (current_col + 1) % len(self.selection_columns)
            if self.selected_item_index >= len(self.selection_columns[new_col]):
                self.selected_item_index = len(self.selection_columns[new_col]) - 1
            self.selected_column = new_col

        selected_item = self.selection_columns[self.selected_column][self.selected_item_index]
        self.selection_indicator = {
            'x': selected_item['x'],
            'y': selected_item['y'],
            'width': selected_item['width'],
            'height': selected_item['height']
        }

    """Подтверждает выбор в окне выбора"""

    def confirm_selection(self):
        if not self.selection_items:
            return

        selected_item = self.selection_columns[self.selected_column][self.selected_item_index]

        # Если это выбор предмета
        if self.current_selection_type == 'itemIcon':
            # Сохраняем выбранный предмет и его параметры
            self.selected_item_for_zone = selected_item['text']
            self.temp_selected_item = selected_item
            self.temp_selected_item_index = self.selected_item_index
            self.temp_selected_column = self.selected_column

            # Обводим выбранный предмет оранжевым
            for item in self.selection_items:
                item['selected'] = False
            selected_item['selected'] = True

            # Переходим в режим выбора зоны
            self.ui_state = STATE_ZONE_SELECTION
            print(f"Выбран предмет: {selected_item['text']}. Теперь выберите зону для применения.")

            # Инициализируем целевую зону (начинаем с зоны, из которой был сделан выбор)
            self.target_zone_index = self.original_zone_index
            self.selected_button_zone = self.original_zone_index
            self.move_zone_selection('')  # Инициализируем индикатор зоны

        else:
            # Для других типов выбора (атака, защита, лечение) - стандартная логика
            for item in self.selection_items:
                item['selected'] = False

            selected_item['selected'] = True

            # Очищаем предыдущий выбор в этой зоне, если он был
            if self.active_zone_index in self.confirmed_selections:
                print(f"Перезапись выбора в зоне {self.active_zone_index + 1}")
                # Сбрасываем подтверждённый статус для всех кнопок в этой зоне
                for button in self.buttons_list:
                    if button.zone_index == self.active_zone_index:
                        button.is_confirmed = False

            self.confirmed_selections[self.active_zone_index] = {
                'type': self.current_selection_type,
                'item': selected_item['text']
            }

            if self.active_zone_index not in self.selected_zones:
                self.selected_zones.append(self.active_zone_index)
                self.selected_zones.sort()

            # Устанавливаем подтверждённый статус только для выбранной кнопки в зоне
            for button in self.buttons_list:
                if (button.zone_index == self.active_zone_index and
                        button.button_type == self.current_selection_type):
                    button.is_confirmed = True
                    self.selected_buttons[self.active_zone_index] = {
                        'zone_index': self.active_zone_index,
                        'button_index': button.button_index,
                        'button_type': button.button_type
                    }
                    break

            print(
                f"Выбрано для зоны {self.active_zone_index + 1}: {selected_item['text']} (тип: {self.current_selection_type})")

            self.curr_choice = {"action_type": "", "action_data": {}}
            self.curr_hero = self.hero_type_list[self.active_zone_index]
            possible_support_heros = [0, 1, 2]
            possible_support_heros.remove(self.active_zone_index)

            if self.curr_hero == "attack":
                if selected_item['text'][:-2] == 'Враг':
                    self.curr_choice["action_type"] = "main"
                    self.curr_choice["action_data"]["attack_enemies"] = int(selected_item['text'][-1]) - 1
                elif selected_item['text'][:-2] == 'Персонаж':
                    self.curr_choice["action_type"] = "support"
                    support_hero_index = int(selected_item['text'][-1]) - 1
                    support_hero = self.hero_type_list[possible_support_heros[support_hero_index]]
                    self.curr_choice["action_data"]["support_hero"] = support_hero
                else:
                    self.curr_choice["other"] = self.current_selection_type

            elif self.curr_hero == "defense":
                if selected_item['text'][:-2] == 'Союзник':
                    self.curr_choice["action_type"] = "main"
                elif selected_item['text'][:-2] == 'Персонаж':
                    support_hero_index = int(selected_item['text'][-1]) - 1
                    support_hero = self.hero_type_list[possible_support_heros[support_hero_index]]
                    self.curr_choice["action_data"]["support_hero"] = support_hero
                else:
                    self.curr_choice["other"] = self.current_selection_type

            else:
                if selected_item['text'][:-2] == 'Пациент':
                    self.curr_choice["action_type"] = "main"
                    self.curr_choice["action_data"]["heal_hero"] = self.hero_type_list[
                        int(selected_item['text'][-1]) - 1
                    ]
                elif selected_item['text'][:-2] == 'Персонаж':
                    support_hero_index = int(selected_item['text'][-1]) - 1
                    support_hero = self.hero_type_list[possible_support_heros[support_hero_index]]
                    self.curr_choice["action_data"]["support_hero"] = support_hero
                else:
                    self.curr_choice["other"] = self.current_selection_type

            self.selected_data[self.curr_hero] = self.curr_choice
            print(self.selected_data)

            if len(self.selected_zones) == 3:
                print("Все зоны выбраны! Переход в режим ожидания...")
                self.ui_state = STATE_ALL_SELECTED
                self.selected_button_zone = 0
                self.selected_button_index = 0
                self.update_button_indicator()
            else:
                self.reset_selection()
                self.move_to_next_zone()

    """Подтверждает выбор зоны для предмета"""

    def confirm_zone_selection_for_item(self):
        if not self.selected_item_for_zone:
            return

        # ВАЖНО: предмет подтверждается для зоны, из которой был сделан выбор (original_zone_index),
        # но применяется к целевой зоне (target_zone_index)
        zone_index = self.original_zone_index  # Зона, из которой делался выбор

        # Очищаем предыдущий выбор в этой зоне, если он был
        if zone_index in self.confirmed_selections:
            print(f"Перезапись выбора в зоне {zone_index + 1}")
            # Сбрасываем подтверждённый статус для всех кнопок в этой зоне
            for button in self.buttons_list:
                if button.zone_index == zone_index:
                    button.is_confirmed = False

        # Сохраняем информацию о выборе
        self.confirmed_selections[zone_index] = {
            'type': 'itemIcon',
            'item': self.selected_item_for_zone,
            'applied_to_zone': self.target_zone_index  # Сохраняем, к какой зоне применен
        }

        if zone_index not in self.selected_zones:
            self.selected_zones.append(zone_index)
            self.selected_zones.sort()

        # Устанавливаем подтверждённый статус только для кнопки предмета в зоне
        for button in self.buttons_list:
            if (button.zone_index == zone_index and
                    button.button_type == 'itemIcon'):
                button.is_confirmed = True
                self.selected_buttons[zone_index] = {
                    'zone_index': zone_index,
                    'button_index': button.button_index,
                    'button_type': button.button_type,
                    'applied_to_zone': self.target_zone_index
                }
                break

        print(
            f"Предмет '{self.selected_item_for_zone}' выбран в зоне {zone_index + 1} и применён к зоне {self.target_zone_index + 1}")

        self.curr_choice = {"action_type": "", "action_data": {}}
        self.curr_hero = self.hero_type_list[zone_index]

        item_index = int(self.selected_item_for_zone[-1]) - 1
        item_hero = self.hero_type_list[self.target_zone_index]

        self.curr_choice["action_type"] = "item"
        self.curr_choice["action_data"]["item"] = item_index
        self.curr_choice["action_data"]["item_hero"] = item_hero

        self.selected_data[self.curr_hero] = self.curr_choice
        print(self.selected_data)


        # Сбрасываем временные данные
        self.selected_item_for_zone = None
        self.temp_selected_item = None
        self.temp_selected_item_index = None
        self.temp_selected_column = None
        self.original_zone_index = None
        self.target_zone_index = None

        # Проверяем, все ли зоны выбраны
        if len(self.selected_zones) == 3:
            print("Все зоны выбраны! Переход в режим ожидания...")
            self.ui_state = STATE_ALL_SELECTED
            self.selected_button_zone = 0
            self.selected_button_index = 0
            self.update_button_indicator()
        else:
            # Возвращаемся в нормальный режим
            self.ui_state = STATE_NORMAL
            self.selection_zone = None
            self.selection_items = []
            self.selection_columns = []
            self.selection_indicator = None
            self.current_selection_type = None
            self.active_zone_index = None
            self.item_subwindow = None
            self.selection_buttons_list.clear()
            self.selection_icons_list.clear()

            # Переходим к следующей зоне
            self.move_to_next_zone()

    """Мгновенный выбор для кнопки ауры (без окна выбора)"""

    def immediate_auro_dop_selection(self, zone_index):
        if self.ui_state == STATE_ALL_SELECTED:
            return

        self.active_zone_index = zone_index
        self.current_selection_type = 'auroDopIcon'

        selected_item_text = "Кнопка 1"

        # Очищаем предыдущий выбор в этой зоне, если он был
        if self.active_zone_index in self.confirmed_selections:
            print(f"Перезапись выбора в зоне {self.active_zone_index + 1}")
            # Сбрасываем подтверждённый статус для всех кнопок в этой зоне
            for button in self.buttons_list:
                if button.zone_index == self.active_zone_index:
                    button.is_confirmed = False

        self.confirmed_selections[self.active_zone_index] = {
            'type': self.current_selection_type,
            'item': selected_item_text
        }

        if self.active_zone_index not in self.selected_zones:
            self.selected_zones.append(self.active_zone_index)
            self.selected_zones.sort()

        # Устанавливаем подтверждённый статус только для выбранной кнопки в зоне
        for button in self.buttons_list:
            if (button.zone_index == self.active_zone_index and
                    button.button_type == 'auroDopIcon'):
                button.is_confirmed = True
                self.selected_buttons[self.active_zone_index] = {
                    'zone_index': self.active_zone_index,
                    'button_index': button.button_index,
                    'button_type': button.button_type
                }
                break

        if self.ui_state == STATE_SELECTION:
            self.reset_selection()

        if len(self.selected_zones) == 3:
            print("Все зоны выбраны! Переход в режим ожидания...")
            self.ui_state = STATE_ALL_SELECTED
            self.selected_button_zone = 0
            self.selected_button_index = 0
            self.update_button_indicator()

    """Обновляет текстуру кнопки при наведении"""

    def update_button_texture(self, button, is_hovered):
        if is_hovered != button.is_hovered:
            button.is_hovered = is_hovered

    """Добавляет единицу ауры"""

    def add_aura(self):
        self.aura += 1
        if self.aura > self.max_aura:
            self.aura = 10
        print(f"Аура: {self.aura}/{self.max_aura}")
        # Обновляем спрайты точек ауры при изменении уровня маны
        self.update_aura_point_sprites()

    """Отрисовывает счётчик ауры в панели"""

    def draw_aura_counter_in_panel(self, panel_x, panel_y):
        if self.aura_bar_texture:
            # Подвинули текстуру шкалы Ауры влево и вверх
            aura_start_x = panel_x - self.small_panel_width / 2 + 10
            aura_y = panel_y + 10
            start_x = aura_start_x + 5

            segment_width = 8
            segment_height = 25
            segment_spacing = 3

            total_bar_width = (self.max_aura * (segment_width + segment_spacing) - segment_spacing) * 2
            bar_left = start_x - segment_width
            bar_bottom = aura_y - segment_height
            bar_top = aura_y + segment_height

            # 1. Рисуем спрайты точек ауры в ОДНОЙ линии
            # Вычисляем общую длину для всех спрайтов
            point_count = AURA_POINT_COUNTS.get(self.aura, 0)
            point_start_x = bar_left + 6
            point_spacing = 1

            # Если это максимальный уровень ауры, создаём увеличенный пробел между предпоследней и последней точкой
            extra_spacing_for_gap = 0
            if self.aura == 10:
                # Для 10 уровня создаём пробел, пропуская одну точку
                point_count -= 1  # Уменьшаем количество точек, так как одну пропускаем
                # Увеличиваем отступ перед последней точкой
                extra_spacing_for_gap = 2  # Дополнительный пробел

            # Вычисляем центр шкалы по вертикали
            bar_center_y = bar_bottom + (bar_top - bar_bottom) / 2
            point_y = bar_center_y - 10  # Центрируем спрайты по вертикали

            # Устанавливаем позиции для спрайтов
            points_placed = 0
            for i, sprite in enumerate(self.aura_bar_point_sprites):
                if points_placed >= point_count:
                    break

                # Вычисляем позицию по X
                point_x = point_start_x + (points_placed * point_spacing)

                # Если это последняя точка при максимальном уровне ауры, добавляем дополнительный пробел
                if self.aura == 10 and points_placed == point_count - 1:
                    point_x += extra_spacing_for_gap

                sprite.center_x = point_x
                sprite.center_y = point_y
                points_placed += 1

            # Отрисовываем спрайты точек ауры
            self.aura_bar_point_sprites.draw()

            # 2. Затем рисуем саму шкалу ауры ПОВЕРХ всех спрайтов
            bar_rect = arcade.LRBT(
                left=bar_left,
                right=bar_left + total_bar_width,
                bottom=bar_bottom,
                top=bar_top
            )

            arcade.draw_texture_rect(
                self.aura_bar_texture,
                bar_rect
            )

            # Добавляем счётчик ауры справа от панели - ПРОСТО ЦИФРУ БЕЗ ФОНА
            counter_x = panel_x + self.small_panel_width / 2 + 60
            counter_y = panel_y

            # Текст счётчика (только текущее значение, без максимального)
            text = arcade.Text(
                f"{self.aura}",
                counter_x,
                counter_y,
                arcade.color.LIGHT_GRAY,
                22,
                anchor_x="center",
                anchor_y="center",
                bold=True,
                font_name=self.font_name  # Применяем шрифт к счётчику
            )
            text.draw()

            return

        # Если текстура НЕ загружена, рисуем обычный интерфейс
        aura_start_x = panel_x - self.small_panel_width / 2 + 25
        aura_y = panel_y

        arcade.draw_text(
            "AP",
            aura_start_x - 10,
            aura_y,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        segment_width = 8
        segment_height = 25
        segment_spacing = 3

        start_x = aura_start_x + 20

        total_bar_width = self.max_aura * (segment_width + segment_spacing) - segment_spacing
        bar_left = start_x - segment_width / 2
        bar_bottom = aura_y - segment_height / 2
        bar_rect = arcade.LRBT(
            left=bar_left,
            right=bar_left + total_bar_width,
            bottom=bar_bottom,
            top=bar_bottom + segment_height
        )

        arcade.draw_rect_filled(bar_rect, arcade.color.DARK_SLATE_GRAY)
        arcade.draw_rect_outline(bar_rect, arcade.color.LIGHT_GRAY, 1)

        for i in range(self.max_aura):
            segment_x = start_x + i * (segment_width + segment_spacing)

            if i < self.aura:
                segment_color = arcade.color.AQUA  # Заполненный сегмент
            else:
                segment_color = arcade.color.DARK_GRAY  # Пустой сегмент

            segment_rect = arcade.LRBT(
                left=segment_x - segment_width / 2,
                right=segment_x + segment_width / 2,
                bottom=aura_y - segment_height / 2,
                top=aura_y + segment_height / 2
            )
            arcade.draw_rect_filled(segment_rect, segment_color)
            arcade.draw_rect_outline(segment_rect, arcade.color.LIGHT_GRAY, 1)

        # Просто цифра без фона
        number_x = start_x + self.max_aura * (segment_width + segment_spacing) + 25
        arcade.draw_text(
            f"{self.aura}",
            number_x - 5,
            aura_y,
            arcade.color.LIGHT_GRAY,
            24,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

    """Отрисовывает минимизированный счётчик ауры"""

    def draw_aura_counter_minimized(self):
        panel_x = 90
        panel_y = 40

        if not self.aura_bar_texture:
            small_panel_rect = arcade.LRBT(
                left=panel_x - self.small_panel_width / 2,
                right=panel_x + self.small_panel_width / 2,
                bottom=panel_y - self.small_panel_height / 2,
                top=panel_y + self.small_panel_height / 2
            )
            arcade.draw_rect_filled(small_panel_rect, self.small_panel_color)
            arcade.draw_rect_outline(small_panel_rect, arcade.color.LIGHT_GRAY, 2)

        self.draw_aura_counter_in_panel(panel_x, panel_y)

    """Отрисовывает описание предметов"""

    def draw_item_subwindow(self):
        if not self.item_subwindow:
            return

        subwindow_rect = arcade.LRBT(
            left=self.item_subwindow['x'] - self.item_subwindow['width'] / 2,
            right=self.item_subwindow['x'] + self.item_subwindow['width'] / 2,
            bottom=self.item_subwindow['y'] - self.item_subwindow['height'] / 2,
            top=self.item_subwindow['y'] + self.item_subwindow['height'] / 2
        )

        if self.item_subwindow['texture']:
            arcade.draw_texture_rect(
                self.item_subwindow['texture'],
                subwindow_rect
            )
        else:
            arcade.draw_rect_filled(subwindow_rect, arcade.color.DARK_GRAY)

        arcade.draw_rect_outline(subwindow_rect, arcade.color.LIGHT_GRAY, 2)

        # Используем Text для заголовка
        title_text = arcade.Text(
            self.item_subwindow['title'],
            self.item_subwindow['x'],
            self.item_subwindow['y'] + self.item_subwindow['height'] // 2 - 15,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
            anchor_y="center",
            bold=True,
            font_name=self.font_name  # Применяем шрифт к заголовку
        )
        title_text.draw()

        text_x = self.item_subwindow['x'] - self.item_subwindow['width'] / 2 + 10
        text_y = self.item_subwindow['y']
        text_width = self.item_subwindow['width'] - 20

        # Используем Text для описания
        description_text = arcade.Text(
            self.item_subwindow['description'],
            text_x,
            text_y,
            arcade.color.WHITE,
            12,
            anchor_x="left",
            anchor_y="center",
            width=text_width,
            align="center",
            font_name=self.font_name  # Применяем шрифт к описанию
        )
        description_text.draw()

    """Отрисовывает окно выбора целей/предметов"""

    def draw_selection_zone(self):
        if not self.selection_zone:
            return

        zone_rect = arcade.LRBT(
            left=self.selection_zone['x'] - self.selection_zone['width'] / 2,
            right=self.selection_zone['x'] + self.selection_zone['width'] / 2,
            bottom=self.selection_zone['y'] - self.selection_zone['height'] / 2,
            top=self.selection_zone['y'] + self.selection_zone['height'] / 2
        )
        arcade.draw_rect_filled(zone_rect, self.selection_zone['color'])
        arcade.draw_rect_outline(zone_rect, arcade.color.LIGHT_GRAY, 2)

        if self.selection_zone['title']:
            # Используем Text для заголовка окна выбора
            title_text = arcade.Text(
                self.selection_zone['title'],
                self.selection_zone['x'],
                self.selection_zone['y'] + self.selection_zone['height'] // 2 - 15,
                arcade.color.LIGHT_GRAY,
                16,
                anchor_x="center",
                anchor_y="center",
                bold=True,
                font_name=self.font_name  # Применяем шрифт к заголовку окна
            )
            title_text.draw()

        if self.divider_visible and self.divider_x and self.current_selection_type in ['actionIcon_1', 'actionIcon_2',
                                                                                       'actionIcon_3']:
            divider_top = self.selection_zone['y'] + 69
            divider_bottom = self.selection_zone['y'] - 69

            arcade.draw_line(
                self.divider_x, divider_top,
                self.divider_x, divider_bottom,
                arcade.color.GRAY, 2
            )

        self.selection_buttons_list.draw()
        self.selection_icons_list.draw()

        for item in self.selection_items:
            # Только для режима выбора предметов (STATE_SELECTION) и если предмет не выбран, рисуем белую обводку
            if self.ui_state == STATE_SELECTION and not item['selected']:
                highlight_rect = arcade.LRBT(
                    left=item['x'] - item['width'] / 2 - 1,
                    right=item['x'] + item['width'] / 2 + 1,
                    bottom=item['y'] - item['height'] / 2 - 1,
                    top=item['y'] + item['height'] / 2 + 1
                )
                arcade.draw_rect_outline(highlight_rect, arcade.color.WHITE, 1)

            # Используем Text для текста кнопок выбора - подвинули текст вправо, если есть иконка
            text_x = item['x']
            if item['has_icon']:
                text_x += 10  # Сдвигаем текст вправо, если есть иконка

            item_text = arcade.Text(
                item['text'],
                text_x,
                item['y'],
                arcade.color.WHITE,
                12,
                anchor_x="center",
                anchor_y="center",
                font_name=self.font_name
            )
            item_text.draw()

            if item['selected']:
                # Для предметов - оранжевая обводка, для остального - зелёная
                if self.current_selection_type == 'itemIcon':
                    selected_color = arcade.color.ORANGE
                else:
                    selected_color = arcade.color.DARK_GREEN

                selected_rect = arcade.LRBT(
                    left=item['x'] - item['width'] / 2 - 3,
                    right=item['x'] + item['width'] / 2 + 3,
                    bottom=item['y'] - item['height'] / 2 - 3,
                    top=item['y'] + item['height'] / 2 + 3
                )
                arcade.draw_rect_outline(selected_rect, selected_color, 3)

        if self.selection_indicator and self.ui_state == STATE_SELECTION:
            indicator_rect = arcade.LRBT(
                left=self.selection_indicator['x'] - self.selection_indicator['width'] / 2 - 2,
                right=self.selection_indicator['x'] + self.selection_indicator['width'] / 2 + 2,
                bottom=self.selection_indicator['y'] - self.selection_indicator['height'] / 2 - 2,
                top=self.selection_indicator['y'] + self.selection_indicator['height'] / 2 + 2
            )
            arcade.draw_rect_outline(indicator_rect, arcade.color.RED, 3)

        if self.selection_zone.get('show_subwindow', False):
            self.draw_item_subwindow()

    def draw(self):
        # Режим "все зоны выбраны"
        if self.ui_state == STATE_ALL_SELECTED:
            self.draw_aura_counter_minimized()

            all_zones_text = arcade.Text(
                "Все зоны выбраны",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 50,
                arcade.color.WHITE,
                24,
                anchor_x="center",
                anchor_y="center",
                bold=True,
                font_name=self.font_name
            )
            all_zones_text.draw()

            reset_text = arcade.Text(
                "Нажмите R для сброса",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.WHITE,
                18,
                anchor_x="center",
                anchor_y="center",
                font_name=self.font_name
            )
            reset_text.draw()
            return

        # Основная панель интерфейса
        main_panel_rect = arcade.LRBT(
            left=self.main_panel_x - self.main_panel_width / 2,
            right=self.main_panel_x + self.main_panel_width / 2,
            bottom=self.main_panel_y - self.main_panel_height / 2,
            top=self.main_panel_y + self.main_panel_height / 2
        )
        arcade.draw_rect_filled(main_panel_rect, self.panel_color)
        arcade.draw_rect_outline(main_panel_rect, arcade.color.LIGHT_GRAY, 2)

        # Верхняя маленькая панель (для ауры) - если нет текстуры
        if not self.aura_bar_texture:
            small_panel_rect = arcade.LRBT(
                left=self.main_panel_x - self.main_panel_width / 2,
                right=self.main_panel_x - self.main_panel_width / 2 + self.small_panel_width,
                bottom=self.main_panel_y + self.main_panel_height / 2,
                top=self.main_panel_y + self.main_panel_height / 2 + self.small_panel_height
            )
            arcade.draw_rect_filled(small_panel_rect, self.small_panel_color)
            arcade.draw_rect_outline(small_panel_rect, arcade.color.LIGHT_GRAY, 2)

            connection_rect = arcade.LRBT(
                left=self.main_panel_x - self.main_panel_width / 2,
                right=self.main_panel_x - self.main_panel_width / 2 + self.small_panel_width,
                bottom=self.main_panel_y + self.main_panel_height / 2,
                top=self.main_panel_y + self.main_panel_height / 2 + 2
            )
            arcade.draw_rect_filled(connection_rect, arcade.color.GRAY)

        self.zones_list.draw()

        for zone in self.zones_list:
            zone_rect = arcade.LRBT(
                left=zone.center_x - zone.width / 2,
                right=zone.center_x + zone.width / 2,
                bottom=zone.center_y - zone.height / 2,
                top=zone.center_y + zone.height / 2
            )

            # Определяем цвета для подтверждённых зон
            zone_colors = {
                0: (143, 43, 43),  # Зона 1: тёмно-красный
                1: (82, 173, 192),  # Зона 2: бирюзовый
                2: (64, 160, 121),  # Зона 3: зелёный
            }

            if zone.zone_index in self.selected_zones:
                # Используем индивидуальный цвет для подтверждённой зоны
                zone_color = zone_colors.get(zone.zone_index, arcade.color.RED)
                arcade.draw_rect_outline(zone_rect, zone_color, 3)  # Выбранная зона
            elif self.ui_state == STATE_ZONE_SELECTION and zone.zone_index == self.selected_button_zone:
                # В режиме выбора зоны для предмета - оранжевая обводка
                arcade.draw_rect_outline(zone_rect, arcade.color.ORANGE, 3)  # Активная зона для предмета
            elif self.button_indicator and zone.zone_index == self.button_indicator[
                'zone_index'] and self.ui_state == STATE_NORMAL:
                arcade.draw_rect_outline(zone_rect, arcade.color.YELLOW, 3)  # Активная зона в обычном режиме
            else:
                arcade.draw_rect_outline(zone_rect, arcade.color.LIGHT_GRAY, 1)  # Обычная зона

        self.icons_list.draw()

        for i, icon in enumerate(self.icons_list):
            zone_number_text = arcade.Text(
                str(i + 1),  # Номер зоны
                icon.center_x,
                icon.center_y,
                arcade.color.WHITE,
                10,
                anchor_x="center",
                anchor_y="center",
                bold=True,
                font_name=self.font_name  # Применяем шрифт к номерам зон
            )
            zone_number_text.draw()

        self.buttons_list.draw()

        for button in self.buttons_list:
            button_rect = arcade.LRBT(
                left=button.center_x - button.width / 2,
                right=button.center_x + button.width / 2,
                bottom=button.center_y - button.height / 2,
                top=button.center_y + button.height / 2
            )

            if button.is_confirmed:
                # Используем те же цвета, что и для зон
                zone_colors = {
                    0: (143, 43, 43),  # Зона 1
                    1: (82, 173, 192),  # Зона 2
                    2: (64, 160, 121),  # Зона 3
                }
                zone_color = zone_colors.get(button.zone_index, arcade.color.RED)
                arcade.draw_rect_outline(button_rect, zone_color, 3)

        # Индикатор зоны в режиме выбора зоны для предмета
        if self.ui_state == STATE_ZONE_SELECTION and self.button_indicator:
            indicator_rect = arcade.LRBT(
                left=self.button_indicator['x'] - self.button_indicator['width'] / 2 - 2,
                right=self.button_indicator['x'] + self.button_indicator['width'] / 2 + 2,
                bottom=self.button_indicator['y'] - self.button_indicator['height'] / 2 - 2,
                top=self.button_indicator['y'] + self.button_indicator['height'] / 2 + 2
            )
            arcade.draw_rect_outline(indicator_rect, arcade.color.ORANGE, 3)

        # Индикатор кнопки только в обычном режиме
        if self.button_indicator and self.ui_state == STATE_NORMAL:
            indicator_rect = arcade.LRBT(
                left=self.button_indicator['x'] - self.button_indicator['width'] / 2 - 2,
                right=self.button_indicator['x'] + self.button_indicator['width'] / 2 + 2,
                bottom=self.button_indicator['y'] - self.button_indicator['height'] / 2 - 2,
                top=self.button_indicator['y'] + self.button_indicator['height'] / 2 + 2
            )
            arcade.draw_rect_outline(indicator_rect, arcade.color.YELLOW, 3)

        if self.ui_state == STATE_SELECTION or (self.ui_state == STATE_ZONE_SELECTION and self.selection_zone):
            self.draw_selection_zone()

        # Отрисовка счётчика ауры
        if not self.aura_bar_texture:
            self.draw_aura_counter_in_panel(self.small_panel_x, self.small_panel_y)
        else:
            self.draw_aura_counter_in_panel(self.small_panel_x, self.small_panel_y)

        # Отрисовка подтверждённых выборов
        if self.confirmed_selections:
            selection_text_y = self.main_panel_y + self.main_panel_height / 2 + 70

            confirmed_text = arcade.Text(
                "Подтверждённые выборы:",
                self.main_panel_x,
                selection_text_y,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center",
                anchor_y="center",
                bold=True,
                font_name=self.font_name
            )
            confirmed_text.draw()

            for i, (zone_idx, selection) in enumerate(self.confirmed_selections.items()):
                zone_text = f"Зона {zone_idx + 1}: {selection['item']}"
                if selection['type'] == 'itemIcon' and 'applied_to_zone' in selection:
                    applied_to = selection['applied_to_zone']
                    zone_text += f" (→ зона {applied_to + 1})"

                selection_text = arcade.Text(
                    zone_text,
                    self.main_panel_x,
                    selection_text_y - 25 * (i + 1),
                    arcade.color.LIGHT_GRAY,
                    12,
                    anchor_x="center",
                    anchor_y="center",
                    font_name=self.font_name
                )
                selection_text.draw()

        # Отрисовка инструкции в режиме выбора зоны для предмета
        if self.ui_state == STATE_ZONE_SELECTION and self.selected_item_for_zone:
            instruction_y = self.main_panel_y - self.main_panel_height / 2 - 30

            # Информация о выбранном предмете и текущей выбранной зоне
            if self.original_zone_index is not None and self.target_zone_index is not None:
                target_zone_text = f"Предмет будет применён к зоне {self.target_zone_index + 1}"
            else:
                target_zone_text = "Выберите зону для применения предмета"

            item_text = arcade.Text(
                f"Выбран предмет: {self.selected_item_for_zone}",
                SCREEN_WIDTH // 2,
                instruction_y,
                arcade.color.YELLOW,
                16,
                anchor_x="center",
                anchor_y="center",
                bold=True,
                font_name=self.font_name
            )
            item_text.draw()

            confirm_text = arcade.Text(
                f"Выбор подтвердится для зоны {self.original_zone_index + 1}",
                SCREEN_WIDTH // 2,
                instruction_y - 25,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center",
                anchor_y="center",
                font_name=self.font_name
            )
            confirm_text.draw()

            target_text = arcade.Text(
                target_zone_text,
                SCREEN_WIDTH // 2,
                instruction_y - 50,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center",
                anchor_y="center",
                font_name=self.font_name
            )
            target_text.draw()

            controls_text = arcade.Text(
                "Нажмите ENTER для подтверждения, BACKSPACE для возврата к выбору предмета",
                SCREEN_WIDTH // 2,
                instruction_y - 75,
                arcade.color.LIGHT_GRAY,
                12,
                anchor_x="center",
                anchor_y="center",
                font_name=self.font_name
            )
            controls_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.M:
            self.add_aura()

        elif key == arcade.key.R:
            if self.ui_state == STATE_ALL_SELECTED:
                self.ui_state = STATE_NORMAL
                self.confirmed_selections = {}
                self.selected_zones = []
                self.selected_buttons = {}
                for button in self.buttons_list:
                    button.is_confirmed = False
                self.selected_button_zone = 0
                self.selected_button_index = 0
                self.update_button_indicator()

                self.fb.phase_manager.data_handler(self.selected_data)
                print("Все выборы сброшены. Возврат в нормальный режим.")

        elif self.ui_state == STATE_NORMAL:
            if key == arcade.key.LEFT:
                self.move_button_selection('left')
            elif key == arcade.key.RIGHT:
                self.move_button_selection('right')
            elif key == arcade.key.UP:
                self.move_button_selection('up')
            elif key == arcade.key.DOWN:
                self.move_button_selection('down')
            elif key == arcade.key.ENTER or key == arcade.key.RETURN:
                self.confirm_button_selection()
            elif key == arcade.key.C:
                if self.selected_zones:
                    self.confirmed_selections = {}
                    self.selected_zones = []
                    self.selected_buttons = {}
                    for button in self.buttons_list:
                        button.is_confirmed = False
                    self.selected_button_zone = 0
                    self.selected_button_index = 0
                    self.update_button_indicator()
                    print("Все выборы зон сброшены")

        elif self.ui_state == STATE_SELECTION:
            if key == arcade.key.LEFT:
                self.move_selection('left')
            elif key == arcade.key.RIGHT:
                self.move_selection('right')
            elif key == arcade.key.UP:
                self.move_selection('up')
            elif key == arcade.key.DOWN:
                self.move_selection('down')
            elif key == arcade.key.ENTER or key == arcade.key.RETURN:
                self.confirm_selection()
            elif key == arcade.key.BACKSPACE:
                self.reset_selection()

        elif self.ui_state == STATE_ZONE_SELECTION:
            if key == arcade.key.LEFT:
                self.move_zone_selection('left')
            elif key == arcade.key.RIGHT:
                self.move_zone_selection('right')
            elif key == arcade.key.UP:
                self.move_zone_selection('up')
            elif key == arcade.key.DOWN:
                self.move_zone_selection('down')
            elif key == arcade.key.ENTER or key == arcade.key.RETURN:
                self.confirm_zone_selection_for_item()
            elif key == arcade.key.BACKSPACE:
                # Возвращаемся к выбору предмета, очищаем оранжевую обводку
                self.ui_state = STATE_SELECTION
                if self.temp_selected_item is not None:
                    # Снимаем оранжевую обводку с предмета
                    for item in self.selection_items:
                        item['selected'] = False

                    self.selected_column = self.temp_selected_column
                    self.selected_item_index = self.temp_selected_item_index
                    self.selection_indicator = {
                        'x': self.temp_selected_item['x'],
                        'y': self.temp_selected_item['y'],
                        'width': self.temp_selected_item['width'],
                        'height': self.temp_selected_item['height']
                    }
                print("Возврат к выбору предмета")
