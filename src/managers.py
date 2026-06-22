import asyncio
from typing import List

from src.models import Task
from src.interfaces import TaskRepositoryInterface


class TaskManager:
    def __init__(self, repository: TaskRepositoryInterface):
        self.repository = repository
        self.tasks: List[Task] = self.repository.load_all()

    def get_active_tasks(self) -> List[Task]:
        """アクティブな（未完了の）タスク一覧を返す"""
        return [t for t in self.tasks if t.is_active]

    def get_inactive_tasks(self) -> List[Task]:
        """非アクティブな（完了・アーカイブされた）タスク一覧を返す"""
        return [t for t in self.tasks if not t.is_active]

    def add_task(self, title: str):
        next_id = max([t.task_id for t in self.tasks], default=0) + 1
        new_task = Task(task_id=next_id, title=title)
        self.tasks.append(new_task)
        self.repository.save_all(self.tasks)  # 変更があったら即座にCSVへ保存
        print(f"【システム】タスク「{title}」(ID:{next_id}) を登録しました。")

    def edit_task(self, task_id: int, new_title: str):
        for task in self.tasks:
            if task.task_id == task_id:
                task.title = new_title
                self.repository.save_all(self.tasks)
                print(
                    f"【システム】ID:{task_id} のタスク名を「{new_title}」に変更しました。"
                )
                return
        print(f"【エラー】ID:{task_id} のタスクが見つかりません。")

    def toggle_active(self, task_id: int, is_active: bool):
        """タスクのアクティブ状態を切り替える（非アクティブ化 / 再アクティブ化）"""
        for task in self.tasks:
            if task.task_id == task_id:
                task.is_active = is_active
                if is_active:
                    # 再アクティブ化の時は、進捗を0%に戻す（お兄ちゃんの要望ね！）
                    task.progress = 0
                    task.status = "未着手"
                    print(
                        f"【システム】ID:{task_id} のタスクを再アクティブ化しました（通常一覧へ復帰）。"
                    )
                else:
                    task.progress = 100
                    task.status = "完了"
                    print(
                        f"【システム】ID:{task_id} のタスクを非アクティブ化しました（履歴へ移動）。"
                    )
                self.repository.save_all(self.tasks)
                return
        print(f"【エラー】ID:{task_id} のタスクが見つかりません。")

    def delete_task(self, task_id: int):
        """指定されたIDのタスクをリストおよびCSVから完全に削除する"""
        for task in self.tasks:
            if task.task_id == task_id:
                self.tasks.remove(task)  # メモリのリストから削除（幽霊タスク化の防止）
                self.repository.save_all(self.tasks)  # CSVファイルを丸ごと上書き保存
                print(
                    f"【システム】ID:{task_id} のタスクを完全に削除しました。"
                )
                return
        print(f"【エラー】ID:{task_id} のタスクが見つかりません。")

    # def get_task_by_id(self, task_id):
    #     for task in self.tasks:
    #         if task.task_id == task_id:
    #             return task
    #     return None

    # def display_all_tasks(self):
    #     for task in self.tasks:
    #         task.display_task()
    #         print("-" * 20)

    async def _run_single_task(self, task: Task):
        """[非同期内部メソッド] 1つのタスクの進捗を非同期で進める"""
        task.status = "実行中"
        print(f"【開始】ID:{task.task_id}「{task.title}」を開始します。")

        # 0%から100%まで、10%ずつ進捗を進める（擬似的な重い処理）
        for i in range(1, 11):
            task.progress = i * 10
            # 進捗ログを出力（非同期で混ざり合う様子がわかるようにID付きで）
            print(
                f" └─ [ID:{task.task_id}] {task.title}: {task.progress}% 完了"
            )

            # ここで「作業待ち時間」をシミュレート。これが非同期のキモ！
            # time.sleepを使うと全体がフリーズするから、必ずasyncio.sleepを使うの
            await asyncio.sleep(0.3)

        # 100%になったらステータスを完了にし、自動で非アクティブ化（履歴へ移動）
        task.status = "完了"
        task.is_active = False
        print(
            f"【完了】ID:{task.task_id}「{task.title}」が完了し、履歴へ移動しました。✅"
        )

    async def run_pipeline_tasks(self, task_ids: List[int]):
        """ユーザーが選択した複数のタスクを、非同期で【同時に】一斉実行する"""
        # 指定されたIDに一致し、かつ今動かせる（アクティブな）タスクだけを抽出
        targets = [
            t
            for t in self.tasks
            if t.task_id in task_ids and t.is_active and t.progress < 100
        ]

        if not targets:
            print("【システム】実行対象の有効なタスクがありません。")
            return

        print(
            f"\n=== 非同期パイプライン始動（対象タスク数: {len(targets)}個） ==="
        )

        # ★これが非同期処理の魔法の呪文！
        # 抽出した全タスクの処理を一斉にスタートさせて、すべてが終わるのを同時に待つ
        await asyncio.gather(*[self._run_single_task(t) for t in targets])

        # すべての並行処理が終わったら、一括してCSVに保存する（整合性の担保）
        self.repository.save_all(self.tasks)
        print("=== 全タスクの非同期一括処理が完了し、CSVに保存しました ===\n")
