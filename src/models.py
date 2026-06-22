from dataclasses import dataclass


@dataclass
class Task:
    task_id: int
    title: str
    progress: int = 0
    status: str = "未着手"
    is_active: bool = True
