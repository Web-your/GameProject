import re
import arcade
from PIL import ImageFont
import pyglet
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from arcade import SpriteList
from pyglet.event import EVENT_HANDLE_STATE
from pyglet.resource import texture

import EasySprite


class Dialog():
    def __init__(self, coordinates, text=None, file_text=None, width=None):
        self.base_settings = {"id": 0, "font": "", "color": (255, 255, 255), "font_size": 18,
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
