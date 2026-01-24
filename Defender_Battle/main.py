# Name: Иван, Date: 05.01.2026, WhatYouDo: механика боя защитника (передвижение/увороты)
# Name: Иван, Date: 06.01.2026, WhatYouDo: добавил класс механик, кристаллы, коллизию, пульсацию от урона
# Name: Иван, Date: 07.01.2026, WhatYouDo: улучшил текстуры, коллизию, механики, добавил звуки, тряску, текст счёта

import arcade
import random
import math
import EasySprite



# Менеджер сцен - обновляет волны и окна --------------------------------------------------------------------->
class SceneManager:
    def __init__(self, defender):
        self.df = defender

        # Сцены - реализуют механику каждой волны, переключают на нужное окно
        start_scene = StartScene(defender)
        wave_scene = WaveScene(defender)
        finish_scene = FinishScene(defender)

        # Добавляем сцены в очередь
        self.timeline = [wave_scene]
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



# Сцены --------------------------------------------------------------------->

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


# Волна 1 - 3 механики: воспламеняющаяся доска, пули, аура
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

        # self.fire_board_mech.setup()
        # arcade.schedule(self.bullet_mech.setup, 2)
        # arcade.schedule(self.cristal_mech.setup, 2)

        self.bullet_mech.setup()
        self.cristal_mech.setup()

        self.player_music = arcade.play_sound(self.main_music, volume=0)
        arcade.schedule(self.stop, self.wave_time)

    # Останавливаем механики
    def stop(self, delta_time=0):
        arcade.unschedule(self.stop)
        self.bullet_mech.stop()
        self.cristal_mech.stop()
        self.fire_board_mech.stop()

        arcade.schedule(self.stop_next, self.pause1_time)

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
        arcade.play_sound(finish_sound, 0)
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
            cell.texture = cell.texture_list[0]

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
            cell.texture = cell.texture_list[1]
        arcade.schedule(self.change_for_fire, self.danger_time)

    # Сменяем текстуру на огонь и включаем режим воспламенения
    def change_for_fire(self, delta_time=0):
        arcade.unschedule(self.change_for_fire)
        for cell in self.active_cells:
            cell.texture = cell.texture_list[2]
        self.df.is_fire = True

        # Эффекты звука и тряски
        fire_sound = arcade.load_sound("Defender_Battle/Static/Sounds/fire_sound.wav")
        arcade.play_sound(fire_sound, 0)
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

    def setup(self, delta_time=0):
        arcade.unschedule(self.setup)
        self.is_active = True
        self.next()

    def next(self, delta_time=0):
        arcade.unschedule(self.next)

        if self.is_active:
            spawn_place = random.choice(["top", "bottom", "left", "right"])
            bullet = Bullet(spawn_place, self.df)
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

    def setup(self, delta_time=0):
        arcade.unschedule(self.setup)
        self.is_active = True
        self.next()

    def next(self, delta_time=0):
        arcade.unschedule(self.next)

        if self.is_active:
            cell = random.choice(self.free_cells)
            self.free_cells.remove(cell)
            cristal = AuraPoint(cell.center_x, cell.center_y, self.free_cells, cell, self.df)
            self.df.aura_list.append(cristal)
            arcade.schedule(self.next, self.tick)

    def stop(self):
        self.is_active = False



# Окна --------------------------------------------------------------------->
# Здесь прописываем, какие объекты отрисовывать и обновлять
class StartView(arcade.View):
    def __init__(self, defender):
        super().__init__()
        self.df = defender

    def on_draw(self):
        self.clear()
        df = self.df

        df.board.draw()
        df.countdown_list.draw()
        df.mg_box.draw()


class WaveView(arcade.View):
    def __init__(self, defender):
        super().__init__()
        self.df = defender
        self.keys_pressed = set()

    def on_update(self, delta_time):
        self.df.camera_shake.update(delta_time)

        self.df.player.update(delta_time, self.keys_pressed)
        self.df.bullet_list.update(delta_time)
        self.df.aura_list.update(delta_time)

    def on_draw(self):
        self.clear()
        df = self.df

        df.camera_shake.update_camera()
        df.camera.use()
        # df.board.draw()
        df.player_list.draw()
        df.aura_list.draw()
        df.bullet_list.draw()

        df.interface_camera.use()
        df.mg_box.draw()

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)


class FinishView(arcade.View):
    def __init__(self, defender):
        super().__init__()
        self.df = defender

    def on_draw(self):
        self.clear()
        df = self.df

        df.board.draw()
        df.finish_list.draw()
        df.mg_box.draw()



# Объекты и спрайты --------------------------------------------------------------------->

# Спрайт обратного отсчёта
class Countdown(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.center_x = x
        self.center_y = y
        self.curr_index = 0

        self.textures = EasySprite.Animate(
            "Defender_Battle/Static/Textures/start_numbers.png",
            3,
            15
        ).get_texture_lst()

        self.texture = self.textures[0]
        self.scale = 1


# Спрайт - надпись в конце боя
class FinishText(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.center_x = x
        self.center_y = y
        self.texture = arcade.load_texture("Defender_Battle/Static/Textures/finish_text.png")
        self.scale = 1


# Спрайт клетки
class Cell(arcade.Sprite):
    def __init__(self, x, y, board):
        super().__init__(x, y)
        self.cell_size = board.cell_size
        self.texture_list = board.cell_textures

        self.center_x = x
        self.center_y = y

        self.texture = self.texture_list[0]
        self.scale = 1


# Доска, состоит из клеток
class Board:
    def __init__(self, defender):
        self.df = defender
        self.frame = defender.mini_window.frame

        self.cell_textures = EasySprite.Animate(
            "Defender_Battle/Static/Textures/cell_textures.png",
            3,
            5
        ).get_texture_lst()

        # Параметры мини-окна
        minw_w = defender.width
        minw_h = defender.height
        minw_x = defender.x
        minw_y = defender.y
        minw_center_x = defender.center_x
        minw_center_y = defender.center_y

        # Размер клетки
        self.cell_size = 70

        # Размеры поля в клетках
        self.width = 10
        self.height = 10

        # Настройки цветов
        self.frame_color = (255, 50, 0, 100)
        self.grid_color = (0, 0, 0, 100)
        self.pulse_color = (255, 150, 0, 100)

        # Отступ поля
        self.indent_x = minw_x + (minw_w - self.width * self.cell_size) // 2
        self.indent_y = minw_y + (minw_h - self.height * self.cell_size) // 2

        # Центр поля
        self.center_x = minw_center_x
        self.center_y = minw_center_y

        self.cells_list = arcade.SpriteList()
        for row in range(self.height):
            for col in range(self.width):
                x = self.indent_x + col * self.cell_size + self.cell_size // 2
                y = self.indent_y + row * self.cell_size + self.cell_size // 2
                cell = Cell(x, y, self)
                self.cells_list.append(cell)

    def draw(self):
        # Пульсация при воспламенении
        if self.df.is_fire:
            self.frame.curr_color = self.pulse_color
            self.frame.curr_border_width = 10
        else:
            self.frame.curr_color = self.frame_color
            self.frame.curr_border_width = 5

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

        self.animate_textures = EasySprite.Animate(
            "Defender_Battle/Static/Textures/Heart.png",
            1,
            scale = self.pl_size / 15
        ).get_texture_lst()

        self.shield_texture = EasySprite.load_texture(
            "Defender_Battle/Static/Textures/player_shield_pixel.png",
            self.pl_size / 16
        )

        self.center_x = x
        self.center_y = y
        self.texture = self.shield_texture
        self.scale = 1

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
            self.texture = self.shield_texture
        else:
            self.is_shield = False
            self.texture = self.animate_textures[0]

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
                arcade.play_sound(damage_sound, 0)
                # self.df.background.start_pulse()
                self.df.health_lose += self.health_lose_boost
                self.was_damage_from_fire = True
        else:
            if not arcade.check_for_collision_with_list(self, self.df.active_cells):
                self.was_damage_from_fire = False
            else:
                ...
                # self.df.background.start_pulse()


# Спрайт пули
class Bullet(arcade.Sprite):
    def __init__(self, spawn_place, defender):
        super().__init__()
        self.df = defender

        # Сколько урона нанесено игроку от 1 пули
        self.health_lose_boost = 0.5

        self.board = defender.board
        self.player = defender.player

        self.spawn_place = spawn_place
        self.indent = 15

        if self.spawn_place == "top":
            self.center_x = random.randrange(round(self.df.left + self.indent), round(self.df.right - self.indent))
            self.center_y = self.df.top + self.indent
        elif self.spawn_place == "bottom":
            self.center_x = random.randrange(round(self.df.left + self.indent), round(self.df.right - self.indent))
            self.center_y = self.df.bottom - self.indent
        elif self.spawn_place == "left":
            self.center_x = self.df.left - self.indent
            self.center_y = random.randrange(round(self.df.bottom + self.indent), round(self.df.top - self.indent))
        else:
            self.center_x = self.df.right + self.indent
            self.center_y = random.randrange(self.df.bottom + self.indent, self.df.top - self.indent)

        self.spawn_direction_dict = {
            "top": (0, -1),
            "bottom": (0, 1),
            "left": (1, 0),
            "right": (-1, 0)
        }
        self.direction = self.spawn_direction_dict[spawn_place]
        self.speed = 100

        self.texture = EasySprite.load_texture("Defender_Battle/Static/Textures/bullet_pixel.png", 3)
        self.scale = 1

    def update(self, delta_time):
        self.move_to_player(delta_time)
        # if not self.df.is_wave_active:
        #     self.speed = 400
        #     self.move_forward(delta_time)
        # else:
        #     self.move_to_player(delta_time)
        #     self.check_for_collision()

    def check_for_collision(self):
        if arcade.check_for_collision(self, self.player):
            if not self.player.is_shield:
                # self.background.start_pulse()
                damage_sound = arcade.load_sound("Defender_Battle/Static/Sounds/get_damage.wav")
                arcade.play_sound(damage_sound, 0)
                self.df.health_lose += self.health_lose_boost
            else:
                hit_sound = arcade.load_sound("Defender_Battle/Static/Sounds/hit_bullet_from_shield.wav")
                arcade.play_sound(hit_sound, 0)
            self.remove_from_sprite_lists()

    def move_forward(self, delta_time):
        dx, dy = self.direction
        self.center_x += self.speed * dx * delta_time
        self.center_y += self.speed * dy * delta_time

        is_outside = False
        if self.spawn_place == "top":
            is_outside = self.center_y < self.df.bottom - self.indent
        elif self.spawn_place == "bottom":
            is_outside = self.center_y > self.df.top + self.indent
        elif self.spawn_place == "left":
            is_outside = self.center_x > self.df.right + self.indent
        else:
            is_outside = self.center_x < self.df.left - self.indent

        if is_outside:
            self.remove_from_sprite_lists()
            print(self.spawn_place)

    def move_to_player(self, delta_time):
        plx = self.player.center_x
        ply = self.player.center_y
        rx = self.center_x - plx
        ry =  self.center_y - ply
        angle = math.atan2(ry, rx)

        dx, dy = self.direction

        if self.spawn_place == "top" or self.spawn_place == "bottom":
            chx = math.cos(angle) * self.speed * delta_time * -1
            chy = self.speed * delta_time * dy
        else:
            chx = self.speed * delta_time * dx
            chy = math.sin(angle) * self.speed * delta_time * -1

        self.center_x += chx
        self.center_y += chy


# Спрайт ауры
class AuraPoint(arcade.Sprite):
    def __init__(self, x, y, free_cells, my_cell, defender):
        super().__init__(x, y)
        self.df = defender

        # Сколько урона нанесено врагу от 1 кристала
        self.damage_attack_boost = 1

        self.my_cell = my_cell
        self.free_cells = free_cells

        self.center_x = x
        self.center_y = y
        self.texture = EasySprite.load_texture("Defender_Battle/Static/Textures/aura_point.png", 2)
        self.scale = 1

        self.is_moved = False # Движется ли кристалл (движется к монстру, если его собрал игрок)
        # Конечная точка, куда движется кристалл, когда его собрал игрок
        self.finish_x = defender.right + 50
        self.finish_y = defender.center_x // 2
        self.speed = 150

    def update(self, delta_time):
        if not self.is_moved:
            if self.df.is_wave_active:
                # Проверка на коллизию с игроком
                if not self.is_moved:
                    if arcade.check_for_collision(self, self.df.player):
                        cristal_sound = arcade.load_sound("Defender_Battle/Static/Sounds/get_cristal.wav")
                        arcade.play_sound(cristal_sound, 0)
                        self.df.damage_attack += self.damage_attack_boost
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

        self.fight_box = main_scene_manager.fb

        # Дополнительные графические объекты
        self.mg_box = self.fight_box.mg_box
        # Мини-окно
        self.mini_window = self.mg_box.mini_window

        # Параметры мини-окна
        self.left = self.mini_window.left
        self.right = self.mini_window.right
        self.top = self.mini_window.top
        self.bottom = self.mini_window.bottom

        self.x = self.mini_window.x
        self.y = self.mini_window.y

        self.width = self.mini_window.width
        self.height = self.mini_window.height

        self.center_x = self.mini_window.center_x
        self.center_y = self.mini_window.center_y

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

        # Объекты и спрайты
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
        self.aura_list = arcade.SpriteList() # Аура

        # Очки за раунд
        self.health_lose = 0  # Здоровья потеряно у персонажа
        self.damage_attack = 0  # Урона нанесено врагу

        # Окна
        self.start_view = StartView(self)
        self.wave_view = WaveView(self)
        self.finish_view = FinishView(self)

        # Собственный менеджер сцен - обновляет волны и окна
        self.scene_manager = SceneManager(self)


# Функция для запуска мини-игры защитника
def setup_defender(main_scene_manager):
    DefenderBox(main_scene_manager)
