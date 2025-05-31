from data_base import DatabaseManager
from entities import *

def main():
    # Создаем подключение к базе данных
    db = DatabaseManager()
    
    try:
        # Заполняем таблицу самолетов
        planes = [
            {
                "name": "Су - 34",
                "n_rocket": 6,
                "sigma_z": 400.0,
                "psi_max": 60.0,
                "t_aim": 5.0,
                "gap_max": 7,
                "visibility": 3.0,
                "P_detect": ([[0, 5000, 10000], [1.0, 0.5, 0]])
            },
            {
                "name": "Cу - 25",
                "n_rocket": 6,
                "sigma_z": 600.0,
                "psi_max": 50,
                "t_aim": 8.5,
                "gap_max": 6,
                "visibility": 3.0,
                "P_detect": ([[0, 4000, 8000], [1.0, 0.5, 0]])
            },
            {
                "name": "МиГ - 29",
                "n_rocket": 4,
                "sigma_z": 500.0,
                "psi_max": 45.0,
                "t_aim": 7.0,
                "gap_max": 9,
                "visibility": 2.5,
                "P_detect": ([[0, 1.0], [4000, 0.5], [8000, 0]])
            }
        ]
        
        print("Добавляем самолеты:")
        for plane_data in planes:
            plane = Plane()
            for key, value in plane_data.items():
                setattr(plane, key, value)
            plane_id = db.save_plane(plane)
            print(f"  - {plane.name} (ID: {plane_id})")
        
        # Заполняем таблицу ракет
        rockets = [
            {
                "name": "Х - 29Л",
                "type": "фугас",
                "R_min": 2000.0,
                "R_max": 8000.0,
                "midle_speed": 600.0,
                "angle_effect": 45.0
            },
            {
                "name": "Вихрь М",
                "type": "кумулятив",
                "R_min": 1500.0,
                "R_max": 8000.0,
                "midle_speed": 8000.0,
                "angle_effect": 45.0
            },

        ]
        
        print("\nДобавляем ракеты:")
        for rocket_data in rockets:
            rocket = Rocket()
            for key, value in rocket_data.items():
                setattr(rocket, key, value)
            rocket_id = db.save_rocket(rocket)
            print(f"  - {rocket.name} (ID: {rocket_id})")
        
        # Заполняем таблицу целей
        purposes = [
            {
                "name": "Элементарная цель",
                "a": 7.5,
                "b": 3.5,
                "h": 2.5,
                "R_defeat": 2.0,
                "average_number": 3.0,
                "x_purpose": 0.0,
                "y_purpose": 0.0
            },

        ]
        
        print("\nДобавляем цели:")
        for purpose_data in purposes:
            purpose = Purpose()
            for key, value in purpose_data.items():
                setattr(purpose, key, value)
            purpose_id = db.save_purpose(purpose)
            print(f"  - {purpose.name} (ID: {purpose_id})")
        
        # Заполняем таблицу систем ПВО
        air_defenses = [
            {
                "name": "Роланд 2",
                "n_defense": 3,
                "n_rocket_d": 4,
                "v_defense": 500.0,
                "t_passive": 5.0,
                "t_changing": 10.0,
                "t_def": 3.0,
                "x_defense": [0.0, 2000.0, 3000.0],
                "y_defense": [0.0, 1500.0, 2500.0],
                "l_min": 500.0,
                "l_max": 6000.0,
                "angle_effect": 90.0,
                "width_defense": 5000.0,
                "h_max": 5000.0,
                "P_defeat": 0.6,
                "P_detect": ([[0, 1.0], [20000, 0.5], [40000, 0.0]])
            },
        ]
        
        print("\nДобавляем системы ПВО:")
        for air_defense_data in air_defenses:
            air_defense = AirDefense()
            for key, value in air_defense_data.items():
                setattr(air_defense, key, value)
            air_defense_id = db.save_air_defense(air_defense)
            print(f"  - {air_defense.name} (ID: {air_defense_id})")
        
        # Заполняем таблицу рельефа
        reliefs = [
            {
                "name": "Равнина",
                "P_see": ([[0.0, 1.0], [5000, 0.75], [10000, 0.42], [20000, 0.12], [30000, 0.0]])
            },

        ]
        
        print("\nДобавляем рельефы:")
        for relief_data in reliefs:
            relief = Relief()
            for key, value in relief_data.items():
                setattr(relief, key, value)
            relief_id = db.save_relief(relief)
            print(f"  - {relief.name} (ID: {relief_id})")
        
        print("\nБаза данных успешно заполнена!")
        
    finally:
        # Закрываем соединение с базой данных
        db.close()


if __name__ == "__main__":
    main()