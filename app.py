# """ Name: Иван, Date: 05.01.2026, WhatYouDo: пример объединения игры"""
import arcade

from Defender_Battle.main import setup_defender


# Пример, как можно объединить все бои и механики
class MainTimer:
    def __init__(self, window):
        self.window = window

        # Список сцен, боёв, механик
        self.scenes = ["Defender_Battle", "FlyArrowsMehanic", "Lines", "Persons_Dialogs", "Menu"]
        # Текущая сцена
        self.curr_index = 0

        # Вызываем следующую сцену
        self.next()

    def next(self):
        # Получаем сцену текущую
        scene = self.scenes[self.curr_index]

        # Обновляем индекс в списке так, как это надо (Или не обновляем вовсе)
        self.curr_index += 1

        # Запускаем нужную функцию в соответствии со сценой
        if scene == "Defender_Battle":
            setup_defender(self) # Запускаем текущую сцену, обязательно предаём главный таймер
        if scene == "FlyArrowsMehanic":
            print("FlyArrowsMehanic")
        ...


if __name__ == "__main__":
    window = arcade.Window(1200, 800, "Механика боя Защитника", resizable=False, fullscreen=False)
    timer = MainTimer(window)
    arcade.run()

"""
Чтобы начать бой, импортируем и запускаем функцию setup_defender
Она создаст временный объект Defender
При инициализации Defender автоматом переключится на новое окно боя
"""