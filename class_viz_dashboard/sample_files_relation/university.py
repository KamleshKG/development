from dataclasses import dataclass, field
from typing import List


# Aggregation
@dataclass
class Professor:
    name: str


@dataclass
class Department:
    name: str
    professors: List[Professor] = field(default_factory=list)  # Aggregation

    def add_professor(self, professor: Professor) -> None:
        self.professors.append(professor)


# Association
@dataclass
class Course:
    title: str


@dataclass
class Student:
    name: str
    courses: List[Course] = field(default_factory=list)  # Association

    def enroll(self, course: Course) -> None:
        self.courses.append(course)