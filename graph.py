import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import copy

class BaseGraph:
    """Базовый класс для графиков с общими методами"""
    
    def __init__(self):
        self.figure = None
        self.canvas = None
        self.toolbar = None
        self.zoom_button = None
        self.zoom_icon = None
        # Загружаем иконку при инициализации
        self._load_zoom_icon()
    
    def _setup_figure(self, figsize=(8, 4), dpi=100):
        """Настройка базовой фигуры"""
        self.figure = Figure(figsize=figsize, dpi=dpi)
        self.ax = self.figure.add_subplot(111)
    
    def _load_zoom_icon(self):
        """Загружает иконку лупы из файла"""
        try:
            from PIL import Image, ImageTk
            # Предполагаем, что файл называется 'zoom_icon.png' и лежит в той же папке
            image = Image.open("pictures/zoom_icon.png")
            image = image.resize((16, 16), Image.LANCZOS)  # Ресайз до нужного размера
            self.zoom_icon = ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Не удалось загрузить иконку: {e}")
            # Фолбэк на простую текстовую кнопку
            self.zoom_icon = None

    def _create_zoom_button(self, parent):
        """Создает кнопку увеличения с загруженной иконкой или текстом"""
        if self.zoom_icon:
            btn = tk.Button(
                parent,
                image=self.zoom_icon,
                command=self.show_in_new_window,
                bd=0,
                bg='white',
                activebackground='lightgray',
                relief=tk.FLAT
            )
        else:
            # Фолбэк вариант если иконка не загрузилась
            btn = tk.Button(
                parent,
                text="+",
                command=self.show_in_new_window,
                bd=0,
                bg='white',
                activebackground='lightgray',
                fg='gray',
                font=('Arial', 10, 'bold'),
                relief=tk.FLAT,
                width=2,
                height=1
            )
        return btn
    
    def display(self, root, show_toolbar=True, show_zoom_button=True, pack_options=None):
        """
        Отображает график в Tkinter окне.
        """
        if self.figure is None:
            raise ValueError("Сначала необходимо построить график методом build()")
            
        # Очищаем предыдущий график, если он есть
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            if self.toolbar is not None:
                self.toolbar.destroy()
            if self.zoom_button is not None:
                self.zoom_button.destroy()
        
        # Создаем canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.draw()
        
        # Настройки по умолчанию для pack()
        default_pack_options = {'side': tk.TOP, 'fill': tk.BOTH, 'expand': True}
        if pack_options:
            default_pack_options.update(pack_options)
        
        # Упаковываем canvas
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(**default_pack_options)
        
        # Добавляем панель инструментов если требуется
        if show_toolbar:
            self.toolbar = NavigationToolbar2Tk(self.canvas, root)
            self.toolbar.update()
            canvas_widget.pack(**default_pack_options)
        
        # Добавляем кнопку увеличения если требуется
        if show_zoom_button:
            self.zoom_button = self._create_zoom_button(canvas_widget)
            self.zoom_button.place(relx=0.98, rely=0.98, anchor='se')
    
    def show_in_new_window(self, title="График"):
        """Открывает график в новом отдельном окне"""
        if self.figure is None:
            raise ValueError("Сначала необходимо построить график методом build()")
        
        new_window = tk.Toplevel()
        new_window.title(title)
        new_window.geometry("2000x1000")
        
        # Создаем копию фигуры для нового окна
        fig_copy = copy.deepcopy(self.figure)
        
        # Создаем canvas для нового окна
        canvas = FigureCanvasTkAgg(fig_copy, master=new_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Добавляем панель инструментов
        toolbar = NavigationToolbar2Tk(canvas, new_window)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Кнопка закрытия
        btn_close = ttk.Button(new_window, text="Закрыть", command=new_window.destroy)
        btn_close.pack(side=tk.BOTTOM, pady=5)
        
        # Обработчик закрытия окна
        def on_close():
            canvas.get_tk_widget().destroy()
            toolbar.destroy()
            new_window.destroy()
        
        new_window.protocol("WM_DELETE_WINDOW", on_close)
    
    def clear(self):
        """Очищает график"""
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
            
        if self.toolbar is not None:
            self.toolbar.destroy()
            self.toolbar = None
            
        if self.zoom_button is not None:
            self.zoom_button.destroy()
            self.zoom_button = None
            
        if self.figure is not None:
            self.figure.clf()
            self.figure = None
    
    def _configure_axes(self, x_label="", y_label="", title="", grid=True):
        """Общая конфигурация осей"""
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.set_title(title)
        self.ax.grid(grid)
        
        if hasattr(self, 'legend_needed') and self.legend_needed:
            self.ax.legend()
        
        self.figure.tight_layout()


class LinearGraph(BaseGraph):
    """Класс для построения линейных графиков с возможностью постепенного добавления данных"""
    
    def __init__(self):
        super().__init__()
        self.data_sets = []
        self.legend_needed = False
    
    def add_data_set(self, *data_set):
        """Добавляет новый набор данных для построения графика
        
        Аргументы:
            data_set: Может быть одним из:
                     - (x, y)
                     - (x, y, params)
        """
        self.data_sets.append(data_set)
        return self  # для возможности цепочки вызовов
    
    def build(self, x_label="X", y_label="Y", title="", grid=True):
        self._setup_figure()
        
        default_params = {
            'color': None,
            'linewidth': 2,
            'marker': 'o',
            'linestyle': '-',
            'label': None,
        }
        
        for data_set in self.data_sets:
            if not (2 <= len(data_set) <= 3):
                raise ValueError(f"Неверный формат данных. Ожидается 2 или 3 элемента, получено {len(data_set)}")
            
            if len(data_set) == 2:
                x, y = data_set
                params = default_params.copy()
            else:
                x, y, params = data_set
                params = {**default_params, **params}
                if params['label'] is not None:
                    self.legend_needed = True
            
            self.ax.plot(x, y, 
                        color=params['color'],
                        linewidth=params['linewidth'],
                        marker=params['marker'],
                        linestyle=params['linestyle'],
                        label=params['label'])
        
        self._configure_axes(x_label, y_label, title, grid)


class BarGraph(BaseGraph):
    """Класс для построения столбчатых диаграмм"""
    
    def __init__(self, x_labels, y_data, params=None):
        super().__init__()
        self.x_labels = x_labels
        self.y_data = y_data
        self.params = params if params is not None else {}
        self.legend_needed = False
    
    def build(self, x_label="", y_label="", title="", grid=True):
        self._setup_figure()
        
        default_params = {
            'color': 'blue',
            'width': 0.8,
            'alpha': 0.7,
            'edgecolor': 'white',
            'label': None,
        }
        
        params = {**default_params, **self.params}
        if params['label'] is not None:
            self.legend_needed = True
        
        index = np.arange(len(self.x_labels))
        self.ax.bar(index, self.y_data, 
                   width=params['width'],
                   color=params['color'],
                   alpha=params['alpha'],
                   label=params['label'],
                   edgecolor=params['edgecolor'])
        
        self.ax.set_xticks(index)
        self.ax.set_xticklabels(self.x_labels)
        self.ax.set_ylim(0, None)
        
        self._configure_axes(x_label, y_label, title, grid)

# Пример использования
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Графики с возможностью детализации")
    root.geometry("1000x700")
    
    # Создаем основной фрейм
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Создаем график
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    graph = LinearGraph(
        (x, y1, {'color': 'blue', 'label': 'sin(x)'}),
        (x, y2, {'color': 'red', 'label': 'cos(x)'})
    )
    graph.build(title="Тригонометрические функции", x_label="x", y_label="y")
    
    # Отображаем график в основном окне
    graph_frame = ttk.Frame(main_frame)
    graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    graph.display(graph_frame, show_toolbar=False)
    
    # Добавляем кнопку для открытия в новом окне
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X, padx=10, pady=5)
    
    btn_open = ttk.Button(btn_frame, text="Открыть в отдельном окне", 
                         command=graph.show_in_new_window)
    btn_open.pack(pady=5)
    
    root.mainloop()