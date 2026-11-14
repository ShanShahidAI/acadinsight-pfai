"""Simple OOP models: directly matches the Programming for AI proposal."""
from dataclasses import dataclass

@dataclass
class Student:
    id: str
    name: str
    program: str = 'BS Artificial Intelligence'
    section: str = 'AI/3-1'

@dataclass
class Subject:
    id: str
    student_id: str
    code: str
    name: str
    credits: float

@dataclass
class Assessment:
    id: str
    subject_id: str
    component: str
    obtained: float
    max_marks: float
    weight: float

@dataclass
class Attendance:
    id: str
    subject_id: str
    attended: int
    held: int

@dataclass
class PreviousSemester:
    id: str
    student_id: str
    title: str
    credits: float
    gpa: float
