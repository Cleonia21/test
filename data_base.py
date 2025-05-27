import sqlite3
import json
import numpy as np
from typing import Optional, Union, List
from entities import *

class DatabaseManager:
    def __init__(self, db_name: str = "military_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Создает таблицы в базе данных в соответствии с моделями классов"""
        # Таблица для самолетов
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS planes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            n_rocket INTEGER,
            sigma_z REAL,
            psi_max REAL,
            t_aim REAL,
            v REAL,
            gap_max REAL,
            visibility REAL,
            P_detect TEXT
        )
        """)
        
        # Таблица для ракет
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS rockets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            R_min REAL,
            R_max REAL,
            midle_speed REAL,
            angle_effect REAL
        )
        """)
        
        # Таблица для целей
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS purposes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            a REAL,
            b REAL,
            h REAL,
            R_defeat REAL,
            average_number REAL,
            x_purpose REAL,
            y_purpose REAL
        )
        """)
        
        # Таблица для систем ПВО
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS air_defenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            n_defense INTEGER,
            n_rocket_d INTEGER,
            v_defense REAL,
            t_passive REAL,
            t_changing REAL,
            t_def REAL,
            x_defense TEXT,
            y_defense TEXT,
            l_min REAL,
            l_max REAL,
            angle_effect REAL,
            width_defense REAL,
            h_max REAL,
            P_defeat REAL,
            P_detect TEXT
        )
        """)
        
        # Таблица для рельефа
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS reliefs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            P_see TEXT
        )
        """)
        
        self.conn.commit()

    def _object_to_dict(self, obj: Union[Plane, Rocket, Purpose, AirDefense, Relief]) -> dict:
        """Конвертирует объект в словарь для сохранения в БД"""
        data = vars(obj).copy()
        
        # Конвертируем numpy массивы в JSON
        for key, value in data.items():
            if isinstance(value, np.ndarray):
                data[key] = json.dumps(value.tolist())
            elif isinstance(value, bool):
                data[key] = int(value)  # SQLite не имеет типа BOOLEAN, используем INTEGER
        
        return data

    def _dict_to_object(self, data: dict, obj_class):
        """Конвертирует словарь из БД в объект с учетом разных типов полей"""

        def convert_value(x):
            """Конвертирует значение в float, если возможно"""
            try:
                return float(x) if isinstance(x, (int, float, str)) else x
            except (ValueError, TypeError):
                return 0.0

        obj = obj_class()

        for key, value in data.items():
            if value is None:
                continue

            # Поля, которые должны быть двумерными массивами
            if key in ['P_detect', 'P_see']:
                if isinstance(value, str):
                    try:
                        loaded = json.loads(value)
                        # Убедимся, что это двумерный массив
                        if isinstance(loaded, list):
                            if loaded and isinstance(loaded[0], list):
                                # Это уже двумерный массив - оставляем как есть
                                setattr(obj, key, loaded)
                            else:
                                # Делаем двумерным (оборачиваем в список)
                                setattr(obj, key, [loaded])
                        else:
                            # Одиночное значение - делаем двумерным
                            setattr(obj, key, [[loaded]])
                    except json.JSONDecodeError:
                        setattr(obj, key, [[]])  # Пустой двумерный массив
                else:
                    setattr(obj, key, value if isinstance(value, list) else [[value]])

            # Поля, которые должны быть одномерными списками
            elif key in ['x_defense', 'y_defense']:
                if isinstance(value, str):
                    try:
                        loaded = json.loads(value)
                        # Убедимся, что это одномерный список
                        if isinstance(loaded, list):
                            if loaded and isinstance(loaded[0], list):
                                # Если это двумерный массив, берем первую строку
                                setattr(obj, key, loaded[0])
                            else:
                                # Это уже одномерный список
                                setattr(obj, key, loaded)
                        else:
                            # Одиночное значение - делаем списком
                            setattr(obj, key, [loaded])
                    except json.JSONDecodeError:
                        setattr(obj, key, [])  # Пустой одномерный список
                else:
                    setattr(obj, key, value if isinstance(value, list) else [value])

            # Все остальные поля
            else:
                setattr(obj, key, value)

        return obj

    # Методы для работы с Plane
    def save_plane(self, plane: Plane) -> int:
        """Сохраняет объект Plane в базу данных"""
        plane_data = self._object_to_dict(plane)
        columns = ', '.join(plane_data.keys())
        placeholders = ', '.join(['?'] * len(plane_data))
        
        sql = f"INSERT INTO planes ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, tuple(plane_data.values()))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_plane(self, plane_id: int) -> Optional[Plane]:
        """Получает Plane по ID"""
        self.cursor.execute("SELECT * FROM planes WHERE id=?", (plane_id,))
        row = self.cursor.fetchone()
        if not row:
            return None
            
        columns = [column[0] for column in self.cursor.description]
        plane_data = dict(zip(columns, row))
        return self._dict_to_object(plane_data, Plane)

    def get_all_planes(self) -> List[Plane]:
        """Получает все Plane из базы"""
        self.cursor.execute("SELECT * FROM planes")
        rows = self.cursor.fetchall()
        
        result = []
        for row in rows:
            columns = [column[0] for column in self.cursor.description]
            plane_data = dict(zip(columns, row))
            result.append(self._dict_to_object(plane_data, Plane))
        
        return result

    def update_plane(self, plane: Plane) -> bool:
        """Обновляет данные Plane в базе"""
        if not hasattr(plane, 'id') or plane.id is None:
            return False
            
        plane_data = self._object_to_dict(plane)
        updates = ', '.join([f"{key}=?" for key in plane_data.keys()])
        
        sql = f"UPDATE planes SET {updates} WHERE id=?"
        params = tuple(plane_data.values()) + (plane.id,)
        
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_plane(self, plane_id: int) -> bool:
        """Удаляет Plane из базы"""
        self.cursor.execute("DELETE FROM planes WHERE id=?", (plane_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # Методы для работы с Rocket
    def save_rocket(self, rocket: Rocket) -> int:
        """Сохраняет объект Rocket в базу данных"""
        rocket_data = self._object_to_dict(rocket)
        columns = ', '.join(rocket_data.keys())
        placeholders = ', '.join(['?'] * len(rocket_data))
        
        sql = f"INSERT INTO rockets ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, tuple(rocket_data.values()))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_rocket(self, rocket_id: int) -> Optional[Rocket]:
        """Получает Rocket по ID"""
        self.cursor.execute("SELECT * FROM rockets WHERE id=?", (rocket_id,))
        row = self.cursor.fetchone()
        if not row:
            return None
            
        columns = [column[0] for column in self.cursor.description]
        rocket_data = dict(zip(columns, row))
        return self._dict_to_object(rocket_data, Rocket)

    def get_all_rockets(self) -> List[Rocket]:
        """Получает все Rocket из базы"""
        self.cursor.execute("SELECT * FROM rockets")
        rows = self.cursor.fetchall()
        
        result = []
        for row in rows:
            columns = [column[0] for column in self.cursor.description]
            rocket_data = dict(zip(columns, row))
            result.append(self._dict_to_object(rocket_data, Rocket))
        
        return result

    def update_rocket(self, rocket: Rocket) -> bool:
        """Обновляет данные Rocket в базе"""
        if not hasattr(rocket, 'id') or rocket.id is None:
            return False
            
        rocket_data = self._object_to_dict(rocket)
        updates = ', '.join([f"{key}=?" for key in rocket_data.keys()])
        
        sql = f"UPDATE rockets SET {updates} WHERE id=?"
        params = tuple(rocket_data.values()) + (rocket.id,)
        
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_rocket(self, rocket_id: int) -> bool:
        """Удаляет Rocket из базы"""
        self.cursor.execute("DELETE FROM rockets WHERE id=?", (rocket_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # Методы для работы с Purpose
    def save_purpose(self, purpose: Purpose) -> int:
        """Сохраняет объект Purpose в базу данных"""
        purpose_data = self._object_to_dict(purpose)
        columns = ', '.join(purpose_data.keys())
        placeholders = ', '.join(['?'] * len(purpose_data))
        
        sql = f"INSERT INTO purposes ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, tuple(purpose_data.values()))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_purpose(self, purpose_id: int) -> Optional[Purpose]:
        """Получает Purpose по ID"""
        self.cursor.execute("SELECT * FROM purposes WHERE id=?", (purpose_id,))
        row = self.cursor.fetchone()
        if not row:
            return None
            
        columns = [column[0] for column in self.cursor.description]
        purpose_data = dict(zip(columns, row))
        return self._dict_to_object(purpose_data, Purpose)

    def get_all_purposes(self) -> List[Purpose]:
        """Получает все Purpose из базы"""
        self.cursor.execute("SELECT * FROM purposes")
        rows = self.cursor.fetchall()
        
        result = []
        for row in rows:
            columns = [column[0] for column in self.cursor.description]
            purpose_data = dict(zip(columns, row))
            result.append(self._dict_to_object(purpose_data, Purpose))
        
        return result

    def update_purpose(self, purpose: Purpose) -> bool:
        """Обновляет данные Purpose в базе"""
        if not hasattr(purpose, 'id') or purpose.id is None:
            return False
            
        purpose_data = self._object_to_dict(purpose)
        updates = ', '.join([f"{key}=?" for key in purpose_data.keys()])
        
        sql = f"UPDATE purposes SET {updates} WHERE id=?"
        params = tuple(purpose_data.values()) + (purpose.id,)
        
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_purpose(self, purpose_id: int) -> bool:
        """Удаляет Purpose из базы"""
        self.cursor.execute("DELETE FROM purposes WHERE id=?", (purpose_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # Методы для работы с AirDefense
    def save_air_defense(self, air_defense: AirDefense) -> int:
        """Сохраняет объект AirDefense в базу данных"""
        air_defense_data = self._object_to_dict(air_defense)
        columns = ', '.join(air_defense_data.keys())
        placeholders = ', '.join(['?'] * len(air_defense_data))
        
        sql = f"INSERT INTO air_defenses ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, tuple(air_defense_data.values()))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_air_defense(self, air_defense_id: int) -> Optional[AirDefense]:
        """Получает AirDefense по ID"""
        self.cursor.execute("SELECT * FROM air_defenses WHERE id=?", (air_defense_id,))
        row = self.cursor.fetchone()
        if not row:
            return None
            
        columns = [column[0] for column in self.cursor.description]
        air_defense_data = dict(zip(columns, row))
        return self._dict_to_object(air_defense_data, AirDefense)

    def get_all_air_defenses(self) -> List[AirDefense]:
        """Получает все AirDefense из базы"""
        self.cursor.execute("SELECT * FROM air_defenses")
        rows = self.cursor.fetchall()
        
        result = []
        for row in rows:
            columns = [column[0] for column in self.cursor.description]
            air_defense_data = dict(zip(columns, row))
            result.append(self._dict_to_object(air_defense_data, AirDefense))
        
        return result

    def update_air_defense(self, air_defense: AirDefense) -> bool:
        """Обновляет данные AirDefense в базе"""
        if not hasattr(air_defense, 'id') or air_defense.id is None:
            return False
            
        air_defense_data = self._object_to_dict(air_defense)
        updates = ', '.join([f"{key}=?" for key in air_defense_data.keys()])
        
        sql = f"UPDATE air_defenses SET {updates} WHERE id=?"
        params = tuple(air_defense_data.values()) + (air_defense.id,)
        
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_air_defense(self, air_defense_id: int) -> bool:
        """Удаляет AirDefense из базы"""
        self.cursor.execute("DELETE FROM air_defenses WHERE id=?", (air_defense_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # Методы для работы с Relief
    def save_relief(self, relief: Relief) -> int:
        """Сохраняет объект Relief в базу данных"""
        relief_data = self._object_to_dict(relief)
        columns = ', '.join(relief_data.keys())
        placeholders = ', '.join(['?'] * len(relief_data))
        
        sql = f"INSERT INTO reliefs ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, tuple(relief_data.values()))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_relief(self, relief_id: int) -> Optional[Relief]:
        """Получает Relief по ID"""
        self.cursor.execute("SELECT * FROM reliefs WHERE id=?", (relief_id,))
        row = self.cursor.fetchone()
        if not row:
            return None
            
        columns = [column[0] for column in self.cursor.description]
        relief_data = dict(zip(columns, row))
        return self._dict_to_object(relief_data, Relief)

    def get_all_reliefs(self) -> List[Relief]:
        """Получает все Relief из базы"""
        self.cursor.execute("SELECT * FROM reliefs")
        rows = self.cursor.fetchall()
        
        result = []
        for row in rows:
            columns = [column[0] for column in self.cursor.description]
            relief_data = dict(zip(columns, row))
            result.append(self._dict_to_object(relief_data, Relief))
        
        return result

    def update_relief(self, relief: Relief) -> bool:
        """Обновляет данные Relief в базе"""
        if not hasattr(relief, 'id') or relief.id is None:
            return False
            
        relief_data = self._object_to_dict(relief)
        updates = ', '.join([f"{key}=?" for key in relief_data.keys()])
        
        sql = f"UPDATE reliefs SET {updates} WHERE id=?"
        params = tuple(relief_data.values()) + (relief.id,)
        
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_relief(self, relief_id: int) -> bool:
        """Удаляет Relief из базы"""
        self.cursor.execute("DELETE FROM reliefs WHERE id=?", (relief_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def close(self):
        """Закрывает соединение с базой данных"""
        self.conn.close()

# Пример использования
if __name__ == "__main__":
    db = DatabaseManager()

    # Пример сохранения и получения данных о самолете
    plane_data = {
        "name": "F-16",
        "n_rocket": 4,
        "sigma_z": 1.5,
        "psi_max": 30.0,
        "t_aim": 10.5,
        "v": 800.0,
        "gap_max": 200.0,
        "visibility": 0.9,
        "P_detect": np.array([[0.1, 0.2], [0.3, 0.4]])
    }
    plane_id = db.save_plane(plane_data)
    print(f"Самолет сохранен с ID: {plane_id}")
    
    retrieved_plane = db.get_plane(plane_id)
    print("Данные самолета:", retrieved_plane)
    print("Тип P_detect:", type(retrieved_plane['P_detect']))

    # Пример сохранения и получения данных о ракете
    rocket_data = {
        "name": "AIM-120",
        "type": "воздух-воздух",
        "R_min": 500.0,
        "R_max": 18000.0,
        "midle_speed": 1020.0,
        "angle_effect": 60.0
    }
    rocket_id = db.save_rocket(rocket_data)
    print(f"Ракета сохранена с ID: {rocket_id}")
    
    retrieved_rocket = db.get_rocket(rocket_id)
    print("Данные ракеты:", retrieved_rocket)

    db.close()


