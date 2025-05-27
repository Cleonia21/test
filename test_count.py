import pytest
from math import isclose
from count import *
from entities import Plane, Purpose, Rocket, AirDefense, Relief

class testBD:

    def get_all_planes(self):
        return None

    def get_all_rockets(self):
        return None

    def get_all_purposes(self):
        return None

    def get_all_air_defenses(self):
        return None

    def get_all_reliefs(self):
        return None


def test_data():
    plane = Plane()
    plane.name="TestPlane"
    plane.sigma_z=500
    plane.gap_max=5
    plane.t_aim=10
    plane.psi_max=60
    plane.n_rocket=4
    plane.P_detect=[[1000, 0.8], [4000, 0.6], [20000, 0.1]]


    purpose = Purpose()
    purpose.a=5
    purpose.b=4
    purpose.h=3
    purpose.R_defeat=2
    purpose.average_number=2

    rocket = Rocket()
    rocket.name="TestRocket"
    rocket.R_min=500
    rocket.angle_effect=45
    rocket.type="фугас"

    air_defence = AirDefense()
    air_defence.P_detect=[[1000, 0.9], [8000, 0.7], [20000, 0.5]]
    air_defence.n_defense=2
    air_defence.n_rocket_d=4
    air_defence.v_defense=400
    air_defence.t_passive=5
    air_defence.t_changing=3
    air_defence.t_def=10
    air_defence.x_defense=[0, 200]
    air_defence.y_defense=[0, 150]
    air_defence.l_min=500
    air_defence.l_max=6000
    air_defence.width_defense=5000
    air_defence.h_max=5000
    air_defence.P_defeat=0.8

    relief = Relief()
    relief.P_see=[[1000, 0.9], [8000, 0.7], [20000, 0.5]]

    return CurrentDataSet(
        plane=plane,
        purpose=purpose,
        rocket=rocket,
        air_defence=air_defence,
        relief=relief,
        v=200,
        h=100,
        z=50,
        plane_num=2
    )

@pytest.fixture
def sample_current_data():
    return test_data()

@pytest.fixture
def sample_probab_data():
    tmp = test_data()
    probab_data = ProbabSurlData(
        P_detect=tmp.air_defence.P_detect,
        n_defense=tmp.air_defence.n_defense,
        n_rocket_d=tmp.air_defence.n_rocket_d,
        v_defense=tmp.air_defence.v_defense,
        t_passive=tmp.air_defence.t_passive,
        t_changing=tmp.air_defence.t_changing,
        t_def=tmp.air_defence.t_def,
        x_defense=tmp.air_defence.x_defense,
        y_defense=tmp.air_defence.y_defense,
        l_min=tmp.air_defence.l_min,
        l_max=tmp.air_defence.l_max,
        width_defense=tmp.air_defence.width_defense,
        h_max=tmp.air_defence.h_max,
        P_defeat=tmp.air_defence.P_defeat,
        P_see=tmp.relief.P_see,
        R_min=tmp.rocket.R_min,
        gap_max=tmp.plane.gap_max,
        t_aim=tmp.plane.t_aim,
        psi_max=tmp.plane.psi_max,
        angle_effect=tmp.rocket.angle_effect,
        n_planes=tmp.plane_num,
        h=tmp.h,
        v=tmp.v,
        z=tmp.z
    )
    return probab_data
    

def test_calculate_probabilities(sample_current_data):
    count = Count(testBD())
    data_K = count._calculate_probabilities(sample_current_data)
    
    assert isinstance(data_K, Data_K)
    assert 0 <= data_K.P_def <= 1
    assert 0 <= data_K.P4 <= 1
    assert 0 <= data_K.P5 <= 1
    assert 0 <= data_K.P_prl1 <= 1
    assert 0 <= data_K.P_prl2 <= 1
    assert 0 <= data_K.W_a <= 1
    assert 0 <= data_K.W_a_max <= 1
    assert data_K.plane_name == "TestPlane"
    assert data_K.rocket_name == "TestRocket"
    assert data_K.v == 200
    assert data_K.h == 100
    assert data_K.z == 50

def test_polygon(sample_current_data):
    count = Count(testBD())
    P_def = count._polygon(sample_current_data)
    
    assert isinstance(P_def, float)
    assert 0 <= P_def <= 1
    
    # Проверка для другого типа ракеты
    sample_current_data.rocket.type = "кумулятив"
    P_def_non_fugas = count._polygon(sample_current_data)
    assert 0 <= P_def_non_fugas <= 1

def test_P_prl1(sample_probab_data):
    count = Count(testBD())
    
    P_prl1 = count._P_prl1(sample_probab_data)
    assert isinstance(P_prl1, float)
    assert 0 <= P_prl1 <= 1


def test_P_prl2(sample_probab_data):
    count = Count(testBD())

    P_prl2 = count._P_prl2(sample_probab_data)
    assert isinstance(P_prl2, float)
    assert 0 <= P_prl2 <= 1

def test_P_4(sample_probab_data):
    count = Count(testBD())

    P_4 = count._P_4(sample_probab_data)
    assert isinstance(P_4, float)
    assert 0 <= P_4 <= 1

def test_ZVA(sample_probab_data):
    count = Count(testBD())
    
    D_ob = count._ZVA(sample_probab_data)
    assert isinstance(D_ob, float)
    assert D_ob > 0

def test_P_z():
    count = Count(testBD())
    sigma_z = 100
    z_values = [-200, -100, 0, 100, 200]
    
    for z in z_values:
        p = count._P_z(sigma_z, z)
        assert isinstance(p, float)
        assert 0 <= p <= 1
    
    # Проверка для списка значений
    p_list = count._P_z(sigma_z, z_values)
    assert len(p_list) == len(z_values)
    assert all(isinstance(p, float) for p in p_list)

def test_choice():
    count = Count(testBD())
    P_detect = [[100, 0.9], [200, 0.7], [300, 0.5]]
    
    # Точное совпадение
    assert count._choice(P_detect, 200) == 0.7
    
    # Между значениями
    result = count._choice(P_detect, 150)
    expected = (0.9 + 0.7) / 2
    assert isclose(result, expected)
    
    # За пределами диапазона
    assert count._choice(P_detect, 50) == 0.9
    assert count._choice(P_detect, 350) == 0.5
    
    # Пустые данные
    assert count._choice([], 100) is None
    #assert count._choice([[100, 0.5]], 100) is None