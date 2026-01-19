""" Name: Юрий, Date: 03.01.2026, WhatYouDo: сделал механику стрелочек"""
# Name: Иван, Date: 09.01.2026, WhatYouDo: добавил функции stop и setup_attack, обновил пути к текстурам

import arcade
from pyglet.graphics import Batch


class AttackView(arcade.View):
    def __init__(self, main_scene_manager):
        super().__init__()
        self.main_scene_manager = main_scene_manager
        self.fight_box = main_scene_manager.fight_box

        self.mg_box = self.fight_box.mg_box
        self.mini_window = self.mg_box.mini_window

        arcade.set_background_color(arcade.color.BLACK)
        self.setup2()

    def setup(self):
        ...

    def setup2(self):
        self.arrows = [[0, 1, 2], [1, 2, 1], [2, 3, 1], [3, 4, 1], [2, 5, 4], [0, 4, 1]] # создаём или передаём массив стрелок
        ### Первое число в массиве стрелок направление 0-влево, 1-вверх, 2-вправо, 3-вниз
        # Второе число это номер цикла###
        self.cycle_time = 0.5 # создаём или передаём время цикла
        self.total_time = 0.0
        self.speed = 400
        self.count = 0
        self.time_stop = max(self.arrows, key=lambda x: x[1])[1] * self.cycle_time + 4 + (200 / self.speed)
        self.arrows_0 = set()
        self.arrows_1 = set()
        self.arrows_2 = set()
        self.arrows_3 = set()
        for index, tcycle, tarrow in self.arrows:
            if index == 0:
                self.arrows_0.add((tcycle * self.cycle_time + 2, tarrow))
            elif index == 1:
                self.arrows_1.add((tcycle * self.cycle_time + 2, tarrow))
            elif index == 2:
                self.arrows_2.add((tcycle * self.cycle_time + 2, tarrow))
            elif index == 3:
                self.arrows_3.add((tcycle * self.cycle_time + 2, tarrow))

        self.detect_sprite_0 = arcade.Sprite("FlyArrowsMehanic/detect_arrow0.png", scale=0.5)
        self.detect_sprite_1 = arcade.Sprite("FlyArrowsMehanic/detect_arrow1.png", scale=0.5)
        self.detect_sprite_2 = arcade.Sprite("FlyArrowsMehanic/detect_arrow2.png", scale=0.5)
        self.detect_sprite_3 = arcade.Sprite("FlyArrowsMehanic/detect_arrow3.png", scale=0.5)
        self.detect_sprite_0.center_x = self.mini_window.x + self.mini_window.width // 5
        self.detect_sprite_0.center_y = self.mini_window.y + self.mini_window.height - 100
        self.detect_sprite_1.center_x = self.mini_window.x + self.mini_window.width // 5 * 2
        self.detect_sprite_1.center_y = self.mini_window.y + self.mini_window.height - 100
        self.detect_sprite_2.center_x = self.mini_window.x + self.mini_window.width // 5 * 3
        self.detect_sprite_2.center_y = self.mini_window.y + self.mini_window.height - 100
        self.detect_sprite_3 .center_x = self.mini_window.x + self.mini_window.width // 5 * 4
        self.detect_sprite_3 .center_y = self.mini_window.y + self.mini_window.height - 100

        self.all_sprites = arcade.SpriteList()
        self.all_sprites.append(self.detect_sprite_0)
        self.all_sprites.append(self.detect_sprite_1)
        self.all_sprites.append(self.detect_sprite_2)
        self.all_sprites.append(self.detect_sprite_3)
        self.keys_pressed = set()

        self.all_arrow_sprites = arcade.SpriteList()
        self.keys_last_0 = None
        self.keys_last_1 = None
        self.keys_last_2 = None
        self.keys_last_3 = None

        self.long_arrow_0 = []
        self.long_arrow_1 = []
        self.long_arrow_2 = []
        self.long_arrow_3 = []

    def on_draw(self):
        """Этот метод отвечает за отрисовку содержимого окна"""
        self.clear()
        fb = self.fight_box

        self.all_arrow_sprites.draw()
        arcade.draw_lbwh_rectangle_filled(self.mini_window.x, 0, self.mini_window.width, self.mini_window.y,
                                          arcade.color.BLACK)
        arcade.draw_lbwh_rectangle_filled(self.mini_window.x, self.mini_window.height + 80, self.mini_window.width,
                                          self.height - self.mini_window.height + 60,
                                          arcade.color.BLACK)
        self.all_sprites.draw()

        self.all_arrow_sprites.draw()
        self.all_sprites.draw()

        self.mg_box.draw()

    def on_update(self, delta_time):
        """Этот метод отвечает за обновление логики игры (анимации, взаимодействия и т. д.)"""
        self.total_time += delta_time

        if self.total_time >= self.time_stop:
            self.stop()

        self.fly_arrows()
        self.fly_arrows_vid(delta_time)
        if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
            for i, tarrow in self.arrows_0:
                if i - 0.2 < self.keys_pressed_0 < i + 0.2 and tarrow <= 1:
                    self.detect_sprite_0.scale = 0.6
                    if i != self.keys_last_0:
                        self.count += 1
                        self.keys_last_0 = i
                    break
                elif (i - 0.2 < self.keys_pressed_0 < i + 0.2 and tarrow > 1 and
                      i + (tarrow - 1) * self.cycle_time + 0.2 > self.total_time):
                    self.detect_sprite_0.scale = 0.6
                    self.long_arrow_0 = [i, tarrow]
                    break
            else:
                self.detect_sprite_0.scale = 0.4
        elif self.long_arrow_0:
            if (self.long_arrow_0[0] + (self.long_arrow_0[1] - 1) * self.cycle_time - 0.2 < self.keys_released_0
                    < self.long_arrow_0[0] + (self.long_arrow_0[1] - 1) * self.cycle_time + 0.2):
                self.count += 1
            self.long_arrow_0 = []
        else:
            self.detect_sprite_0.scale = 0.5
        if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
            for i, tarrow in self.arrows_3:
                if i - 0.2 < self.keys_pressed_3 < i + 0.2 and tarrow <= 1:
                    self.detect_sprite_3.scale = 0.6
                    if i != self.keys_last_3:
                        self.count += 1
                        self.keys_last_3 = i
                    break
                elif (i - 0.2 < self.keys_pressed_3 < i + 0.2 and tarrow > 1 and
                          i + (tarrow - 1) * self.cycle_time + 0.2 > self.total_time):
                    self.detect_sprite_3.scale = 0.6
                    self.long_arrow_3 = [i, tarrow]
                    break
            else:
                self.detect_sprite_3.scale = 0.4
        elif self.long_arrow_3:
            if (self.long_arrow_3[0] + (self.long_arrow_3[1] - 1) * self.cycle_time - 0.2 < self.keys_released_3
                    < self.long_arrow_3[0] + (self.long_arrow_3[1] - 1) * self.cycle_time + 0.2):
                self.count += 1
            self.long_arrow_3 = []
        else:
            self.detect_sprite_3.scale = 0.5
        if arcade.key.UP in self.keys_pressed or arcade.key.W in self.keys_pressed:
            for i, tarrow in self.arrows_1:
                if i - 0.2 < self.keys_pressed_1 < i + 0.2 and tarrow <= 1:
                    self.detect_sprite_1.scale = 0.6
                    if i != self.keys_last_1:
                        self.count += 1
                        self.keys_last_1 = i
                    break
                elif (i - 0.2 < self.keys_pressed_1 < i + 0.2 and tarrow > 1 and
                          i + (tarrow - 1) * self.cycle_time + 0.2 > self.total_time):
                    self.detect_sprite_1.scale = 0.6
                    self.long_arrow_1 = [i, tarrow]
                    break
            else:
                self.detect_sprite_1.scale = 0.4
        elif self.long_arrow_1:
            if (self.long_arrow_1[0] + (self.long_arrow_1[1] - 1) * self.cycle_time - 0.2 < self.keys_released_1
                    < self.long_arrow_1[0] + (self.long_arrow_1[1] - 1) * self.cycle_time + 0.2):
                self.count += 1
            self.long_arrow_1 = []
        else:
            self.detect_sprite_1.scale = 0.5
        if arcade.key.DOWN in self.keys_pressed or arcade.key.S in self.keys_pressed:
            for i, tarrow in self.arrows_2:
                if i - 0.2 < self.keys_pressed_2 < i + 0.2 and tarrow <= 1:
                    self.detect_sprite_2.scale = 0.6
                    if i != self.keys_last_2:
                        self.count += 1
                        self.keys_last_2 = i
                    break
                elif (i - 0.2 < self.keys_pressed_2 < i + 0.2 and tarrow > 1 and
                          i + (tarrow - 1) * self.cycle_time + 0.2 > self.total_time):
                    self.detect_sprite_2.scale = 0.6
                    self.long_arrow_2 = [i, tarrow]
                    break
            else:
                self.detect_sprite_2.scale = 0.4
        elif self.long_arrow_2:
            if (self.long_arrow_2[0] + (self.long_arrow_2[1] - 1) * self.cycle_time - 0.2 < self.keys_released_2
                    < self.long_arrow_2[0] + (self.long_arrow_2[1] - 1) * self.cycle_time + 0.2):
                self.count += 1
            self.long_arrow_2 = []
        else:
            self.detect_sprite_2.scale = 0.5

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            if arcade.key.LEFT == key or arcade.key.A == key:
                self.keys_released_0 = self.total_time
            elif arcade.key.UP == key or arcade.key.W == key:
                self.keys_released_1 = self.total_time
            elif arcade.key.DOWN == key or arcade.key.S == key:
                self.keys_released_2 = self.total_time
            elif arcade.key.RIGHT == key or arcade.key.D == key:
                self.keys_released_3 = self.total_time
            self.keys_pressed.remove(key)

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
        dct_index = {
            0: "FlyArrowsMehanic/arrow0.png",
            1: "FlyArrowsMehanic/arrow1.png",
            2: "FlyArrowsMehanic/arrow2.png",
            3: "FlyArrowsMehanic/arrow3.png"
        }

        for i, item in enumerate(self.arrows):
            index, tcycle, tarrow = item
            if self.total_time - 2 >= tcycle * self.cycle_time - (400/self.speed) and tarrow <= 1:

                player_sprite = arcade.Sprite(dct_index[index], scale=0.5)
                if index == 0:
                    player_sprite.center_x = self.mini_window.x + self.mini_window.width // 5
                    player_sprite.center_y = self.mini_window.y + self.mini_window.height - 500
                elif index == 1:
                    player_sprite.center_x = self.mini_window.x + self.mini_window.width // 5 * 2
                    player_sprite.center_y = self.mini_window.y + self.mini_window.height - 500
                elif index == 2:
                    player_sprite.center_x = self.mini_window.x + self.mini_window.width // 5 * 3
                    player_sprite.center_y = self.mini_window.y + self.mini_window.height - 500
                elif index == 3:
                    player_sprite.center_x = self.mini_window.x + self.mini_window.width // 5 * 4
                    player_sprite.center_y = self.mini_window.y + self.mini_window.height - 500
                self.all_arrow_sprites.append(player_sprite)
                del self.arrows[i]
            elif self.total_time - 2 >= tcycle * self.cycle_time - (400/self.speed) and tarrow > 1:

                player_sprite = arcade.Sprite(dct_index[index], scale=0.5)
                if index == 0:
                    player_sprite.center_x = self.mini_window.x + self.mini_window.width // 5
                    player_sprite.center_y = self.mini_window.y + self.mini_window.height - 500
                    dop_sprite = arcade.Sprite("FlyArrowsMehanic/ArrowAddEnd.png", scale=0.5)
                    dop_sprite.center_x = self.mini_window.x + self.mini_window.width // 5
                    dop_sprite.center_y = self.mini_window.y + self.mini_window.height - 500 - (tarrow - 1) * self.cycle_time * self.speed
                    self.all_arrow_sprites.append(dop_sprite)
                    for j in range(int((self.cycle_time * self.speed / 20) * (tarrow - 1))):
                        dop_sprite = arcade.Sprite("FlyArrowsMehanic/ArrowAdd.png", scale=0.5)
                        dop_sprite.center_x = self.mini_window.x + self.mini_window.width // 5
                        dop_sprite.center_y = self.mini_window.y + self.mini_window.height - 500 - ((j + 1) * 20)
                        self.all_arrow_sprites.append(dop_sprite)
                elif index == 1:
                    player_sprite.center_x = self.mini_window.x + self.mini_window.width // 5 * 2
                    player_sprite.center_y = self.mini_window.y + self.mini_window.height - 500
                    dop_sprite = arcade.Sprite("FlyArrowsMehanic/ArrowAddEnd.png", scale=0.5)
                    dop_sprite.center_x = self.mini_window.x + self.mini_window.width // 5 * 2
                    dop_sprite.center_y = self.mini_window.y + self.mini_window.height - 500 - (tarrow - 1) * self.cycle_time * self.speed
                    self.all_arrow_sprites.append(dop_sprite)
                    for j in range(int((self.cycle_time * self.speed / 20) * (tarrow - 1))):
                        dop_sprite = arcade.Sprite("FlyArrowsMehanic/ArrowAdd.png", scale=0.5)
                        dop_sprite.center_x = self.mini_window.x + self.mini_window.width // 5 * 2
                        dop_sprite.center_y = self.mini_window.y + self.mini_window.height - 500 - ((j + 1) * 20)
                        self.all_arrow_sprites.append(dop_sprite)
                elif index == 2:
                    player_sprite.center_x = self.mini_window.x + self.mini_window.width // 5 * 3
                    player_sprite.center_y = self.mini_window.y + self.mini_window.height - 500
                    dop_sprite = arcade.Sprite("FlyArrowsMehanic/ArrowAddEnd.png", scale=0.5)
                    dop_sprite.center_x = self.mini_window.x + self.mini_window.width // 5 * 3
                    dop_sprite.center_y = self.mini_window.y + self.mini_window.height - 500 - (tarrow - 1) * self.cycle_time * self.speed
                    self.all_arrow_sprites.append(dop_sprite)
                    for j in range(int((self.cycle_time * self.speed / 20) * (tarrow - 1))):
                        dop_sprite = arcade.Sprite("FlyArrowsMehanic/ArrowAdd.png", scale=0.5)
                        dop_sprite.center_x = self.mini_window.x + self.mini_window.width // 5 * 3
                        dop_sprite.center_y = self.mini_window.y + self.mini_window.height - 500 - ((j + 1) * 20)
                        self.all_arrow_sprites.append(dop_sprite)
                elif index == 3:
                    player_sprite.center_x = self.mini_window.x + self.mini_window.width // 5 * 4
                    player_sprite.center_y = self.mini_window.y + self.mini_window.height - 500
                    dop_sprite = arcade.Sprite("FlyArrowsMehanic/ArrowAddEnd.png", scale=0.5)
                    dop_sprite.center_x = self.mini_window.x + self.mini_window.width // 5 * 4
                    dop_sprite.center_y = self.mini_window.y + self.mini_window.height - 500 - (tarrow - 1) * self.cycle_time * self.speed
                    self.all_arrow_sprites.append(dop_sprite)
                    for j in range(int((self.cycle_time * self.speed / 20) * (tarrow - 1))):
                        dop_sprite = arcade.Sprite("FlyArrowsMehanic/ArrowAdd.png", scale=0.5)
                        dop_sprite.center_x = self.mini_window.x + self.mini_window.width // 5 * 4
                        dop_sprite.center_y = self.mini_window.y + self.mini_window.height - 500 - ((j + 1) * 20)
                        self.all_arrow_sprites.append(dop_sprite)
                self.all_arrow_sprites.append(player_sprite)
                del self.arrows[i]

    def fly_arrows_vid(self, delta_time):
        for i, arrow in enumerate(self.all_arrow_sprites):
            arrow.center_y += self.speed * delta_time
            if arrow.center_y > self.mini_window.height + 100:
                self.all_arrow_sprites.pop(i)

    # Функция для выхода из мини-боя
    def stop(self):
        self.main_scene_manager.next_scene()


# Функция для запуска мини-боёвки атаки
def setup_attack(main_scene_manager, *settings):
    attack_view = AttackView(main_scene_manager)
    main_scene_manager.window.show_view(attack_view)
