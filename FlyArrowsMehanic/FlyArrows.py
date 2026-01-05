""" Name: Юрий, Date: 03.01.2026, WhatYouDo: сделал механику стрелочек"""
import arcade
from arcade.types import Color
from pyglet.graphics import Batch

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Flying arrows"

class MyGame(arcade.Window):
    def __init__(self, width, height, title, side, color):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)
        self.width = width
        self.height = height

    def setup(self):
        self.arrows = [[0, 1, 2], [1, 2, 1], [2, 3, 1], [3, 4, 1], [2, 5, 1], [0, 4, 1]] # создаём или передаём массив стрелок
        ### Первое число в массиве стрелок направление 0-влево, 1-вверх, 2-вправо, 3-вниз
        # Второе число это номер цикла###
        self.cycle_time = 0.5 # создаём или передаём время цикла
        self.total_time = 0.0
        self.speed = 400
        self.count = 0
        self.arrows_0 = set()
        self.arrows_1 = set()
        self.arrows_2 = set()
        self.arrows_3 = set()
        for index, tcycle, tarrow in self.arrows:
            if index == 0:
                self.arrows_0.add(tcycle * self.cycle_time + 2)
            elif index == 1:
                self.arrows_1.add(tcycle * self.cycle_time + 2)
            elif index == 2:
                self.arrows_2.add(tcycle * self.cycle_time + 2)
            elif index == 3:
                self.arrows_3.add(tcycle * self.cycle_time + 2)

        self.detect_sprite_0 = arcade.Sprite("detect_arrow0.png", scale=0.5)
        self.detect_sprite_1 = arcade.Sprite("detect_arrow1.png", scale=0.5)
        self.detect_sprite_2 = arcade.Sprite("detect_arrow2.png", scale=0.5)
        self.detect_sprite_3 = arcade.Sprite("detect_arrow3.png", scale=0.5)
        self.detect_sprite_0.center_x = self.width // 5
        self.detect_sprite_0.center_y = self.height - 100
        self.detect_sprite_1.center_x = self.width // 5 * 2
        self.detect_sprite_1.center_y = self.height - 100
        self.detect_sprite_2.center_x = self.width // 5 * 3
        self.detect_sprite_2.center_y = self.height - 100
        self.detect_sprite_3 .center_x = self.width // 5 * 4
        self.detect_sprite_3 .center_y = self.height - 100

        self.all_sprites = arcade.SpriteList()
        self.all_sprites.append(self.detect_sprite_0)
        self.all_sprites.append(self.detect_sprite_1)
        self.all_sprites.append(self.detect_sprite_2)
        self.all_sprites.append(self.detect_sprite_3)
        self.keys_pressed = set()

        self.all_arrow_sprites = arcade.SpriteList()
        self.keys_pressed_last_0 = None
        self.keys_pressed_last_1 = None
        self.keys_pressed_last_2 = None
        self.keys_pressed_last_3 = None

    def on_draw(self):
        """Этот метод отвечает за отрисовку содержимого окна"""
        self.clear()
        self.all_arrow_sprites.draw()
        self.all_sprites.draw()
        self.batch.draw()

    def on_update(self, delta_time):
        """Этот метод отвечает за обновление логики игры (анимации, взаимодействия и т. д.)"""
        self.total_time += delta_time
        self.fly_arrows()
        self.fly_arrows_vid(delta_time)
        if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
            for i in self.arrows_0:
                if i - 0.2 < self.keys_pressed_0 < i + 0.2:
                    self.detect_sprite_0.scale = 0.6
                    if self.keys_pressed_0 != self.keys_pressed_last_0:
                        self.count += 1
                        self.keys_pressed_last_0 = self.keys_pressed_0
                    break
            else:
                self.detect_sprite_0.scale = 0.4
        else:
            self.detect_sprite_0.scale = 0.5
        if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
            for i in self.arrows_3:
                if i - 0.2 < self.keys_pressed_3 < i + 0.2:
                    self.detect_sprite_3.scale = 0.6
                    if self.keys_pressed_3 != self.keys_pressed_last_3:
                        self.count += 1
                        self.keys_pressed_last_3 = self.keys_pressed_3
                    break
            else:
                self.detect_sprite_3.scale = 0.4
        else:
            self.detect_sprite_3.scale = 0.5
        if arcade.key.UP in self.keys_pressed or arcade.key.W in self.keys_pressed:
            for i in self.arrows_1:
                if i - 0.2 < self.keys_pressed_1 < i + 0.2:
                    self.detect_sprite_1.scale = 0.6
                    if self.keys_pressed_1 != self.keys_pressed_last_1:
                        self.count += 1
                        self.keys_pressed_last_1 = self.keys_pressed_1
                    break
            else:
                self.detect_sprite_1.scale = 0.4
        else:
            self.detect_sprite_1.scale = 0.5
        if arcade.key.DOWN in self.keys_pressed or arcade.key.S in self.keys_pressed:
            for i in self.arrows_2:
                if i - 0.2 < self.keys_pressed_2 < i + 0.2:
                    self.detect_sprite_2.scale = 0.6
                    if self.keys_pressed_2 != self.keys_pressed_last_2:
                        self.count += 1
                        self.keys_pressed_last_2 = self.keys_pressed_2
                    break
            else:
                self.detect_sprite_2.scale = 0.4
        else:
            self.detect_sprite_2.scale = 0.5

        self.batch = Batch()
        self.fonts = arcade.Text(
            f"Счёт: {self.count}",
            10,
            30,
            arcade.color.WHITE,
            16,
            batch=self.batch
        )

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
            if arcade.key.LEFT == key or arcade.key.A == key:
                self.keys_released_0 = self.total_time
            elif arcade.key.UP == key or arcade.key.W == key:
                self.keys_released_1 = self.total_time
            elif arcade.key.DOWN == key or arcade.key.S == key:
                self.keys_released_2 = self.total_time
            elif arcade.key.RIGHT == key or arcade.key.D == key:
                self.keys_released_3 = self.total_time

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        if arcade.key.LEFT == key or arcade.key.A == key:
            self.keys_pressed_0 = self.total_time
            self.keys_released_0 = None
        elif arcade.key.UP == key or arcade.key.W == key:
            self.keys_pressed_1 = self.total_time
            self.keys_released_1 = None
        elif arcade.key.DOWN == key or arcade.key.S == key:
            self.keys_pressed_2 = self.total_time
            self.keys_released_2 = None
        elif arcade.key.RIGHT == key or arcade.key.D == key:
            self.keys_pressed_3 = self.total_time
            self.keys_released_3 = None

    def fly_arrows(self):
        dct_index = {0: "arrow0.png", 1: "arrow1.png", 2: "arrow2.png", 3: "arrow3.png"}
        for i, item in enumerate(self.arrows):
            index, tcycle, tarrow = item
            if self.total_time - 2 >= tcycle * self.cycle_time - (400/self.speed):
                player_sprite = arcade.Sprite(dct_index[index], scale=0.5)
                if index == 0:
                    player_sprite.center_x = self.width // 5
                    player_sprite.center_y = self.height - 500
                elif index == 1:
                    player_sprite.center_x = self.width // 5 * 2
                    player_sprite.center_y = self.height - 500
                elif index == 2:
                    player_sprite.center_x = self.width // 5 * 3
                    player_sprite.center_y = self.height - 500
                elif index == 3:
                    player_sprite.center_x = self.width // 5 * 4
                    player_sprite.center_y = self.height - 500
                self.all_arrow_sprites.append(player_sprite)
                del self.arrows[i]

    def fly_arrows_vid(self, delta_time):
        for i, arrow in enumerate(self.all_arrow_sprites):
            arrow.center_y += self.speed * delta_time
            if arrow.center_y > 800:
                self.all_arrow_sprites.pop(i)



def setup_game(width=900, height=600, title="Flying arrows", side=100, color="#ff40ff"):
    game = MyGame(width, height, title, side, color)
    game.setup()
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()