from PIL import Image
import arcade
import io



class EasySprite():
    def __init__(self):
        ...

    @staticmethod
    def upscale_image( filename, scale):
        img = Image.open(filename)
        scale_factor = scale
        new_size = (img.width * scale_factor, img.height * scale_factor)
        new_img = img.resize(new_size, Image.NEAREST)
        img_bytes = io.BytesIO()
        new_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        texture = arcade.load_texture(img_bytes)
        return texture

    @staticmethod
    def upscale_texture(img, scale):
        scale_factor = scale
        new_size = (img.width * scale_factor, img.height * scale_factor)
        new_img = img.resize(new_size, Image.NEAREST)
        img_bytes = io.BytesIO()
        new_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        texture = arcade.load_texture(img_bytes)
        return texture

    class Animate():
        def __init__(self, sprite_file=None, step=32, fps=1, automatic=None):
            if sprite_file is None:
                self.lst_img_texture = []
                self.fps = fps
                self.step = step
                self.texture_change_time = 0
                self.current_texture = 0
            else:
                img = Image.open(sprite_file)
                self.lst_img_texture = []
                self.lst_img = []
                self.fps = fps
                self.step = step
                self.texture_change_time = 0
                self.current_texture = 0
                for i in range(img.width // step):
                    img_shot = img.crop((i * step, 0, (i * step) + step, img.height))
                    self.lst_img.append(img_shot)
                    img_bytes = io.BytesIO()
                    img_shot.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    texture = arcade.load_texture(img_bytes)
                    self.lst_img_texture.append(texture)

        def update(self, delta_time):
            self.texture_change_time += delta_time
            if self.texture_change_time >= 1 / self.fps:
                self.texture_change_time = 0
                self.current_texture += 1
                if self.current_texture >= len(self.lst_img_texture):
                    self.current_texture = 0

        def update_and_give(self, delta_time):
            self.texture_change_time += delta_time
            if self.texture_change_time >= 1 / self.fps:
                self.texture_change_time = 0
                self.current_texture += 1
                if self.current_texture >= len(self.lst_img_texture):
                    self.current_texture = 0
            return self.lst_img_texture[self.current_texture]

        def give_current_texture(self):
            return self.lst_img_texture[self.current_texture]

        def give_current_image(self):
            return self.lst_img[self.current_texture]

        def upscale_all(self, scale):
            self.lst_img_texture = []
            for img in self.lst_img:
                scale_factor = scale
                new_size = (img.width * scale_factor, img.height * scale_factor)
                new_img = img.resize(new_size, Image.NEAREST)
                img_bytes = io.BytesIO()
                new_img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                texture = arcade.load_texture(img_bytes)
                self.lst_img_texture.append(texture)


        def sprite_sheet_to_animate(self, sprite_file, step=32, fps=1, automatic=None):
            img = Image.open(sprite_file)
            self.fps = fps
            self.step = step
            self.texture_change_time = 0
            self.current_texture = 0
            for i in range(img.width // step):
                img_shot = img.crop((i * step, 0, (i * step) + step, img.height))
                img_bytes = io.BytesIO()
                img_shot.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                texture = arcade.load_texture(img_bytes)
                self.lst_img_texture.append(texture)


from arcade.types import Color

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Example"


class MyGame(arcade.Window):
    def __init__(self, width, height, title, side, color):
        super().__init__(width, height, title)
        self.width = width
        self.height = height

    def setup(self):
        heart_sprite_upscale = arcade.Sprite(EasySprite.upscale_image("Heart.png", 10)) # Моё увеличение
        heart_sprite_upscale.center_x = self.width // 3
        heart_sprite_upscale.center_y = self.height // 2

        heart_sprite_no = arcade.Sprite("Heart.png", scale=10) # Увеличение arcade
        heart_sprite_no.center_x = self.width // 3 * 2
        heart_sprite_no.center_y = self.height // 2

        self.bomb_sprite = Bomb() # Анимация с помощью доп класса
        self.bomb_sprite.center_x = self.width // 2
        self.bomb_sprite.center_y = self.height // 4

        self.bomb_animate = EasySprite.Animate(sprite_file="bomb-Sheet.png", fps=4, step=16)  # Анимация напрямую
        self.bomb_animate.upscale_all(10)
        self.bomb_sprite2 = arcade.Sprite(self.bomb_animate.give_current_texture())
        self.bomb_sprite2.center_x = self.width // 2
        self.bomb_sprite2.center_y = self.height // 4 * 3

        self.lst_sprite = arcade.SpriteList()
        self.lst_sprite.append(heart_sprite_upscale)
        self.lst_sprite.append(heart_sprite_no)
        self.lst_sprite.append(self.bomb_sprite)
        self.lst_sprite.append(self.bomb_sprite2)

    def on_draw(self):
        self.clear()
        self.lst_sprite.draw()

    def on_update(self, delta_time):
        """Передаем delta_time в update_animation"""
        self.bomb_sprite.update_animation(delta_time)
        self.bomb_sprite2.texture = self.bomb_animate.update_and_give(delta_time)


class Bomb(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.bomb_animate = EasySprite.Animate(sprite_file="bomb-Sheet.png", fps=4, step=16)  # fps=10
        self.bomb_animate.upscale_all(10)
        self.texture = self.bomb_animate.give_current_texture()

    def update_animation(self, delta_time: float = 1 / 60):
        # Передаем delta_time в update_and_give
        self.texture = self.bomb_animate.update_and_give(delta_time)




def setup_game(width=900, height=600, title="Flying squares", side=100, color="#ff40ff"):
    game = MyGame(width, height, title, side, color)
    game.setup()
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()