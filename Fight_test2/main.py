import arcade


def attack_setup(main_scene_manager):
    print("attack")
    main_scene_manager.next_scene()

def defender_setup(main_scene_manager):
    print("defender")
    main_scene_manager.next_scene()

def heal_setup(main_scene_manager):
    print("heal")
    main_scene_manager.next_scene()

def menu_setup(main_scene_manager):
    # fight_box = main_scene_manager.fight_box
    # fight_box.window.show_view(fight_box.menu_view)
    print("menu")
    main_scene_manager.next_scene()


# Переключается меду сценами, окнами и мини-играми
class SceneManager:
    def __init__(self, fight_box):
        self.fight_box = fight_box

        # self.scenes = ["menu", "attack_mech", "defender_mech", "heal_mech"]
        self.scenes = [menu_setup, attack_setup, defender_setup, heal_setup]
        self.curr_scene_index = 0

        print("start")
        self.next_scene()

    def next_scene(self):
        if self.curr_scene_index >= len(self.scenes):
            print("stop")
        else:
            func = self.scenes[self.curr_scene_index]
            self.curr_scene_index += 1
            func(self)


class MenuScene:
    def __init__(self):
        ...


class MenuView(arcade.View):
    def init(self):
        ...

    def setup(self):
        ...

    def on_show(self):
        ...

    def update(self):
        ...

    def draw(self):
        ...


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


# <-------------------------------------------------------------------------------------------------------------------
# Содержит все объекты
class FightBox:
    def __init__(self, main_scene_manager):
        # self.main_scene_manager = main_scene_manager # Ссылка на предыдущий менеджер сцен
        # self.window = main_scene_manager.window # Ссылка на окно

        self.scene_manager = SceneManager(self) # Собственный менеджер сцен


def setup_fight(main_scene_manager):
    FightBox(main_scene_manager)


if __name__ == "__main__":
    main_scene_manager = None
    setup_fight(main_scene_manager)
