import arcade
from PIL import Image


class EasySprite:
    @staticmethod
    def load_image(image_path, scale=1):
        image = Image.open(image_path)
        image = EasySprite.resize_image(image, scale)
        return image

    @staticmethod
    def resize_image(image, scale):
        new_size = (round(image.width * scale), round(image.height * scale))
        image = image.resize(new_size, Image.Resampling.NEAREST)
        return image

    @staticmethod
    def resize_texture(texture, scale):
        image = texture.image
        new_image = EasySprite.resize_image(image, scale)
        texture = arcade.Texture(new_image)
        return texture
