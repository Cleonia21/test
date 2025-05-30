from typing import Dict, List, Type, Union
from entities import *

class DBCache:
    def __init__(self):
        # Инициализируем хранилища для каждого типа объектов
        self._cache: Dict[Type, List[int]] = {
            Plane: [],
            Rocket: [],
            Purpose: [],
            AirDefense: [],
            Relief: []
        }
    
    def add_ids(self, obj_type: Type[Union[Plane, Rocket, Purpose, AirDefense, Relief]], ids: List[int]):
        """Добавляет список ID для указанного типа объекта"""
        if obj_type in self._cache:
            self._cache[obj_type].extend(ids)
        else:
            raise ValueError(f"Unsupported object type: {obj_type}")
    
    def get_ids(self, obj_type: Type[Union[Plane, Rocket, Purpose, AirDefense, Relief]]) -> List[int]:
        """Возвращает список ID для указанного типа объекта"""
        return self._cache.get(obj_type, [])
    
    def clear_ids(self, obj_type: Type[Union[Plane, Rocket, Purpose, AirDefense, Relief]]):
        """Очищает кэш для указанного типа объекта"""
        if obj_type in self._cache:
            self._cache[obj_type] = []
    
    def clear_all(self):
        """Очищает весь кэш"""
        for key in self._cache:
            self._cache[key] = []
    
    def count(self, obj_type: Type[Union[Plane, Rocket, Purpose, AirDefense, Relief]]) -> int:
        """Возвращает количество ID для указанного типа объекта"""
        return len(self._cache.get(obj_type, []))
    
    def total_count(self) -> int:
        """Возвращает общее количество ID во всем кэше"""
        return sum(len(ids) for ids in self._cache.values())
    
    def __contains__(self, item: tuple[Type[Union[Plane, Rocket, Purpose, AirDefense, Relief]], int]):
        """Проверяет, содержится ли ID для указанного типа объекта в кэше"""
        obj_type, id_int = item
        return id_int in self._cache.get(obj_type, [])
    
    def __str__(self) -> str:
        """Строковое представление кэша"""
        return "\n".join(
            f"{cls.__name__}: {len(ids)} items" 
            for cls, ids in self._cache.items()
        )
    
# Пример использования
if __name__ == "__main__":
    cache = DBCache()

    # Добавляем ID самолетов
    cache.add_ids(Plane, [1, 2, 3])

    # Добавляем ID ракет
    cache.add_ids(Rocket, [101, 102])

    # Проверяем наличие
    print((Plane, 1) in cache)  # True
    print((Rocket, 1) in cache)  # False

    # Получаем все ID целей
    purpose_ids = cache.get_ids(Purpose)
    print(purpose_ids)  # []

    # Очищаем кэш для самолетов
    cache.clear_ids(Plane)
    print(cache.count(Plane))  # 0