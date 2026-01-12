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
