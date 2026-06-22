

import csv
from dataclasses import asdict
import os
import pathlib
from typing import List

from src.interfaces import TaskRepositoryInterface
from src.models import Task


class TaskRepository(TaskRepositoryInterface):
    """tasks.csvからタスクを読み込み、保存するクラス"""
    def __init__(self, file_path: str = pathlib.Path.cwd() / "./data/tasks.csv"):
        self.file_path = file_path

    def load_all(self) -> List[Task]:
        """tasks.csvが無い時は空のリストを返す"""
        if not os.path.exists(self.file_path):
            return []
        tasks = []
        with open(self.file_path, mode="r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                task = Task(
                    task_id=int(row["task_id"]),
                    title=row["title"],
                    progress=int(row["progress"]),
                    status=row["status"],
                    is_active=row["is_active"].lower() == "true",
                )
                tasks.append(task)
            return tasks

    def save_all(self, tasks: List[Task]):
        """tasks.csvに全てのタスクを保存する"""
        pathlib.Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)
    
        with open(self.file_path, mode="w", encoding="utf-8", newline="") as file:
            fieldnames = ["task_id", "title", "progress", "status", "is_active"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for task in tasks:
                writer.writerow(asdict(task))