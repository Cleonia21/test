import numpy as np

class Plane:
    def __init__(self):
        self.name: str = ""
        self.n_rocket: int = 0
        self.sigma_z: int = 0.0
        self.psi_max: float = 0.0
        self.t_aim: float = 0.0
        self.gap_max: float = 0.0
        self.visibility: float = 0.0
        self.P_detect: list = [[]]  # 2D массив вероятностей обнаружения

class Rocket:
    def __init__(self):
        self.name: str = ""
        self.type: str = ""
        self.R_min: float = 0.0
        self.R_max: float = 0.0
        self.midle_speed: float = 0.0
        self.angle_effect: float = 0.0

class Purpose:
    def __init__(self):
        self.name: str = ""
        self.a: float = 0.0
        self.b: float = 0.0
        self.h: float = 0.0
        self.R_defeat: float = 0.0
        self.average_number: float = 0.0
        self.x_purpose: float = 0.0
        self.y_purpose: float = 0.0

class AirDefense:
    def __init__(self):
        self.name: str = ""
        self.n_defense: int = 0
        self.n_rocket_d: int = 0
        self.v_defense: float = 0.0
        self.t_passive: float = 0.0
        self.t_changing: float = 0.0
        self.t_def: float = 0.0
        self.x_defense: list = []
        self.y_defense: list = []
        self.l_min: float = 0.0
        self.l_max: float = 0.0
        self.angle_effect: float = 0.0
        self.width_defense: float = 0.0
        self.h_max: float = 0.0
        self.P_defeat: float = 0.0
        self.P_detect: list = [[]]  # 2D массив вероятностей обнаружения

class Relief:
    def __init__(self):
        self.name: str = ""
        self.P_see: list = [[]]  # 2D массив вероятностей видимости