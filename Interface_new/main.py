""" Name: Максим | Date: 10.01.2026 | WhatYouDo: Загрузил обновлённый интерфейс """
from PIL import Image
import arcade
import io

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 600
MAIN_PANEL_WIDTH = 960
MAIN_PANEL_HEIGHT = 200
BUTTON_WIDTH = 50
BUTTON_HEIGHT = 50
PANEL_MARGIN = 10
ELEMENT_MARGIN = 3

STATE_NORMAL = "normal"
STATE_SELECTION = "selection"
STATE_ALL_SELECTED = "all_selected"


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

        self.background_color = arcade.color.BLACK
        self.panel_color = arcade.color.BLACK
        self.small_panel_color = arcade.color.DIM_GRAY

        self.main_panel_width = MAIN_PANEL_WIDTH
        self.main_panel_height = MAIN_PANEL_HEIGHT + 100

        self.main_panel_x = SCREEN_WIDTH // 2
        self.main_panel_y = MAIN_PANEL_HEIGHT // 2 + 50

        self.small_panel_width = 180
        self.small_panel_height = 40
        self.small_panel_x = self.main_panel_x - self.main_panel_width / 2 + self.small_panel_width / 2
        self.small_panel_y = self.main_panel_y + self.main_panel_height / 2 + self.small_panel_height / 2

        self.buttons_list = arcade.SpriteList()
        self.zones_list = arcade.SpriteList()
        self.icons_list = arcade.SpriteList()

        self.selection_zone = None
        self.selection_items = []
        self.selection_columns = []
        self.selection_indicator = None
        self.selected_item_index = 0
        self.selected_column = 0
        self.active_zone_index = None

        self.current_selection_type = None
        self.ui_state = STATE_NORMAL

        self.aura = 0
        self.max_aura = 10

        self.confirmed_selections = {}
        self.selected_zones = []

        self.textures = {}
        self.button_sprites = {}
        self.zone_texture = None
        self.load_textures()

        self.create_interface()

    def load_textures(self):
        try:
            self.zone_texture = EasySprite.upscale_image("Field.png", 2)
        except Exception as e:
            print(f"Ошибка при загрузке текстуры Field.png: {e}")
            self.zone_texture = None

        texture_files = {
            'actionIcon_1': 'actionIcon_1.png',
            'actionIcon_2': 'actionIcon_2.png',
            'actionIcon_3': 'actionIcon_3.png',
            'itemIcon': 'itemIcon.png',
            'auroDopIcon': 'auroDopIcon.png',
        }

        texture_colors = {
            'actionIcon_1': arcade.color.RED,
            'actionIcon_2': arcade.color.BLUE,
            'actionIcon_3': arcade.color.GREEN,
            'itemIcon': arcade.color.PURPLE,
            'auroDopIcon': arcade.color.ORANGE,
        }

        for name, filename in texture_files.items():
            try:
                upscaled_texture = EasySprite.upscale_image(filename, 4)

                self.textures[name] = upscaled_texture

                sprite = arcade.Sprite()
                sprite.texture = upscaled_texture

                scale_x = BUTTON_WIDTH / sprite.width
                scale_y = BUTTON_HEIGHT / sprite.height
                sprite.scale = min(scale_x, scale_y)

                self.button_sprites[name] = sprite

            except Exception as e:
                print(f"Ошибка при загрузке текстуры {filename}: {e}")
                self.textures[name] = None
                self.button_sprites[name] = None

        for name, color in texture_colors.items():
            self.textures[name + '_color'] = color
            self.textures[name + '_color_active'] = (
                max(0, color[0] - 30),
                max(0, color[1] - 30),
                max(0, color[2] - 30)
            )

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

    def create_interface(self):
        zone_width = (self.main_panel_width - PANEL_MARGIN * 4) // 3 - 60
        zone_height = 80

        for i in range(3):
            zone_x = (self.main_panel_x - self.main_panel_width / 2 + PANEL_MARGIN +
                      zone_width // 2 + i * (zone_width + PANEL_MARGIN) + 20 * i + 40)
            zone_y = self.main_panel_y + 50

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

                self.buttons_list.append(button_sprite)

    def create_selection_zone(self, selection_type, zone_index):
        if self.ui_state == STATE_ALL_SELECTED:
            return

        self.current_selection_type = selection_type
        self.active_zone_index = zone_index

        if selection_type == 'actionIcon_1':
            title = "Выбор цели для атаки"
            item_prefix = "Враг"
        elif selection_type == 'actionIcon_2':
            title = "Выбор цели для защиты"
            item_prefix = "Союзник"
        elif selection_type == 'actionIcon_3':
            title = "Выбор цели для лечения"
            item_prefix = "Пациент"
        elif selection_type == 'itemIcon':
            title = "Выбор предмета"
            item_prefix = "Предмет"

        selection_height = 120
        selection_y = 80

        self.selection_zone = {
            'x': SCREEN_WIDTH // 2,
            'y': selection_y,
            'width': SCREEN_WIDTH - 40,
            'height': selection_height,
            'color': arcade.color.DARK_GRAY,
            'title': title
        }

        self.selection_columns = []

        self.selection_items = []
        item_width = 70
        item_height = 30
        items_per_column = 3
        column_count = 3

        column_spacing = 85

        for col in range(column_count):
            column_x = 50 + col * column_spacing
            column_items = []

            for row in range(items_per_column):
                item_y = selection_y + 30 - row * (item_height + 10)
                item_num = col * 3 + row + 1

                item = {
                    'x': column_x,
                    'y': item_y,
                    'width': item_width,
                    'height': item_height,
                    'text': f"{item_prefix} {item_num}",
                    'column': col,
                    'row': row,
                    'selected': False
                }
                column_items.append(item)
                self.selection_items.append(item)

            self.selection_columns.append(column_items)

        if column_count >= 3:
            self.divider_x = 50 + 1 * column_spacing + column_spacing / 2 + 5
            self.divider_visible = True
        else:
            self.divider_x = None
            self.divider_visible = False

        self.update_selection_indicator()

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

    def start_selection_mode(self, selection_type, zone_index):
        if self.ui_state == STATE_ALL_SELECTED:
            return

        self.ui_state = STATE_SELECTION
        self.create_selection_zone(selection_type, zone_index)
        print(f"Режим выбора: {selection_type} (Зона {zone_index + 1})")

    def reset_selection(self):
        self.ui_state = STATE_NORMAL
        self.selection_zone = None
        self.selection_items = []
        self.selection_columns = []
        self.selection_indicator = None
        self.current_selection_type = None
        self.active_zone_index = None
        print("Текущий выбор сброшен.")

    def move_selection(self, direction):
        if not self.selection_items:
            return

        current_col = self.selected_column
        current_row = self.selected_item_index

        if direction == 'up':
            new_row = (current_row - 1) % 3
            self.selected_item_index = new_row
        elif direction == 'down':
            new_row = (current_row + 1) % 3
            self.selected_item_index = new_row
        elif direction == 'left':
            new_col = (current_col - 1) % 3
            self.selected_column = new_col
        elif direction == 'right':
            new_col = (current_col + 1) % 3
            self.selected_column = new_col

        selected_item = self.selection_columns[self.selected_column][self.selected_item_index]
        self.selection_indicator = {
            'x': selected_item['x'],
            'y': selected_item['y'],
            'width': selected_item['width'],
            'height': selected_item['height']
        }

    def confirm_selection(self):
        if not self.selection_items:
            return

        selected_item = self.selection_columns[self.selected_column][self.selected_item_index]

        for item in self.selection_items:
            item['selected'] = False

        selected_item['selected'] = True

        self.confirmed_selections[self.active_zone_index] = {
            'type': self.current_selection_type,
            'item': selected_item['text']
        }

        if self.active_zone_index not in self.selected_zones:
            self.selected_zones.append(self.active_zone_index)
            self.selected_zones.sort()

        print(
            f"Выбрано для зоны {self.active_zone_index + 1}: {selected_item['text']} (тип: {self.current_selection_type})")

        if len(self.selected_zones) == 3:
            print("Все зоны выбраны! Переход в режим ожидания...")
            self.ui_state = STATE_ALL_SELECTED
        else:
            self.reset_selection()

    def immediate_auro_dop_selection(self, zone_index):
        if self.ui_state == STATE_ALL_SELECTED:
            return

        self.active_zone_index = zone_index
        self.current_selection_type = 'auroDopIcon'

        selected_item_text = "Кнопка 1"

        self.confirmed_selections[self.active_zone_index] = {
            'type': self.current_selection_type,
            'item': selected_item_text
        }

        if self.active_zone_index not in self.selected_zones:
            self.selected_zones.append(self.active_zone_index)
            self.selected_zones.sort()

        if len(self.selected_zones) == 3:
            print("Все зоны выбраны! Переход в режим ожидания...")
            self.ui_state = STATE_ALL_SELECTED

    def update_button_texture(self, button, is_hovered):
        if is_hovered != button.is_hovered:
            button.is_hovered = is_hovered

    def add_aura(self):
        self.aura += 1
        if self.aura > self.max_aura:
            self.aura = 0
        print(f"Аура: {self.aura}/{self.max_aura}")

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

        segment_width = 8
        segment_height = 25
        segment_spacing = 3

        start_x = aura_start_x + 20

        for i in range(self.max_aura):
            segment_x = start_x + i * (segment_width + segment_spacing)

            if i < self.aura:
                segment_color = arcade.color.AQUA
            else:
                segment_color = arcade.color.DARK_GRAY

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

        if self.divider_x and self.divider_visible:
            divider_top = self.selection_zone['y'] + 45
            divider_bottom = self.selection_zone['y'] - 45

            arcade.draw_line(
                self.divider_x, divider_top,
                self.divider_x, divider_bottom,
                arcade.color.GRAY, 3
            )

        for item in self.selection_items:
            item_rect = arcade.LRBT(
                left=item['x'] - item['width'] / 2,
                right=item['x'] + item['width'] / 2,
                bottom=item['y'] - item['height'] / 2,
                top=item['y'] + item['height'] / 2
            )

            if item['selected']:
                item_color = arcade.color.DARK_GREEN
            else:
                item_color = arcade.color.DARK_GRAY

            arcade.draw_rect_filled(item_rect, item_color)
            arcade.draw_rect_outline(item_rect, arcade.color.LIGHT_GRAY, 1)

            arcade.draw_text(
                item['text'],
                item['x'],
                item['y'],
                arcade.color.WHITE,
                11,
                anchor_x="center",
                anchor_y="center"
            )

        if self.selection_indicator:
            indicator_rect = arcade.LRBT(
                left=self.selection_indicator['x'] - self.selection_indicator['width'] / 2 - 2,
                right=self.selection_indicator['x'] + self.selection_indicator['width'] / 2 + 2,
                bottom=self.selection_indicator['y'] - self.selection_indicator['height'] / 2 - 2,
                top=self.selection_indicator['y'] + self.selection_indicator['height'] / 2 + 2
            )
            arcade.draw_rect_outline(indicator_rect, arcade.color.RED, 3)

    def on_draw(self):
        self.clear()

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

        main_panel_rect = arcade.LRBT(
            left=self.main_panel_x - self.main_panel_width / 2,
            right=self.main_panel_x + self.main_panel_width / 2,
            bottom=self.main_panel_y - self.main_panel_height / 2,
            top=self.main_panel_y + self.main_panel_height / 2
        )
        arcade.draw_rect_filled(main_panel_rect, self.panel_color)
        arcade.draw_rect_outline(main_panel_rect, arcade.color.LIGHT_GRAY, 2)

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
                arcade.draw_rect_outline(zone_rect, arcade.color.RED, 3)
            else:
                arcade.draw_rect_outline(zone_rect, arcade.color.LIGHT_GRAY, 1)

        self.icons_list.draw()

        for i, icon in enumerate(self.icons_list):
            arcade.draw_text(
                str(i + 1),
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
            has_texture = button.normal_texture is not None

            if not has_texture:
                if button.button_index == 0:
                    text = "Кнопка 1"
                elif button.button_index == 1:
                    text = "Кнопка 2"
                elif button.button_index == 2:
                    text = "Кнопка 3"
                else:
                    text = f"Кнопка {button.button_index + 1}"

                arcade.draw_text(
                    text,
                    button.center_x,
                    button.center_y,
                    arcade.color.WHITE,
                    9,
                    anchor_x="center",
                    anchor_y="center",
                    bold=True
                )

        if self.ui_state == STATE_SELECTION:
            self.draw_selection_zone()

        self.draw_aura_counter_in_panel(self.small_panel_x, self.small_panel_y)

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
        if self.ui_state == STATE_NORMAL:
            for button in self.buttons_list:
                left = button.center_x - button.width / 2
                right = button.center_x + button.width / 2
                bottom = button.center_y - button.height / 2
                top = button.center_y + button.height / 2

                is_hovered = (left <= x <= right and bottom <= y <= top)
                if is_hovered != button.is_hovered:
                    button.is_hovered = is_hovered

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.ui_state == STATE_NORMAL:
                for btn in self.buttons_list:
                    left = btn.center_x - btn.width / 2
                    right = btn.center_x + btn.width / 2
                    bottom = btn.center_y - btn.height / 2
                    top = btn.center_y + btn.height / 2

                    if left <= x <= right and bottom <= y <= top:
                        print(
                            f"Нажата кнопка: Зона {btn.zone_index + 1}, Кнопка {btn.button_index + 1})")

                        if btn.button_type == 'auroDopIcon':
                            self.immediate_auro_dop_selection(btn.zone_index)
                        else:
                            self.start_selection_mode(btn.button_type, btn.zone_index)
                        return
            elif self.ui_state == STATE_SELECTION:
                for btn in self.buttons_list:
                    left = btn.center_x - btn.width / 2
                    right = btn.center_x + btn.width / 2
                    bottom = btn.center_y - btn.height / 2
                    top = btn.center_y + btn.height / 2

                    if left <= x <= right and bottom <= y <= top:
                        if btn.zone_index == self.active_zone_index:
                            print(f"Переключение на кнопку: Зона {btn.zone_index + 1}, Кнопка {btn.button_index + 1}")
                            if btn.button_type == 'auroDopIcon':
                                self.immediate_auro_dop_selection(btn.zone_index)
                            else:
                                self.start_selection_mode(btn.button_type, btn.zone_index)
                            return

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()

        elif key == arcade.key.M:
            self.add_aura()

        elif key == arcade.key.R:
            if self.ui_state == STATE_ALL_SELECTED:
                self.ui_state = STATE_NORMAL
                self.confirmed_selections = {}
                self.selected_zones = []
                print("Все выборы сброшены. Возврат в нормальный режим.")

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

        elif self.ui_state == STATE_NORMAL and key == arcade.key.C:
            if self.selected_zones:
                self.confirmed_selections = {}
                self.selected_zones = []
                print("Все выборы зон сброшены")


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Интерфейс с кнопками")
    interface_view = InterfaceView()
    window.show_view(interface_view)
    arcade.run()


if __name__ == "__main__":
    main()