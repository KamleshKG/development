from abc import ABC, abstractmethod
from typing import final


# Explicit interface definition
class Drivable(ABC):
    """Interface defining driving capability (implementation relationship)"""

    @abstractmethod
    def drive(self) -> str:
        raise NotImplementedError


# Base class for inheritance
class Vehicle:
    """Base class for all vehicles (inheritance relationship)"""

    def __init__(self, make: str, model: str):
        self.make = make
        self.model = model


# Car demonstrates inheritance, interface implementation, and composition
@final
class Car(Vehicle, Drivable):
    """
    Car inherits from Vehicle (inheritance)
    Implements Drivable (interface implementation)
    Contains Engine (composition)
    """

    def __init__(self, make: str, model: str):
        super().__init__(make, model)
        self.__engine = self.__create_engine()  # Strong composition

    def drive(self) -> str:
        return f"{self.make} {self.model} is driving"

    @property
    def engine(self) -> 'Engine':
        return self.__engine

    def __create_engine(self) -> 'Engine':
        """Factory method showing composition"""
        return Engine()


@final
class ElectricBicycle(Drivable):
    """Implements Drivable (interface implementation)"""

    def drive(self) -> str:
        return "Pedaling with electric assist"


# Composition class
class Engine:
    """Part-of Car (composition relationship)"""

    def start(self) -> str:
        return "Engine started"