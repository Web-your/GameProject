# from PIL import Image
# import arcade
# import io
#
# class EasySprite:
#     @staticmethod
#     def upscale_image(filename, scale):
#         img = Image.open(filename)
#         scale_factor = scale
#         new_size = (img.width * scale_factor, img.height * scale_factor)
#         new_img = img.resize(new_size, Image.NEAREST)
#         img_bytes = io.BytesIO()
#         new_img.save(img_bytes, format='PNG')
#         img_bytes.seek(0)
#         texture = arcade.load_texture(img_bytes)
#         return texture
#
#     @staticmethod
#     def upscale_texture(img, scale):
#         scale_factor = scale
#         new_size = (img.width * scale_factor, img.height * scale_factor)
#         new_img = img.resize(new_size, Image.NEAREST)
#         img_bytes = io.BytesIO()
#         new_img.save(img_bytes, format='PNG')
#         img_bytes.seek(0)
#         texture = arcade.load_texture(img_bytes)
#         return texture
#
#     class Animate:
#         def __init__(self, sprite_file=None, step=32, fps=1, automatic=None):
#             if sprite_file is None:
#                 self.lst_img_texture = []
#                 self.fps = fps
#                 self.step = step
#                 self.texture_change_time = 0
#                 self.current_texture = 0
#             else:
#                 img = Image.open(sprite_file)
#                 self.lst_img_texture = []
#                 self.lst_img = []
#                 self.fps = fps
#                 self.step = step
#                 self.texture_change_time = 0
#                 self.current_texture = 0
#                 for i in range(img.width // step):
#                     img_shot = img.crop((i * step, 0, (i * step) + step, img.height))
#                     self.lst_img.append(img_shot)
#                     img_bytes = io.BytesIO()
#                     img_shot.save(img_bytes, format='PNG')
#                     img_bytes.seek(0)
#                     texture = arcade.load_texture(img_bytes)
#                     self.lst_img_texture.append(texture)
#
#         def update(self, delta_time):
#             self.texture_change_time += delta_time
#             if self.texture_change_time >= 1 / self.fps:
#                 self.texture_change_time = 0
#                 self.current_texture += 1
#                 if self.current_texture >= len(self.lst_img_texture):
#                     self.current_texture = 0
#
#         def update_and_give(self, delta_time):
#             self.texture_change_time += delta_time
#             if self.texture_change_time >= 1 / self.fps:
#                 self.texture_change_time = 0
#                 self.current_texture += 1
#                 if self.current_texture >= len(self.lst_img_texture):
#                     self.current_texture = 0
#             return self.lst_img_texture[self.current_texture]
#
#         def give_current_texture(self):
#             return self.lst_img_texture[self.current_texture]
#
#         def give_current_image(self):
#             return self.lst_img[self.current_texture]
#
#         def upscale_all(self, scale):
#             self.lst_img_texture = []
#             for img in self.lst_img:
#                 scale_factor = scale
#                 new_size = (round(img.width * scale_factor), round(img.height * scale_factor))
#                 new_img = img.resize(new_size, Image.NEAREST)
#                 img_bytes = io.BytesIO()
#                 new_img.save(img_bytes, format='PNG')
#                 img_bytes.seek(0)
#                 texture = arcade.load_texture(img_bytes)
#                 self.lst_img_texture.append(texture)
#
#         def sprite_sheet_to_animate(self, sprite_file, step=32, fps=1, automatic=None):
#             img = Image.open(sprite_file)
#             self.fps = fps
#             self.step = step
#             self.texture_change_time = 0
#             self.current_texture = 0
#             for i in range(img.width // step):
#                 img_shot = img.crop((i * step, 0, (i * step) + step, img.height))
#                 img_bytes = io.BytesIO()
#                 img_shot.save(img_bytes, format='PNG')
#                 img_bytes.seek(0)
#                 texture = arcade.load_texture(img_bytes)
#                 self.lst_img_texture.append(texture)

import arcade
from PIL import Image


def load_image(image_path: str, scale: float = 1):
    image = Image.open(image_path)
    image = resize(image, scale)
    return image


def load_texture(obj: str | Image.Image, scale: float = 1):
    if isinstance(obj, str):
        image = load_image(obj, scale)
    elif isinstance(obj, Image.Image):
        image = resize(obj, scale)
    else:
        raise TypeError('texture must be str or Image')

    texture = arcade.Texture(image)
    return texture


def resize(obj: str | Image.Image, scale: float = 1):
    if isinstance(obj, Image.Image):
        return resize_image(obj, scale)
    elif isinstance(obj, arcade.Texture):
        return resize_texture(obj, scale)
    else:
        raise TypeError('texture must be str or Image')


def resize_image(image: Image.Image, scale: float):
    new_size = (round(image.width * scale), round(image.height * scale))
    image = image.resize(new_size, Image.Resampling.NEAREST)
    return image


def resize_texture(texture: arcade.Texture, scale: float):
    image = texture.image
    new_image = resize_image(image, scale)
    texture = arcade.Texture(new_image)
    return texture


class Animate:
    def __init__(
            self,
            obj: str | Image.Image,
            scale: float = 1,
            step: int = 32,
            fps: int = 1,
            is_animate: bool = True,
            start_index: int = 0,
    ):
        image = load_image(obj, scale)

        self.texture_lst = []
        self.fps = fps
        self.step = round(step * scale)
        self.change_time = 0
        self.current_texture = start_index

        for i in range(image.width // self.step):
            img_shot = image.crop((i * self.step, 0, (i + 1) * self.step, image.height))
            texture = arcade.Texture(img_shot)
            self.texture_lst.append(texture)

        self.is_animate = is_animate

    def update(self, delta_time):
        if self.is_animate:
            self.change_time += delta_time
            if self.change_time >= 1 / self.fps:
                self.change_time = 0
                self.current_texture += 1
                if self.current_texture >= len(self.texture_lst):
                    self.current_texture = 0

    def update_and_give(self, delta_time):
        if self.is_animate:
            self.update(delta_time)
        return self.texture_lst[self.current_texture]

    def give_current_texture(self):
        return self.texture_lst[self.current_texture]

    def resize_all(self, scale: float):
        self.step *= scale
        for i, texture in enumerate(self.texture_lst):
            self.texture_lst[i] = resize_texture(texture, scale)

    def start(self):
        self.is_animate = True

    def stop(self):
        self.is_animate = False

    def setup(self, start_index: int = 0, is_animate: bool = True):
        self.current_texture = start_index
        self.change_time = 0
        self.is_animate = is_animate
