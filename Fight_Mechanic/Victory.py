import arcade


class Victory(arcade.View):
    def __init__(self, scene_manager):
        super().__init__()

        self.scene_manager = scene_manager
        self.fb = scene_manager.fb

        arcade.schedule(self.stop, 3)

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "Victory",
            self.center_x,
            self.center_y,
        )

    def stop(self, delta_time):
        arcade.unschedule(self.stop)
        self.scene_manager.back()


def setup_victory(scene_manager):
    scene_manager.window.show_view(Victory(scene_manager))
