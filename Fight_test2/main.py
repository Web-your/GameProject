import arcade



# Примеры реализации объектов из других файлов
# <-------------------------------------------------------------------------------------------------------------------

# Предыдущий менеджер сцен для запуска различных полноценных битв, хождений по миру и диалогов с персонажами
class MainSceneManager:
    def __init__(self, window):
        self.window = window
        setup_fight(self)


# Примеры окон - мини-игр
class AttackView(arcade.View):
    def __init__(self, main_scene_manager):
        super().__init__()
        self.main_scene_manager = main_scene_manager
        self.text = "Атака"

    def setup(self):
        ...

    def on_show(self):
        ...

    def on_update(self, delta_time):
        ...

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            self.text,
            self.center_x,
            self.center_y,
            arcade.color.WHITE,
            40
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.back_to_menu()

    def back_to_menu(self):
        self.main_scene_manager.next_scene()


class DefenderView(arcade.View):
    def __init__(self, main_scene_manager):
        super().__init__()
        self.main_scene_manager = main_scene_manager
        self.window = main_scene_manager.window

        self.text = "Защита"

    def setup(self):
        ...

    def on_show(self):
        ...

    def on_update(self, delta_time):
        ...

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            self.text,
            self.center_x,
            self.center_y,
            arcade.color.WHITE,
            40
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.back_to_menu()

    def back_to_menu(self):
        self.main_scene_manager.next_scene()


class HealView(arcade.View):
    def __init__(self, main_scene_manager):
        super().__init__()
        self.main_scene_manager = main_scene_manager
        self.window = main_scene_manager.window

        self.text = "Лечение"

    def setup(self):
        ...

    def on_show(self):
        ...

    def on_update(self, delta_time):
        ...

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            self.text,
            self.center_x,
            self.center_y,
            arcade.color.WHITE,
            40
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.back_to_menu()

    def back_to_menu(self):
        self.main_scene_manager.next_scene()


# Пример функций - мини-игр
def attack_setup(main_scene_manager, *settings):
    attack_view = AttackView(main_scene_manager)
    main_scene_manager.window.show_view(attack_view)


def defender_setup(main_scene_manager, *settings):
    defender_view = DefenderView(main_scene_manager)
    main_scene_manager.window.show_view(defender_view)


def heal_setup(main_scene_manager, *settings):
    heal_view = HealView(main_scene_manager)
    main_scene_manager.window.show_view(heal_view)


def menu_setup(main_scene_manager, *settings):
    main_scene_manager.window.show_view(main_scene_manager.fight_box.menu_view)


# Динамические объекты
# <-------------------------------------------------------------------------------------------------------------------

# Переключается меду сценами, окнами и мини-играми
class SceneManager:
    def __init__(self, fight_box):
        self.fight_box = fight_box
        self.window = fight_box.window

        # Добавляем сцены в очередь: каждая сцена - функция, которая запускает механику мини-битвы
        self.scenes = [menu_setup, attack_setup, defender_setup, heal_setup]
        self.curr_scene_index = 0 # Индекс текущей сцены в очереди

        self.next_scene()

    # Запускаем следующую сцену
    def next_scene(self):
        func = self.scenes[self.curr_scene_index]
        if self.curr_scene_index != 0:
            self.curr_scene_index = 0  # Возвращаемся на меню после мини-боя
        func(self)  # Передаём себя, чтобы вернуться и запустить следующую сцену


# Окно отрисовки меню
class MenuView(arcade.View):
    def __init__(self, fight_box):
        super().__init__()
        self.fight_box = fight_box
        self.text = "Меню"

    def setup(self):
        ...

    def on_show(self):
        ...

    def on_update(self, delta_time):
        ...

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            self.text,
            self.center_x,
            self.center_y,
            arcade.color.WHITE,
            40,
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.KEY_1:
            self.to_attack()
        elif key == arcade.key.KEY_2:
            self.to_defender()
        elif key == arcade.key.KEY_3:
            self.to_heal()

    def to_attack(self):
        self.scene_manager = self.fight_box.scene_manager
        self.scene_manager.curr_scene_index = 1
        self.scene_manager.next_scene()

    def to_defender(self):
        self.scene_manager = self.fight_box.scene_manager
        self.scene_manager.curr_scene_index = 2
        self.scene_manager.next_scene()

    def to_heal(self):
        self.scene_manager = self.fight_box.scene_manager
        self.scene_manager.curr_scene_index = 3
        self.scene_manager.next_scene()


# Статичные объекты и спрайты
# <-------------------------------------------------------------------------------------------------------------------

# Задний фон, анимация фона, персонажи, враги
class Background:
    def __init__(self):
        ...

    def draw(self):
        ...


# Интерфейс, кнопки выбора действия, аура
class Interface:
    def __init__(self):
        ...



# Главное для запуска битвы
# <-------------------------------------------------------------------------------------------------------------------

# Содержит все объекты
class FightBox:
    def __init__(self, main_scene_manager):
        self.main_scene_manager = main_scene_manager # Ссылка на предыдущий менеджер сцен
        self.window = main_scene_manager.window # Ссылка на окно

        self.menu_view = MenuView(self)  # Окно отрисовки меню
        self.scene_manager = SceneManager(self) # Собственный менеджер сцен


# Функция для запуска общей битвы
def setup_fight(main_scene_manager):
    FightBox(main_scene_manager)


# Пример функции для запуска всей программы
if __name__ == "__main__":
    window = arcade.Window(1000, 800, "Общая битва", resizable=False, fullscreen=False)
    main_scene_manager = MainSceneManager(window)
    arcade.run()



# Описание
# <-------------------------------------------------------------------------------------------------------------------
"""
Если вы находитесь в меню, нажмите:
1 - чтобы перейти на атаку
2 - чтобы перейти на защиту
3 - чтобы перейти на лечение

Если вы играете мини-бой, нажмите:
пробел - чтобы вернуться на меню
"""
