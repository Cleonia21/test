import tkinter as tk
from tkinter import ttk
from data_base import DatabaseManager
from window_builder import FormData
from entities import *
from typing import Tuple
from error_handler import ErrorHandler
from typing import List, Dict, Any, Union, Type
from db_cache import DBCache

class FormManager:
    def __init__(self, db_manager: DatabaseManager, form_data: FormData, form_type: BASE_CLASSES_TYPE, db_cache: DBCache, error_handler: ErrorHandler):
        self.db_manager = db_manager
        self.error_handler = error_handler
        self.form_data = form_data
        self.form_type = form_type
        self.msgViewer = MsgViewer(form_data.msg_label)
        self.data_viewer = DataViewer(error_handler, db_cache)
        self._setup_form()
    
    def _setup_form(self):
        """Настройка элементов формы"""
        self.form_data.title.config(text=BASE_CLASSES_MAP[self.form_type])
        self.input_form = InputForm(self.form_data.form, self.form_type)
        
        self.form_data.save_button.config(command=self._on_save)
        self.form_data.delete_button.config(command=self._on_delete)
        self.form_data.show_button.config(command=self._on_show)
    
    def _on_save(self):
        """Обработчик сохранения данных"""
        error_msg = self.input_form.save_data()
        self.msgViewer.show_message(error_msg)
        if not error_msg[0]:
            return
        obj = self.input_form.get_object()
        if obj:
            if self.form_type == Plane:
                self.db_manager.save_plane(obj)
            elif self.form_type == Rocket:
                self.db_manager.save_rocket(obj)
            elif self.form_type == Purpose:
                self.db_manager.save_purpose(obj)
            elif self.form_type == AirDefense:
                self.db_manager.save_air_defense(obj)
            elif self.form_type == Relief:
                self.db_manager.save_relief(obj)
    
    def _on_delete(self):
        """Обработчик удаления данных"""
        obj_id = self.form_data.entry_field.get()
        if not obj_id:
            self.msgViewer.show_message(tuple([False, "Ошибка: Введите ID для удаления"]))
            return
        
        try:
            obj_id = int(obj_id)
            success = False
            if self.form_type == Plane:
                success = self.db_manager.delete_plane(obj_id)
            elif self.form_type == Rocket:
                success = self.db_manager.delete_rocket(obj_id)
            elif self.form_type == Purpose:
                success = self.db_manager.delete_purpose(obj_id)
            elif self.form_type == AirDefense:
                success = self.db_manager.delete_air_defense(obj_id)
            elif self.form_type == Relief:
                success = self.db_manager.delete_relief(obj_id)
                
            if success:
                self.msgViewer.show_message(tuple([True, "Запись успешно удалена"]))
                self.form_data.entry_field.delete(0, tk.END)
            else:
                self.msgViewer.show_message(tuple([False, "Не удалось удалить запись"]))
        except ValueError:
            self.msgViewer.show_message(tuple([False, "ID должен быть числом"]))
        except Exception as e:
            self.msgViewer.show_message(tuple([False, f"Ошибка при удалении: {str(e)}"]))
    
    def _on_show(self):
        """Обработчик отображения данных"""
        try:
            if self.form_type == Plane:
                data = self.db_manager.get_all_planes()
            elif self.form_type == Rocket:
                data = self.db_manager.get_all_rockets()
            elif self.form_type == Purpose:
                data = self.db_manager.get_all_purposes()
            elif self.form_type == AirDefense:
                data = self.db_manager.get_all_air_defenses()
            elif self.form_type == Relief:
                data = self.db_manager.get_all_reliefs()
            else:
                data = []
            
            self.data_viewer.show_data(data, BASE_CLASSES_MAP[self.form_type], self.form_type)  # Используем DataViewer
        except Exception as e:
            self.msgViewer.show_message(tuple([False, f"Ошибка при получении данных: {str(e)}"]))

class DataViewer:
    def __init__(self, error_handler: ErrorHandler, db_cache: DBCache):
        self.error_handler = error_handler
        self.db_cache = db_cache
        self.current_data_type = None  # Тип данных, отображаемых в текущий момент
        self.error_label = None
        self.msgViewer = None
        self.selected_items = set()     # Множество выбранных ID строк
    
    def show_data(self, data: List[Any], title: str, data_type: BASE_CLASSES_TYPE) -> None:
        """Отображает данные в новом окне с поддержкой выбора и кэширования строк"""
        if not data:
            self.error_handler.handle(Exception("No data"), "Нет данных для отображения", False)
            return
        
        self.current_data_type = data_type
        self.selected_items.clear()
        
        window = self._create_base_window(title)
        frame = self._create_scrollable_frame(window)
        tree, scroll_x, scroll_y = self._create_treeview_with_scrollbars(frame)
        columns = self._get_object_columns(data[0])
        
        self._setup_treeview_columns(tree, columns)
        item_id_to_index = self._populate_treeview_data(tree, data, columns)
        self._setup_double_click_handler(tree, item_id_to_index, data, columns)
        self._setup_selection_controls(window, tree, data, data_type)
        self._arrange_widgets_in_grid(tree, scroll_x, scroll_y, frame)

    def _setup_selection_controls(self, parent: tk.Toplevel, tree: ttk.Treeview, 
                                data: List[Any], data_type: BASE_CLASSES_TYPE) -> None:
        """Добавляет элементы управления для выбора строк и работы с кэшем"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопки выбора
        select_frame = ttk.LabelFrame(control_frame, text="Выбор строк")
        select_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(select_frame, text="Выбрать все", 
                 command=lambda: self._select_all_items(tree)).pack(side=tk.LEFT)
        ttk.Button(select_frame, text="Снять выделение", 
                 command=lambda: self._deselect_all_items(tree)).pack(side=tk.LEFT)
        
        # Кнопки кэша
        if data_type is not None:
            cache_frame = ttk.LabelFrame(control_frame, text="Работа с кэшем")
            cache_frame.pack(side=tk.LEFT, padx=5)
            
            ttk.Button(cache_frame, text="Добавить в кэш", 
                      command=lambda: self._add_selected_to_cache(tree, data, data_type)).pack(side=tk.LEFT)
            ttk.Button(cache_frame, text="Очистить кэш", 
                      command=lambda: self._clear_cache_for_type(data_type)).pack(side=tk.LEFT)
            ttk.Button(cache_frame, text="Показать кэш", 
                      command=self._show_cache_status).pack(side=tk.LEFT)
            
        # Label для отображения ошибок
        self.error_label = ttk.Label(control_frame, text="", foreground="red")
        self.error_label.pack(side=tk.RIGHT, padx=5)

        self.msgViewer = MsgViewer(self.error_label, 20000)
        
        # Привязка событий выбора
        tree.bind("<<TreeviewSelect>>", lambda e: self._update_selected_items(tree, data))

    def _select_all_items(self, tree: ttk.Treeview) -> None:
        """Выделяет все строки в таблице"""
        for item in tree.get_children():
            tree.selection_add(item)

    def _deselect_all_items(self, tree: ttk.Treeview) -> None:
        """Снимает выделение со всех строк"""
        tree.selection_remove(*tree.selection())

    def _update_selected_items(self, tree: ttk.Treeview, data: List[Any]) -> None:
        """Обновляет множество выбранных элементов при изменении выделения"""
        selected_ids = [tree.item(item)['values'][0] for item in tree.selection()]
        self.selected_items = set(selected_ids)

    def _add_selected_to_cache(self, tree: ttk.Treeview, data: List[Any], data_type: BASE_CLASSES_TYPE) -> None:
        """Добавляет выбранные строки в кэш"""
        if not self.selected_items:
            self.msgViewer.show_message(tuple([False, "Не выбрано ни одной строки"]))
            return
        
        # Получаем ID выбранных элементов (предполагаем, что первый столбец содержит ID)
        selected_ids = []
        for item in tree.selection():
            values = tree.item(item)['values']
            if values:
                selected_ids.append(int(values[0]))
        
        if selected_ids:
            self.db_cache.add_ids(data_type, selected_ids)
            self.msgViewer.show_message(tuple([True, f"Добавлено {len(selected_ids)} элементов в кэш"]))
        else:
            self.msgViewer.show_message(tuple([False, "Не удалось получить ID выбранных элементов"]))

    def _clear_cache_for_type(self, data_type: BASE_CLASSES_TYPE) -> None:
        """Очищает кэш для указанного типа данных"""
        self.db_cache.clear_ids(data_type)
        self.msgViewer.show_message(tuple([True, f"Кэш для {BASE_CLASSES_MAP[data_type]} очищен"]))

    def _show_cache_status(self) -> None:
        """Показывает текущее состояние кэша"""
        cache_info = str(self.db_cache)
        self.msgViewer.show_message(tuple([True, f"Состояние кэша {cache_info}"]))

    def show_complex_data(self, data: Union[List, Dict], title: str) -> None:
        """Отображает сложные данные (списки/словари) в новом окне"""
        window = self._create_base_window(f"Детали: {title}")
        frame = self._create_scrollable_frame(window)
        tree, scroll_x, scroll_y = self._create_treeview_with_scrollbars(frame)
        
        if isinstance(data, list) and data:
            self._setup_and_populate_list_data(tree, data)
        else:
            self.msgViewer.show_message(tuple([False, "Нет данных для отображения или данные представлены не верно"]))
            return
        
        self._arrange_widgets_in_grid(tree, scroll_x, scroll_y, frame)

    def _create_base_window(self, title: str) -> tk.Toplevel:
        """Создает и возвращает новое окно с заданным заголовком"""
        window = tk.Toplevel()
        window.title(title)
        return window

    def _create_scrollable_frame(self, parent: tk.Widget) -> ttk.Frame:
        """Создает и возвращает frame с возможностью растягивания"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        return frame

    def _create_treeview_with_scrollbars(self, parent: ttk.Frame) -> tuple:
        """Создает и возвращает Treeview с горизонтальной и вертикальной прокруткой"""
        tree = ttk.Treeview(parent)
        scroll_x = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=tree.xview)
        scroll_y = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        return tree, scroll_x, scroll_y

    def _get_object_columns(self, data_item: object) -> List[str]:
        """Возвращает список атрибутов объекта для использования в качестве колонок"""
        return list(vars(data_item).keys())

    def _setup_treeview_columns(self, tree: ttk.Treeview, columns: List[str]) -> None:
        """Настраивает колонки Treeview"""
        tree["columns"] = columns
        tree.column("#0", width=0, stretch=tk.NO)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor=tk.CENTER)

    def _populate_treeview_data(self, tree: ttk.Treeview, data: List[Any], columns: List[str]) -> Dict[str, int]:
        """Заполняет Treeview данными с учетом выбранных элементов в кэше"""
        item_id_to_index = {}
        
        for index, item in enumerate(data):
            values = self._prepare_row_values(item, columns)
            item_id = tree.insert("", tk.END, values=values)
            item_id_to_index[item_id] = index
            
            # Проверяем, есть ли элемент в кэше
            if self.current_data_type is not None and hasattr(item, 'id'):
                if (self.current_data_type, item.id) in self.db_cache:
                    tree.selection_add(item_id)
                    self.selected_items.add(str(item.id))
            
            if self._has_complex_data(item, columns):
                tree.item(item_id, tags=("has_complex",))
        
        return item_id_to_index

    def _prepare_row_values(self, item: Any, columns: List[str]) -> List[str]:
        """Подготавливает значения строки для отображения в Treeview"""
        values = []
        for col in columns:
            value = getattr(item, col)
            if isinstance(value, (list, dict)) and value:
                values.append("Показать массив")
            else:
                values.append(str(value))
        return values

    def _has_complex_data(self, item: Any, columns: List[str]) -> bool:
        """Проверяет, есть ли в объекте сложные данные (списки/словари)"""
        return any(
            isinstance(getattr(item, col), (list, dict)) and getattr(item, col)
            for col in columns
        )

    def _setup_double_click_handler(self, tree: ttk.Treeview, item_id_to_index: Dict[str, int], 
                                  data: List[Any], columns: List[str]) -> None:
        """Настраивает обработчик двойного клика для отображения вложенных данных"""
        def on_item_double_click(event):
            item_id = tree.focus()
            if not item_id or "has_complex" not in tree.item(item_id, "tags"):
                return
                
            col_name = self._get_clicked_column_name(tree, event, columns)
            if not col_name or item_id not in item_id_to_index:
                return
                
            item_data = data[item_id_to_index[item_id]]
            value = getattr(item_data, col_name)
            
            if isinstance(value, (list, dict)) and value:
                self.show_complex_data(value, col_name)
        
        tree.bind("<Double-1>", on_item_double_click)

    def _get_clicked_column_name(self, tree: ttk.Treeview, event: tk.Event, columns: List[str]) -> Union[str, None]:
        """Возвращает название колонки, по которой был сделан клик"""
        col = tree.identify_column(event.x)
        col_index = int(col[1:]) - 1
        return columns[col_index] if col_index < len(columns) else None

    def _arrange_widgets_in_grid(self, tree: ttk.Treeview, scroll_x: ttk.Scrollbar, 
                               scroll_y: ttk.Scrollbar, frame: ttk.Frame) -> None:
        """Размещает виджеты в grid и настраивает растягивание"""
        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def _setup_and_populate_list_data(self, tree: ttk.Treeview, data: List) -> None:
        """Настраивает и заполняет Treeview для отображения списка данных"""
        if self._is_two_dimensional_list(data):
            columns = ["Column 1", "Column 2"]
            self._setup_treeview_columns(tree, columns)
            
            for row in data:
                values = [str(row[0]), str(row[1])] if len(row) >= 2 else [str(row[0]), ""]
                tree.insert("", tk.END, values=values)
        else:
            columns = ["Value"]
            self._setup_treeview_columns(tree, columns)
            
            for item in data:
                tree.insert("", tk.END, values=[str(item)])

    def _is_two_dimensional_list(self, data: List) -> bool:
        """Проверяет, является ли список двумерным"""
        return all(isinstance(row, list) and len(row) >= 2 for row in data)

class MsgViewer:
    def __init__(self, label_widget: ttk.Label, clear_time = 3000):
        """
        Инициализация обработчика сообщений с указанным виджетом Label.
        
        :param label_widget: виджет ttk.Label, в который будут выводиться сообщения
        """
        self.label = label_widget
        self.clear_time = clear_time
        self._clear_id = None  # ID отложенного вызова очистки
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
        Автоматически очищает через 5 секунд.
        
        :param result: Кортеж (статус_успеха, сообщение)
                      где статус_успеха - bool (True = успех, False = ошибка)
        """
        # Отменяем предыдущую запланированную очистку
        if self._clear_id is not None:
            self.label.after_cancel(self._clear_id)
        
        is_success, message = result
        self.clear()
        
        # Устанавливаем текст и стиль
        self.label.config(text=message)
        if is_success:
            self.label.config(style="ErrorHandler.Success.TLabel")
        else:
            self.label.config(style="ErrorHandler.Error.TLabel")
        
        # Запланировать очистку
        self._clear_id = self.label.after(self.clear_time, self.clear)
    
    def clear(self):
        """Очищает Label и возвращает стандартный стиль."""
        self.label.config(text="", style="ErrorHandler.Default.TLabel")
        self._clear_id = None  # Сбрасываем ID таймера

class InputForm:
    def __init__(self, root, form_type=BASE_CLASSES_TYPE):
        self.root = root
        self.form_type = form_type
        self.object = self._create_object()  # Создаем объект соответствующего класса
        
        # Создаем элементы формы
        self._create_widgets()
    
    def _create_object(self):
        """Создает объект в зависимости от типа формы"""
        return self.form_type()
    
    def _create_widgets(self):
        """Создает элементы формы для ввода данных"""
        # Поля ввода в зависимости от типа формы
        if self.form_type == Plane:
            fields = [
                ("Название", "name", "str"),
                ("Количество ракет", "n_rocket", "int"),
                ("Сигма Z", "sigma_z", "float"),
                ("Пси макс", "psi_max", "float"),
                ("Время прицеливания", "t_aim", "float"),
                ("Макс. перегрузка", "gap_max", "float"),
                ("Радио заметность", "visibility", "float"),
                ("P_обнаружения (матрица)", "P_detect", "matrix")
            ]
        
        elif self.form_type == Rocket:
            fields = [
                ("Название", "name", "str"),
                ("Тип", "type", "str"),
                ("R мин", "R_min", "float"),
                ("R макс", "R_max", "float"),
                ("Средняя скорость", "midle_speed", "float"),
                ("Угол действия", "angle_effect", "float")
            ]
            
        elif self.form_type == Purpose:
            fields = [
                ("Название", "name", "str"),
                ("Длинна", "a", "float"),
                ("Ширина", "b", "float"),
                ("Высота", "h", "float"),
                ("R поражения", "R_defeat", "float"),
                ("Среднее число попаданий", "average_number", "float"),
                ("X координата", "x_purpose", "float"),
                ("Z координата", "y_purpose", "float")
            ]
            
        elif self.form_type == AirDefense:
            fields = [
                ("Название", "name", "str"),
                ("Количество ПВО", "n_defense", "int"),
                ("Количество ЗУР", "n_rocket_d", "int"),
                ("Скорость ЗУР", "v_defense", "float"),
                ("Время пассивное", "t_passive", "float"),
                ("Время смены цели", "t_changing", "float"),
                ("Время оценки", "t_def", "float"),
                ("X координата (массив)", "x_defense", "matrix"),
                ("Z координата (массив)", "y_defense", "matrix"),
                ("L мин", "l_min", "float"),
                ("L макс", "l_max", "float"),
                ("Угол действия", "angle_effect", "float"),
                ("Ширина защиты", "width_defense", "float"),
                ("Макс. высота", "h_max", "float"),
                ("P поражения", "P_defeat", "float"),
                ("P обнаружения (матрица)", "P_detect", "matrix")
            ]
            
        elif self.form_type == Relief:
            fields = [
                ("Название", "name", "str"),
                ("P прямой видимости (матрица)", "P_see", "matrix")
            ]
        
        self.entries = {}
        for label_text, attr_name, dtype in fields:
            frame = ttk.Frame(self.root)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            label = ttk.Label(frame, text=label_text, width=25)
            label.pack(side=tk.LEFT)
            
            if dtype == "matrix":
                entry = tk.Text(frame, height=5)
                entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
            else:
                entry = ttk.Entry(frame)
                entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
            
            self.entries[attr_name] = (entry, dtype) 
    
    def _validate_field(self, value, dtype, attr_name=None):
        """Проверяет корректность значения поля с учетом специальных правил"""
        try:
            if dtype == "int":
                val = int(value)
            elif dtype == "float":
                val = float(value)
                # Специальная проверка для gap_max
                if attr_name == "gap_max" and val <= 1:
                    return False
            else:
                return bool(value.strip())  # Для строк проверяем, что не пусто
            
            return True
        except ValueError:
            return False
    
    def _parse_matrix(self, text):
        """Парсит текст матрицы в numpy array"""
        rows = [row.split() for row in text.split('\n') if row.strip()]
        return np.array(rows, dtype=float)
    
    def save_data(self) -> Tuple[bool, str]:
        """Сохраняет введенные данные в объект с проверкой всех полей"""
        error_fields = []
        
        try:
            for attr_name, (entry, dtype) in self.entries.items():
                if dtype == "matrix":
                    text = entry.get("1.0", tk.END).strip()
                    if not text:
                        error_fields.append(attr_name)
                        continue
                        
                    try:
                        matrix = self._parse_matrix(text)
                        if matrix.size == 0:
                            error_fields.append(attr_name)
                            continue
                        setattr(self.object, attr_name, matrix)
                    except ValueError:
                        error_fields.append(attr_name)
                else:
                    value = entry.get().strip()
                    
                    if not value:
                        error_fields.append(attr_name)
                        continue
                        
                    if dtype in ("int", "float"):
                        if not self._validate_field(value, dtype, attr_name):  # Передаем имя поля
                            error_fields.append(attr_name)
                            continue
                        
                        setattr(self.object, attr_name, int(value) if dtype == "int" else float(value))
                    else:
                        setattr(self.object, attr_name, value)
            
            if error_fields:
                return (False, f"Ошибка: не заполнены или некорректны поля - {', '.join(error_fields)}")
            
            return (True, "Данные успешно сохранены!")
        
        except Exception as e:
            return (False, f"Критическая ошибка: {str(e)}")
        
    def get_object(self):
        """Возвращает заполненный объект"""
        return self.object