import arcade
import sys
import os

# Получаем абсолютный путь к текущему файлу
current_dir = os.path.dirname(os.path.abspath(__file__))
# Добавляем путь к папке с мини-игрой
heal_act_path = os.path.join(current_dir, "healFlySticksMechanic")
sys.path.insert(0, heal_act_path)  # Добавляем в начало списка путей

try:
    from healAct import HealTestView, GAME_WIDTH, GAME_HEIGHT

    print("Мини-игра успешно импортирована!")
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print(f"Путь поиска: {heal_act_path}")
    print(f"Содержимое папки: {os.listdir(heal_act_path) if os.path.exists(heal_act_path) else 'Папка не существует'}")
    # Создаём заглушку чтобы код мог работать
    HealTestView = None
    # Размеры для мини-игры (на случай если не импортировались)
    GAME_WIDTH = 800
    GAME_HEIGHT = 250

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Fight test"

BUTTON_WIDTH = 100
BUTTON_HEIGHT = 100
FIELD_HEIGHT = 200

CHARACTER_WIDTH = 120
CHARACTER_HEIGHT = 120
CHARACTER_VERTICAL_SPACING = 50
CHARACTER_Y_OFFSET = 50


class MainGameView(arcade.View):
    """Основное игровое вью"""

    def __init__(self, window):
        super().__init__(window)
        self.window = window

        self.heroes_list = arcade.SpriteList()
        self.enemies_list = arcade.SpriteList()
        self.buttons_list = arcade.SpriteList()
        self.field_list = arcade.SpriteList()
        self.selection_arrows = arcade.SpriteList()
        self.def_shield_list = arcade.SpriteList()

        self.field_texture_path = "ButtonsField.png"

        self.game_state = "IDLE"
        self.active_button = None

        self.arrow_normal_texture = "SelectArrow.png"
        self.arrow_active_texture = "SelectArrow_act.png"
        self.shield_texture = "DEF_icon.png"

        # Звуки
        self.button_select_sound = None
        self.action_start_sound = None

        self.hovered_target = None

        self.field_width = SCREEN_WIDTH * 0.8
        self.field_height = FIELD_HEIGHT
        self.field_x = SCREEN_WIDTH // 2
        self.field_y = FIELD_HEIGHT // 2

        # Переменные для мини-игры
        self.is_in_minigame = False
        self.selected_hero_for_heal = None

        # Здоровье героев
        self.hero_health = [100, 100, 100]  # HP для трёх героев

        # Текстовые объекты для здоровья
        self.health_texts = []

        # Загружаем звуки
        self.load_sounds()

        # Настраиваем игру
        self.setup()

    def load_sounds(self):
        """Загружаем звуковые файлы"""
        try:
            self.button_select_sound = arcade.load_sound("ButtonSelect.wav")
        except:
            print("Звук ButtonSelect.wav не найден")

        try:
            self.action_start_sound = arcade.load_sound("ActionStart.wav")
        except:
            print("Звук ActionStart.wav не найден")

    def play_sound(self, sound):
        """Воспроизвести звук если он загружен"""
        if sound:
            try:
                arcade.play_sound(sound)
            except:
                pass

    def setup(self):
        # Поле с кнопками
        try:
            field_sprite = arcade.Sprite(self.field_texture_path)
            field_sprite.scale_x = self.field_width / field_sprite.width
            field_sprite.scale_y = self.field_height / field_sprite.height
            field_sprite.center_x = self.field_x
            field_sprite.center_y = self.field_y
            self.field_list.append(field_sprite)
        except:
            print(f"Текстура поля не найдена: {self.field_texture_path}")

        button_y = self.field_y
        button_spacing = self.field_width / 3.5

        # Кнопка ATK
        atk_button = self.create_button_with_texture(
            self.field_x - button_spacing,
            button_y,
            "ATK.png",
            "ATK_act.png",
            'ATK'
        )
        self.buttons_list.append(atk_button)

        # Кнопка DEF
        def_button = self.create_button_with_texture(
            self.field_x,
            button_y,
            "DEF.png",
            "DEF_act.png",
            'DEF'
        )
        self.buttons_list.append(def_button)

        # Кнопка HEAL
        heal_button = self.create_button_with_texture(
            self.field_x + button_spacing,
            button_y,
            "HEAL.png",
            "HEAL_act.png",
            'HEAL'
        )
        self.buttons_list.append(heal_button)

        field_top = self.field_y + self.field_height // 2
        available_height = SCREEN_HEIGHT - field_top - CHARACTER_HEIGHT

        hero_x = SCREEN_WIDTH * 0.2

        hero_textures = ["hero1.png", "hero2.png", "hero3.png"]
        if len(hero_textures) > 1:
            total_character_height = len(hero_textures) * CHARACTER_HEIGHT
            total_spacing_height = (len(hero_textures) - 1) * CHARACTER_VERTICAL_SPACING
            total_required_height = total_character_height + total_spacing_height

            if total_required_height > available_height:
                spacing = (available_height - total_character_height) / (len(hero_textures) - 1)
            else:
                spacing = CHARACTER_VERTICAL_SPACING + CHARACTER_HEIGHT

            start_y = SCREEN_HEIGHT - CHARACTER_HEIGHT // 2 - 50

            for i in range(len(hero_textures)):
                hero_y = start_y - i * spacing

                hero = self.create_sprite_with_texture(
                    hero_x,
                    hero_y,
                    hero_textures[i],
                    CHARACTER_WIDTH, CHARACTER_HEIGHT,
                    arcade.color.RED if i == 0 else arcade.color.BLUE if i == 1 else arcade.color.GREEN
                )
                hero.is_hero = True
                hero.index = i
                hero.is_selectable = True
                self.heroes_list.append(hero)
        else:
            hero_y = SCREEN_HEIGHT // 2
            hero = self.create_sprite_with_texture(
                hero_x,
                hero_y,
                hero_textures[0],
                CHARACTER_WIDTH, CHARACTER_HEIGHT,
                arcade.color.RED
            )
            hero.is_hero = True
            hero.index = 0
            hero.is_selectable = True
            self.heroes_list.append(hero)

        enemy_x = SCREEN_WIDTH * 0.8

        if len(hero_textures) > 1:
            total_character_height = len(hero_textures) * CHARACTER_HEIGHT
            total_spacing_height = (len(hero_textures) - 1) * CHARACTER_VERTICAL_SPACING
            total_required_height = total_character_height + total_spacing_height

            if total_required_height > available_height:
                spacing = (available_height - total_character_height) / (len(hero_textures) - 1)
            else:
                spacing = CHARACTER_VERTICAL_SPACING + CHARACTER_HEIGHT

            start_y = SCREEN_HEIGHT - CHARACTER_HEIGHT // 2 - 50

            for i in range(len(hero_textures)):
                enemy_y = start_y - i * spacing

                enemy = self.create_sprite_with_texture(
                    enemy_x,
                    enemy_y,
                    "enemy.png",
                    CHARACTER_WIDTH, CHARACTER_HEIGHT,
                    arcade.color.PURPLE
                )
                enemy.is_hero = False
                enemy.index = i
                enemy.is_selectable = True
                self.enemies_list.append(enemy)
        else:
            enemy_y = SCREEN_HEIGHT // 2
            enemy = self.create_sprite_with_texture(
                enemy_x,
                enemy_y,
                "enemy.png",
                CHARACTER_WIDTH, CHARACTER_HEIGHT,
                arcade.color.PURPLE
            )
            enemy.is_hero = False
            enemy.index = 0
            enemy.is_selectable = True
            self.enemies_list.append(enemy)

    def create_button_with_texture(self, x, y, normal_texture_path, active_texture_path, button_type):
        try:
            button = arcade.Sprite(normal_texture_path)
            scale_x = BUTTON_WIDTH / button.width
            scale_y = BUTTON_HEIGHT / button.height
            button.scale = max(scale_x, scale_y)
        except:
            color = arcade.color.RED if 'ATK' in button_type else arcade.color.BLUE if 'DEF' in button_type else arcade.color.GREEN
            button = arcade.SpriteSolidColor(BUTTON_WIDTH, BUTTON_HEIGHT, color)

        button.center_x = x
        button.center_y = y
        button.type = button_type

        button.normal_texture_path = normal_texture_path
        button.active_texture_path = active_texture_path

        button.normal_color = arcade.color.RED if 'ATK' in button_type else arcade.color.BLUE if 'DEF' in button_type else arcade.color.GREEN
        button.active_color = arcade.color.SCARLET if 'ATK' in button_type else arcade.color.CYAN if 'DEF' in button_type else arcade.color.LIME_GREEN

        return button

    def create_sprite_with_texture(self, x, y, texture_path, width, height, fallback_color):
        try:
            sprite = arcade.Sprite(texture_path)
            scale_x = width / sprite.width
            scale_y = height / sprite.height
            sprite.scale = min(scale_x, scale_y)
        except:
            sprite = arcade.SpriteSolidColor(width, height, fallback_color)
            print(f"Текстура не найдена: {texture_path}")

        sprite.center_x = x
        sprite.center_y = y
        sprite.texture_path = texture_path

        return sprite

    def create_arrow_sprite(self, x, y, is_active=False):
        texture_path = self.arrow_active_texture if is_active else self.arrow_normal_texture

        try:
            arrow = arcade.Sprite(texture_path)
            arrow.scale = 0.15
        except:
            arrow = arcade.SpriteSolidColor(25, 25, arcade.color.ORANGE if is_active else arcade.color.YELLOW)
            print(f"Текстура стрелочки не найдена: {texture_path}")

        arrow.center_x = x
        arrow.center_y = y
        arrow.is_active = is_active

        return arrow

    def create_shield_sprite(self):
        """Создать спрайт щита для DEF"""
        try:
            shield = arcade.Sprite(self.shield_texture)
            shield.scale = 0.3
        except:
            shield = arcade.SpriteSolidColor(80, 80, arcade.color.SILVER)
            print(f"Текстура щита не найдена: {self.shield_texture}")

        # Размещаем щит между средними персонажем и врагом
        if len(self.heroes_list) >= 2 and len(self.enemies_list) >= 2:
            middle_hero = self.heroes_list[1]
            middle_enemy = self.enemies_list[1]

            shield_x = (middle_hero.center_x + middle_enemy.center_x) / 2
            shield_y = (middle_hero.center_y + middle_enemy.center_y) / 2
        else:
            shield_x = SCREEN_WIDTH // 2
            shield_y = SCREEN_HEIGHT // 2

        shield.center_x = shield_x
        shield.center_y = shield_y
        shield.is_shield = True

        return shield

    def show_selection_arrows(self, target_list):
        self.selection_arrows.clear()

        for target in target_list:
            if hasattr(target, 'is_selectable') and target.is_selectable:
                arrow_x = target.center_x
                arrow_y = target.center_y + target.height // 2 + 20

                arrow = self.create_arrow_sprite(arrow_x, arrow_y, False)
                arrow.target = target
                arrow.target_type = "hero" if target.is_hero else "enemy"

                self.selection_arrows.append(arrow)

    def clear_selection(self):
        self.selection_arrows.clear()
        self.def_shield_list.clear()
        self.game_state = "IDLE"
        self.active_button = None
        self.hovered_target = None

        for button in self.buttons_list:
            try:
                button.texture = arcade.load_texture(button.normal_texture_path)
            except:
                if hasattr(button, 'normal_color'):
                    button.color = button.normal_color

    def start_heal_minigame(self, hero_index):
        """Запустить мини-игру лечения"""
        if HealTestView is None:
            print("Мини-игра не загружена!")
            self.clear_selection()
            return

        self.is_in_minigame = True
        self.selected_hero_for_heal = hero_index

        # Создаем и запускаем мини-игру
        self.heal_game_view = HealTestView(
            on_complete_callback=self.on_heal_minigame_complete,
            target_hero_index=hero_index,
            parent_view=self
        )

        # Показываем мини-игру
        self.window.show_view(self.heal_game_view)

    def on_heal_minigame_complete(self, hero_index, success_rate, success_count):
        """Колбэк, вызываемый после завершения мини-игры"""
        # Выходим из режима мини-игры
        self.is_in_minigame = False

        # Вычисляем количество лечения на основе успешных попаданий
        heal_amount = success_count * 5  # 10 HP за каждое успешное попадание

        # Применяем лечение
        if 0 <= hero_index < len(self.hero_health):
            self.hero_health[hero_index] = min(100, self.hero_health[hero_index] + heal_amount)
            # Обновляем текст здоровья
            if hero_index < len(self.health_texts):
                self.health_texts[hero_index].text = f"HP: {self.hero_health[hero_index]}"
            print(f"Герой {hero_index} вылечен на {heal_amount} HP! Текущее HP: {self.hero_health[hero_index]}")

        # Возвращаемся к основному игровому виду
        self.window.show_view(self)

        # Очищаем выбор
        self.clear_selection()

    def on_draw(self):
        self.clear()

        # Если мы в мини-игре, её отрисовка происходит автоматически
        if not self.is_in_minigame:
            self.field_list.draw()
            self.buttons_list.draw()
            self.heroes_list.draw()
            self.enemies_list.draw()
            self.selection_arrows.draw()
            self.def_shield_list.draw()

            # Отображаем здоровье героев с использованием Text объектов
            for health_text in self.health_texts:
                health_text.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        # Если в мини-игре, пропускаем обработку
        if self.is_in_minigame:
            return

        if self.game_state == "IDLE":
            self.hovered_target = None
            for button in self.buttons_list:
                if button.collides_with_point((x, y)):
                    try:
                        button.texture = arcade.load_texture(button.active_texture_path)
                    except:
                        if hasattr(button, 'active_color'):
                            button.color = button.active_color
                else:
                    try:
                        button.texture = arcade.load_texture(button.normal_texture_path)
                    except:
                        if hasattr(button, 'normal_color'):
                            button.color = button.normal_color

        elif self.game_state in ["SELECTING_ENEMY", "SELECTING_HERO"]:
            current_hovered_target = None

            if self.game_state == "SELECTING_ENEMY":
                for enemy in self.enemies_list:
                    if enemy.collides_with_point((x, y)):
                        current_hovered_target = enemy
                        break
            elif self.game_state == "SELECTING_HERO":
                for hero in self.heroes_list:
                    if hero.collides_with_point((x, y)):
                        current_hovered_target = hero
                        break

            if current_hovered_target != self.hovered_target:
                self.hovered_target = current_hovered_target

                for i, arrow in enumerate(self.selection_arrows):
                    is_active = (arrow.target == current_hovered_target)

                    if arrow.is_active != is_active:
                        arrow.is_active = is_active
                        new_arrow = self.create_arrow_sprite(
                            arrow.center_x,
                            arrow.center_y,
                            is_active
                        )
                        new_arrow.target = arrow.target
                        new_arrow.target_type = arrow.target_type
                        self.selection_arrows[i] = new_arrow

    def on_mouse_press(self, x, y, button, modifiers):
        # Если в мини-игре, пропускаем обработку
        if self.is_in_minigame:
            return

        # Если мы в режиме выбора цели
        if self.game_state in ["SELECTING_ENEMY", "SELECTING_HERO"]:
            # Проверяем, нажали ли на стрелочку
            for arrow in self.selection_arrows:
                if arrow.collides_with_point((x, y)):
                    target = arrow.target
                    self.play_sound(self.action_start_sound)

                    if self.active_button == "ATK":
                        print(f"Атака на врага {target.index}!")
                        self.clear_selection()
                    elif self.active_button == "HEAL":
                        # Запускаем мини-игру лечения для выбранного героя
                        print(f"Запуск мини-игры лечения для героя {target.index}!")
                        self.start_heal_minigame(target.index)
                    return

            # Также проверяем нажатие на сами цели
            if self.game_state == "SELECTING_ENEMY":
                for enemy in self.enemies_list:
                    if enemy.collides_with_point((x, y)):
                        self.play_sound(self.action_start_sound)
                        print(f"Атака на врага {enemy.index} (нажатие на цель)!")
                        self.clear_selection()
                        return

            elif self.game_state == "SELECTING_HERO":
                for hero in self.heroes_list:
                    if hero.collides_with_point((x, y)):
                        self.play_sound(self.action_start_sound)
                        print(f"Запуск мини-игры лечения для героя {hero.index} (нажатие на цель)!")
                        self.start_heal_minigame(hero.index)
                        return

        # Проверяем нажатие на щит DEF
        for shield in self.def_shield_list:
            if shield.collides_with_point((x, y)):
                self.play_sound(self.action_start_sound)
                print("Защита активирована по щиту!")
                self.clear_selection()
                return

        # Обрабатываем нажатие на кнопки
        for button_sprite in self.buttons_list:
            if button_sprite.collides_with_point((x, y)):
                self.play_sound(self.button_select_sound)
                print(f"Нажата кнопка: {button_sprite.type}")

                # Если уже выбрана та же кнопка - отменяем
                if self.active_button == button_sprite.type:
                    print(f"Действие {button_sprite.type} отменено")
                    self.clear_selection()
                    return

                # Иначе очищаем предыдущий выбор
                self.clear_selection()

                # Обрабатываем разные кнопки
                if button_sprite.type == "ATK":
                    self.game_state = "SELECTING_ENEMY"
                    self.active_button = "ATK"
                    self.show_selection_arrows(self.enemies_list)
                    print("Выберите цель для атаки!")

                elif button_sprite.type == "HEAL":
                    self.game_state = "SELECTING_HERO"
                    self.active_button = "HEAL"
                    self.show_selection_arrows(self.heroes_list)
                    print("Выберите цель для лечения!")

                elif button_sprite.type == "DEF":
                    self.game_state = "SELECTING_DEF"
                    self.active_button = "DEF"
                    # Создаем щит и добавляем в список
                    shield_sprite = self.create_shield_sprite()
                    self.def_shield_list.append(shield_sprite)
                    print("Нажмите на щит для активации защиты!")

                try:
                    button_sprite.texture = arcade.load_texture(button_sprite.active_texture_path)
                except:
                    if hasattr(button_sprite, 'active_color'):
                        button_sprite.color = button_sprite.active_color


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        # Создаем и показываем основное игровое вью
        main_view = MainGameView(self)
        self.show_view(main_view)


def main():
    window = GameWindow()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()