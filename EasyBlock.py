import arcade
from  PIL import Image
from EazySprite import EasySprite


class VisualBlock:
    def __init__(
            self,
            var1: int,
            var2: int,
            var3: int,
            var4: int,
            base_fon_color: tuple | arcade.color.Color = arcade.color.BLACK,
            base_frame_color: tuple | arcade.color.Color = arcade.color.WHITE,
            base_frame_width: int = 2,
            show_fon: bool = True,
            show_frame: bool = True,
            show_pulse_fon: bool = True,
            show_pulse_frame: bool = True,
            base_pulse_time: float = 0.5,
            creation_type: str = "XYWH"
    ):
        creation_type = creation_type.upper()
        if creation_type == "XYWH":
            self.center_x = var1
            self.center_y = var2

            self.width = var3
            self.height = var4

            self.left = self.center_x - self.width // 2
            self.bottom = self.center_y - self.height // 2
            self.right = self.left + self.width
            self.top = self.bottom + self.height

        elif creation_type == "LBWH":
            self.left = var1
            self.bottom = var2

            self.width = var3
            self.height = var4

            self.right = self.left + self.width
            self.top = self.bottom + self.height

            self.center_x = self.left + self.width // 2
            self.center_y = self.bottom + self.height // 2

        elif creation_type == "LBXY":
            self.left = var1
            self.bottom = var2

            self.center_x = var3
            self.center_y = var4

            self.right = self.left + self.center_x * 2
            self.top = self.bottom + self.center_y * 2

            self.width = self.right - self.left
            self.height = self.top - self.bottom

        else:
            raise ValueError("Invalid creation type")
        
        self.base_fon_color = base_fon_color
        self.base_frame_color = base_frame_color
        self.base_frame_width = base_frame_width
        
        self.show_fon = show_fon
        self.show_frame = show_frame
        
        self.show_pulse_fon =  show_pulse_fon
        self.show_pulse_frame = show_pulse_frame
        self.base_pulse_time = base_pulse_time
        
        self.is_pulse_fon = False
        self.is_pulse_frame = False
        
        self.curr_fon_color = base_fon_color
        self.curr_frame_color = base_frame_color
        self.curr_frame_width = base_frame_width
        
        self.rect = arcade.XYWH(
            self.center_x,
            self.center_y,
            self.width,
            self.height
        )
    
    def draw(self):
        if self.show_fon:
            arcade.draw_rect_filled(self.rect, self.base_fon_color)
        if self.show_frame:
            arcade.draw_rect_outline(self.rect, self.base_frame_color, self.curr_frame_width)
    
    def pulse_fon(self, color, time=None):
        if self.show_pulse_fon:
            if not self.is_pulse_fon:
                if time is None:
                    time = self.base_pulse_time
                self.curr_fon_color = color
                arcade.schedule(self.stop_pulse_fon, time)
    
    def stop_pulse_fon(self):
        arcade.unschedule(self.stop_pulse_fon)
        self.is_pulse_fon = False
        self.curr_fon_color = self.base_fon_color

    def pulse_frame(self, color=None, width=None, time=None):
        if self.show_pulse_frame:
            if not self.is_pulse_frame:
                if color is None:
                    color = self.base_frame_color
                if width is None:
                    width = self.base_frame_width
                if time is None:
                    time = self.base_pulse_time
                self.curr_frame_color = color
                self.curr_frame_width = width
                arcade.schedule(self.stop_pulse_frame, time)

    def stop_pulse_frame(self):
        arcade.unschedule(self.stop_pulse_frame)
        self.is_pulse_frame = False
        self.curr_frame_color = self.base_frame_color
        self.curr_frame_width = self.base_frame_width


class TextureBlock:
    def __init__(
            self,
            var1: int,
            var2: int,
            orig_image,
            scale: float = 1,
            creation_type: str = "LB"
    ):
        if isinstance(orig_image, str):
            orig_image = Image.open(orig_image)

        self.image = EasySprite.resize_image(orig_image, scale)
        self.texture = arcade.Texture(self.image)

        self.width = self.image.width
        self.height = self.image.height
        self.size = [self.width, self.height]

        creation_type = creation_type.upper()
        if creation_type == "LB":
            self.left = var1
            self.bottom = var2
            self.right = self.left + self.width
            self.top = self.bottom + self.height

            self.center_x = self.left + self.width // 2
            self.center_y = self.bottom + self.height // 2

        elif creation_type == "XY":
            self.center_x = var1
            self.center_y = var2

            self.left = self.center_x - self.width // 2
            self.bottom = self.center_y - self.height // 2
            self.right = self.left + self.width
            self.top = self.bottom + self.height

        else:
            raise ValueError("Invalid creation type")

        self.rect = arcade.XYWH(
            self.center_x,
            self.center_y,
            self.width,
            self.height
        )

    def draw(self):
        arcade.draw_texture_rect(self.texture, self.rect)

    def resize(self, scale):
        self.image = EasySprite.resize_image(self.image, scale)
        self.texture = arcade.Texture(self.image)

        self.width = self.image.width
        self.height = self.image.height

        self.rect = arcade.XYWH(
            self.center_x,
            self.center_y,
            self.width,
            self.height
        )
