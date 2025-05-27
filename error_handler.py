import tkinter as tk
from tkinter import ttk
from typing import Tuple

class ErrorHandler:
    def __init__(self, label_widget: ttk.Label):
        """
        Инициализация обработчика сообщений с указанным виджетом Label.
        
        :param label_widget: виджет ttk.Label, в который будут выводиться сообщения
        """
        self.label = label_widget
        self._create_styles()
        
    def _create_styles(self):
        """Создает необходимые стили для виджета Label."""
        style = ttk.Style()
        
        # Стиль для успешных сообщений
        style.configure("ErrorHandler.Success.TLabel", 
                      background="green", 
                      foreground="white",
                      padding=5)
        
        # Стиль для ошибок
        style.configure("ErrorHandler.Error.TLabel", 
                      background="red", 
                      foreground="white",
                      padding=5)
        
        # Стиль по умолчанию
        style.configure("ErrorHandler.Default.TLabel",
                      padding=5)
    
    def show_message(self, result: Tuple[bool, str]) -> None:
        """
        Отображает сообщение с цветным фоном на основе результата операции.
        
        :param result: Кортеж (статус_успеха, сообщение)
                      где статус_успеха - bool (True = успех, False = ошибка)
        """
        is_success, message = result
        self.clear()
        
        # Устанавливаем текст и стиль
        self.label.config(text=message)
        if is_success:
            self.label.config(style="ErrorHandler.Success.TLabel")
        else:
            self.label.config(style="ErrorHandler.Error.TLabel")
    
    def clear(self):
        """Очищает Label и возвращает стандартный стиль."""
        self.label.config(text="", style="ErrorHandler.Default.TLabel")