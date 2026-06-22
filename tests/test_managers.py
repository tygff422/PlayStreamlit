import pytest
from src.managers import TaskManager
from src.interfaces import TaskRepositoryInterface
from src.models import Task

# ==========================================
# フィクスチャ（共通の事前準備マシーン）
# ==========================================
@pytest.fixture
def mock_manager(mocker):
    """Mockを使って..."""
    mock_repo = mocker.MagicMock(spec=TaskRepositoryInterface)
    initial_tasks = [
        Task(task_id=1, title="テストタスク1", progress=100, status="完了", is_active=False),
    ]
    mock_repo.load_all.return_value = initial_tasks
    manager = TaskManager(mock_repo)
    return manager, mock_repo


def test_add_task_id_and_save(mock_manager):
    manager, mock_repo = mock_manager
    manager.add_task("新しいタスク")
    assert len(manager.tasks) == 2
    assert manager.tasks[-1].task_id == 2
    mock_repo.save_all.assert_called_once_with(manager.tasks)


def test_toggle_active_to_true_resets_progress_to_zero(mock_manager):
    manager, mock_repo = mock_manager
    manager.toggle_active(1, is_active=True)
    task = manager.tasks[0]
    assert task.is_active is True
    assert task.progress == 0
    assert task.status == "未着手"
    mock_repo.save_all.assert_called_once_with(manager.tasks)


