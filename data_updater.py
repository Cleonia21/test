import threading
from tkinter import ttk
import tkinter as tk
from graph import LinearGraph, BarGraph

class DataUpdater:
    def __init__(self, count, window_builder):
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
        
        # Запускаем обновление в отдельном потоке
        threading.Thread(target=self._update_data, daemon=True).start()

    def _update_data(self):
        """Основная функция обновления данных"""
        try:
            # Получаем новые данные
            dataGraf1, dataGraf2, dataGraf3 = self.count.count()
            
            # Обновляем графики в основном потоке
            self.window.root.after(0, self._update_charts, dataGraf1, dataGraf2, dataGraf3)
            
        except Exception as e:
            self.window.root.after(0, self._show_error, str(e))
        finally:
            self.window.root.after(0, self._finish_update)

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

    def _show_error(self, error_msg):
        """Показывает сообщение об ошибке"""
        self.loading_label.config(text=f"Ошибка: {error_msg}", foreground="red")
        self.window.root.after(3000, self._hide_status_elements)

    def _finish_update(self):
        """Завершает процесс обновления"""
        self.progress.stop()
        self.loading_label.config(text="Готово!", foreground="green")
        self.update_button.config(state=tk.NORMAL)
        self.window.root.after(2000, self._hide_status_elements)