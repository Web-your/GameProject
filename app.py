# Name: Иван, Date: 08.01.2026, WhatYouDo: создал файл для запуска всей игры

import arcade
from Fight_Mechanic.main import setup_fight


# Менеджер сцен для управления битвами, перемещением героев, диалогами и т.д.
class SceneManager:
    def __init__(self, window):
        self.window = window

    def setup(self):
        # Начинаем одну полноценную боёвку
        setup_fight(self)


if __name__ == "__main__":
    main_window = arcade.Window(1000, 800, "Общая битва", resizable=False, fullscreen=False)
    scene_manager = SceneManager(main_window)
    scene_manager.setup()
    arcade.run()


"""Описание - файл для запуска всей игры"""
