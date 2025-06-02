from typing import List
from dataclasses import dataclass, field

@dataclass
class Professor:
    name: str

@dataclass
class Department:
    professors: List[Professor]  # Aggregation

@dataclass
class Course:
    title: str

@dataclass
class Student:
    courses: List[Course] = field(default_factory=list)  # Aggregation