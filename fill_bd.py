from data_base import DatabaseManager
from entities import *

def main():
    # Создаем подключение к базе данных
    db = DatabaseManager()
    
    try:
        # Заполняем таблицу самолетов
        planes = [
            {
                "name": "F-16",
                "n_rocket": 4,
                "sigma_z": 1.5,
                "psi_max": 30.0,
                "t_aim": 10.5,
                "gap_max": 200.0,
                "visibility": 0.9,
                "P_detect": ([[0.1, 0.2], [0.3, 0.4]])
            },
            {
                "name": "Su-35",
                "n_rocket": 6,
                "sigma_z": 1.2,
                "psi_max": 35.0,
                "t_aim": 8.5,
                "gap_max": 250.0,
                "visibility": 0.8,
                "P_detect": ([[0.2, 0.3], [0.4, 0.5]])
            },
            {
                "name": "F-22",
                "n_rocket": 6,
                "sigma_z": 0.8,
                "psi_max": 40.0,
                "t_aim": 7.0,
                "gap_max": 180.0,
                "visibility": 0.7,
                "P_detect": ([[0.05, 0.1], [0.15, 0.2]])
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
                "name": "AIM-120 AMRAAM",
                "type": "воздух-воздух",
                "R_min": 500.0,
                "R_max": 18000.0,
                "midle_speed": 1020.0,
                "angle_effect": 60.0
            },
            {
                "name": "R-77",
                "type": "воздух-воздух",
                "R_min": 300.0,
                "R_max": 19000.0,
                "midle_speed": 1000.0,
                "angle_effect": 70.0
            },
            {
                "name": "AGM-88 HARM",
                "type": "воздух-земля",
                "R_min": 1000.0,
                "R_max": 15000.0,
                "midle_speed": 950.0,
                "angle_effect": 45.0
            }
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
                "name": "Военный завод",
                "a": 500.0,
                "b": 300.0,
                "h": 50.0,
                "R_defeat": 100.0,
                "average_number": 1.5,
                "x_purpose": 10000.0,
                "y_purpose": 5000.0
            },
            {
                "name": "Аэродром",
                "a": 2000.0,
                "b": 1500.0,
                "h": 10.0,
                "R_defeat": 200.0,
                "average_number": 2.0,
                "x_purpose": 15000.0,
                "y_purpose": 8000.0
            },
            {
                "name": "Радарная станция",
                "a": 100.0,
                "b": 100.0,
                "h": 20.0,
                "R_defeat": 50.0,
                "average_number": 1.0,
                "x_purpose": 12000.0,
                "y_purpose": 6000.0
            }
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
                "name": "S-300",
                "n_defense": 4,
                "n_rocket_d": 8,
                "v_defense": 2000.0,
                "t_passive": 5.0,
                "t_changing": 10.0,
                "t_def": 15.0,
                "x_defense": [1000.0, 2000.0, 3000.0, 4000.0],
                "y_defense": [500.0, 1500.0, 2500.0, 3500.0],
                "l_min": 500.0,
                "l_max": 40000.0,
                "angle_effect": 90.0,
                "width_defense": 120.0,
                "h_max": 27000.0,
                "P_defeat": 0.8,
                "P_detect": ([[0.7, 0.8], [0.85, 0.9]])
            },
            {
                "name": "Patriot",
                "n_defense": 6,
                "n_rocket_d": 12,
                "v_defense": 1800.0,
                "t_passive": 4.0,
                "t_changing": 8.0,
                "t_def": 12.0,
                "x_defense": [5000.0, 6000.0, 7000.0, 8000.0, 9000.0, 10000.0],
                "y_defense": [2000.0, 3000.0, 4000.0, 5000.0, 6000.0, 7000.0],
                "l_min": 1000.0,
                "l_max": 35000.0,
                "angle_effect": 120.0,
                "width_defense": 90.0,
                "h_max": 24000.0,
                "P_defeat": 0.75,
                "P_detect": ([[0.6, 0.7], [0.75, 0.8]])
            },
            {
                "name": "Iron Dome",
                "n_defense": 8,
                "n_rocket_d": 16,
                "v_defense": 1500.0,
                "t_passive": 3.0,
                "t_changing": 6.0,
                "t_def": 9.0,
                "x_defense": [11000.0, 12000.0, 13000.0, 14000.0, 15000.0, 16000.0, 17000.0, 18000.0],
                "y_defense": [8000.0, 9000.0, 10000.0, 11000.0, 12000.0, 13000.0, 14000.0, 15000.0],
                "l_min": 2000.0,
                "l_max": 30000.0,
                "angle_effect": 150.0,
                "width_defense": 60.0,
                "h_max": 20000.0,
                "P_defeat": 0.85,
                "P_detect": ([[0.8, 0.85], [0.9, 0.95]])
            }
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
                "P_see": ([[0.9, 0.95], [0.98, 1.0]])
            },
            {
                "name": "Холмистая местность",
                "P_see": ([[0.7, 0.8], [0.85, 0.9]])
            },
            {
                "name": "Горная местность",
                "P_see": ([[0.5, 0.6], [0.65, 0.75]])
            }
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