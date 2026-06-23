import csv
import pytest
from src.models import Task
from src.repositories import TaskRepository

def test_load_allreturns_empty_list_when_file_not_exists(tmp_path):
    """ファイルが存在しない場合、空のリストを返すことを確認するテスト"""
    test_file = tmp_path / "non_existent_tasks.csv"
    repo = TaskRepository(file_path=test_file)
    assert repo.load_all() == []


def test_save_all_and_load_all(tmp_path):
    """tasks.csvに全てのタスクを保存し、その内容を読み込むことを確認するテスト"""
    test_file = tmp_path / "tasks.csv"
    repo = TaskRepository(file_path=test_file)
    tasks = [
        Task(task_id=1, title="Test Task 1", progress=100, status="完了", is_active=False),
        Task(task_id=2, title="Test Task 2", progress=50, status="進行中", is_active=True),
    ]

    repo.save_all(tasks)
    assert test_file.exists()

    loaded_tasks = repo.load_all()
    assert loaded_tasks == tasks
    assert len(loaded_tasks) == 2

    assert loaded_tasks[0].task_id == 1
    assert loaded_tasks[0].title == "Test Task 1"
    assert loaded_tasks[0].progress == 100
    assert loaded_tasks[0].status == "完了"
    assert loaded_tasks[0].is_active == False

    assert loaded_tasks[1].task_id == 2
    assert loaded_tasks[1].title == "Test Task 2"
    assert loaded_tasks[1].progress == 50
    assert loaded_tasks[1].status == "進行中"
    assert loaded_tasks[1].is_active == True

