import pytest
from src.models import Task

def test_task_init_with_all_arguments():
    task = Task(task_id=1, title="テストタイトル", progress=100, status="完了", is_active=False)
    assert task.task_id == 1
    assert task.title == "テストタイトル"
    assert task.progress == 100
    assert task.status == "完了"
    assert task.is_active == False

def test_task_init_with_default_arguments():
    task = Task(task_id=2, title="テストタイトル2")
    assert task.task_id == 2
    assert task.title == "テストタイトル2"
    assert task.progress == 0
    assert task.status == "未着手"
    assert task.is_active == True
