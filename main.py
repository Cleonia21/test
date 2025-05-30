from graph import *
from window_builder import WindowBuilder
import tkinter as tk
from data_base import DatabaseManager
from form_manager import FormManager
from count import Count
from data_updater import DataUpdater
from error_handler import ErrorHandler
from db_cache import DBCache
from entities import *

# Пример использования
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1500x1000")

    error_handler = ErrorHandler()
    cache = DBCache()

    window = WindowBuilder(root)
    window.build()

    db = DatabaseManager()

    for i, type in enumerate(BASE_CLASSES_MAP.keys()):
        FormManager(db, window.forms_data[i], type, cache, error_handler)

    count = Count(db)

    # Создаем объект для обновления данных
    data_updater = DataUpdater(
        count=count,
        window_builder=window
    )

    graph = LinearGraph()
    graph.build(x_label="количество", y_label="эфективность")
    graph.display(window.chart_area_1)

    graph = BarGraph({0}, {0})
    graph.build(x_label="АК", y_label="эффективность")
    graph.display(window.chart_area_2)

    graph = LinearGraph()
    graph.build(x_label="v", y_label="k")
    graph.display(window.chart_area_3)

    root.mainloop()


'''
Описания основных компонентов приложения(в порядке вызова):

    * WindowBuilder() - Заполняет графическое окно пустыми контейнерами(для последующего заполнения графичискими элементами),
с необходимыми характеристиками(размер, местоположение и т.д.)

    * DatabaseManager() - Подключается/создает базу данных, предоставляет функции для управления данными

    * ErrorHandler() - Отображает уводомления/ошибки на графическом экране - Не верное описание

    * FormManager() - Создает и вставляет на экран "блоки" по работе с объектами(самолет, ракета и т.д.).
Каждый блок содержит кнопки "удалить", "сохранить", "отобразить" и имеет поля для вписывания данных.
Так же кнопкам передается объект БД, для манипуляций с данными.

    * Count() - ...

    * DataUpdater() - Пользуясь объектом count обновляет графики

    * LinearGraph(), BarGraph() родственные классы отрисовывающие линейный, столбчатый график.

Другие(вспомогательные) компоненнты:

    * Entities - Базовые типы приложения, используемые всеми компонентами программы


'''