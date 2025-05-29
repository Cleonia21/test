import math
from data_base import DatabaseManager
from typing import Optional, Union, List
from entities import *
from dataclasses import dataclass
from collections import defaultdict
import bisect

# Создаем экземпляр DatabaseManager
db = DatabaseManager()

@dataclass
class CurrentDataSet:
        plane: Plane
        purpose: Purpose
        rocket: Rocket
        air_defence: AirDefense
        relief: Relief
        v: float
        h: int
        z: int
        plane_num: int

        # def append(self, currentDataSet):
        #     pass


@dataclass
class ProbabSurlData:
        P_detect: any
        n_defense: any
        n_rocket_d: any
        v_defense: any
        t_passive: any
        t_changing: any
        t_def: any
        x_defense: any
        y_defense: any
        l_min: any
        l_max: any
        width_defense: any
        h_max: any
        P_defeat: any
        h: any
        v: any
        z: any
        P_see: any
        R_min: any
        gap_max: any
        t_aim: any
        psi_max: any
        angle_effect: any
        n_planes: any

@dataclass
class GrafForNumPlanes:
    K: float
    plane_name: str
    plane_num: int

@dataclass
class GrafForName:
    K: float
    plane_name: str
    rocket_name: str

@dataclass
class GrafForSpeedHeight:
    K: float
    plane_name: str
    rocket_name: str
    h: int
    v: float

@dataclass
class Data_K:
    P_def: float
    P5: float
    P4: float
    P_prl1: float
    P_prl2: float
    W_a: float
    W_a_max: float
    plane_name: str
    plane_num: int
    rocket_name: str
    v: float
    h: int
    z: int

@dataclass
class das:
    K: float
    v: float
    h: int
    plane_num: int

def degrees_to_radians(degrees):
    return degrees * (math.pi / 180)

class Count():
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.data: CurrentDataSet = []
        self._dataCollection()

    def _dataCollection(self):


        planes = self.db.get_all_planes()
        rockets = self.db.get_all_rockets()
        purposes = self.db.get_all_purposes()
        air_defences = self.db.get_all_air_defenses()
        reliefs = self.db.get_all_reliefs()
        if planes == None or rockets == None or purposes == None or air_defences == None or reliefs == None:
            return

        for plane in planes:
            for purpose in purposes:
                for rocket in rockets:
                    for air_defence in air_defences:
                        for relief in reliefs:
                            for speed in range(100, 301, 50):
                                for height in range(50, 500, 50):
                                    for plane_num in range(1, 6):
                                        for z in range(int(-3 * plane.sigma_z), int(3 * plane.sigma_z), 100):
                                            currentDataSet = CurrentDataSet(
                                                plane=plane,
                                                rocket=rocket,
                                                purpose=purpose, 
                                                air_defence=air_defence,
                                                relief=relief,
                                                plane_num = plane_num,
                                                v = speed,
                                                h = height,
                                                z = z
                                                )
                                            self.data.append(currentDataSet)

    def count(self):
        plane_num_stats = {}  # (plane_name, plane_num) -> NumberContainer
        plane_rocket_stats = {}  # (plane_name, rocket_name) -> NumberContainer
        plane_velocity_altitude_stats = {}  # (plane_name, v, h) -> NumberContainer

        for data_point in self.data:
            prob_data = self._calculate_probabilities(data_point)
            k_value = self._cout_K(prob_data)
            container = NumberContainer(1, k_value)

            # Update plane_num_stats
            key = (prob_data.plane_name, prob_data.plane_num)
            plane_num_stats[key] = plane_num_stats.get(key, NumberContainer(0, 0)) + container

            # Update plane_rocket_stats
            key = (prob_data.plane_name, prob_data.rocket_name)
            plane_rocket_stats[key] = plane_rocket_stats.get(key, NumberContainer(0, 0)) + container

            # Update plane_velocity_altitude_stats
            key = (prob_data.plane_name, prob_data.h)
            plane_velocity_altitude_stats[key] = (plane_velocity_altitude_stats.get(key, NumberContainer(0, 0)) + container, prob_data.v)

        # Process plane number statistics
        plane_stats = {}
        best_plane_name = ""
        best_plane_score = 0
        
        for (plane_name, plane_num), container in plane_num_stats.items():
            avg_k = container.float_value / container.int_value
            
            if plane_name not in plane_stats:
                plane_stats[plane_name] = {
                    "plane_nums": [],
                    "k_values": []
                }
            
            plane_stats[plane_name]["plane_nums"].append(plane_num)
            plane_stats[plane_name]["k_values"].append(avg_k)

            if avg_k > best_plane_score:
                best_plane_name = plane_name
                best_plane_score = avg_k

        # Process plane-rocket combinations
        plane_rocket_scores = {}
        for (plane_name, rocket_name), container in plane_rocket_stats.items():
            avg_k = container.float_value / container.int_value
            plane_rocket_scores[f"{plane_name}{rocket_name}"] = avg_k

        # Process velocity-altitude data for best plane
        altitude_stats = defaultdict(lambda: {"velocity": [], "k_values": []})
        
        for (plane_name, altitude), data in plane_velocity_altitude_stats.items():
            if plane_name == best_plane_name:
                avg_k = data[0].float_value / data[0].int_value
                altitude_stats[altitude]["velocity"].append(data[1])
                altitude_stats[altitude]["k_values"].append(avg_k)

        return plane_stats, plane_rocket_scores, dict(altitude_stats)

    def _cout_K(self,data: Data_K):
        W = (data.P_def * data.P4 * data.W_a + (data.W_a_max - data.W_a) * data.P_def * data.P5 + (1 - data.W_a_max))
        Q = (1 - data.P_prl1 * data.P_prl2) * data.W_a + (data.W_a_max - data.W_a) * (1 - (1 - data.P_prl1 * data.P_prl2)**2) + (1 - data.W_a_max) * (1 - data.P_prl1)
        K = W / Q
        return K

    def _calculate_probabilities(self, data: CurrentDataSet):
        probabSurlData = ProbabSurlData(
            P_detect=data.air_defence.P_detect,
            n_defense=data.air_defence.n_defense,
            n_rocket_d=data.air_defence.n_rocket_d,
            v_defense=data.air_defence.v_defense,
            t_passive=data.air_defence.t_passive,
            t_changing=data.air_defence.t_changing,
            t_def=data.air_defence.t_def,
            x_defense=data.air_defence.x_defense,
            y_defense=data.air_defence.y_defense,
            l_min=data.air_defence.l_min,
            l_max=data.air_defence.l_max,
            width_defense=data.air_defence.width_defense,
            h_max=data.air_defence.h_max,
            P_defeat=data.air_defence.P_defeat,
            P_see=data.relief.P_see,
            R_min=data.rocket.R_min,
            gap_max=data.plane.gap_max,
            t_aim=data.plane.t_aim,
            psi_max=data.plane.psi_max,
            angle_effect=data.rocket.angle_effect,
            n_planes=data.plane_num,
            h=data.h,
            v=data.v,
            z=data.z
        )
        
        P4 = self._P_4(probabSurlData)
        P5 = self._P_prl1(probabSurlData)*self._P_prl2(probabSurlData)
        P_prl1 = self._P_prl1(probabSurlData)
        P_prl2 = self._P_prl2(probabSurlData)

        D3 = data.z / math.sin(degrees_to_radians(data.plane.psi_max))
        probab_average = self._choice(data.plane.P_detect, D3)
        p_z = self._P_z(data.plane.sigma_z, data.z)
        W_a_max = probab_average * p_z

        D_ob = self._ZVA(probabSurlData)
        probab_average = self._choice(data.plane.P_detect, D_ob)
        p_z = self._P_z(data.plane.sigma_z, data.z)
        W_a = probab_average * p_z

        P_def = self._polygon(data)

        data_K = Data_K(
            P_def=P_def,
            P4=P4,
            P5=P5,
            P_prl1=P_prl1,
            P_prl2=P_prl2,
            W_a_max=W_a_max,
            W_a=W_a,
            plane_name=data.plane.name,
            plane_num=data.plane_num,
            rocket_name=data.rocket.name,
            v=data.v,
            h=data.h,
            z=data.z
        )

        return data_K
    
    def count_test(self):
        tmp_data: CurrentDataSet = self.data
        result_data: type = []
        for d in tmp_data:
            d.purpose.R = 10
            d.purpose.kjsdfhkjvjksd = 2189312
            result = self._polygon(d)
            result_data.append(result)
        return result_data

    def _polygon(self, data: CurrentDataSet) -> float:
        # Базовые параметры
        tet = math.atan2(data.h, degrees_to_radians(data.rocket.R_min))  # arctg(altitude/R_min)
        ctg_tet = 1 / math.tan(degrees_to_radians(tet)) if math.tan(degrees_to_radians(tet)) != 0 else float('inf')
        sig_x = 4
        sig_y = 4

        a = data.purpose.a
        b = data.purpose.b
        h = data.purpose.h
        R_defeat = data.purpose.R_defeat
        # Расчет параметров в зависимости от типа оружия
        if data.rocket.type.lower() == "фугас":
            x1, y1 = 0, 0
            al1 = -b / 2 - R_defeat
            bt1 = b / 2 + R_defeat
            ga1 = -a / 2 - R_defeat
            de1 = a / 2 + R_defeat

            x2 = (b + R_defeat + h * ctg_tet) / 2
            y2 = 0
            al2 = b / 2 + R_defeat
            bt2 = b / 2 + h * ctg_tet
            ga2 = -a / 2
            de2 = a / 2
        else:
            x1, y1 = 0, 0
            al1 = -b / 2
            bt1 = b / 2
            ga1 = -a / 2
            de1 = a / 2

            x2 = (b + h * ctg_tet) / 2
            y2 = 0
            al2 = b / 2
            bt2 = b / 2 + h * ctg_tet
            ga2 = -a / 2
            de2 = a / 2

        def lagrange_function(x: float) -> float:
            """Функция Лагранжа (упрощенная реализация)"""
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))
        
        # Расчет вероятности поражения P_polygon
        term1 = (lagrange_function((bt1 - x1) / sig_x) - lagrange_function((al1 - x1) / sig_x))
        term2 = (lagrange_function((de1 - y1) / sig_y) - lagrange_function((ga1 - y1) / sig_y))
        term3 = (lagrange_function((bt2 - x2) / sig_x) - lagrange_function((al2 - x2) / sig_x))
        term4 = (lagrange_function((de2 - y2) / sig_y) - lagrange_function((ga2 - y2) / sig_y))

        P_polygon = term1 * term2 + term3 * term4

        # Расчет итоговой вероятности поражения
        if data.rocket.type.lower() == "фугас":
            P_def = 1 - (1 - P_polygon) ** (data.plane.n_rocket * data.plane_num)
        else:
            P_def = 1 - (1 - P_polygon / data.purpose.average_number) ** (data.plane.n_rocket * data.plane_num)

        return P_def

    def _P_prl1(self, data: ProbabSurlData):
        global P_all_survive
        g = 9.81  # ускорение свободного падения (м/с²)

        # Расчет D3
        D3 = data.z / math.sin(degrees_to_radians(data.psi_max))

        total_N = 0.0
        N_per_sphere = []

        # Обработка каждой сферы защиты
        for i in range(data.n_defense):
            sphere_x = data.x_defense[i]
            sphere_y = data.y_defense[i]
            sphere_radius = data.l_max  # Используем максимальный радиус

            # Проверка, находится ли точка (0, altitude, z) внутри сферы
            distance_squared = (sphere_x - 0) ** 2 + (sphere_y - data.h) ** 2 + data.z ** 2
            if distance_squared > sphere_radius ** 2:
                # Точка вне сферы - нет перехвата
                N_per_sphere.append(0)
                continue

            # Расчет правой границы сферы на высоте altitude
            right_bound = sphere_x + math.sqrt(sphere_radius ** 2 - (data.h - sphere_y) ** 2 - data.z ** 2)

            # Расчет длины отрезка перехвата
            segment_length = max(0, right_bound - (sphere_y + data.l_min))

            D_pys = segment_length
            N = 0.0
            P_see_r = 0.0
            while D_pys > 0 or N < data.n_rocket_d:
                t_per = D_pys / (data.v + data.v_defense) + data.t_def
                if data.h == 50:
                    P_see_r = self._choice(data.P_see, D_pys)
                if data.h > 50:
                    P_see_r = self._choice(data.P_see, D_pys) + 0.1 * data.h - 50 / 50
                if P_see_r > 1:
                    P_see_r = 1
                if t_per * data.v > D_pys:
                    P_detect_current = self._choice(data.P_detect, D_pys) * P_see_r
                    N += P_detect_current
                D_pys -= data.v * t_per

            N = min(N, data.n_rocket_d)
            N_per_sphere.append(N)
            total_N += N

        # Итоговая вероятность поражения одной цели
        P_kill = 1 - (1 - data.P_defeat) ** (total_N / data.n_planes)

        # Вероятность, что все самолёты выживут
        P_all_survive = (1 - P_kill)

        return P_all_survive
    
    def _P_prl2(self, data: ProbabSurlData):
        g = 9.81  # ускорение свободного падения (м/с²)

        # Расчет D3
        D3 = data.z / math.sin(degrees_to_radians(data.psi_max))

        total_N = 0.0
        N_per_sphere = []

        # Обработка каждой сферы защиты
        for i in range(data.n_defense):
            sphere_x = data.x_defense[i]
            sphere_y = data.y_defense[i]
            sphere_radius = data.l_max  # Используем максимальный радиус

            # Проверка, находится ли точка (0, altitude, z) внутри сферы
            distance_squared = (sphere_x - 0) ** 2 + (sphere_y - data.h) ** 2 + data.z ** 2
            if distance_squared > sphere_radius ** 2:
                # Точка вне сферы - нет перехвата
                N_per_sphere.append(0)
                continue

            # Расчет правой границы сферы на высоте altitude
            right_bound = sphere_x + math.sqrt(sphere_radius ** 2 - (data.h - sphere_y) ** 2 - data.z ** 2)

            # Расчет длины отрезка перехвата
            segment_length = max(0, right_bound - (sphere_y + data.l_min))

            D_pys = segment_length
            N = 0.0
            P_see_r = 0.0
            while D_pys > 0 and N < data.n_rocket_d:
                t_per = D_pys / (data.v_defense - data.v) + data.t_def
                if data.h == 50:
                    P_see_r = self._choice(data.P_see, D_pys)
                if data.h > 50:
                    P_see_r = self._choice(data.P_see, D_pys) + 0.1 * data.h - 50 / 50
                if P_see_r > 1:
                    P_see_r = 1
                if t_per * data.v > D_pys:
                    P_detect_current = self._choice(data.P_detect, D_pys) * P_see_r
                    N += P_detect_current
                D_pys -= data.v * t_per

            N = min(N, data.n_rocket_d)
            N_per_sphere.append(N)
            total_N += N

        # Итоговая вероятность поражения одной цели
        P_kill = 1 - (1 - data.P_defeat) ** (total_N / data.n_planes)

        # Вероятность, что все самолёты выживут
        P_all_survive = (1 - P_kill)

        return P_all_survive

    def _P_4(self, data: ProbabSurlData):
        g = 9.81  # ускорение свободного падения (м/с²)

        # Расчет D1, y_0, fi_0, R
        sqrt_part = math.sqrt(abs(data.z ** 2 - data.R_min ** 2))
        D1 = math.sqrt(data.R_min ** 2 + (data.v * data.t_aim) ** 2 + 2 * data.v * data.t_aim * sqrt_part)

        y_0 = math.sqrt(data.R_min ** 2 + (data.v * data.t_aim) ** 2 + 2 * data.v * data.t_aim * math.cos(degrees_to_radians(data.psi_max)))
        fi_0 = abs(math.asin(degrees_to_radians(data.R_min * math.sin(degrees_to_radians(data.psi_max)) / y_0)))
        R = data.v ** 2 / (g * math.sqrt(data.gap_max ** 2 - 1))

        # Решение уравнения для alf методом Ньютона
        def equation(alf):
            return data.z - (y_0 * math.sin(degrees_to_radians(alf)) + R * (1 - math.cos(degrees_to_radians(alf - fi_0))))

        alf = 0.5
        tolerance = 1e-6
        max_iter = 100

        for _ in range(max_iter):
            f = equation(alf)
            df = y_0 * math.cos(degrees_to_radians(alf)) - R * math.sin(degrees_to_radians(alf - fi_0))
            alf_new = alf - f / df

            if abs(alf_new - alf) < tolerance:
                break
            alf = alf_new

        # Расчет x_2 и D2
        x_2 = y_0 * math.cos(degrees_to_radians(alf)) + R * math.sin(degrees_to_radians(alf - fi_0))
        D2 = math.sqrt(x_2 ** 2 + data.z ** 2)

        # Расчет D3
        D3 = data.z / math.sin(degrees_to_radians(data.psi_max))

        total_P_kill = 0.0
        N_per_sphere = []
        N_sym = 0.0

        # Обработка каждой сферы защиты
        for i in range(data.n_defense):
            sphere_x = data.x_defense[i]
            sphere_y = data.y_defense[i]
            sphere_radius = (data.l_min + data.l_max) / 2  # Средний радиус сферы защиты

            # Проверка пересечения траектории со сферой
            distance_to_axis = math.sqrt((sphere_x - 0) ** 2 + (sphere_y - data.h) ** 2)
            if distance_to_axis > sphere_radius:
                N_per_sphere.append(0)
                continue

            # Инициализация переменных для текущей сферы
            D_pys = 0.0
            N = 0.0
            P_see_r = 0.0

            # Проверка условий D1 > D2 и D3
            if D1 > D2 and D3 < D1:
                # Расчет длины отрезков между y_defense+l_min и правой границей сферы
                right_bound = sphere_x + math.sqrt(sphere_radius ** 2 - (data.h - sphere_y) ** 2 - data.z ** 2)
                D_pys = max(0, right_bound - (sphere_y + data.l_min))

                # Расчет количества ракет и вероятности поражения для этого отрезка
                while D_pys > 0 and N < data.n_rocket_d:
                    t_per = D_pys / (data.v + data.v_defense) + data.t_def
                    if data.h == 50:
                        P_see_r = self._choice(data.P_see, D_pys)
                    if data.h > 50:
                        P_see_r = self._choice(data.P_see, D_pys) + 0.1 * data.h - 50 / 50
                    if P_see_r > 1:
                        P_see_r = 1
                    if t_per * data.v > D_pys:
                        P_detect_current = self._choice(data.P_detect, D_pys) * P_see_r
                        N += P_detect_current
                        D_pys -= data.v * t_per
                        # Вероятность поражения на этом участке
                    else:
                        break

            else:
                  # Расчет суммы двух отрезков (если есть)
                  right_bound = sphere_x + math.sqrt(sphere_radius ** 2 - (data.h - sphere_y) ** 2 - data.z ** 2)
                  left_bound = sphere_x - math.sqrt(sphere_radius ** 2 - (data.h - sphere_y) ** 2 - data.z ** 2)

                  # Первый отрезок
                  segment1 = 0
                  if right_bound > min(D2, D3) and (data.h - sphere_y) ** 2 + data.z ** 2 <= sphere_radius ** 2:
                     if D2 > D3:
                        x_start = x_2
                     else:
                        x_start = math.sqrt(D3 ** 2 - data.z ** 2)
                     segment1 = max(0, right_bound - x_start)

                  # Второй отрезок
                  segment2 = 0
                  if right_bound > min(D2, D3):
                    segment2 = max(0, min(right_bound, max(D2, D3)) - max(left_bound, min(D2, D3)))

                  D_pys = segment1 + segment2
                  N = 0
                  P_see_r = 0.0

                  while D_pys > 0 and N < data.n_rocket_d:
                      t_per = D_pys / (data.v + data.v_defense) + data.t_def
                      if data.h == 50:
                          P_see_r = self._choice(data.P_see, D_pys)
                      if data.h > 50:
                          P_see_r = self._choice(data.P_see, D_pys) + 0.1 * data.h - 50 / 50
                      if P_see_r > 1:
                          P_see_r = 1
                      if t_per * data.v > D_pys:
                          P_detect_current = self._choice(data.P_detect, D_pys) * P_see_r
                          N += P_detect_current
                          D_pys -= data.v * t_per
                      else:
                          break
                  N = min(N, data.n_rocket_d)
                  N_sym += N

        # Итоговая вероятность поражения одной цели
        P_kill = 1 - (1-data.P_defeat)**(N_sym/data.n_planes)

        # Вероятность, что все самолёты выживут
        P_all_survive = (1 - P_kill)

        return P_all_survive

    # def _W_a(self, data: CurrentDataSet, z: int, v: float):
    #     D_ob = self._ZVA(data, v)
    #     probab_average = self._choice(data.plane.P_detect, D_ob)
    #     p_z = self._P_z(data.plane.sigma_z, z)
    #     W_a = probab_average * p_z
    #     return W_a

    def _ZVA(self, data: ProbabSurlData) -> float:
        #print('zva')
        g = 9.81  # ускорение свободного падения (м/с²)

        # Расчет D1
        sqrt_part = math.sqrt(abs(data.R_min ** 2 - data.z ** 2))
        D1 = math.sqrt(data.R_min ** 2 + (data.v * data.t_aim) ** 2 + 2 * data.v * data.t_aim * sqrt_part)

        # Расчет y_0 и fi_0
        y_0 = math.sqrt(data.R_min ** 2 + (data.v * data.t_aim) ** 2 + 2 * data.v * data.t_aim * data.angle_effect)
        fi_0 = math.asin(degrees_to_radians(data.R_min * data.angle_effect / y_0))

        # Расчет R
        R = data.v ** 2 / (g * math.sqrt(data.gap_max ** 2 - 1))

        # Решение уравнения для alf (итеративный метод)
        def equation(alf):
            return data.z - (y_0 * math.sin(degrees_to_radians(alf)) + R * (1 - math.cos(degrees_to_radians(alf - fi_0))))

        # Начальное приближение
        alf = 0.5
        tolerance = 1e-6
        max_iter = 100

        for i in range(max_iter):
            #print(i)
            f = equation(alf)
            df = y_0 * math.cos(degrees_to_radians(alf)) - R * math.sin(degrees_to_radians(alf - fi_0))

            alf_new = alf - f / df

            if abs(alf_new - alf) < tolerance:
                break
            alf = alf_new

        # Расчет x_2 и D2
        x_2 = y_0 * math.cos(degrees_to_radians(alf)) + R * math.sin(degrees_to_radians(alf - fi_0))
        D2 = math.sqrt(x_2 ** 2 + data.z ** 2)

        # Расчет D3
        D3 = data.z / math.sin(degrees_to_radians(data.psi_max))

        # Выбор максимальной дистанции
        return max(D1, D2, D3)
    
    def _P_z(self, sigma_z: float, z: float) -> float:
        """
        Плотность вероятности нормального распределения
        """
        if isinstance(z, list):
            return [self._P_z(sigma_z, zi) for zi in z]

        coefficient = 1 / (sigma_z * math.sqrt(2 * math.pi))
        exponent = -0.5 * ((z / sigma_z) ** 2)
        return coefficient * math.exp(exponent)

    from typing import List, Optional

    from typing import List, Optional

    def _choice(self, P_detect, D_ob):

        # Проверка на пустые входные данные
        if not P_detect or not isinstance(P_detect, list) or len(P_detect) == 0:
            return None

        try:
            # Извлекаем первый столбец (значения D)
            D_values = [row[0] for row in P_detect]

            # Проверка, что D_ob - число
            if not isinstance(D_ob, (int, float)):
                return None

            # Сортируем массив по D_values
            P_detect_sorted = sorted(P_detect, key=lambda x: x[0])
            D_sorted = [row[0] for row in P_detect_sorted]
            P_sorted = [row[1] for row in P_detect_sorted]

            # Проверка на пустой массив после сортировки
            if not D_sorted:
                return None

            # Используем bisect для поиска позиции
            pos = bisect.bisect_left(D_sorted, D_ob)

            if pos == 0:
                return P_sorted[0]
            elif pos == len(D_sorted):
                return P_sorted[-1]
            elif D_sorted[pos] == D_ob:
                return P_sorted[pos]
            else:
                # Проверка на возможность интерполяции
                if pos >= len(D_sorted) or pos - 1 < 0:
                    return None
                return (P_sorted[pos - 1] + P_sorted[pos]) / 2

        except (TypeError, IndexError) as e:
            # Обработка возможных ошибок
            print(f"Error in _choice: {e}")
            return None
    """
    def _choice(self, P_detect: List[List[float]], D_ob: float) -> Optional[float]:
        
        if not P_detect or len(P_detect) < 2:
            return None

        # Сортируем по первому элементу (D)
        sorted_data = sorted(P_detect, key=lambda x: x[0])
        D_values = [x[0] for x in sorted_data]
        P_values = [x[1] for x in sorted_data]

        # Находим ближайшие значения
        closest = sorted(sorted_data, key=lambda x: abs(x[0] - D_ob))[:2]

        # Среднее арифметическое вероятностей
        return sum(x[1] for x in closest) / 2
         """

class NumberContainer:
    def __init__(self, int_value: int, float_value: float):
        self.int_value = int_value
        self.float_value = float_value

    def __add__(self, other):
        if isinstance(other, NumberContainer):
            new_int = self.int_value + other.int_value
            new_float = self.float_value + other.float_value
            return NumberContainer(new_int, new_float)
        else:
            raise TypeError("Unsupported operand type for +: expected 'NumberContainer'")

    def __repr__(self):
        return f"NumberContainer(int_value={self.int_value}, float_value={self.float_value})"