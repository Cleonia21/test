import logging
from tkinter import messagebox
import traceback
from typing import Callable, Optional

class ErrorHandler:
    """Обработчик ошибок: логирует в консоль и показывает сообщение пользователю."""
    
    def __init__(self, app_name: str = "Приложение"):
        """
        :param app_name: Название приложения (для заголовка ошибки).
        """
        self.app_name = app_name
        self._setup_logging()

    def _setup_logging(self):
        """Настройка логирования в консоль."""
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )

    def handle(
        self,
        error: Exception,
        user_message: Optional[str] = None,
        show_traceback: bool = False
    ):
        """
        Обрабатывает ошибку: логирует и показывает сообщение.
        
        :param error: Исключение (Exception).
        :param user_message: Сообщение для пользователя (если None, берётся str(error)).
        :param show_traceback: Показывать ли технические детали (traceback) пользователю.
        """
        # Логируем ошибку
        logging.error(f"Ошибка: {error}\n{traceback.format_exc()}")

        # Формируем сообщение для пользователя
        if user_message is None:
            user_message = str(error)
        
        if show_traceback:
            user_message += f"\n\nДетали:\n{traceback.format_exc()}"

        # Показываем ошибку в GUI
        messagebox.showerror(
            title=f"Ошибка в {self.app_name}",
            message=user_message
        )

    def wrap(self, func: Callable):
        """Декоратор для автоматической обработки ошибок в функциях."""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.handle(e)
        return wrapper