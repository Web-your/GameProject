""" Name: Максим | Date: 27.01.2026 | WhatYouDo: очинил расположение палочек(написав 6 символов ._.) """
# Name: Иван, Date: 08.01.2026, WhatYouDo: Добавил функцию setup_heal для запуска мини-боя лечения

import arcade
import random
import sys
import os

'''Константы'''
# Настройка элементов
STICK_WIDTH = 30
STICK_HEIGHT = 80
STICK_SPEED = 3
JUMP_HEIGHT = 100

FIELD_WIDTH = 100
FIELD_HEIGHT = 119

BACKGROUND_WIDTH = 750
BACKGROUND_HEIGHT = 120


# Палочки
class HealActThingy(arcade.Sprite):
    def __init__(self, view, x_offset=0, from_right=False, is_trick=False, is_jumper=False):
        super().__init__()

        self.is_trick = is_trick
        self.is_jumper = is_jumper
        self.is_jumping = False
        self.has_jumped_over_field = False
        self.jump_progress = 0
        self.jump_direction = 1
        self.original_y = view.center_y + 120
        self.field_center_x = view.center_x

        # Определяем путь к текстурам относительно текущего файла
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Загрузка текстур для прыгающих палочек
        if is_jumper:
            texture_path = os.path.join(current_dir, "healActMoveThingy.png")
            try:
                self.texture = arcade.load_texture(texture_path)
            except:
                self.texture = arcade.make_soft_square_texture(STICK_WIDTH, arcade.color.YELLOW,
                                                               outer_alpha=255)
        # Загрузка текстур для фальшивых палочек
        elif is_trick:
            texture_path = os.path.join(current_dir, "healActTrickThingy.png")
            try:
                self.texture = arcade.load_texture(texture_path)
            except:
                self.texture = arcade.make_soft_square_texture(STICK_WIDTH, arcade.color.RED,
                                                               outer_alpha=255)
        # Загрузка текстур для обычных палочек
        else:
            texture_path = os.path.join(current_dir, "healActThingy.png")
            try:
                self.texture = arcade.load_texture(texture_path)
            except:
                self.texture = arcade.make_soft_square_texture(STICK_WIDTH, arcade.color.WHITE,
                                                               outer_alpha=255)

        self.center_y = self.original_y

        # Настройка стороны
        if from_right:
            self.center_x = view.center_x + STICK_WIDTH + x_offset
            self.change_x = -STICK_SPEED
        else:
            self.center_x = -STICK_WIDTH - x_offset
            self.change_x = STICK_SPEED

        self.active = True
        self.was_hit = False
        self.was_missed = False
        self.from_right = from_right
        self.original_from_right = from_right

    def update(self, delta_time: float = 1 / 60):
        if self.is_jumper and not self.has_jumped_over_field:
            field_left_edge = self.field_center_x - (FIELD_WIDTH / 2)
            field_right_edge = self.field_center_x + (FIELD_WIDTH / 2)
            if not self.original_from_right:
                if self.center_x >= field_left_edge - 20 and not self.is_jumping:
                    self.start_jump()
            else:
                if self.center_x <= field_right_edge + 20 and not self.is_jumping:
                    self.start_jump()
        if self.is_jumping:
            self.update_jump(delta_time)
        else:
            self.center_x += self.change_x

    '''2 класса на реализацию прыжка'''

    def start_jump(self):
        if not self.is_jumping and not self.has_jumped_over_field:
            self.is_jumping = True
            self.jump_progress = 0

            if not self.original_from_right:
                self.jump_direction = -1
            else:
                self.jump_direction = 1

    def update_jump(self, delta_time):
        if self.is_jumping:
            jump_speed = delta_time * 4

            self.jump_progress += jump_speed

            if self.jump_progress >= 1:
                self.jump_progress = 1
                self.is_jumping = False
                self.has_jumped_over_field = True
                self.center_y = self.original_y

                self.change_x = -self.change_x
                self.from_right = not self.original_from_right

                self.center_x += self.change_x
            else:
                t = self.jump_progress
                if t < 0.5:
                    progress = 2 * t
                else:
                    progress = 2 * (1 - t)
                current_height = JUMP_HEIGHT * progress

                if self.jump_direction > 0:
                    self.center_y = self.original_y + current_height
                else:
                    self.center_y = self.original_y - current_height
                self.center_x += self.change_x * 4


class HealTestView(arcade.View):
    """Вью для мини-игры Heal Test"""

    def __init__(self, main_scene_manager, target_hero_index=0, parent_view=None):
        super().__init__()
        self.main_scene_manager = main_scene_manager
        self.f_box = main_scene_manager.fb
        self.mg_box = self.f_box.mg_box
        self.mini_window = self.mg_box.mini_window

        # Параметры мини-окна
        self.mw_left = self.mini_window.left
        self.mw_right = self.mini_window.right
        self.mw_top = self.mini_window.top
        self.mw_bottom = self.mini_window.bottom

        self.mw_x = self.mini_window.x
        self.mw_y = self.mini_window.y

        self.mw_width = self.mini_window.width
        self.mw_height = self.mini_window.height

        self.mw_center_x = self.mini_window.center_x
        self.mw_center_y = self.mini_window.center_y

        self.stick_list = None
        self.field_list = None
        self.background_list = None

        # звуки
        self.hit_sound = None
        self.miss_sound = None
        self.trick_sound = None

        self.background_right_edge = 0
        self.background_left_edge = 0

        # Таймер для закрытия окна
        self.close_timer = 0
        self.should_close = False

        # Колбэк для возврата в основную игру
        self.on_complete_callback = main_scene_manager.next_scene

        # Какого героя лечим
        self.target_hero_index = target_hero_index

        # Родительское вью для возврата
        self.parent_view = parent_view

        # Результаты игры
        self.success_count = 0
        self.total_sticks = 0

        self.setup()

    def setup(self):
        """Настройка игры"""
        self.stick_list = arcade.SpriteList()
        self.field_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()

        self.load_sounds()
        self.load_background()
        self.load_interaction_field()

        self.close_timer = 0
        self.should_close = False
        self.success_count = 0
        self.total_sticks = 0

        # Начальный спавн - только 5 обычных палочек слева
        self.spawn_sticks(from_right=False, is_trick=False, is_jumper=False, count=5)

    # Загрузка звуков
    def load_sounds(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        try:
            sound_path = os.path.join(current_dir, "healActHit.wav")
            self.hit_sound = arcade.load_sound(sound_path)
        except:
            # Используем стандартные звуки arcade
            self.hit_sound = arcade.Sound(":resources:sounds/hit3.wav")

        try:
            sound_path = os.path.join(current_dir, "healActMiss.wav")
            self.miss_sound = arcade.load_sound(sound_path)
        except:
            self.miss_sound = arcade.Sound(":resources:sounds/error4.wav")

        try:
            sound_path = os.path.join(current_dir, "healActTrick.wav")
            self.trick_sound = arcade.load_sound(sound_path)
        except:
            self.trick_sound = arcade.Sound(":resources:sounds/error2.wav")

    # Фон
    def load_background(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        texture_path = os.path.join(current_dir, "healActField.png")

        try:
            background = arcade.Sprite(texture_path)
            background.width = BACKGROUND_WIDTH
            background.height = BACKGROUND_HEIGHT
            background.center_x = self.mw_center_x
            background.center_y = self.mw_center_y

            self.background_left_edge = background.center_x - (background.width / 2)
            self.background_right_edge = background.center_x + (background.width / 2)

            self.background_list.append(background)
        except:
            self.background_left_edge = 0
            self.background_right_edge = self.mw_width

    # Центральная часть
    def load_interaction_field(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        texture_path = os.path.join(current_dir, "healActButton.png")

        try:
            field_sprite = arcade.Sprite(texture_path)
        except:
            field_sprite = arcade.SpriteSolidColor(FIELD_WIDTH, FIELD_HEIGHT,
                                                   arcade.color.GREEN)

        scale_w = FIELD_WIDTH / field_sprite.width
        scale_h = FIELD_HEIGHT / field_sprite.height
        field_sprite.scale = min(scale_w, scale_h)

        field_sprite.center_x = self.mw_center_x
        field_sprite.center_y = self.mw_center_y

        self.field_list.append(field_sprite)

    # Создание палок с одной стороны
    def spawn_sticks(self, from_right=False, is_trick=False, is_jumper=False, count=5):
        x_offset = 0

        for i in range(count):
            stick = HealActThingy(self, x_offset, from_right, is_trick, is_jumper)

            min_distance = 10
            max_distance = 100
            distance = random.randint(min_distance, max_distance)

            x_offset += distance + STICK_WIDTH

            self.stick_list.append(stick)
            self.total_sticks += 1

        if from_right:
            self.stick_list.sort(key=lambda s: s.center_x, reverse=True)
        else:
            self.stick_list.sort(key=lambda s: s.center_x)

    def on_draw(self):
        # Очищаем экран черным цветом
        self.clear(arcade.color.BLACK)

        # Позиция мини-игры на экране (по центру)
        game_x = self.mw_center_x
        game_y = self.mw_center_y

        # Рисуем мини-игру
        self.background_list.draw()
        self.field_list.draw()
        self.stick_list.draw()

        self.mg_box.draw()

    # Удаление лишних палок
    def clean_inactive_sticks(self):
        sticks_to_remove = []
        for stick in self.stick_list:
            if not stick.active:
                sticks_to_remove.append(stick)
        for stick in sticks_to_remove:
            self.stick_list.remove(stick)

    def check_game_completion(self):
        """Проверка, все ли палочки обработаны"""
        if len(self.stick_list) == 0 and not self.should_close:
            self.should_close = True
            self.close_timer = 1.0  # 1 секунда до закрытия

    def close_game(self):
        """Завершение мини-игры и возврат в основную игру"""
        # Вычисляем эффективность лечения
        if self.total_sticks > 0:
            success_rate = self.success_count / self.total_sticks
        else:
            success_rate = 0

        # Вызываем колбэк с результатами
        if self.on_complete_callback:
            self.on_complete_callback(self.target_hero_index, success_rate, self.success_count)

    def on_update(self, delta_time):
        # Если таймер закрытия активен
        if self.should_close:
            self.close_timer -= delta_time
            if self.close_timer <= 0:
                self.close_game()
            return

        # Обновление палочек
        for stick in self.stick_list:
            if stick.active:
                stick.update(delta_time)

        # Проверка выхода за границы фона
        for stick in self.stick_list:
            if stick.active and not stick.was_hit and not stick.was_missed:
                if stick.from_right:
                    stick_left_edge = stick.center_x - (stick.width / 2)
                    if stick_left_edge < self.background_left_edge:
                        if stick.is_trick:
                            stick.was_hit = True
                            self.success_count += 1
                            arcade.play_sound(self.hit_sound)
                        else:
                            stick.was_missed = True
                            arcade.play_sound(self.miss_sound)
                        stick.active = False
                else:
                    stick_right_edge = stick.center_x + (stick.width / 2)
                    if stick_right_edge > self.background_right_edge:
                        if stick.is_trick:
                            stick.was_hit = True
                            self.success_count += 1
                            arcade.play_sound(self.hit_sound)
                        else:
                            stick.was_missed = True
                            arcade.play_sound(self.miss_sound)
                        stick.active = False

        self.clean_inactive_sticks()

        # Удаление палочек за пределами экрана
        for stick in self.stick_list:
            if (stick.from_right and stick.center_x < -STICK_WIDTH) or \
                    (not stick.from_right and stick.center_x > self.mw_width + STICK_WIDTH):
                stick.active = False

        # Проверка завершения игры
        self.check_game_completion()

    # Обработка нажатия
    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE and not self.should_close:
            for stick in self.stick_list:
                if stick.active and not stick.was_hit and not stick.was_missed:
                    if stick.is_jumper and stick.is_jumping:
                        continue

                    if len(self.field_list) > 0:
                        field = self.field_list[0]
                        if field.collides_with_sprite(stick):
                            if stick.is_trick:  # =)
                                stick.was_hit = True
                                arcade.play_sound(self.trick_sound)
                            else:
                                stick.was_hit = True
                                self.success_count += 1
                                arcade.play_sound(self.hit_sound)
                            stick.active = False
                            break


def setup_heal(main_scene_manager, *settings):
    heal_view = HealTestView(main_scene_manager)
    main_scene_manager.window.show_view(heal_view)