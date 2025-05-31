import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass

@dataclass
class FormData:
    """Класс для хранения данных одной формы"""
    form: ttk.Frame
    title: ttk.Label
    show_button: ttk.Button
    entry_field: ttk.Entry
    save_button: ttk.Button
    delete_button: ttk.Button
    msg_label: ttk.Label

class WindowBuilder:
    def __init__(self, root):
        """
        Инициализация панели
        
        :param root: корневое окно Tkinter
        """
        self.root = root
        self.input_window = None  # Ссылка на окно с формами ввода
        
        # Публичные переменные для основных областей
        self.update_button = None     # Кнопка обновления (заменяет update_area)
        self.edit_data_button = None  # Кнопка для открытия окна с формами
        self.chart_area_1 = None    # Область для графика 1
        self.chart_area_2 = None    # Область для графика 2
        self.chart_area_3 = None    # Область для графика 3
        
        # Список объектов FormData для хранения информации о формах
        self.forms_data: FormData = []
        
    def build(self):
        """
        Создает и возвращает полностью настроенный интерфейс
        """
        self._create_main_structure()
        self._create_input_window()  # Создаем окно с формами (но пока не показываем)
    
    def _create_main_structure(self):
        """Создает основную структуру разделов окна"""
        # Главный вертикальный контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя панель с сообщениями и кнопками
        top_panel = ttk.Frame(main_frame)
        top_panel.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопка обновления (справа)
        self.update_button = ttk.Button(
            top_panel, 
            text="Построить графики",
            width=20
        )
        self.update_button.pack(side=tk.RIGHT, padx=5)
        
        # Кнопка для открытия окна с формами
        self.edit_data_button = ttk.Button(
            top_panel,
            text="Изменить данные",
            width=18,
            command=self._show_input_window
        )
        self.edit_data_button.pack(side=tk.RIGHT, padx=5)
        
        # Основная область с графиками
        charts_paned = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        charts_paned.pack(fill=tk.BOTH, expand=True)

        # Области для графиков
        self.chart_area_1 = ttk.Frame(charts_paned)
        charts_paned.add(self.chart_area_1, weight=1)

        self.chart_area_2 = ttk.Frame(charts_paned)
        charts_paned.add(self.chart_area_2, weight=1)

        self.chart_area_3 = ttk.Frame(charts_paned)
        charts_paned.add(self.chart_area_3, weight=1)
    
    def _create_input_window(self):
        """Создает отдельное окно с формами ввода"""
        self.input_window = tk.Toplevel(self.root)
        self.input_window.geometry("800x1000")
        self.input_window.title("Редактирование данных")
        self.input_window.withdraw()  # Скрываем окно при создании
        
        # Настраиваем прокручиваемую область с формами ввода
        scrollable_frame = self._create_scroll_container(self.input_window)

        for i in range(5):
            self._create_input_form(scrollable_frame)
            
        # Настраиваем поведение при закрытии окна
        self.input_window.protocol("WM_DELETE_WINDOW", self._hide_input_window)
    
    def _show_input_window(self):
        """Показывает окно с формами ввода"""
        if self.input_window:
            self.input_window.deiconify()
            self.input_window.focus_set()
    
    def _hide_input_window(self):
        """Скрывает окно с формами ввода вместо закрытия"""
        self.input_window.withdraw()
    
    def _create_input_form(self, parent):
        """Создает одну форму ввода с элементами управления"""
        # Создаем контейнер для формы
        form = ttk.Frame(parent, relief=tk.RAISED, borderwidth=2, padding=10)
        form.pack(fill=tk.X, pady=5, ipadx=5, ipady=5)
        
        # Создаем элементы формы

        # Сообщение об ошибках (слева)
        msg_label = ttk.Label(form)
        msg_label.pack(fill=tk.X, pady=5)

        lbl_title = ttk.Label(form, font=('Arial', 10, 'bold'))
        lbl_title.pack(anchor='center', pady=(0, 5))  # Изменено на center
        
        btn_show = ttk.Button(form, text="Показать все", width=len("Показать все "))
        btn_show.pack(anchor='w', pady=2)
        
        entry_delete_frame = ttk.Frame(form)
        entry_delete_frame.pack(fill=tk.X, pady=5)

        btn_delete = ttk.Button(
            entry_delete_frame, 
            text="Удалить", 
            style='Danger.TButton', 
            width=len("Удалить ")
        )
        btn_delete.pack(side=tk.LEFT, padx=(0, 5))
        
        entry = ttk.Entry(entry_delete_frame)
        entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        btn_save = ttk.Button(form, text="Сохранить", width=len("Сохранить "))
        btn_save.pack(anchor='w', pady=2)
        
        # Создаем и сохраняем объект с данными формы
        form_data = FormData(
            form=form,
            msg_label=msg_label,
            title=lbl_title,
            show_button=btn_show,
            entry_field=entry,
            save_button=btn_save,
            delete_button=btn_delete
        )
        self.forms_data.append(form_data)
    
    def _create_scroll_container(self, parent):
        """Создает контейнер с вертикальной прокруткой"""
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(container)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="frame")
        
        def _configure_scroll(event):
            canvas.itemconfig("frame", width=canvas.winfo_width())
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        canvas.bind("<Configure>", _configure_scroll)
        
        return scrollable_frame