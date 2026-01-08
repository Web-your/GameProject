from PIL import Image
import arcade
import io

class EasySprite:
    @staticmethod
    def upscale_image(filename, scale):
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

    class Animate:
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
