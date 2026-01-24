""" Name: Максим | Date: 23.01.2026 | WhatYouDo: Обновил выбор: убрал фон у кнопок ывбора, добавил окошко под описание предмета """
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
STATE_NORMAL = "normal"
STATE_SELECTION = "selection"
STATE_ALL_SELECTED = "all_selected"

'''Юрин класс'''


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
        self.buttons_list = arcade.SpriteList()  # Список кнопок
        self.zones_list = arcade.SpriteList()  # Список зон
        self.icons_list = arcade.SpriteList()  # Список иконок зон
        self.selection_buttons_list = arcade.SpriteList()  # Список кнопок выбора

        # Переменные для режима выбора
        self.selection_zone = None  # Зона выбора (окно с целями/предметами)
        self.selection_items = []  # Элементы для выбора
        self.selection_columns = []  # Колонки элементов
        self.selection_indicator = None  # Индикатор текущего выбора в окне выбора
        self.selected_item_index = 0  # Индекс выбранного элемента в колонке
        self.selected_column = 0  # Индекс выбранной колонки
        self.active_zone_index = None  # Индекс активной зоны (0, 1, 2)

        # Состояния интерфейса
        self.current_selection_type = None  # Тип текущего выбора (actionIcon_1 и т.д.)
        self.ui_state = STATE_NORMAL  # Текущее состояние интерфейса

        # Аура
        self.aura = 0
        self.max_aura = 10

        # Данные о сделанных выборах
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
        self.selection_button_texture = None  # Текстура для кнопок выбора
        self.item_subwindow_texture = None  # Текстура для подокна предметов
        self.load_textures()

        # Подокно для предметов
        self.item_subwindow = None

        # Создание интерфейса
        self.create_interface()
        self.update_button_indicator()

    """Загрузка всех текстур для интерфейса"""

    def load_textures(self):
        try:
            self.zone_texture = EasySprite.upscale_image("Field.png", 2)
        except Exception as e:
            print(f"Ошибка при загрузке текстуры Field.png: {e}")
            self.zone_texture = None

        # Загрузка текстуры для кнопок выбора (ЗАМЕНА: Field.png -> SelectionLine.png)
        try:
            self.selection_button_texture = EasySprite.upscale_image("SelectionLine.png", 4)
        except Exception as e:
            print(f"Ошибка при загрузке текстуры SelectionLine.png для кнопок выбора: {e}")
            self.selection_button_texture = None

        # Загрузка текстуры для подокна предметов
        try:
            self.item_subwindow_texture = EasySprite.upscale_image("Field.png", 2)
        except Exception as e:
            print(f"Ошибка при загрузке текстуры Field.png для подокна предметов: {e}")
            self.item_subwindow_texture = None

        # Файлы текстур для кнопок
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

                # Масштабирование спрайта под размер кнопки
                scale_x = BUTTON_WIDTH / sprite.width
                scale_y = BUTTON_HEIGHT / sprite.height
                sprite.scale = min(scale_x, scale_y)

                self.button_sprites[name] = sprite

            except Exception as e:
                print(f"Ошибка при загрузке текстуры {filename}: {e}")
                self.textures[name] = None
                self.button_sprites[name] = None

        # Создание цветов для активного и обычного состояния кнопок
        for name, color in texture_colors.items():
            self.textures[name + '_color'] = color
            self.textures[name + '_color_active'] = (
                max(0, color[0] - 30),
                max(0, color[1] - 30),
                max(0, color[2] - 30)
            )

    """Создание спрайта кнопки с текстурой или цветом"""

    def create_button_sprite(self, x, y, texture_name, width, height, is_dropdown=False, is_first_button=False):
        normal_color = self.textures.get(texture_name + '_color', arcade.color.DARK_GRAY)
        active_color = self.textures.get(texture_name + '_color_active', arcade.color.GRAY)

        # Создание кнопки с текстурой (для первой кнопки в зоне)
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

        # Создание кнопки с текстурой (для остальных кнопок)
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

        # Создание цветной кнопки (если текстура не загружена)
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

    """Создание спрайта зоны с текстурой или цветом"""

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

    """Создание спрайта кнопки выбора с текстурой SelectionLine.png"""

    def create_selection_button_sprite(self, x, y, width, height, text):
        # Создаем спрайт с текстурой SelectionLine.png (ЗАМЕНА)
        if self.selection_button_texture:
            sprite = arcade.Sprite()
            sprite.texture = self.selection_button_texture
            sprite.center_x = x
            sprite.center_y = y

            # Масштабируем под нужный размер
            scale_x = width / sprite.width
            scale_y = height / sprite.height
            sprite.scale = min(scale_x, scale_y)

            sprite.width = width
            sprite.height = height
        else:
            # Если текстура не загружена, создаем серую кнопку
            sprite = arcade.SpriteSolidColor(width, height, arcade.color.DARK_GRAY)
            sprite.center_x = x
            sprite.center_y = y

        # Сохраняем текст для отрисовки
        sprite.button_text = text
        return sprite

    """Создание всех элементов интерфейса: зон, иконок и кнопок"""

    def create_interface(self):
        zone_width = (self.main_panel_width - PANEL_MARGIN * 4) // 3 - 60
        zone_height = 80

        # Создание 3 зон
        for i in range(3):
            # Позиция зоны
            zone_x = (self.main_panel_x - self.main_panel_width / 2 + PANEL_MARGIN +
                      zone_width // 2 + i * (zone_width + PANEL_MARGIN) + 20 * i + 40)
            zone_y = self.main_panel_y + 60

            # Создание спрайта зоны
            zone_sprite = self.create_zone_sprite(zone_x, zone_y, zone_width, zone_height, i)
            self.zones_list.append(zone_sprite)

            # Позиция иконки зоны (смещена влево от центра зоны)
            icon_x = zone_x - zone_width / 2 + 25
            icon_y = zone_y

            # Создание иконки зоны
            icon_sprite = arcade.SpriteSolidColor(20, 20, arcade.color.GRAY)
            icon_sprite.center_x = icon_x
            icon_sprite.center_y = icon_y
            icon_sprite.sprite_type = "icon"
            icon_sprite.zone_index = i
            self.icons_list.append(icon_sprite)

            # Создание 3 кнопок в каждой зоне
            for j in range(3):
                # Позиция кнопки (смещена вправо относительно иконки)
                button_x = icon_x + 30 + j * (BUTTON_WIDTH + ELEMENT_MARGIN) + BUTTON_WIDTH / 2
                button_y = zone_y

                # Определение типа кнопки в зависимости от позиции
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

                # Создание спрайта кнопки
                button_sprite = self.create_button_sprite(
                    button_x,
                    button_y,
                    texture_name,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT,
                    is_first_button=is_first_button
                )

                # Установка свойств кнопки
                button_sprite.button_type = texture_name
                button_sprite.zone_index = i
                button_sprite.button_index = j
                button_sprite.is_main_button = (j == 0)  # Первая кнопка - основная
                button_sprite.is_confirmed = False

                self.buttons_list.append(button_sprite)

    """Обновление позиции индикатора выбранной кнопки"""

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

    """Перемещение выбора кнопок в обычном режиме"""

    def move_button_selection(self, direction):
        if self.ui_state != STATE_NORMAL:
            return

        total_buttons = 9
        current_flat_index = self.selected_button_zone * 3 + self.selected_button_index

        # Обработка нажатий клавиш для навигации
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

    """Подтверждение выбора кнопки в обычном режиме"""

    def confirm_button_selection(self):
        if self.ui_state != STATE_NORMAL:
            return

        # Поиск выбранной кнопки
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

        # Обработка разных типов кнопок
        if selected_button.button_type == 'auroDopIcon':
            # Кнопка ауры
            self.immediate_auro_dop_selection(selected_button.zone_index)
            self.move_to_next_zone()
        else:
            # Остальные кнопки - переход в режим выбора
            self.start_selection_mode(selected_button.button_type, selected_button.zone_index)

    def move_to_next_zone(self):
        """Переход к следующей незаполненной зоне"""
        for zone_idx in range(3):
            next_zone = (self.selected_button_zone + zone_idx + 1) % 3
            if next_zone not in self.selected_zones:
                self.selected_button_zone = next_zone
                self.selected_button_index = 0
                self.update_button_indicator()
                return

    """Создание окна выбора целей или предметов"""

    def create_selection_zone(self, selection_type, zone_index):
        if self.ui_state == STATE_ALL_SELECTED:
            return

        self.current_selection_type = selection_type
        self.active_zone_index = zone_index

        # Очищаем список кнопок выбора
        self.selection_buttons_list.clear()
        self.item_subwindow = None  # Сбрасываем подокно

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
            show_subwindow = True  # Показываем подокно для предметов

        # Параметры окна выбора
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

        # Описание предметов
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

        # Размеры кнопок выбора
        item_width = 125
        item_height = 35

        # Настройка колонок в зависимости от типа выбора
        if selection_type in ['actionIcon_1', 'actionIcon_2', 'actionIcon_3']:
            column_count = 2
            column_spacing = 165
            items_per_column = 3
        else:
            column_count = 3
            column_spacing = 140
            items_per_column = 3

        # Создание колонок и элементов
        for col in range(column_count):
            column_x = 90 + col * column_spacing
            column_items = []

            # Определение количества элементов в колонке
            if selection_type in ['actionIcon_1', 'actionIcon_2', 'actionIcon_3']:
                if col == 0:
                    current_items_count = 3
                else:
                    current_items_count = 2
            else:
                current_items_count = 3

            # Создание элементов в колонке
            for row in range(current_items_count):
                item_y = selection_y + 45 - row * (item_height + 12)

                # Определение текста элемента
                if selection_type in ['actionIcon_1', 'actionIcon_2', 'actionIcon_3']:
                    if col == 0:
                        item_text = f"{item_prefix} {row + 1}"  # Стандартные названия
                    else:
                        item_text = column2_items[row] if row < len(
                            column2_items) else f"{item_prefix} {row + 4}"  # Пользовательские названия
                else:
                    item_num = col * 3 + row + 1
                    item_text = f"{item_prefix} {item_num}"

                # Создание спрайта кнопки с текстурой SelectionLine.png
                button_sprite = self.create_selection_button_sprite(
                    column_x,
                    item_y,
                    item_width,
                    item_height,
                    item_text
                )

                # Добавляем спрайт в список
                self.selection_buttons_list.append(button_sprite)

                # Создание элемента с ссылкой на спрайт
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

        # Настройка разделителя между колонками
        if selection_type in ['actionIcon_1', 'actionIcon_2', 'actionIcon_3']:
            self.divider_x = 70 + 0.7 * column_spacing
            self.divider_visible = True
        else:
            self.divider_x = None
            self.divider_visible = False

        self.update_selection_indicator()

    """Обновление индикатора выбора в окне выбора"""

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

    """Запуск режима выбора целей/предметов"""

    def start_selection_mode(self, selection_type, zone_index):
        if self.ui_state == STATE_ALL_SELECTED:
            return

        self.ui_state = STATE_SELECTION
        self.create_selection_zone(selection_type, zone_index)
        print(f"Режим выбора: {selection_type} (Зона {zone_index + 1})")

    """Сброс текущего режима выбора"""

    def reset_selection(self):
        self.ui_state = STATE_NORMAL
        self.selection_zone = None
        self.selection_items = []
        self.selection_columns = []
        self.selection_indicator = None
        self.current_selection_type = None
        self.active_zone_index = None
        self.item_subwindow = None
        # Очищаем список кнопок выбора
        self.selection_buttons_list.clear()
        print("Текущий выбор сброшен.")

    """Перемещение выбора в окне выбора"""

    def move_selection(self, direction):
        if not self.selection_items:
            return

        current_col = self.selected_column
        current_row = self.selected_item_index

        current_column_items = len(self.selection_columns[current_col])

        # Обработка навигации по элементам
        if direction == 'up':
            new_row = (current_row - 1) % current_column_items
            self.selected_item_index = new_row
        elif direction == 'down':
            new_row = (current_row + 1) % current_column_items
            self.selected_item_index = new_row
        elif direction == 'left':
            new_col = (current_col - 1) % len(self.selection_columns)
            # Проверка существования элемента с таким же индексом в новой колонке
            if self.selected_item_index >= len(self.selection_columns[new_col]):
                self.selected_item_index = len(self.selection_columns[new_col]) - 1
            self.selected_column = new_col
        elif direction == 'right':
            new_col = (current_col + 1) % len(self.selection_columns)
            # Проверка существования элемента с таким же индексом в новой колонке
            if self.selected_item_index >= len(self.selection_columns[new_col]):
                self.selected_item_index = len(self.selection_columns[new_col]) - 1
            self.selected_column = new_col

        # Обновление индикатора выбора
        selected_item = self.selection_columns[self.selected_column][self.selected_item_index]
        self.selection_indicator = {
            'x': selected_item['x'],
            'y': selected_item['y'],
            'width': selected_item['width'],
            'height': selected_item['height']
        }

    """Подтверждение выбора в окне выбора"""

    def confirm_selection(self):
        if not self.selection_items:
            return

        selected_item = self.selection_columns[self.selected_column][self.selected_item_index]

        # Сброс предыдущих выборов и установка нового
        for item in self.selection_items:
            item['selected'] = False

        selected_item['selected'] = True

        # Сохранение выбора
        self.confirmed_selections[self.active_zone_index] = {
            'type': self.current_selection_type,
            'item': selected_item['text']
        }

        # Добавление зоны в список выбранных
        if self.active_zone_index not in self.selected_zones:
            self.selected_zones.append(self.active_zone_index)
            self.selected_zones.sort()

        # Помечаем соответствующую кнопку как подтверждённую
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

        # Проверка, все ли зоны выбраны
        if len(self.selected_zones) == 3:
            print("Все зоны выбраны! Переход в режим ожидания...")
            self.ui_state = STATE_ALL_SELECTED
            self.selected_button_zone = 0
            self.selected_button_index = 0
            self.update_button_indicator()
        else:
            # Возврат в обычный режим и переход к следующей зоне
            self.reset_selection()
            self.move_to_next_zone()

    """Мгновенный выбор для кнопки ауры (без окна выбора)"""

    def immediate_auro_dop_selection(self, zone_index):
        if self.ui_state == STATE_ALL_SELECTED:
            return

        self.active_zone_index = zone_index
        self.current_selection_type = 'auroDopIcon'

        selected_item_text = "Кнопка 1"

        # Сохранение выбора
        self.confirmed_selections[self.active_zone_index] = {
            'type': self.current_selection_type,
            'item': selected_item_text
        }

        # Добавление зоны в список выбранных
        if self.active_zone_index not in self.selected_zones:
            self.selected_zones.append(self.active_zone_index)
            self.selected_zones.sort()

        # Помечаем кнопку ауры как подтверждённую
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

        # Сброс режима выбора, если он был активен
        if self.ui_state == STATE_SELECTION:
            self.reset_selection()

        # Проверка, все ли зоны выбраны
        if len(self.selected_zones) == 3:
            print("Все зоны выбраны! Переход в режим ожидания...")
            self.ui_state = STATE_ALL_SELECTED
            self.selected_button_zone = 0
            self.selected_button_index = 0
            self.update_button_indicator()

    """Обновление текстуры кнопки при наведении"""

    def update_button_texture(self, button, is_hovered):
        if is_hovered != button.is_hovered:
            button.is_hovered = is_hovered

    """Добавление единицы ауры"""

    def add_aura(self):
        self.aura += 1
        if self.aura > self.max_aura:
            self.aura = 0
        print(f"Аура: {self.aura}/{self.max_aura}")

    """Отрисовка счётчика ауры в панели"""

    def draw_aura_counter_in_panel(self, panel_x, panel_y):
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

        # Сегменты ауры
        segment_width = 8
        segment_height = 25
        segment_spacing = 3

        start_x = aura_start_x + 20

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

        # Числовое значение ауры
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

    """Отрисовка минимизированного счётчика ауры (в режиме всех выбрано)"""

    def draw_aura_counter_minimized(self):
        panel_x = 90
        panel_y = 40

        small_panel_rect = arcade.LRBT(
            left=panel_x - self.small_panel_width / 2,
            right=panel_x + self.small_panel_width / 2,
            bottom=panel_y - self.small_panel_height / 2,
            top=panel_y + self.small_panel_height / 2
        )
        arcade.draw_rect_filled(small_panel_rect, self.small_panel_color)
        arcade.draw_rect_outline(small_panel_rect, arcade.color.LIGHT_GRAY, 2)

        self.draw_aura_counter_in_panel(panel_x, panel_y)

    """Отрисовка подокна для предметов"""

    def draw_item_subwindow(self):
        if not self.item_subwindow:
            return

        # Фон подокна
        subwindow_rect = arcade.LRBT(
            left=self.item_subwindow['x'] - self.item_subwindow['width'] / 2,
            right=self.item_subwindow['x'] + self.item_subwindow['width'] / 2,
            bottom=self.item_subwindow['y'] - self.item_subwindow['height'] / 2,
            top=self.item_subwindow['y'] + self.item_subwindow['height'] / 2
        )

        # Если есть текстура, создаем спрайт
        if self.item_subwindow['texture']:
            # Рисуем текстуру
            arcade.draw_texture_rect(
                self.item_subwindow['texture'],
                subwindow_rect
            )
        else:
            # Или рисуем серый прямоугольник
            arcade.draw_rect_filled(subwindow_rect, arcade.color.DARK_GRAY)

        # Рамка подокна
        arcade.draw_rect_outline(subwindow_rect, arcade.color.LIGHT_GRAY, 2)

        # Заголовок подокна (в верхней части)
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

        # Описание предмета
        text_x = self.item_subwindow['x'] - self.item_subwindow['width'] / 2 + 10
        text_y = self.item_subwindow['y']
        text_width = self.item_subwindow['width'] - 20

        # Рисуем текст с выравниванием по центру
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

    """Отрисовка окна выбора целей/предметов"""

    def draw_selection_zone(self):
        if not self.selection_zone:
            return

        # Фон окна выбора
        zone_rect = arcade.LRBT(
            left=self.selection_zone['x'] - self.selection_zone['width'] / 2,
            right=self.selection_zone['x'] + self.selection_zone['width'] / 2,
            bottom=self.selection_zone['y'] - self.selection_zone['height'] / 2,
            top=self.selection_zone['y'] + self.selection_zone['height'] / 2
        )
        arcade.draw_rect_filled(zone_rect, self.selection_zone['color'])
        arcade.draw_rect_outline(zone_rect, arcade.color.LIGHT_GRAY, 2)

        # Заголовок окна (только если он задан)
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

        # Разделитель между колонками (для action кнопок)
        if self.divider_visible and self.divider_x and self.current_selection_type in ['actionIcon_1', 'actionIcon_2',
                                                                                       'actionIcon_3']:
            divider_top = self.selection_zone['y'] + 69
            divider_bottom = self.selection_zone['y'] - 69

            arcade.draw_line(
                self.divider_x, divider_top,
                self.divider_x, divider_bottom,
                arcade.color.GRAY, 2
            )

        # Отрисовка кнопок выбора через SpriteList
        self.selection_buttons_list.draw()

        # Отрисовка текста поверх кнопок и выделений
        for item in self.selection_items:
            # Тонкое белое выделение для всех кнопок
            highlight_rect = arcade.LRBT(
                left=item['x'] - item['width'] / 2 - 1,
                right=item['x'] + item['width'] / 2 + 1,
                bottom=item['y'] - item['height'] / 2 - 1,
                top=item['y'] + item['height'] / 2 + 1
            )
            arcade.draw_rect_outline(highlight_rect, arcade.color.WHITE, 1)

            # Текст элемента поверх кнопки
            arcade.draw_text(
                item['text'],
                item['x'],
                item['y'],
                arcade.color.WHITE,
                12,
                anchor_x="center",
                anchor_y="center"
            )

            # Рамка для выбранного элемента (толще)
            if item['selected']:
                selected_rect = arcade.LRBT(
                    left=item['x'] - item['width'] / 2 - 3,
                    right=item['x'] + item['width'] / 2 + 3,
                    bottom=item['y'] - item['height'] / 2 - 3,
                    top=item['y'] + item['height'] / 2 + 3
                )
                arcade.draw_rect_outline(selected_rect, arcade.color.DARK_GREEN, 3)

        # Индикатор текущего выбора (красная рамка)
        if self.selection_indicator:
            indicator_rect = arcade.LRBT(
                left=self.selection_indicator['x'] - self.selection_indicator['width'] / 2 - 2,
                right=self.selection_indicator['x'] + self.selection_indicator['width'] / 2 + 2,
                bottom=self.selection_indicator['y'] - self.selection_indicator['height'] / 2 - 2,
                top=self.selection_indicator['y'] + self.selection_indicator['height'] / 2 + 2
            )
            arcade.draw_rect_outline(indicator_rect, arcade.color.RED, 3)

        # Отрисовка подокна для предметов (если нужно) - теперь увеличенное
        if self.selection_zone.get('show_subwindow', False):
            self.draw_item_subwindow()

    """Основной метод отрисовки интерфейса"""

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

        # Верхняя маленькая панель (для ауры)
        small_panel_rect = arcade.LRBT(
            left=self.main_panel_x - self.main_panel_width / 2,
            right=self.main_panel_x - self.main_panel_width / 2 + self.small_panel_width,
            bottom=self.main_panel_y + self.main_panel_height / 2,
            top=self.main_panel_y + self.main_panel_height / 2 + self.small_panel_height
        )
        arcade.draw_rect_filled(small_panel_rect, self.small_panel_color)
        arcade.draw_rect_outline(small_panel_rect, arcade.color.LIGHT_GRAY, 2)

        # Соединительная линия между панелями
        connection_rect = arcade.LRBT(
            left=self.main_panel_x - self.main_panel_width / 2,
            right=self.main_panel_x - self.main_panel_width / 2 + self.small_panel_width,
            bottom=self.main_panel_y + self.main_panel_height / 2,
            top=self.main_panel_y + self.main_panel_height / 2 + 2
        )
        arcade.draw_rect_filled(connection_rect, arcade.color.GRAY)

        # Отрисовка зон
        self.zones_list.draw()

        # Рамки зон (разные цвета в зависимости от состояния)
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

        # Отрисовка иконок зон
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

        # Отрисовка кнопок
        self.buttons_list.draw()

        # Рамки подтверждённых кнопок
        for button in self.buttons_list:
            button_rect = arcade.LRBT(
                left=button.center_x - button.width / 2,
                right=button.center_x + button.width / 2,
                bottom=button.center_y - button.height / 2,
                top=button.center_y + button.height / 2
            )

            if button.is_confirmed:
                arcade.draw_rect_outline(button_rect, arcade.color.RED, 3)

        # Индикатор текущей кнопки (жёлтая рамка)
        if self.button_indicator and self.ui_state == STATE_NORMAL:
            indicator_rect = arcade.LRBT(
                left=self.button_indicator['x'] - self.button_indicator['width'] / 2 - 2,
                right=self.button_indicator['x'] + self.button_indicator['width'] / 2 + 2,
                bottom=self.button_indicator['y'] - self.button_indicator['height'] / 2 - 2,
                top=self.button_indicator['y'] + self.button_indicator['height'] / 2 + 2
            )
            arcade.draw_rect_outline(indicator_rect, arcade.color.YELLOW, 3)

        # Отрисовка окна выбора (если активно)
        if self.ui_state == STATE_SELECTION:
            self.draw_selection_zone()

        # Отрисовка счётчика ауры
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

    """Обработка движения мыши"""

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    """Обработка нажатия кнопок мыши"""

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    """Обработка нажатия клавиш клавиатуры"""

    def on_key_press(self, key, modifiers):
        # Добавление ауры
        if key == arcade.key.M:
            self.add_aura()

        # Сброс всех выборов (только в режиме всех выбрано)
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

        # Обычный режим (навигация по кнопкам)
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
                # Сброс всех выборов зон
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

        # Режим выбора (навигация в окне выбора)
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