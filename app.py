# Name: Иван, Date: 08.01.2026, WhatYouDo: создал файл для запуска всей игры

import arcade
from Fight_Mechanic.main import setup_fight
from StartGame.dialogMechanic import setup_menu


# Менеджер сцен для управления битвами, перемещением героев, диалог2ами и т.д.
class SceneManager:
    def __init__(self, window):
        self.window = window

        self.scenes = [setup_menu, setup_fight]
        self.curr_scene_index = 0

    def setup(self):
        self.curr_scene_index = 0
        self.next_scene()

    def next_scene(self):
        func = self.scenes[self.curr_scene_index]
        self.curr_scene_index += 1
        func(self)


if __name__ == "__main__":
    main_window = arcade.Window(1000, 700, "Общая битва", resizable=False, fullscreen=False)
    scene_manager = SceneManager(main_window)
    scene_manager.setup()
    arcade.run()


"""Описание - файл для запуска всей игры"""
