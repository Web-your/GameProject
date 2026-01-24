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
            img_count: int = 1,
            scale: float = 1,
            fps: int = 1,
            is_animate: bool = False,
            start_index: int = 0,
    ):
        image = load_image(obj, scale)

        self.texture_lst = []
        self.img_count = img_count

        self.fps = fps
        self.change_time = 0
        self.current_texture = start_index

        self.step = image.width // img_count

        self.width = image.width
        self.height = image.height

        for i in range(img_count):
            img_shot = image.crop((i * self.step, 0, (i + 1) * self.step, self.height))
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

    def update_and_get(self, delta_time):
        if self.is_animate:
            self.update(delta_time)
        return self.texture_lst[self.current_texture]

    def get_current_texture(self):
        return self.texture_lst[self.current_texture]

    def get_texture_lst(self):
        return self.texture_lst

    def resize_all(self, scale: float):
        self.step  = round(scale * self.step)
        self.width = round(self.width * scale)
        self.height = round(self.height * scale)
        for i, texture in enumerate(self.texture_lst):
            self.texture_lst[i] = resize_texture(texture, scale)

    def start(self, fps: int | None = None):
        if fps:
            self.fps = fps
        self.is_animate = True

    def stop(self):
        self.is_animate = False

    def setup(self, start_index: int = 0, is_animate: bool = True):
        self.current_texture = start_index
        self.change_time = 0
        self.is_animate = is_animate
