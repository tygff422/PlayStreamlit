
from src.managers import TaskManager
from src.repositories import TaskRepository


def test_task_management_flow(tmp_path):
    """結合テスト：タスク追加から保存、読み込みまでの一連のフローを正常に連動させて検証"""
    test_file = tmp_path / "integration_tasks.csv"
    repository = TaskRepository(test_file)

    manager = TaskManager(repository=repository)

    manager.add_task(title="結合テストを書く")
    manager.add_task(title="Streamlitで画面を作る")

    new_manager = TaskManager(repository=repository)
    all_tasks = new_manager.get_active_tasks()

    assert len(all_tasks) == 2
    assert all_tasks[0].title == "結合テストを書く"
    assert all_tasks[1].title == "Streamlitで画面を作る"

