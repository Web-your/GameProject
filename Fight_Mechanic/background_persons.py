import arcade
import EasySprite


class HealthBar:
    def __init__(
            self,
            center_x: int,
            center_y: int,
            width: int = 100,
            height: int = 10,
            health_factor: float = 1
    ):
        self.health_factor = health_factor  # Доля здоровья

        self.width = width
        self.height = height
        self.center_x = center_x
        self.center_y = center_y

        self.curr_health_color = arcade.color.GREEN
        self.rest_health_color = arcade.color.RED
        self.frame_color = (100, 80, 80)

    def update(self, new_health_factor):
        self.health_factor = new_health_factor

    def draw(self):
        bottom = self.center_y - self.height // 2

        # Текущее здоровье (зелёный)
        curr_health_width = self.width * self.health_factor
        curr_health_left = self.center_x - self.width // 2
        arcade.draw_lbwh_rectangle_filled(
            curr_health_left,
            bottom,
            curr_health_width,
            self.height,
            self.curr_health_color
        )

        # Остаток здоровья до максимума (красный)
        rest_health_width = self.width - curr_health_width
        rest_health_left = curr_health_left + curr_health_width
        arcade.draw_lbwh_rectangle_filled(
            rest_health_left,
            bottom,
            rest_health_width,
            self.height,
            self.rest_health_color
        )

        # Обводка
        arcade.draw_lbwh_rectangle_outline(
            self.center_x - self.width // 2,
            self.center_y - self.height // 2,
            self.width,
            self.height,
            self.frame_color,
            2
        )


class BackgroundPerson(arcade.Sprite):
    def __init__(self, x, y, texture_path, img_count=1):
        super().__init__(x, y)

        self.center_x = x
        self.center_y = y

        self.animation = EasySprite.Animate(texture_path, img_count, 1.5, 8, True)
        self.texture = self.animation.get_current_texture()
        self.scale = 1

        self.health_bar = HealthBar(
            int(self.center_x),
            int(self.center_y) + self.texture.height // 2,
            self.texture.width,
        )

    def update_animation(self, delta_time):
        self.texture = self.animation.update_and_get(delta_time)


class BackPersBox:
    def __init__(self, fb):
        self.fb = fb
        width = self.fb.width

        self.sprite_list = arcade.SpriteList()

        # Создаём героев
        self.attack_pers = BackgroundPerson(
            100,
            350,
            "Fight_Mechanic/Static/background_persons/Attacker.png",
        )
        self.sprite_list.append(self.attack_pers)

        self.defense_pers = BackgroundPerson(
            100,
            350 + 120,
            "Fight_Mechanic/Static/background_persons/Attacker.png",
        )
        self.sprite_list.append(self.defense_pers)

        self.heal_pers = BackgroundPerson(
            100,
            350 + 120 * 2,
            "Fight_Mechanic/Static/background_persons/Attacker.png",
        )
        self.sprite_list.append(self.heal_pers)

        # Создаём врагов
        self.enemies0 = BackgroundPerson(
            width - 100,
            350,
            "Fight_Mechanic/Static/background_persons/Sprits_Per-Sheet.png",
            3
        )
        self.sprite_list.append(self.enemies0)

        self.enemies1 = BackgroundPerson(
            width - 100,
            350 + 120,
            "Fight_Mechanic/Static/background_persons/Sprits_Per-Sheet.png",
            3
        )
        self.sprite_list.append(self.enemies1)

        self.enemies2 = BackgroundPerson(
            width - 100,
            350 + 120 * 2,
            "Fight_Mechanic/Static/background_persons/Sprits_Per-Sheet.png",
            3
        )
        self.sprite_list.append(self.enemies2)

        self.hero_dict = {
            "attack": self.attack_pers,
            "defense": self.defense_pers,
            "heal": self.heal_pers
        }
        self.enemies_list = [self.enemies0, self.enemies1, self.enemies2]

    def draw(self):
        self.sprite_list.draw()
        for person in self.sprite_list:
            person.health_bar.draw()

    def update(self, delta_time):
        self.sprite_list.update_animation(delta_time)
