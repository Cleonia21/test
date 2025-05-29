import tkinter as tk
from tkinter import ttk
from data_base import DatabaseManager
from window_builder import FormData
from error_handler import ErrorHandler
from entities import *
from typing import Tuple

class FormManager:
    def __init__(self, form_data: FormData, errors: ErrorHandler, db_manager: DatabaseManager, form_type: str):
        self.form_data = form_data
        self.db_manager = db_manager
        self.form_type = form_type
        self.errors = errors
        self._setup_form()
    
    def _setup_form(self):
        """Настройка элементов формы"""
        self.form_data.title.config(text=self.form_type)
        self.input_form = InputForm(self.form_data.form, self.form_type)
        
        self.form_data.save_button.config(command=self._on_save)
        self.form_data.delete_button.config(command=self._on_delete)
        self.form_data.show_button.config(command=self._on_show)
    
    def _on_save(self):
        """Обработчик сохранения данных"""
        # Сначала проверяем валидность данных
        error_msg = self.input_form.save_data()
        self.errors.show_message(error_msg)
        if not error_msg[0]:
            return
        # Получаем объект из формы
        obj = self.input_form.get_object()
        if obj:
            # Сохраняем в БД в зависимости от типа
            if self.form_type == "Plane":
                self.db_manager.save_plane(obj)
            elif self.form_type == "Rocket":
                self.db_manager.save_rocket(obj)
            elif self.form_type == "Purpose":
                self.db_manager.save_purpose(obj)
            elif self.form_type == "AirDefense":
                self.db_manager.save_air_defense(obj)
            elif self.form_type == "Relief":
                self.db_manager.save_relief(obj)
    
    def _on_delete(self):
        """Обработчик удаления данных"""
        obj_id = self.form_data.entry_field.get()
        if not obj_id:
            self.errors.show_message(tuple([False, "Ошибка: Введите ID для удаления"]))
            return
        
        try:
            obj_id = int(obj_id)
            success = False
            if self.form_type == "Plane":
                success = self.db_manager.delete_plane(obj_id)
            elif self.form_type == "Rocket":
                success = self.db_manager.delete_rocket(obj_id)
            elif self.form_type == "Purpose":
                success = self.db_manager.delete_purpose(obj_id)
            elif self.form_type == "AirDefense":
                success = self.db_manager.delete_air_defense(obj_id)
            elif self.form_type == "Relief":
                success = self.db_manager.delete_relief(obj_id)
                
            if success:
                self.errors.show_message(tuple([True, "Запись успешно удалена"]))
                self.form_data.entry_field.delete(0, tk.END)
            else:
                self.errors.show_message(tuple([False, "Не удалось удалить запись"]))
        except ValueError:
            self.errors.show_message(tuple([False, "ID должен быть числом"]))
        except Exception as e:
            self.errors.show_message(tuple([False, f"Ошибка при удалении: {str(e)}"]))
    
    def _on_show(self):
        """Обработчик отображения данных"""
        try:
            if self.form_type == "Plane":
                data = self.db_manager.get_all_planes()
            elif self.form_type == "Rocket":
                data = self.db_manager.get_all_rockets()
            elif self.form_type == "Purpose":
                data = self.db_manager.get_all_purposes()
            elif self.form_type == "AirDefense":
                data = self.db_manager.get_all_air_defenses()
            elif self.form_type == "Relief":
                data = self.db_manager.get_all_reliefs()
            else:
                data = []
            
            self._show_data_in_window(data)
        except Exception as e:
            self.errors.show_message(tuple([False, f"Ошибка при получении данных: {str(e)}"]))
    
    def _show_data_in_window(self, data: list):
        """Отображает данные в новом окне в виде таблицы"""
        if not data:
            self.errors.show_message(tuple([False, "Нет данных для отображения"]))
            return
            
        window = tk.Toplevel()
        window.title(f"Данные: {self.form_type}")
        
        # Создаем Treeview с горизонтальной прокруткой
        frame = ttk.Frame(window)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tree = ttk.Treeview(frame)
        scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        
        # Получаем названия колонок
        columns = list(vars(data[0]).keys())
        tree["columns"] = columns
        
        # Настраиваем заголовки
        tree.column("#0", width=0, stretch=tk.NO)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor=tk.CENTER)
        
        # Добавляем данные
        for item in data:
            values = [getattr(item, col) for col in columns]
            tree.insert("", tk.END, values=values)
        
        # Размещаем элементы
        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        
        # Настраиваем растягивание
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

class InputForm:
    def __init__(self, root, form_type="Plane"):
        self.root = root
        self.form_type = form_type
        self.object = self._create_object()  # Создаем объект соответствующего класса
        
        # Создаем элементы формы
        self._create_widgets()
    
    def _create_object(self):
        """Создает объект в зависимости от типа формы"""
        classes = {
            "Plane": Plane,
            "Rocket": Rocket,
            "Purpose": Purpose,
            "AirDefense": AirDefense,
            "Relief": Relief
        }
        return classes[self.form_type]()
    
    def _create_widgets(self):
        """Создает элементы формы для ввода данных"""
        # Поля ввода в зависимости от типа формы
        if self.form_type == "Plane":
            fields = [
                ("Название", "name", "str"),
                ("Количество ракет", "n_rocket", "int"),
                ("Сигма Z", "sigma_z", "float"),
                ("Пси макс", "psi_max", "float"),
                ("Время прицеливания", "t_aim", "float"),
                #("Скорость", "v", "float"),
                ("Макс. перегрузка", "gap_max", "float"),
                ("Радио заметность", "visibility", "float"),
                ("P_обнаружения (матрица)", "P_detect", "matrix")
            ]
        
        elif self.form_type == "Rocket":
            fields = [
                ("Название", "name", "str"),
                ("Тип", "type", "str"),
                ("R мин", "R_min", "float"),
                ("R макс", "R_max", "float"),
                ("Средняя скорость", "midle_speed", "float"),
                ("Угол действия", "angle_effect", "float")
            ]
            
        elif self.form_type == "Purpose":
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
            
        elif self.form_type == "AirDefense":
            fields = [
                ("Название", "name", "str"),
                ("Количество ПВО", "n_defense", "int"),
                ("Количество ЗУР", "n_rocket_d", "int"),
                ("Скорость ЗУР", "v_defense", "float"),
                ("Время пассивное", "t_passive", "float"),
                ("Время смены цели", "t_changing", "float"),
                ("Время оценки", "t_def", "float"),
                ("X координата (матрица)", "x_defense", "matrix"),
                ("Z координата (матрица)", "y_defense", "matrix"),
                ("L мин", "l_min", "float"),
                ("L макс", "l_max", "float"),
                ("Угол действия", "angle_effect", "float"),
                ("Ширина защиты", "width_defense", "float"),
                ("Макс. высота", "h_max", "float"),
                ("P поражения", "P_defeat", "float"),
                ("P обнаружения (матрица)", "P_detect", "matrix")
            ]
            
        elif self.form_type == "Relief":
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