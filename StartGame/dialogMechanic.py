import re
from turtledemo.penrose import start
import numpy as np
import arcade
from PIL import ImageFont
import pyglet
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from arcade import SpriteList
from pyglet.event import EVENT_HANDLE_STATE
from pyglet.resource import texture
import os.path
import EasySprite


class Dialog:
    def __init__(self, coordinates, text=None, file_text=None, width=None):
        self.base_settings = {"id": 0, "font": "StartGame/web_ibm_mda.ttf", "color": (255, 255, 255), "font_size": 18,
                              "twitch": 0, "time_appear": 0.05,"can_break": True, "break": False, "text": ""}
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.replicas = []
        self.replicas_active = 0
        self.simvol_time = 0
        self.width = width
        self.visable_text = []
        self.shift_x = 0
        self.shift_y = 0
        self.replic = 0
        if file_text and not text:
            with open(file_text, "r", encoding="utf8") as file:
                self.data = file.read().split("<*>")
                self.refresh_data()
        elif text and not file_text:
            self.data = text.split("<*>")
            self.refresh_data()

    def set_font(self, dict, data):
        dict["font"] = data
        return dict

    def set_font_size(self, dict, data):
        dict["font_size"] = int(data)
        return dict

    def set_color(self, dict, data):
        if data.startswith("rgb("):
            dict["color"] = tuple(map(int, [item.strip() for item in data[4:-1].split(",")]))
        return dict

    def set_twitch(self, dict, data):
        dict["twitch"] = float(data)
        return dict

    def set_time_appear(self, dict, data):
        dict["time_appear"] = float(data)
        return dict

    def set_break(self, dict, data):
        if data == "true":
            dict["break"] = True
        else:
            dict["break"] = False
        return dict

    def refresh_data(self):
        all_comands = {"font": self.set_font, "color": self.set_color, "twitch": self.set_twitch,
                       "time_appear": self.set_time_appear, "break": self.set_break, "font_size": self.set_font_size}
        pattern = "<([^>]*)>(.*?)<\/>"
        self.replicas = []
        content = self.data
        for line in content:
            words = []
            matches = re.finditer(pattern, line)
            shift_in_start = 0
            clean_line = line
            if matches:
                for match in matches:
                    user_comands = [item.strip().split("=") for item in match.group(1).split(";")]

                    base_words = clean_line[:match.start() - shift_in_start]
                    settings_base_words = self.base_settings.copy()
                    settings_base_words["id"] = len(words)
                    settings_base_words["text"] = base_words
                    words.append(settings_base_words)

                    settings_user_words = self.base_settings.copy()
                    settings_user_words["id"] = len(words)
                    settings_user_words["text"] = match.group(2)

                    clean_line = clean_line[match.end() - shift_in_start:]
                    shift_in_start = match.end()

                    for user_cmd in user_comands:
                        print(user_cmd)
                        for cmd in all_comands.keys():
                            if user_cmd[0] == cmd:
                                settings_user_words = all_comands[user_cmd[0]](settings_user_words, user_cmd[1])
                    words.append(settings_user_words)
            if clean_line:
                base_words = clean_line
                settings_base_words = self.base_settings.copy()
                settings_base_words["id"] = len(words)
                settings_base_words["text"] = base_words
                words.append(settings_base_words)
            self.replicas.append(words)

    def update_text(self, delta_time):
        self.simvol_time += delta_time
        replic = self.replicas[self.replicas_active]
        if self.replic < len(replic):
            item = replic[self.replic]
            chars_to_show = min(int(self.simvol_time / item["time_appear"]), len(item["text"]))
            pyglet.font.add_file(item["font"])
            font_prop = fm.FontProperties(fname=item["font"])

            text_width = (item["font_size"] - 2) * len(item["text"])
            text_height = item["font_size"] + (item["font_size"] // 2)
            if self.width - self.shift_x != 0:
                if (text_width / (self.width - self.shift_x) >= 1 and not (item["can_break"])) or item["break"]:
                    self.shift_y += text_height
                    self.shift_x = 0

            if chars_to_show > 0:
                text = item["text"][:chars_to_show]
                text_obj = arcade.Text(
                    text=text,
                    x=self.x + self.shift_x,
                    y=self.y - self.shift_y,
                    color=item["color"],
                    font_size=item["font_size"],
                    font_name=font_prop.get_name(),
                )

                if item["id"] >= len(self.visable_text):
                    self.visable_text.append(text_obj)
                else:
                    self.visable_text[item["id"]] = text_obj

            if chars_to_show >= len(item["text"]):
                self.shift_x += text_width
                self.simvol_time = 0
                self.replic += 1

    def update_replicas(self):
        if self.replicas_active + 1 < len(self.replicas):
            self.replicas_active += 1
            self.replic = 0
            self.visable_text = []
            self.simvol_time = 0
            self.shift_x = 0
            self.shift_y = 0

    def get_replic(self):
        ...

    def get_active_replic(self):
        ...

    def draw(self):
        for item in self.visable_text:
            item.draw()

class Button:
    def __init__(self, x, y, width, height, text="", font=None, font_size=None, color=None, color_act=None, line_width=None, line_width_act=None):
        self.state_act = False
        self.button_state = False
        self.box_button = (x, y, width, height)
        self.options_button = {'text': "","font": "", "font_size": 18, "color": (255, 255, 255),
                               "color_act": (255, 255, 255), "line_width": 2, "line_width_act": 2}
        pyglet.font.add_file("StartGame/web_ibm_mda.ttf")
        font_prop = fm.FontProperties(fname="StartGame/web_ibm_mda.ttf")
        self.options_button["font"] = font_prop.get_name()
        if text != "":
            self.set_text(text)
        if not font is None:
            self.set_font(font)
        if not font_size is None:
            self.set_font_size(font_size)
        if not color is None:
            self.set_color(color)
        if not color_act is None:
            self.set_color_act(color_act)
        if not line_width is None:
            self.set_line_width(line_width)
        if not line_width_act is None:
            self.set_line_width_act(line_width_act)

    def set_text(self, text):
        self.options_button["text"] = text

    def set_font(self, font):
        pyglet.font.add_file(font)
        font_prop = fm.FontProperties(fname=font)
        self.options_button["font"] = font_prop.get_name()

    def set_font_size(self, font_size):
        self.options_button["font_size"] = font_size

    def set_color(self, color):
        self.options_button["color"] = color

    def set_color_act(self, color_act):
        self.options_button["color_act"] = color_act

    def set_line_width(self, line_width):
        self.options_button["line_width"] = line_width

    def set_line_width_act(self, line_width_act):
        self.options_button["line_width_act"] = line_width_act

    def set_button_options(self, x, y, width, height):
        self.box_button = (x, y, width, height)

    def update_state(self, x=None, y=None, state=None):
        if not x is None and not y is None:
            if (self.box_button[0] - self.box_button[2] // 2 <= x <= self.box_button[0] + self.box_button[2] // 2 and
                    self.box_button[1] - self.box_button[3] // 2 <= y <= self.box_button[1] + self.box_button[3]):
                self.state_act = True
            else:
                self.state_act = False
        if not state is None:
            if state:
                self.state_act = True
            else:
                self.state_act = False

    def press(self):
        self.button_state = not self.button_state

    def draw(self):
        if not self.state_act:
            arcade.draw_lbwh_rectangle_outline(self.box_button[0] - self.box_button[2] // 2,
                                               self.box_button[1] - self.box_button[3] // 2,
                                               self.box_button[2],
                                               self.box_button[3],
                                               self.options_button["color"],
                                               border_width=self.options_button["line_width"])
            text = arcade.Text(
                text=self.options_button["text"],
                x=self.box_button[0],
                y=self.box_button[1],
                color=self.options_button["color"],
                font_size=self.options_button["font_size"],
                width=self.box_button[2],
                anchor_x="center",
                anchor_y="center",
                font_name=self.options_button["font"]
            )
            text.draw()
        elif self.state_act:
            arcade.draw_lbwh_rectangle_outline(self.box_button[0] - self.box_button[2] // 2,
                                               self.box_button[1] - self.box_button[3] // 2,
                                               self.box_button[2],
                                               self.box_button[3],
                                               self.options_button["color_act"],
                                               border_width=self.options_button["line_width_act"])
            text = arcade.Text(
                text=self.options_button["text"],
                x=self.box_button[0],
                y=self.box_button[1],
                color=self.options_button["color_act"],
                font_size=self.options_button["font_size"],
                width=self.box_button[2],
                anchor_x="center",
                anchor_y="center",
                font_name=self.options_button["font"],
                bold=True
            )
            text.draw()

class ButtonGroup:
    def __init__(self, *elements, division="all"):
        division_dict = {"all": 0, "left-right": 1, "up-down": 2}
        self.buttons = np.array(elements)
        self.division = division_dict[division]
        self.active_index = 0
        if len(self.buttons.shape) > 2:
            self.active_index = (0, 0)
        if len(self.buttons.shape) < 2 and self.division == 0:
            self.division = 1

    def update_state_buttons(self, key):
        if key == arcade.key.ENTER:
            if self.division != 0:
                self.buttons[self.active_index].press()
            else:
                self.buttons[self.active_index[0]][self.active_index[1]].press()

        if ((key == arcade.key.W) or (key == arcade.key.UP)) and self.division == 2:
            if self.active_index != 0:
                self.active_index -= 1
        elif ((key == arcade.key.W) or (key == arcade.key.UP)) and self.division == 0:
            if self.active_index[1] != 0:
                self.active_index[1] -= 1

        if (key == arcade.key.S) or (key == arcade.key.DOWN) and self.division == 2:
            if self.active_index != self.buttons.shape[0] - 1:
                self.active_index += 1
        elif (key == arcade.key.S or key == arcade.key.DOWN) and self.division == 0:
            if self.active_index[1] != self.buttons.shape[1] - 1:
                self.active_index[1] += 1

        if (key == arcade.key.A or key == arcade.key.LEFT) and self.division == 1:
            if self.active_index != 0:
                self.active_index -= 1
        elif (key == arcade.key.A or key == arcade.key.LEFT) and self.division == 0:
            if self.active_index[0] != 0:
                self.active_index[0] -= 1

        if (key == arcade.key.D or key == arcade.key.RIGHT) and self.division == 1:
            if self.active_index != self.buttons.shape[0] - 1:
                self.active_index += 1
        elif (key == arcade.key.D or key == arcade.key.RIGHT) and self.division == 0:
            if self.active_index[0] != self.buttons.shape[0] - 1:
                self.active_index[0] += 1

    def draw(self):
        if self.division != 0:
            for i in range(len(self.buttons)):
                button = self.buttons[i]
                if i == self.active_index:
                    button.update_state(state=True)
                else:
                    button.update_state(state=False)
                button.draw()
        else:
            ...

import arcade
import random

import arcade
from arcade.types import Color

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Alfa.Ver01"
MENU_STATE = 0

class StartMenu(arcade.View):
    def __init__(self, main_scene_manager):
        super().__init__()
        self.main_scene_manager = main_scene_manager

        self.keys = set()
        self.menu_state = MENU_STATE
        pyglet.font.add_file("StartGame/pixcyr2.ttf")
        self.setup2()

    def setup2(self):  # Список списков координат квадратов для рисования
        self.dialog = Dialog((100, 80), file_text="StartGame/hernia.txt", width=300)
        self.dialog.base_settings["time_appear"] = 0.1
        self.dialog.base_settings["color"] = (183,120,56)
        self.dialog.base_settings["font_size"] = 22
        self.dialog.refresh_data()

        file_path = "SaveData.csv"
        self.saves = os.path.exists(file_path)
        if self.saves:
            self.button_game = Button(self.width // 2, self.height // 6 * 3, 200, 60, text="Продолжить",
                                      line_width_act=4)
            self.button_options = Button(self.width // 2, self.height // 6, 200, 60, text="Настройки",
                                         line_width_act=4)
            self.button_new_game = Button(self.width // 2, self.height // 6 * 2, 200, 60, text="Новая игра",
                                          line_width_act=4)
            self.group_button = ButtonGroup(self.button_game, self.button_new_game, self.button_options, division="up-down")
        else:
            self.button_options = Button(self.width // 2, self.height // 6 * 2, 200, 60, text="Настройки",
                                         line_width_act=4)
            self.button_new_game = Button(self.width // 2, self.height // 6 * 3, 200, 60, text="Новая игра",
                                          line_width_act=4)
            self.group_button = ButtonGroup(self.button_new_game, self.button_options, division="up-down")

        image = arcade.Sprite(EasySprite.load_texture("StartGame/Start.png", 3.5))
        image.center_x = self.width // 2
        image.center_y = self.height // 3 * 1.8
        self.story_sprits = arcade.SpriteList()
        self.story_sprits.append(image)
        font_prop = fm.FontProperties(fname="StartGame/pixcyr2.ttf")
        self.text_press = arcade.Text(
            text="press enter",
            x=self.width // 2 - 80,
            y=self.height // 3,
            color=(255, 255, 255),
            font_size=18,
            font_name=font_prop.get_name(),
        )

    def on_draw(self):
        """Этот метод отвечает за отрисовку содержимого окна"""
        self.clear()
        if self.menu_state == 0:
           self.dialog.draw()
           self.story_sprits.draw()
        elif self.menu_state == 1:
            self.text_press.draw()
        elif self.menu_state == 2:
            self.group_button.draw()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> EVENT_HANDLE_STATE:
        ...

    def on_key_press(self, symbol: int, modifiers: int):
        self.keys.add(symbol)
        if self.menu_state == 2:
            self.group_button.update_state_buttons(symbol)

    def on_update(self, delta_time):
        """Этот метод отвечает за обновление логики игры (анимации, взаимодействия и т. д.)"""
        self.dialog.update_text(delta_time)
        if arcade.key.ENTER in self.keys and self.menu_state == 0:
            if len(self.dialog.replicas) == self.dialog.replicas_active + 1:
                self.menu_state += 1
            self.dialog.update_replicas()
            self.keys.remove(arcade.key.ENTER)
        elif arcade.key.ENTER in self.keys and self.menu_state == 1:
            self.menu_state += 1

        if self.button_new_game.button_state:
            self.main_scene_manager.next_scene()
            with open("SaveData.csv", "w") as file:
                file.write("Создано")
            print("StartGame")

        if self.saves:
            if self.button_game.button_state:
                self.main_scene_manager.next_scene()


def setup_menu(main_scene_manager):
    main_scene_manager.window.show_view(StartMenu(main_scene_manager))
