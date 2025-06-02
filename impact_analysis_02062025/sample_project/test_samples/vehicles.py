from abc import ABC, abstractmethod

class Drivable(ABC):
    @abstractmethod
    def drive(self):
        pass

class Engine:
    pass

class Car(Drivable):
    def __init__(self):
        self.__engine: Engine = Engine()  # Strong composition

    def drive(self):
        pass

class ElectricBicycle(Drivable):
    def drive(self):
        pass