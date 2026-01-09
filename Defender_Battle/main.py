# Name: Иван, Date: 05.01.2026, WhatYouDo: механика боя защитника (передвижение/увороты)
# Name: Иван, Date: 06.01.2026, WhatYouDo: добавил класс механик, кристаллы, коллизию, пульсацию от урона
# Name: Иван, Date: 07.01.2026, WhatYouDo: улучшил текстуры, коллизию, механики, добавил звуки, тряску, текст счёта

import arcade
from pyglet.graphics import Batch
import random
import math



# Таймер (Динамический) - обновляет волны и окна --------------------------------------------------------------------->
class SceneManager:
    def __init__(self, defender):
        self.df = defender

        # Сцены - реализуют механику каждой волны, переключают на нужное окно
        start_scene = StartScene(defender)
        wave_scene = WaveScene(defender)
        finish_scene = FinishScene(defender)

        # Добавляем сцены в очередь
        self.timeline = [start_scene, wave_scene, finish_scene]
        self.curr_index = 0

        # Вызываем следующую сцену
        self.next()

    def next(self, delta_time=0):
        # Получаем сцену и обновляем индекс в очереди
        if self.curr_index >= len(self.timeline):
            # В конце выходим из мини-игры
            self.back()
        else:
            scene = self.timeline[self.curr_index]
            self.curr_index += 1
            scene.setup() # Запускаем текущую сцену

    # Выходим из боёвки
    def back(self):
        # Запускаем следующий бой в главном менеджере сцен
        self.df.main_scene_manager.next_scene()



# Сцены (динамические) --------------------------------------------------------------------->

# Обратный отсчёт
class StartScene:
    def __init__(self, defender):
        self.df = defender
        self.tick = 1 # Время между обновлениями

    def setup(self):
        self.df.window.show_view(self.df.start_view) # Включаем нужное окно
        self.next() # Пошагово обновляем сцену

    def next(self, delta_time=0):
        countdown = self.df.countdown

        arcade.unschedule(self.next) # Обязательно удаляем таймер
        if countdown.curr_index >= len(countdown.textures):
            countdown.curr_index = 0
            # По завершении запускаем следующую сцену в таймере
            self.df.scene_manager.next()
        else:
            # Сменяем текстуру обратного отсчёта на следующую
            countdown.texture = countdown.textures[countdown.curr_index]
            countdown.curr_index += 1
            arcade.schedule(self.next, self.tick) # Выставляем время для следующего обновления


# Волна 1 - 3 механики: воспламеняющаяся доска, пули, кристаллы атаки
class WaveScene:
    def __init__(self, defender):
        self.df = defender

        # Музыка в течении боя
        self.main_music = arcade.load_sound("Defender_Battle/Static/Sounds/main_music.mp3")
        self.player_music = None

        # Выбираем механики для волны
        self.fire_board_mech = FireBoardMechanic(self, self.df)
        self.bullet_mech = BulletMechanic(self.df)
        self.cristal_mech = CristalMechanic(self.df)

        self.wave_time = 20 # Время волны
        self.pause1_time = 1.5 # Время после последнего воспламенения, когда активны спрайты
        self.pause2_time = 1.5 # Время до финиша, когда спрайты не активны

    # Запускаем механики
    def setup(self):
        self.df.window.show_view(self.df.wave_view)
        self.df.is_wave_active = True
        self.fire_board_mech.setup()
        self.bullet_mech.setup()
        self.cristal_mech.setup()
        self.player_music = arcade.play_sound(self.main_music, volume=0.25)
        arcade.schedule(self.stop, self.wave_time)

    # Останавливаем механики
    def stop(self, delta_time=0):
        arcade.unschedule(self.stop)
        self.bullet_mech.stop()
        self.cristal_mech.stop()
        self.fire_board_mech.stop()

    # Останавливаем спрайты, когда завершится последнее воспламенение
    def stop_next(self, delta_time=0):
        arcade.unschedule(self.stop_next)
        self.df.is_wave_active = False
        arcade.schedule(self.next_scene, self.pause2_time)

    def next_scene(self, delta_time=0):
        arcade.unschedule(self.next_scene)
        arcade.stop_sound(self.player_music)
        self.df.scene_manager.next()


# Сцена в конце боя
class FinishScene:
    def __init__(self, defender):
        self.df = defender
        self.finish_time = 1 # Время сцены

    def setup(self):
        self.df.window.show_view(self.df.finish_view) # Включаем нужное окно
        finish_sound = arcade.load_sound("Defender_Battle/Static/Sounds/finish_sound.wav")
        arcade.play_sound(finish_sound)
        arcade.schedule(self.next_scene, self.finish_time)

    def next_scene(self, delta_time=0):
        arcade.unschedule(self.next_scene)
        self.df.scene_manager.next()



#Реализация основных механик (динамические) --------------------------------------------------------------------->

# Воспламенение плитки (3 состояния - обычное, предупреждение, огонь)
class FireBoardMechanic:
    def __init__(self, wave_scene, defender):
        self.df = defender
        self.wave_scene = wave_scene

        self.board = defender.board
        self.player = defender.player
        self.background = defender.background

        # Активна ли данная механика
        self.is_active_mech = False

        # Время между состояниями
        self.pause_time = 0.5
        self.danger_time = 2
        self.fire_time = 1

        # Вероятность воспламенения клетки
        self.active_prob = 0.3

        # Клетки, которые будут воспламеняться
        self.active_cells = defender.active_cells

    def setup(self):
        self.is_active_mech = True
        self.next()

    def next(self, delta_time=0):
        arcade.unschedule(self.next)

        # Увеличиваем вероятность активации клетки
        self.active_prob += 0.025

        # Возвращаемся к обычному состоянию
        for cell in self.active_cells:
            cell.texture = arcade.load_texture("Defender_Battle/Static/Cell_Textures/base.png")
            cell.scale = cell.cell_size / 100

        self.df.is_fire = False
        self.active_cells.clear()

        # При активации механики
        if self.is_active_mech:

            # Рандомно выбираем клетки для воспламенения
            for cell in self.board.cells_list:
                if random.random() <= self.active_prob:
                    self.active_cells.append(cell)

            # Выставляем время для следующего состояния - другая функция
            arcade.schedule(self.change_for_danger, self.pause_time)

        # В конце останавливаем другие спрайты
        else:
            arcade.schedule(self.wave_scene.stop_next, self.wave_scene.pause1_time)

    # Просто сменяем текстуру на предупреждение
    def change_for_danger(self, delta_time=0):
        arcade.unschedule(self.change_for_danger)
        for cell in self.active_cells:
            cell.texture = arcade.load_texture("Defender_Battle/Static/Cell_Textures/danger.png")
            cell.scale = cell.cell_size / 100
        arcade.schedule(self.change_for_fire, self.danger_time)

    # Сменяем текстуру на огонь и включаем режим воспламенения
    def change_for_fire(self, delta_time=0):
        arcade.unschedule(self.change_for_fire)
        for cell in self.active_cells:
            cell.texture = arcade.load_texture("Defender_Battle/Static/Cell_Textures/fire.png")
            cell.scale = cell.cell_size / 100
        self.df.is_fire = True

        # Эффекты звука и тряски
        fire_sound = arcade.load_sound("Defender_Battle/Static/Sounds/fire_sound.wav")
        arcade.play_sound(fire_sound, 1.5)
        self.df.camera_shake.start()

        arcade.schedule(self.next, self.fire_time)

    def stop(self):
        self.is_active_mech = False


# Полёт пули
class BulletMechanic:
    def __init__(self, defender):
        self.df = defender

        self.board = defender.board
        self.player = defender.player

        self.is_active = False # Активна ли механика
        self.tick = 1.2 # Время между спавном новой пули

    def setup(self):
        self.is_active = True
        self.next()

    def next(self, delta_time=0):
        board = self.board
        arcade.unschedule(self.next)

        if self.is_active:
            top = board.indent_y + board.height * board.cell_size - 20
            bottom = board.indent_y + 20
            bullet = Bullet(self.df.width + 50, random.randrange(bottom, top), self.df)
            self.df.bullet_list.append(bullet)
            arcade.schedule(self.next, self.tick)

    def stop(self):
        self.is_active = False


class CristalMechanic:
    def __init__(self, defender):
        self.df = defender

        self.player = defender.player
        self.board = defender.board

        self.is_active = False
        self.tick = 6  # Время между спавном кристаллов

        self.free_cells = arcade.SpriteList()# Свободные (Не занятые кристаллом) клетки - сначала все
        for cell in self.board.cells_list:
            self.free_cells.append(cell)

    def setup(self):
        self.is_active = True
        self.next()

    def next(self, delta_time=0):
        arcade.unschedule(self.next)

        if self.is_active:
            cell = random.choice(self.free_cells)
            self.free_cells.remove(cell)
            cristal = AttackCristal(cell.center_x, cell.center_y, self.free_cells, cell, self.df)
            self.df.cristal_list.append(cristal)
            arcade.schedule(self.next, self.tick)

    def stop(self):
        self.is_active = False



# Окна (динамические) --------------------------------------------------------------------->
# Здесь прописываем, какие объекты отрисовывать и обновлять
class StartView(arcade.View):
    def __init__(self, defender):
        super().__init__()
        self.df = defender

    def setup(self):
        ...

    def on_show(self):
        ...

    def on_update(self, delta_time):
        ...

    def on_draw(self):
        self.clear()
        df = self.df

        df.background.draw()
        df.board.draw()
        df.countdown_list.draw()


class WaveView(arcade.View):
    def __init__(self, defender):
        super().__init__()
        self.df = defender

        self.keys_pressed = set()

    def setup(self):
        ...

    def on_show(self):
        ...

    def on_update(self, delta_time):
        self.df.camera_shake.update(delta_time)

        self.df.player.update(delta_time, self.keys_pressed)
        self.df.bullet_list.update(delta_time)
        self.df.cristal_list.update(delta_time)

    def on_draw(self):
        self.clear()
        df = self.df

        self.df.camera_shake.update_camera()
        self.df.camera.use()
        df.background.draw()
        df.board.draw()
        df.player_list.draw()
        df.bullet_list.draw()
        df.cristal_list.draw()

        self.df.interface_camera.use()
        self.df.batch.draw()

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)


class FinishView(arcade.View):
    def __init__(self, defender):
        super().__init__()
        self.df = defender

    def setup(self):
        ...

    def on_show(self):
        ...

    def on_update(self, delta_time):
        ...

    def on_draw(self):
        self.clear()
        df = self.df

        df.background.draw()
        df.board.draw()
        df.finish_list.draw()



# Объекты и спрайты (статичные) --------------------------------------------------------------------->

# Фоновые объекты
class Background:
    def __init__(self, defender):
        self.df = defender
        self.fon = arcade.load_texture("Defender_Battle/Static/fon_black.png")

        # Настройки пульсации при получении урона игроком
        self.pulse_time = 0.5
        self.is_pulse = False
        self.pulse_color = (255, 0, 0, 100)

    def draw(self):
        df = self.df
        # Отрисовка фона
        rect = arcade.rect.XYWH(df.center_x, df.center_y, df.width, df.height)
        arcade.draw_texture_rect(self.fon, rect)
        # arcade.draw_rect_filled(rect, arcade.color.BLACK)

        # Отрисовка пульсации
        if self.is_pulse:
            arcade.draw_lbwh_rectangle_outline(0, 0, df.width, df.height, self.pulse_color, 50)

    def start_pulse(self):
        if not self.is_pulse:
            arcade.schedule(self.stop_pulse, self.pulse_time)
            self.is_pulse = True

    def stop_pulse(self, delta_time=0):
        arcade.unschedule(self.stop_pulse)
        self.is_pulse = False


# Спрайт обратного отсчёта
class Countdown(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.center_x = x
        self.center_y = y
        self.scale = 2

        self.textures = []
        self.curr_index = 0
        for i in range(3, 0, -1):
            texture = arcade.load_texture(f"Defender_Battle/Static/Start_Numbers/{i}.png")
            self.textures.append(texture)


# Спрайт - надпись в конце боя
class FinishText(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.center_x = x
        self.center_y = y
        self.texture = arcade.load_texture("Defender_Battle/Static/finish_text.png")
        self.scale = 1


# Спрайт клетки
class Cell(arcade.Sprite):
    def __init__(self, x, y, cell_size):
        super().__init__(x, y)
        self.cell_size = cell_size

        self.center_x = x
        self.center_y = y
        self.texture = arcade.load_texture("Defender_Battle/Static/Cell_Textures/base.png")
        self.scale = cell_size / 100


# Доска, состоит из клеток
class Board:
    def __init__(self, defender):
        self.df = defender

        scr_w = defender.width
        scr_h = defender.height

        self.cell_size = 70
        # Размеры поля в клетках
        self.width = 10
        self.height = 10

        # Настройки цветов
        self.frame_color = (255, 50, 0, 100)
        self.grid_color = (0, 0, 0, 100)
        self.pulse_color = (255, 150, 0, 100)

        # Отступ поля
        self.indent_x = (scr_w - self.width * self.cell_size) // 2
        self.indent_y = (scr_h - self.height * self.cell_size) // 2

        # Центр поля
        self.center_x = (self.width - self.indent_x) // 2
        self.center_y = (self.height - self.indent_y) // 2

        self.cells_list = arcade.SpriteList()
        for row in range(self.height):
            for col in range(self.width):
                x = self.indent_x + col * self.cell_size + self.cell_size // 2
                y = self.indent_y + row * self.cell_size + self.cell_size // 2
                cell = Cell(x, y, self.cell_size)
                self.cells_list.append(cell)

    def draw(self):
        # Пульсация при воспламенении
        if self.df.is_fire:
            color = self.pulse_color
            border = 50
        else:
            color = self.frame_color
            border = 25

        # Подсветка доски
        arcade.draw_lbwh_rectangle_outline(
            self.indent_x,
            self.indent_y,
            self.width * self.cell_size,
            self.height * self.cell_size,
            color,
            border
        )

        # Отрисовка клеток
        self.cells_list.draw()

        # Подсветка сетки
        for row in range(self.height):
            for col in range(self.width):
                x = self.indent_x + col * self.cell_size
                y = self.indent_y + row * self.cell_size
                arcade.draw_lbwh_rectangle_outline(
                    x,
                    y,
                    self.cell_size,
                    self.cell_size,
                    self.grid_color,
                    5
                )


# Спрайт игрока
class Player(arcade.Sprite):
    def __init__(self, x, y, defender):
        super().__init__(x, y)
        self.df = defender

        self.board = defender.board

        # Здоровья потеряно при контакте с воспламенённой клеткой
        self.health_lose_boost = 1

        self.pl_size = 40
        self.center_x = x
        self.center_y = y
        self.texture = arcade.load_texture("Defender_Battle/Static/Player_Textures/base.png")
        self.scale = self.pl_size / 64

        self.speed = 150

        self.is_shield = False
        self.was_damage_from_fire = False

    def update(self, delta_time, keys_pressed):
        board = self.board

        # Перемещение
        dx, dy = 0, 0
        if arcade.key.LEFT in keys_pressed or arcade.key.A in keys_pressed:
            dx -= self.speed * delta_time
        if arcade.key.RIGHT in keys_pressed or arcade.key.D in keys_pressed:
            dx += self.speed * delta_time
        if arcade.key.UP in keys_pressed or arcade.key.W in keys_pressed:
            dy += self.speed * delta_time
        if arcade.key.DOWN in keys_pressed or arcade.key.S in keys_pressed:
            dy -= self.speed * delta_time

        self.center_x += dx
        self.center_y += dy

        # Если игрок не движется, то срабатывает щит, при нажатии на пробел
        if dx == 0 and dy == 0:
            self.is_shield = True
            self.texture = arcade.load_texture("Defender_Battle/Static/Player_Textures/shield.png")
            self.scale = self.pl_size / 100
        else:
            self.is_shield = False
            self.texture = arcade.load_texture("Defender_Battle/Static/Player_Textures/base.png")
            self.scale = self.pl_size / 64

        # Проверка на границы - игрок ходит в пределах доски
        left = board.indent_x
        right = board.indent_x + board.width * board.cell_size
        bottom = board.indent_y
        top = board.indent_y + board.height * board.cell_size

        indent = self.pl_size // 2 + 5

        if self.center_x < left + indent:
            self.center_x = left + indent
        if self.center_x > right - indent:
            self.center_x = right - indent
        if self.center_y > top - indent:
            self.center_y = top - indent
        if self.center_y < bottom + indent:
            self.center_y = bottom + indent

        # Проверка на коллизию с воспламенёнными клетками
        if not self.was_damage_from_fire:
            if self.df.is_fire and arcade.check_for_collision_with_list(self, self.df.active_cells):
                damage_sound = arcade.load_sound("Defender_Battle/Static/Sounds/get_damage.wav")
                arcade.play_sound(damage_sound, 3)
                self.df.background.start_pulse()
                self.df.health_lose += self.health_lose_boost
                self.df.update_score_text()
                self.was_damage_from_fire = True
        else:
            if not arcade.check_for_collision_with_list(self, self.df.active_cells):
                self.was_damage_from_fire = False
            else:
                self.df.background.start_pulse()


# Спрайт пули
class Bullet(arcade.Sprite):
    def __init__(self, x, y, defender):
        super().__init__(x, y)
        self.df = defender

        # Сколько урона нанесено игроку от 1 пули
        self.health_lose_boost = 0.5

        self.board = defender.board
        self.player = defender.player
        self.background = defender.background

        self.bul_size = 30
        self.center_x = x
        self.center_y = y
        self.texture = arcade.load_texture("Defender_Battle/Static/bullet.png")
        self.scale = self.bul_size / 100

        self.speed = 100

    def update(self, delta_time):
        if not self.df.is_wave_active:
            self.speed = 400
            self.move_forward(delta_time)
        else:
            self.check_for_collision()

            right = self.board.indent_x + self.board.width * self.board.cell_size
            left = self.board.indent_x

            if self.center_x > right or self.center_x < left:
                self.move_forward(delta_time)
            else:
                self.move_to_player(delta_time)

    def check_for_collision(self):
        if arcade.check_for_collision(self, self.player):
            if not self.player.is_shield:
                self.background.start_pulse()
                damage_sound = arcade.load_sound("Defender_Battle/Static/Sounds/get_damage.wav")
                arcade.play_sound(damage_sound, 3)
                self.df.health_lose += self.health_lose_boost
                self.df.update_score_text()
            else:
                hit_sound = arcade.load_sound("Defender_Battle/Static/Sounds/hit_bullet_from_shield.wav")
                arcade.play_sound(hit_sound, 1)
            self.remove_from_sprite_lists()

    def move_forward(self, delta_time):
        self.center_x -= self.speed * delta_time
        if self.center_x < -100:
            self.remove_from_sprite_lists()

    def move_to_player(self, delta_time):
        plx = self.player.center_x
        ply = self.player.center_y
        rx = self.center_x - plx
        ry =  self.center_y - ply

        angle = math.atan2(ry, rx)
        dx = self.speed * delta_time
        dy = math.sin(angle) * self.speed * delta_time
        self.center_x -= dx
        self.center_y -= dy


# Спрайт кристалла для атаки
class AttackCristal(arcade.Sprite):
    def __init__(self, x, y, free_cells, my_cell, defender):
        super().__init__(x, y)
        self.df = defender

        # Сколько урона нанесено врагу от 1 кристала
        self.damage_attack_boost = 1

        self.my_cell = my_cell
        self.free_cells = free_cells

        self.cristal_size = 30
        self.center_x = x
        self.center_y = y
        self.texture = arcade.load_texture("Defender_Battle/Static/attack_cristal.png")
        self.scale = self.cristal_size / 100

        self.is_moved = False # Движется ли кристалл (движется к монстру, если его собрал игрок)
        # Конечная точка, куда движется кристалл, когда его собрал игрок
        self.finish_x = defender.width + 50
        self.finish_y = defender.height // 2
        self.speed = 150

    def update(self, delta_time):
        if not self.is_moved:
            if self.df.is_wave_active:
                # Проверка на коллизию с игроком
                if not self.is_moved:
                    if arcade.check_for_collision(self, self.df.player):
                        cristal_sound = arcade.load_sound("Defender_Battle/Static/Sounds/get_cristal.wav")
                        arcade.play_sound(cristal_sound, 0.25)
                        self.df.damage_attack += self.damage_attack_boost
                        self.df.update_score_text()
                        self.is_moved = True
            else:
                self.remove_from_sprite_lists()

        # Движемся к монстру справа
        else:
            rx = self.finish_x - self.center_x
            ry = self.finish_y - self.center_y
            angle = math.atan2(ry, rx)
            dx = math.cos(angle) * self.speed * delta_time
            dy = math.sin(angle) * self.speed * delta_time
            self.center_x += dx
            self.center_y += dy

            if self.center_x >= self.finish_x:
                self.is_moved = False
                self.free_cells.append(self.my_cell)
                self.remove_from_sprite_lists()



# <--------------------------------------------------------------------->
# DefenderBox - содержит все окна, сцены, спрайты и прочие объекты, к которым можно обратиться
# Передаёт себя всем объектам, чтобы они имели связь друг с другом
class DefenderBox:
    def __init__(self, main_scene_manager):
        # Обязательно передаём главный менеджер сцен общего боя, чтобы в конце выйти и запустить следующий бой
        self.main_scene_manager = main_scene_manager
        # Обязательно получаем основное окно при создании, чтобы переключаться между сценами
        self.window = main_scene_manager.window

        # Параметры окна
        self.width = self.window.width
        self.height = self.window.height
        self.center_x = self.window.center_x
        self.center_y = self.window.center_y

        # Камера для тряски
        self.camera = arcade.camera.Camera2D()
        self.camera_shake = arcade.camera.grips.ScreenShake2D(
            self.camera.view_data,
            max_amplitude=10.0,
            acceleration_duration=0.1,
            falloff_time=0.5,
            shake_frequency=10.0
        )

        # Камера для интерфейса
        self.interface_camera = arcade.camera.Camera2D()

        # Состояние
        self.is_wave_active = False # Активна ли волна

        self.active_cells = arcade.SpriteList() # Клетки поля, которые воспламеняются
        self.is_fire = False # Есть ли воспламенение

        # Объекты и спрайты (статичные)
        self.background = Background(self) # Фоновые объекты, такие как фон, подсветка, доп персонажи для красоты
        self.board = Board(self) # Основное поле, по которому перемещается персонаж

        self.countdown = Countdown(self.center_x, self.center_y) # Спрайт с цифрами для обратного отсчёта
        self.countdown_list = arcade.SpriteList()
        self.countdown_list.append(self.countdown)

        self.finish_text = FinishText(self.center_x, self.center_y) # Надпись в конце
        self.finish_list = arcade.SpriteList()
        self.finish_list.append(self.finish_text)

        self.player = Player(self.center_x, self.center_y, self) # Игрок
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        self.bullet_list = arcade.SpriteList() # Пули
        self.cristal_list = arcade.SpriteList() # Кристаллы атаки

        # Очки за раунд
        self.health_lose = 0  # Здоровья потеряно у персонажа
        self.damage_attack = 0  # Урона нанесено врагу

        self.batch = Batch()

        self.damage_attack_text = arcade.Text(
            f"Урона нанесено {self.damage_attack}",
            40,
            100,
            arcade.color.WHITE,
            font_size=16,
            batch=self.batch
        )

        self.health_lose_text = arcade.Text(
            f"Здоровья потеряно -{self.health_lose}",
            40,
            50,
            arcade.color.WHITE,
            font_size=16,
            batch=self.batch
        )

        # Окна (динамические)
        self.start_view = StartView(self)
        self.wave_view = WaveView(self)
        self.finish_view = FinishView(self)

        # Собственный менеджер сцен (динамический) - обновляет волны и окна
        self.scene_manager = SceneManager(self)

    # Обновляет текст счёта
    def update_score_text(self):
        self.damage_attack_text.text = f"Урона нанесено {self.damage_attack}"
        self.health_lose_text.text = f"Здоровья потеряно -{self.health_lose}"


# Функция для запуска мини-игры защитника
def setup_defender(main_scene_manager):
    DefenderBox(main_scene_manager)
