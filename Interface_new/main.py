""" Name: Максим | Date: 24.01.2026 | WhatYouDo: Обновил интерфейс: добавил текстуру шкале ауры и исправил баг мульти-выбора """
from PIL import Image
import arcade
import io

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

"""Класс Юры"""


class EasySprite:
    @staticmethod
    def upscale_image(filename, scale):
        img = Image.open(filename)
        scale_factor = scale
        new_size = (img.width * scale_factor, img.height * scale_factor)
        new_img = img.resize(new_size, Image.NEAREST)
        img_bytes = io.BytesIO()
        new_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        texture = arcade.load_texture(img_bytes)
        return texture

    @staticmethod
    def upscale_texture(img, scale):
        scale_factor = scale
        new_size = (img.width * scale_factor, img.height * scale_factor)
        new_img = img.resize(new_size, Image.NEAREST)
        img_bytes = io.BytesIO()
        new_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        texture = arcade.load_texture(img_bytes)
        return texture


class InterfaceView(arcade.View):
    """Основной класс интерфейса"""

    def __init__(self):
        super().__init__()

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
        self.aura = 0  # Текущее значение ауры
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
        self.load_textures()

        # Подокно для предметов
        self.item_subwindow = None

        # Создание интерфейса
        self.create_interface()
        self.update_button_indicator()

    def load_textures(self):
        """Загружает все текстуры для интерфейса"""
        try:
            self.zone_texture = EasySprite.upscale_image("Field.png", 2)
        except Exception as e:
            print(f"Ошибка при загрузке текстуры Field.png: {e}")
            self.zone_texture = None

        try:
            self.selection_button_texture = EasySprite.upscale_image("SelectionLine.png", 4)
        except Exception as e:
            print(f"Ошибка при загрузке текстуры SelectionLine.png: {e}")
            self.selection_button_texture = None

        try:
            self.item_subwindow_texture = EasySprite.upscale_image("Field.png", 2)
        except Exception as e:
            print(f"Ошибка при загрузке текстуры Field.png: {e}")
            self.item_subwindow_texture = None

        try:
            # Загружаем текстуру ауры
            self.aura_bar_texture = EasySprite.upscale_image("AuraBar.png", 2)
        except Exception as e:
            print(f"Ошибка при загрузке текстуры AuraBar.png: {e}")
            self.aura_bar_texture = None

        # Файлы текстур для кнопок действий
        texture_files = {
            'actionIcon_1': 'actionIcon_1.png',
            'actionIcon_2': 'actionIcon_2.png',
            'actionIcon_3': 'actionIcon_3.png',
            'itemIcon': 'itemIcon.png',
            'auroDopIcon': 'auroDopIcon.png',
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

    def create_selection_button_sprite(self, x, y, width, height, text):
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
        return sprite

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

        self.selection_buttons_list.clear()
        self.item_subwindow = None

        # Настройки для разных типов выбора
        if selection_type == 'actionIcon_1':
            title = "Выбор цели для атаки"
            item_prefix = "Враг"
            column2_items = ["Персонаж 1", "Персонаж 2"]
            show_subwindow = False
        elif selection_type == 'actionIcon_2':
            title = "Выбор цели для защиты"
            item_prefix = "Союзник"
            column2_items = ["Персонаж 1", "Персонаж 2"]
            show_subwindow = False
        elif selection_type == 'actionIcon_3':
            title = "Выбор цели для лечения"
            item_prefix = "Пациент"
            column2_items = ["Персонаж 1", "Персонаж 2"]
            show_subwindow = False
        elif selection_type == 'itemIcon':
            title = None
            item_prefix = "Предмет"
            column2_items = ["Предмет 1", "Предмет 2", "Предмет 3"]
            show_subwindow = True

        selection_height = 140
        selection_y = 70

        self.selection_zone = {
            'x': SCREEN_WIDTH // 2,
            'y': selection_y,
            'width': SCREEN_WIDTH - 40,
            'height': selection_height,
            'color': arcade.color.BLACK,
            'title': title,
            'show_subwindow': show_subwindow
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

                button_sprite = self.create_selection_button_sprite(
                    column_x,
                    item_y,
                    item_width,
                    item_height,
                    item_text
                )

                self.selection_buttons_list.append(button_sprite)

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

        if len(self.selected_zones) == 3:
            print("Все зоны выбраны! Переход в режим ожидания...")
            self.ui_state = STATE_ALL_SELECTED
            self.selected_button_zone = 0
            self.selected_button_index = 0
            self.update_button_indicator()
        else:
            self.reset_selection()
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

    def update_button_texture(self, button, is_hovered):
        """Обновляет текстуру кнопки при наведении"""
        if is_hovered != button.is_hovered:
            button.is_hovered = is_hovered

    def add_aura(self):
        """Добавляет единицу ауры"""
        self.aura += 1
        if self.aura > self.max_aura:
            self.aura = 0
        print(f"Аура: {self.aura}/{self.max_aura}")

    """Отрисовывает счётчик ауры в панели"""

    def draw_aura_counter_in_panel(self, panel_x, panel_y):
        if self.aura_bar_texture:
            # Если текстура загружена, рисуем только её
            segment_width = 8
            segment_height = 25
            segment_spacing = 3

            aura_start_x = panel_x - self.small_panel_width / 2 + 25
            aura_y = panel_y
            start_x = aura_start_x + 20

            total_bar_width = (self.max_aura * (segment_width + segment_spacing) - segment_spacing) * 2
            bar_left = start_x - segment_width
            bar_bottom = aura_y - segment_height
            bar_top = aura_y + segment_height

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

        number_x = start_x + self.max_aura * (segment_width + segment_spacing) + 15
        arcade.draw_text(
            f"{self.aura}",
            number_x - 5,
            aura_y,
            arcade.color.LIGHT_GRAY,
            20,
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

        arcade.draw_text(
            self.item_subwindow['title'],
            self.item_subwindow['x'],
            self.item_subwindow['y'] + self.item_subwindow['height'] // 2 - 15,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        text_x = self.item_subwindow['x'] - self.item_subwindow['width'] / 2 + 10
        text_y = self.item_subwindow['y']
        text_width = self.item_subwindow['width'] - 20

        arcade.draw_text(
            self.item_subwindow['description'],
            text_x,
            text_y,
            arcade.color.WHITE,
            12,
            anchor_x="left",
            anchor_y="center",
            align="center",
            width=text_width
        )

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
            arcade.draw_text(
                self.selection_zone['title'],
                self.selection_zone['x'],
                self.selection_zone['y'] + self.selection_zone['height'] // 2 - 15,
                arcade.color.LIGHT_GRAY,
                16,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )

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

        for item in self.selection_items:
            highlight_rect = arcade.LRBT(
                left=item['x'] - item['width'] / 2 - 1,
                right=item['x'] + item['width'] / 2 + 1,
                bottom=item['y'] - item['height'] / 2 - 1,
                top=item['y'] + item['height'] / 2 + 1
            )
            arcade.draw_rect_outline(highlight_rect, arcade.color.WHITE, 1)

            arcade.draw_text(
                item['text'],
                item['x'],
                item['y'],
                arcade.color.WHITE,
                12,
                anchor_x="center",
                anchor_y="center"
            )

            if item['selected']:
                selected_rect = arcade.LRBT(
                    left=item['x'] - item['width'] / 2 - 3,
                    right=item['x'] + item['width'] / 2 + 3,
                    bottom=item['y'] - item['height'] / 2 - 3,
                    top=item['y'] + item['height'] / 2 + 3
                )
                arcade.draw_rect_outline(selected_rect, arcade.color.DARK_GREEN, 3)

        if self.selection_indicator:
            indicator_rect = arcade.LRBT(
                left=self.selection_indicator['x'] - self.selection_indicator['width'] / 2 - 2,
                right=self.selection_indicator['x'] + self.selection_indicator['width'] / 2 + 2,
                bottom=self.selection_indicator['y'] - self.selection_indicator['height'] / 2 - 2,
                top=self.selection_indicator['y'] + self.selection_indicator['height'] / 2 + 2
            )
            arcade.draw_rect_outline(indicator_rect, arcade.color.RED, 3)

        if self.selection_zone.get('show_subwindow', False):
            self.draw_item_subwindow()

    def on_draw(self):
        self.clear()

        # Режим "все зоны выбраны"
        if self.ui_state == STATE_ALL_SELECTED:
            self.draw_aura_counter_minimized()

            arcade.draw_text(
                "Все зоны выбраны",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 50,
                arcade.color.WHITE,
                24,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )
            arcade.draw_text(
                "Нажмите R для сброса",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.WHITE,
                18,
                anchor_x="center",
                anchor_y="center"
            )
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

            if zone.zone_index in self.selected_zones:
                arcade.draw_rect_outline(zone_rect, arcade.color.RED, 3)  # Выбранная зона
            elif self.button_indicator and zone.zone_index == self.button_indicator['zone_index']:
                arcade.draw_rect_outline(zone_rect, arcade.color.YELLOW, 3)  # Активная зона
            else:
                arcade.draw_rect_outline(zone_rect, arcade.color.LIGHT_GRAY, 1)  # Обычная зона

        self.icons_list.draw()

        for i, icon in enumerate(self.icons_list):
            arcade.draw_text(
                str(i + 1),  # Номер зоны
                icon.center_x,
                icon.center_y,
                arcade.color.WHITE,
                10,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )

        self.buttons_list.draw()

        for button in self.buttons_list:
            button_rect = arcade.LRBT(
                left=button.center_x - button.width / 2,
                right=button.center_x + button.width / 2,
                bottom=button.center_y - button.height / 2,
                top=button.center_y + button.height / 2
            )

            if button.is_confirmed:
                arcade.draw_rect_outline(button_rect, arcade.color.RED, 3)

        if self.button_indicator and self.ui_state == STATE_NORMAL:
            indicator_rect = arcade.LRBT(
                left=self.button_indicator['x'] - self.button_indicator['width'] / 2 - 2,
                right=self.button_indicator['x'] + self.button_indicator['width'] / 2 + 2,
                bottom=self.button_indicator['y'] - self.button_indicator['height'] / 2 - 2,
                top=self.button_indicator['y'] + self.button_indicator['height'] / 2 + 2
            )
            arcade.draw_rect_outline(indicator_rect, arcade.color.YELLOW, 3)

        if self.ui_state == STATE_SELECTION:
            self.draw_selection_zone()

        # Отрисовка счётчика ауры
        if not self.aura_bar_texture:
            self.draw_aura_counter_in_panel(self.small_panel_x, self.small_panel_y)
        else:
            self.draw_aura_counter_in_panel(self.small_panel_x, self.small_panel_y)

        # Отрисовка подтверждённых выборов
        if self.confirmed_selections:
            selection_text_y = self.main_panel_y + self.main_panel_height / 2 + 70
            arcade.draw_text(
                "Подтверждённые выборы:",
                self.main_panel_x,
                selection_text_y,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )

            for i, (zone_idx, selection) in enumerate(self.confirmed_selections.items()):
                zone_text = f"Зона {zone_idx + 1}: {selection['item']}"
                arcade.draw_text(
                    zone_text,
                    self.main_panel_x,
                    selection_text_y - 25 * (i + 1),
                    arcade.color.LIGHT_GRAY,
                    12,
                    anchor_x="center",
                    anchor_y="center"
                )

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

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


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Интерфейс с кнопками")
    interface_view = InterfaceView()
    window.show_view(interface_view)
    arcade.run()


if __name__ == "__main__":
    main()