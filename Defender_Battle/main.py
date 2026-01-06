# """ Name: Иван, Date: 05.01.2026, WhatYouDo: механика боя защитника (передвижение/увороты)"""
# """ Name: Иван, Date: 06.01.2026, WhatYouDo: добавил класс механик, кристаллы, коллизию, пульсацию от урона"""
import arcade
import random
import math


# Таймер (Динамический) - обновляет волны и окна
class Timer:
    def __init__(self, defender):
        self.df = defender

        # Сцены - реализуют механику каждой волны, переключают на нужное окно
        start_scene = StartScene(defender)
        wave1_scene = Wave1Scene(defender)
        finish_scene = FinishScene(defender)

        # Добавляем сцены в очередь
        self.timeline = [start_scene, wave1_scene, finish_scene]
        self.curr_index = 0

        # Вызываем следующую сцену
        self.next()

    def next(self, delta_time=0):
        # Получаем сцену и обновляем индекс в очереди
        if self.curr_index >= len(self.timeline):
            # В конце выходим и запускаем следующий бой в главном таймере
            self.df.main_timer.next()
        else:
            scene = self.timeline[self.curr_index]
            self.curr_index += 1
            scene.setup() # Запускаем текущую сцену


# Сцены (динамические)

# Обратный отсчёт
class StartScene:
    def __init__(self, defender):
        self.df = defender
        self.tick = 1 # Время между обновлениями

    def setup(self):
        self.df.window.show_view(self.df.start_view) # Включаем нужное окно
        self.next() # Пошагово обновляем сцену

    def next(self, delta_time=0):
        cuontdown = self.df.countdown

        arcade.unschedule(self.next) # Обязательно удаляем таймер
        if cuontdown.curr_index >= len(cuontdown.textures):
            cuontdown.curr_index = 0
            # По завершении запускаем следующую сцену в таймере
            self.df.timer.next()
        else:
            # Сменяем текстуру обратного отсчёта на следующую
            cuontdown.texture = cuontdown.textures[cuontdown.curr_index]
            cuontdown.curr_index += 1
            arcade.schedule(self.next, self.tick) # Выставляем время для следующего обновления


# Волна 1 - 2 механики: воспламеняющаяся доска и пули
class Wave1Scene:
    def __init__(self, defender):
        self.df = defender

        # Выбираем механики для волны
        self.fire_board_mech = FireBoardMechanic(self.df)
        self.bullet_mech = BulletMechanic(self.df)
        self.cristal_mech = CristalMechanic(self.df)

        self.wave_time = 54 # Время волны
        self.pause_time = 10 # Время после волны до следующей сцены

    # Запускаем механики
    def setup(self):
        self.df.window.show_view(self.df.wave1_view)
        self.fire_board_mech.setup()
        self.bullet_mech.setup()
        self.cristal_mech.setup()
        arcade.schedule(self.stop, self.wave_time)

    # Останавливаем механики
    def stop(self, delta_time=0):
        arcade.unschedule(self.stop)
        self.fire_board_mech.stop()
        self.bullet_mech.stop()
        self.cristal_mech.stop()
        arcade.schedule(self.next_scene, self.pause_time)

    def next_scene(self, delta_time=0):
        arcade.unschedule(self.next_scene)
        self.df.timer.next()


# Сцена в крнце боя
class FinishScene:
    def __init__(self, defender):
        self.df = defender
        self.finish_time = 2 # Время сцены

    def setup(self):
        self.df.window.show_view(self.df.finish_view) # Включаем нужное окно
        arcade.schedule(self.next_scene, self.finish_time)

    def next_scene(self, delta_time=0):
        arcade.unschedule(self.next_scene)
        self.df.timer.next()


#Реализация основных механик (динамические)

# Воспламенение плитки (3 состояния - обычное, предупреждение, огонь)
class FireBoardMechanic:
    def __init__(self, defender):
        self.df = defender

        self.board = defender.board
        self.player = defender.player
        self.background = defender.background

        # Активна ли данная механика
        self.is_active = False

        # Время между состояниями
        self.pause_time = 0.5
        self.danger_time = 2
        self.fire_time = 1

        # Клетки, которые будут воспламеняться
        self.active_cells = arcade.SpriteList()

    def setup(self):
        self.is_active = True
        self.next()

    def next(self, delta_time=0):
        arcade.unschedule(self.next)

        # Возвращаемся к обычному состоянию
        for cell in self.active_cells:
            cell.texture = arcade.load_texture("Defender_Battle/Static/Cell_Textures/base.png")
            cell.scale = 70 / 236

        self.active_cells.clear()

        # При активном состоянии
        if self.is_active:
            # Рандомно выбираем клетки для воспламенения
            for cell in self.board.cells_list:
                if random.random() >= 0.3:
                    self.active_cells.append(cell)
            # Выставляем время для следующего состояния - другая функция
            arcade.schedule(self.change_for_danger, self.pause_time)

    # Просто сменяем текстуру на предупреждение
    def change_for_danger(self, delta_time=0):
        arcade.unschedule(self.change_for_danger)
        for cell in self.active_cells:
            cell.texture = arcade.load_texture("Defender_Battle/Static/Cell_Textures/danger.png")
            cell.scale = 70 / 626
        arcade.schedule(self.change_for_fire, self.danger_time)

    # Сменяем текстуру на огонь
    def change_for_fire(self, delta_time=0):
        arcade.unschedule(self.change_for_fire)
        for cell in self.active_cells:
            cell.texture = arcade.load_texture("Defender_Battle/Static/Cell_Textures/fire.png")
            cell.scale = 70 / 350
            if arcade.check_for_collision_with_list(self.player, self.active_cells):
                self.background.start_pulse()
        # Возвращаемся к обычному состоянию и запускаем следующее обновление
        arcade.schedule(self.next, self.fire_time)

    def stop(self):
        self.is_active = False


# Полёт пули
class BulletMechanic:
    def __init__(self, defender):
        self.df = defender

        self.board = defender.board
        self.player = defender.player

        self.is_active = False

        self.tick = 1.2 # Время между спавном новой пули

    def setup(self):
        self.is_active = True
        self.next()

    def next(self, delta_time=0):
        arcade.unschedule(self.next)

        if self.is_active:
            bullet = Bullet(self.df.width + 50, random.randrange(20, self.df.height - 20), self.df)
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

        self.tick = 6 # Время между спавном кристаллов

    def setup(self):
        self.is_active = True
        self.next()

    def next(self, delta_time=0):
        arcade.unschedule(self.next)

        if self.is_active:
            cell = random.choice(self.board.cells_list)
            cristal = AttackCristal(cell.center_x, cell.center_y, self.df)
            self.df.cristal_list.append(cristal)
            arcade.schedule(self.next, self.tick)

    def stop(self):
        self.is_active = False


# Окна (динамические)
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


class Wave1View(arcade.View):
    def __init__(self, defender):
        super().__init__()
        self.df = defender

        self.keys_pressed = set()

    def setup(self):
        ...

    def on_show(self):
        ...

    def on_update(self, delta_time):
        self.df.player.update(delta_time, self.keys_pressed)
        self.df.bullet_list.update(delta_time)
        self.df.cristal_list.update(delta_time)

    def on_draw(self):
        self.clear()
        df = self.df

        df.background.draw()
        df.board.draw()
        df.player_list.draw()
        df.bullet_list.draw()
        df.cristal_list.draw()

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


# Объекты и спрайты (статичные)

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
        self.scale = 0.5


# Спрайт клетки
class Cell(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.center_x = x
        self.center_y = y
        self.texture = arcade.load_texture("Defender_Battle/Static/Cell_Textures/base.png")
        self.scale = 70 / 236


# Доска, состоит из клеток
class Board:
    def __init__(self, defender):
        self.df = defender

        scr_w = defender.width
        scr_h = defender.height
        self.cell_size = 70
        self.width = 10
        self.height = 10

        self.indent_x = (scr_w - self.width * self.cell_size) // 2
        self.indent_y = (scr_h - self.height * self.cell_size) // 2

        self.cells_list = arcade.SpriteList()
        self.cells = [[]] * self.height

        for row in range(self.height):
            for col in range(self.width):
                x = self.indent_x + col * self.cell_size + self.cell_size // 2
                y = self.indent_y + row * self.cell_size + self.cell_size // 2
                cell = Cell(x, y)
                self.cells_list.append(cell)
                self.cells[row].append(cell)

    def draw(self):
        self.cells_list.draw()


# Спрайт игрока
class Player(arcade.Sprite):
    def __init__(self, x, y, defender):
        super().__init__(x, y)
        self.df = defender

        self.board = defender.board

        self.center_x = x
        self.center_y = y
        self.texture = arcade.load_texture("Defender_Battle/Static/Player_Textures/base.png")
        self.scale = 0.5

        self.speed = 150

        self.is_shield = False

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

        # Если не игрок движется, то срабатывает щит, при нажатии на пробел
        if dx == 0 and dy == 0 and arcade.key.SPACE in keys_pressed:
            self.is_shield = True
            self.texture = arcade.load_texture("Defender_Battle/Static/Player_Textures/shield.png")
            self.scale = 0.5
        else:
            self.is_shield = False
            self.texture = arcade.load_texture("Defender_Battle/Static/Player_Textures/base.png")
            self.scale = 0.5

        # Проверка на границы - игрок ходит в пределах доски
        left = board.indent_x
        right = board.indent_x + board.width * board.cell_size
        bottom = board.indent_y
        top = board.indent_y + board.height * board.cell_size

        if self.center_x < left:
            self.center_x = left
        if self.center_x > right:
            self.center_x = right
        if self.center_y > top:
            self.center_y = top
        if self.center_y < bottom:
            self.center_y = bottom


# Спрайт пули
class Bullet(arcade.Sprite):
    def __init__(self, x, y, defender):
        super().__init__(x, y)

        self.dfr = defender

        self.board = defender.board
        self.player = defender.player
        self.background = defender.background

        self.center_x = x
        self.center_y = y
        self.texture = arcade.load_texture("Defender_Battle/Static/bullet.png")
        self.scale = 0.5

        self.speed = 100

    def update(self, delta_time):
        right = self.board.indent_x + self.board.width * self.board.cell_size
        left = self.board.indent_x
        if self.center_x > right or self.center_x < left:
            self.move_forward(delta_time)
        else:
            self.move_to_player(delta_time)

        if arcade.check_for_collision(self, self.player):
            if not self.player.is_shield:
                self.background.start_pulse()
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
        # dx = math.cos(angle) * self.speed * delta_time
        dx = self.speed * delta_time
        dy = math.sin(angle) * self.speed * delta_time
        self.center_x -= dx
        self.center_y -= dy


# Спрайт кристалла для атаки
class AttackCristal(arcade.Sprite):
    def __init__(self, x, y, defender):
        super().__init__(x, y)
        self.df = defender

        self.center_x = x
        self.center_y = y
        self.texture = arcade.load_texture("Defender_Battle/Static/attack_cristal.png")
        self.scale = 0.5

        self.is_moved = False # Движется ли кристалл (движется к монстру, если его собрал игрок)
        # Конечная точка, куда движется кристалл, когда его собрал игрок
        self.finish_x = defender.width + 20
        self.finish_y = defender.height // 2
        self.speed = 150

    def update(self, delta_time):
        # Проверка на коллизию с игроком
        if arcade.check_for_collision(self, self.df.player):
            self.is_moved = True

        if self.is_moved:
            rx = self.finish_x - self.center_x
            ry = self.finish_y - self.center_y
            angle = math.atan2(ry, rx)
            dx = math.cos(angle) * self.speed * delta_time
            dy = math.sin(angle) * self.speed * delta_time
            self.center_x += dx
            self.center_y += dy

            if self.center_x >= self.finish_x:
                self.is_moved = False


# Defender - содержит все окна, сцены, спрайты и прочие объекты, к которым можно обратиться
# Передаёт себя всем объектам, чтобы они имели связь друг с другом
class Defender:
    def __init__(self, main_timer):
        # Обязательно передаём главный таймер всей игры, чтобы в конце выйти и запустить следующий бой
        self.main_timer = main_timer
        # Обязательно получаем основное окно при создании, чтобы переключаться между сценами
        self.window = main_timer.window

        # Параметры окна
        self.width = self.window.width
        self.height = self.window.height
        self.center_x = self.window.center_x
        self.center_y = self.window.center_y

        # Очки за раунд
        self.health_lose = 0 # Здоровья потеряно у персонажа
        self.damage_attack = 0 # Урона нанесено врагу

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

        # Окна (динамические)
        self.start_view = StartView(self)
        self.wave1_view = Wave1View(self)
        self.finish_view = FinishView(self)

        # Таймер (динамический) - обновляет волны и окна
        self.timer = Timer(self)


def setup_defender(timer):
    Defender(timer)
