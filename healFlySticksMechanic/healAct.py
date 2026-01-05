""" Name: Максим | Date: 05.01.2026 | WhatYouDo: Сделал механику палочек """

# Импорты
import arcade
import random

'''Константы'''
# Настройки окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 250
SCREEN_TITLE = "Heal test"

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
class healActThingy(arcade.Sprite):
    def __init__(self, x_offset=0, from_right=False, is_trick=False, is_jumper=False):
        super().__init__()

        self.is_trick = is_trick
        self.is_jumper = is_jumper
        self.is_jumping = False
        self.has_jumped_over_field = False
        self.jump_progress = 0
        self.jump_direction = 1
        self.original_y = SCREEN_HEIGHT // 2
        self.field_center_x = SCREEN_WIDTH // 2

        # Загрузка текстур для прыгающих палочек
        if is_jumper:
            try:
                self.texture = arcade.load_texture("healActMoveThingy.png")
            except:
                self.texture = arcade.make_soft_square_texture(STICK_WIDTH, arcade.color.YELLOW,
                                                               outer_alpha=255)
        # Закрузка текстур для фальшивых палочек
        elif is_trick:
            try:
                self.texture = arcade.load_texture("healActTrickThingy.png")
            except:
                self.texture = arcade.make_soft_square_texture(STICK_WIDTH, arcade.color.RED,
                                                               outer_alpha=255)
        # Загрузка текстур для обычных палочек
        else:
            try:
                self.texture = arcade.load_texture("healActThingy.png")
            except:
                self.texture = arcade.make_soft_square_texture(STICK_WIDTH, arcade.color.WHITE,
                                                               outer_alpha=255)

        self.center_y = self.original_y

        # Настройка стороны
        if from_right:
            self.center_x = SCREEN_WIDTH + STICK_WIDTH + x_offset
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


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.stick_list = None
        self.field_list = None
        self.background_list = None

        # звуки
        self.hit_sound = None
        self.miss_sound = None
        self.trick_sound = None

        # Подсчёт счёта
        self.total_sticks = 0
        self.hit_count = 0
        self.miss_count = 0
        self.trick_count = 0

        self.background_right_edge = 0
        self.background_left_edge = 0

        self.load_sounds()
        self.setup()

    # Загрузка звуков
    def load_sounds(self):
        try:
            self.hit_sound = arcade.load_sound("healActHit.wav")
        except:
            self.hit_sound = arcade.Sound(arcade.resources.sound_laser2)

        try:
            self.miss_sound = arcade.load_sound("healActMiss.wav")
        except:
            self.miss_sound = arcade.Sound(arcade.resources.sound_lose1)

        try:
            self.trick_sound = arcade.load_sound("healActTrick.wav")
        except:
            self.trick_sound = arcade.Sound(arcade.resources.sound_error2)

    def setup(self):
        self.stick_list = arcade.SpriteList()
        self.field_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.load_background()
        self.load_interaction_field()
        self.total_sticks = 0
        self.hit_count = 0
        self.miss_count = 0
        self.trick_count = 0
        self.spawn_five_sticks(from_right=False)

    # Фон
    def load_background(self):
        try:
            background = arcade.Sprite("healActField.png")
            background.width = BACKGROUND_WIDTH
            background.height = BACKGROUND_HEIGHT
            background.center_x = SCREEN_WIDTH // 2
            background.center_y = SCREEN_HEIGHT // 2

            self.background_left_edge = background.center_x - (background.width / 2)
            self.background_right_edge = background.center_x + (background.width / 2)

            self.background_list.append(background)
        except:
            self.background_left_edge = 0
            self.background_right_edge = SCREEN_WIDTH

    # Центральная часть
    def load_interaction_field(self):
        try:
            field_sprite = arcade.Sprite("healActButton.png")
        except:
            field_sprite = arcade.SpriteSolidColor(FIELD_WIDTH, FIELD_HEIGHT,
                                                   arcade.color.GREEN)

        scale_w = FIELD_WIDTH / field_sprite.width
        scale_h = FIELD_HEIGHT / field_sprite.height
        field_sprite.scale = min(scale_w, scale_h)

        field_sprite.center_x = SCREEN_WIDTH // 2
        field_sprite.center_y = SCREEN_HEIGHT // 2

        self.field_list.append(field_sprite)

    # Создание палок с одной стороны
    def spawn_sticks(self, from_right=False, with_tricks=False, with_jumpers=False):
        x_offset = 0

        for i in range(5):
            if with_jumpers:
                is_jumper = random.choice([True, False])
                is_trick = False if is_jumper else (with_tricks and random.choice([True, False]))
            else:
                is_jumper = False
                is_trick = with_tricks and random.choice([True, False])

            stick = healActThingy(x_offset, from_right, is_trick, is_jumper)

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

    # Создание палок с разных сторон
    def spawn_mixed_sticks(self, with_tricks=False, with_jumpers=False):
        for i in range(5):
            from_right = random.choice([True, False])

            if with_jumpers:
                is_jumper = random.choice([True, False])
                is_trick = False if is_jumper else (with_tricks and random.choice([True, False]))
            else:
                is_jumper = False
                is_trick = with_tricks and random.choice([True, False])

            stick = healActThingy(i * 50, from_right, is_trick, is_jumper)

            self.stick_list.append(stick)
            self.total_sticks += 1

    def on_draw(self):
        self.clear(arcade.color.BLACK)
        self.background_list.draw()
        self.field_list.draw()
        self.stick_list.draw()

    # Удаление лишних палок
    def clean_inactive_sticks(self):
        sticks_to_remove = []
        for stick in self.stick_list:
            if not stick.active:
                sticks_to_remove.append(stick)
        for stick in sticks_to_remove:
            self.stick_list.remove(stick)

    def on_update(self, delta_time):
        for stick in self.stick_list:
            if stick.active:
                stick.update(delta_time)

        for stick in self.stick_list:
            if stick.active and not stick.was_hit and not stick.was_missed:
                if stick.from_right:
                    stick_left_edge = stick.center_x - (stick.width / 2)
                    if stick_left_edge < self.background_left_edge:
                        if stick.is_trick:
                            stick.was_hit = True
                            self.hit_count += 1
                            arcade.play_sound(self.hit_sound)
                        else:
                            stick.was_missed = True
                            self.miss_count += 1
                            arcade.play_sound(self.miss_sound)
                        stick.active = False
                else:
                    stick_right_edge = stick.center_x + (stick.width / 2)
                    if stick_right_edge > self.background_right_edge:
                        if stick.is_trick:
                            stick.was_hit = True
                            self.hit_count += 1
                            arcade.play_sound(self.hit_sound)
                        else:
                            stick.was_missed = True
                            self.miss_count += 1
                            arcade.play_sound(self.miss_sound)
                        stick.active = False

        self.clean_inactive_sticks()

        for stick in self.stick_list:
            if (stick.from_right and stick.center_x < -STICK_WIDTH) or \
                    (not stick.from_right and stick.center_x > SCREEN_WIDTH + STICK_WIDTH):
                stick.active = False

    # Обработка нажатия
    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            for stick in self.stick_list:
                if stick.active and not stick.was_hit and not stick.was_missed:
                    if stick.is_jumper and stick.is_jumping:
                        continue

                    if len(self.field_list) > 0:
                        field = self.field_list[0]
                        if field.collides_with_sprite(stick):
                            if stick.is_trick:  # =)
                                stick.was_hit = True
                                self.trick_count += 1
                                arcade.play_sound(self.trick_sound)
                            else:
                                stick.was_hit = True
                                self.hit_count += 1
                                arcade.play_sound(self.hit_sound)
                            stick.active = False
                            break


'''Тут идёт блок main и т.п.'''
def main():
    window = Game()
    arcade.run()


if __name__ == "__main__":
    main()