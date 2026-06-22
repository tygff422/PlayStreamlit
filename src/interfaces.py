# src/interfaces.py
from abc import ABC, abstractmethod
from typing import List
from src.models import Task

class TaskRepositoryInterface(ABC):
    @abstractmethod
    def save_all(self, tasks: List[Task]) -> None:
        pass

    @abstractmethod
    def load_all(self) -> List[Task]:
        pass
