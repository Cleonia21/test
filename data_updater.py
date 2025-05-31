import threading
from tkinter import ttk
import tkinter as tk
from graph import LinearGraph, BarGraph
from count import Count
from window_builder import WindowBuilder

class DataUpdater:
    def __init__(self, count: Count, window_builder: WindowBuilder):
        """
        Инициализация обновления данных
        
        :param count: объект Count для получения данных
        :param window_builder: объект WindowBuilder с элементами интерфейса
        """
        self.count = count
        self.window = window_builder
        
        # Настраиваем кнопку обновления
        self.update_button = self.window.update_button
        self.update_button.config(command=self._start_update_process)
        
        # Создаем элементы для отображения статуса обновления
        self.status_frame = ttk.Frame(self.window.update_button.master)
        self.status_frame.pack(side=tk.RIGHT, padx=10)
        
        self.loading_label = ttk.Label(self.status_frame, text="")
        self.loading_label.pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(
            self.status_frame,
            orient=tk.HORIZONTAL,
            length=100,
            mode='indeterminate'
        )
        
        # Изначально скрываем элементы статуса
        self._hide_status_elements()

    def _start_update_process(self):
        """Запускает процесс обновления в отдельном потоке"""
        # Блокируем кнопку на время обновления
        self.update_button.config(state=tk.DISABLED)
        self._show_status("Обновление данных...")
        self.progress.start()
        self.count.dataCollection()
        
        # Запускаем обновление в отдельном потоке
        threading.Thread(target=self._update_data, daemon=True).start()

    def _validate_graph_data(self, dataGraf1, dataGraf2, dataGraf3):
        """Проверяет данные графиков на корректность"""
        # Проверка на пустые данные
        if not dataGraf1 or not dataGraf2 or not dataGraf3:
            raise ValueError("Один или несколько графиков содержат пустые данные")
        
        # Проверка структуры данных для каждого графика
        self._validate_linear_graph_data(dataGraf1, "График 1")
        self._validate_bar_graph_data(dataGraf2, "График 2")
        self._validate_linear_graph_data(dataGraf3, "График 3")

    def _validate_linear_graph_data(self, graph_data, graph_name):
        """Проверяет данные для линейного графика"""
        if not isinstance(graph_data, dict):
            raise TypeError(f"{graph_name}: Ожидался словарь данных, получен {type(graph_data)}")
        
        # for plane_name, data_points in graph_data.items():
        #     if not isinstance(plane_name, str):
        #         raise TypeError(f"{graph_name}: Ключи должны быть строками (названиями плоскостей)")
            
        #     if not isinstance(data_points, tuple) or len(data_points) != 2:
        #         raise ValueError(f"{graph_name}: Данные должны быть кортежем из двух элементов (x, y)")
            
        #     x_data, y_data = data_points
            
        #     if not isinstance(x_data, (list, tuple)) or not isinstance(y_data, (list, tuple)):
        #         raise TypeError(f"{graph_name}: Данные x и y должны быть списками или кортежами")
            
        #     if len(x_data) != len(y_data):
        #         raise ValueError(f"{graph_name}: Данные x и y должны иметь одинаковую длину")
            
        #     if len(x_data) == 0:
        #         raise ValueError(f"{graph_name}: Нет данных для плоскости {plane_name}")

    def _validate_bar_graph_data(self, graph_data, graph_name):
        """Проверяет данные для столбчатого графика"""
        if not isinstance(graph_data, dict):
            raise TypeError(f"{graph_name}: Ожидался словарь данных, получен {type(graph_data)}")
        
        # if len(graph_data) == 0:
        #     raise ValueError(f"{graph_name}: Нет данных для отображения")
        
        # for category, value in graph_data.items():
        #     if not isinstance(category, str):
        #         raise TypeError(f"{graph_name}: Ключи должны быть строками (категориями)")
            
        #     if not isinstance(value, (int, float)):
        #         raise TypeError(f"{graph_name}: Значения должны быть числами, получен {type(value)} для категории {category}")

    def _update_data(self):
        """Основная функция обновления данных"""
        try:
            # Получаем новые данные
            dataGraf1, dataGraf2, dataGraf3 = self.count.count()
            
            # Комплексная проверка данных
            self._validate_graph_data(dataGraf1, dataGraf2, dataGraf3)
            
            # Обновляем графики в основном потоке
            self.window.root.after(0, lambda: self._update_charts(dataGraf1, dataGraf2, dataGraf3))
            self.window.root.after(0, lambda: self._finish_update(success=True))
            
        except Exception as e:
            error_msg = str(e)
            self.window.root.after(0, lambda: self._finish_update(success=False, error_msg=error_msg))

    def _update_charts(self, dataGraf1, dataGraf2, dataGraf3):
        """Обновляет графики с новыми данными"""
        # Получаем области графиков из window_builder
        chart_areas = [
            self.window.chart_area_1,
            self.window.chart_area_2,
            self.window.chart_area_3
        ]
        
        # Очищаем предыдущие графики
        for area in chart_areas:
            for widget in area.winfo_children():
                widget.destroy()
        
        # Строим новые графики
        graph = LinearGraph()
        for planeName, (x, y) in dataGraf1.items():
            graph.add_data_set(dataGraf1[planeName][x], dataGraf1[planeName][y], {'label': planeName})
        graph.build(x_label="количество", y_label="эфективность")
        graph.display(chart_areas[0])

        graph = BarGraph(dataGraf2.keys(), dataGraf2.values())
        graph.build(x_label="АК", y_label="эффективность")
        graph.display(chart_areas[1])

        graph = LinearGraph()
        for planeName, (x, y) in dataGraf3.items():
            graph.add_data_set(dataGraf3[planeName][x], dataGraf3[planeName][y], {'label': planeName})
        graph.build(x_label="v", y_label="k")
        graph.display(chart_areas[2])

    def _show_status(self, message):
        """Показывает статус обновления"""
        self.loading_label.config(text=message, foreground="black")
        self.progress.pack(side=tk.LEFT, padx=(5, 0))
        self.status_frame.pack(side=tk.RIGHT, padx=10)

    def _hide_status_elements(self):
        """Скрывает элементы статуса"""
        self.progress.pack_forget()
        self.loading_label.config(text="")
        self.status_frame.pack_forget()

    def _finish_update(self, success=True, error_msg=None):
        """Завершает процесс обновления"""
        self.progress.stop()
        
        if success:
            self.loading_label.config(text="Готово!", foreground="green")
        else:
            self.loading_label.config(text=f"Ошибка: {error_msg}", foreground="red")
            print(f"Ошибка: {error_msg}")
        
        self.update_button.config(state=tk.NORMAL)
        
        # Прячем статус через 3 секунды (если ошибка) или 2 секунды (если успех)
        delay = 10000 if not success else 2000
        self.window.root.after(delay, self._hide_status_elements)