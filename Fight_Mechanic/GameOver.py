import arcade


class GameOver(arcade.View):
    def __init__(self, scene_manager):
        super().__init__()

        self.scene_manager = scene_manager
        self.fb = scene_manager.fb

        arcade.schedule(self.stop, 3)

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "Game Over",
            self.center_x,
            self.center_y,
        )

    def stop(self, delta_time):
        arcade.unschedule(self.stop)
        self.scene_manager.back()


def setup_game_over(scene_manager):
    scene_manager.window.show_view(GameOver(scene_manager))
