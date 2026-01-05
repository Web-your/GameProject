# """ Name: Иван, Date: 05.01.2026, WhatYouDo: механика боя защитника (передвижение/увороты)"""
import arcade
import random


# Таймер (Динамический) - обновляет волны и окна
class Timer:
    def __init__(self, defender):
        self.df = defender

        # Сцены - реализуют механику каждой волны, переключают на нужное коно
        start_scene = StartScene(defender)
        wave1_scene = Wave1Scene(defender)
        wave2_scene = Wave2Scene(defender)

        # Добавляем сцены в очередь
        self.timeline = [start_scene, wave1_scene, wave2_scene]
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
class StartScene:
    def __init__(self, defender):
        self.df = defender
        self.tick = 1 # Время между обновлениями

    def setup(self):
        self.df.window.show_view(self.df.start_view) # Включаем нужное окно
        self.next() # Пошагово обновляем сцену

    def next(self, delta_time=0):
        cuontdown = self.df.countdown

        arcade.unschedule(self.next) # Обязаьельно удаляем таймер
        if cuontdown.curr_index >= len(cuontdown.textures):
            print("stop")
            cuontdown.curr_index = 0
            # По завершении запускаем следующую сцену в таймере
            self.df.timer.next()
        else:
            # Сменяем текстуру обратного отсчёта на слудующую
            cuontdown.texture = cuontdown.textures[cuontdown.curr_index]
            cuontdown.curr_index += 1
            arcade.schedule(self.next, self.tick) # Выставляем время для следующего обновления


# Воспламенение плитки (3 состояния - обычное, предупреждение, огонь)
class Wave1Scene:
    def __init__(self, defender):
        self.df = defender

        self.board = defender.board
        self.player = defender.player

        # Количество циклов обновлений
        self.count_shocks = 10
        self.curr_shock = 0

        # Время между состояниями
        self.pause_time = 0.5
        self.danger_time = 2
        self.fire_time = 1

        # Клетки, которые будут воспламеняться
        self.active_cells = []

    def setup(self):
        self.df.window.show_view(self.df.wave1_view)
        self.next()

    def next(self, delta_time=0):
        arcade.unschedule(self.next)
        self.curr_shock += 1

        # Возвращаемся к обычному состоянию
        for cell in self.active_cells:
            cell.texture = arcade.load_texture("Defender_Battle/Static/Cell_Textures/base.png")
            cell.scale = 70 / 236

        self.active_cells = []

        if self.curr_shock >= self.count_shocks:
            print("victory")
            # Переходим к новой волне
            self.df.timer.next()
        else:
            # Рандомно выбираем клетки для воспламенения
            for cell in self.board.cells_list:
                if random.random() >= 0.3:
                    self.active_cells.append(cell)
            # Выставляем время для следующего состояния - другая функция
            arcade.schedule(self.change_for_danger, self.pause_time)

    def change_for_danger(self, delta_time):
        # Просто сменяем текстуру на предупреждение
        arcade.unschedule(self.change_for_danger)
        for cell in self.active_cells:
            cell.texture = arcade.load_texture("Defender_Battle/Static/Cell_Textures/danger.png")
            cell.scale = 70 / 626
        arcade.schedule(self.change_for_fire, self.danger_time)

    def change_for_fire(self, delta_time):
        # Сменяем текстуру на огонь
        arcade.unschedule(self.change_for_fire)
        for cell in self.active_cells:
            cell.texture = arcade.load_texture("Defender_Battle/Static/Cell_Textures/fire.png")
            cell.scale = 70 / 350

            # Проверка на коллизию с игроком
            if any(arcade.check_for_collision(self.player, cell) for cell in self.active_cells):
                print("fall")
        arcade.schedule(self.next, self.fire_time) # Возвращаемся к обычному состоянию и запускаем следующее обновление


class Wave2Scene:
    def __init__(self, defender):
        self.df = defender

        self.board = defender.board
        self.player = defender.player

        self.count_shocks = 10
        self.curr_shock = 0

        self.tick = 1

    def setup(self):
        self.df.window.show_view(self.df.wave2_view)
        self.next()

    def next(self, delta_time=0):
        arcade.unschedule(self.next)
        self.curr_shock += 1

        if self.curr_shock >= self.count_shocks:
            print("victory")
            self.df.timer.next()
        else:
            bullet = Bullet(self.df.width + 50, random.randrange(20, self.df.height - 20), self.df)
            self.df.bullet_list.append(bullet)
            arcade.schedule(self.next, self.tick)


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

    def on_draw(self):
        self.clear()
        df = self.df

        df.background.draw()
        df.board.draw()
        df.player_list.draw()

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)


class Wave2View(arcade.View):
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

    def on_draw(self):
        self.clear()
        df = self.df

        df.background.draw()
        df.board.draw()
        df.bullet_list.draw()
        df.player_list.draw()

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)


# Объекты и спрайты (статичные)

# Фоновые объекты
class Background:
    def __init__(self, defender):
        self.df = defender
        self.fon = arcade.load_texture("Defender_Battle/Static/fon.png")

    def draw(self):
        df = self.df
        rect = arcade.rect.XYWH(df.center_x, df.center_y, df.width, df.height)
        arcade.draw_texture_rect(self.fon, rect)


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


# Спрайт клетки
class Cell(arcade.Sprite):
    def __init__(self, size, center_x, center_y):
        super().__init__(center_x, center_y)

        self.size = [size, size]
        self.center_x = center_x
        self.center_y = center_y

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
                cell = Cell(self.cell_size, x, y)
                self.cells_list.append(cell)
                self.cells[row].append(cell)

    def draw(self):
        self.cells_list.draw()


# Спрайт игрока
class Player(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.center_x = x
        self.center_y = y
        self.texture = arcade.load_texture("Defender_Battle/Static/Player_Textures/base.png")
        self.scale = 0.5

        self.speed = 150

    def update(self, delta_time, keys_pressed):
        dx, dy = 0, 0
        if arcade.key.LEFT in keys_pressed or arcade.key.A in keys_pressed:
            dx -= self.speed * delta_time
        if arcade.key.RIGHT in keys_pressed or arcade.key.D in keys_pressed:
            dx += self.speed * delta_time
        if arcade.key.UP in keys_pressed or arcade.key.W in keys_pressed:
            dy += self.speed * delta_time
        if arcade.key.DOWN in keys_pressed or arcade.key.S in keys_pressed:
            dy -= self.speed * delta_time

        if dx != 0 and dy != 0:
            factor = 0.7071
            dx *= factor
            dy *= factor

        self.center_x += dx
        self.center_y += dy


# Спрайт пули
class Bullet(arcade.Sprite):
    def __init__(self, x, y, defender):
        super().__init__(x, y)

        self.dfr = defender

        self.center_x = x
        self.center_y = y
        self.texture = arcade.load_texture("Defender_Battle/Static/bullet.png")
        self.scale = 0.5

        self.speed = 150

    def update(self, delta_time):
        if self.center_x < -100:
            self.remove_from_sprite_lists()

        else:
            self.center_x -= self.speed * delta_time


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

        # Объекты и спрайты (статичные)
        self.background = Background(self) # Фоновые объекты, такие как фон, подсветка, доп персонажи для красоты
        self.board = Board(self) # Основное поле, по которому перемещается персонаж

        self.countdown = Countdown(self.center_x, self.center_y) # Спрайт с цифрами для обратного отсчёта
        self.countdown_list = arcade.SpriteList()
        self.countdown_list.append(self.countdown)

        self.player = Player(self.center_x, self.center_y) # Игрок
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        self.bullet_list = arcade.SpriteList() # Пули

        # Окна (динамические)
        self.start_view = StartView(self)
        self.wave1_view = Wave1View(self)
        self.wave2_view = Wave2View(self)
        # self.finish_view = FinishView(self)

        # Таймер (динамический) - обновляет волны и окна
        self.timer = Timer(self)


def setup_defender(timer):
    Defender(timer)
