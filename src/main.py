

# ==========================================
# 動作確認用のテストコード 01
# ==========================================
# if __name__ == "__main__":
#     print("=== Step 1: 動作確認開始 ===")

#     # 1. リポジトリの準備
#     repo = TaskRepository("./data/tasks_test.csv")

#     # 2. テスト用データの作成
#     test_tasks = [
#         Task(task_id=1, title="音響バッファの検証"),
#         Task(task_id=2, title="LED消灯テスト", progress=50, status="実行中"),
#     ]

#     # 3. CSVへ保存
#     print("データをCSVに保存します...")
#     repo.save_all(test_tasks)

#     # 4. CSVから再読み込み
#     print("CSVからデータを読み込みます...")
#     loaded_tasks = repo.load_all()

#     # 5. 中身の確認
#     for t in loaded_tasks:
#         print(
#             f"ID:{t.task_id} | タイトル:{t.title} | 進捗:{t.progress}% | ステータス:{t.status} | アクティブ:{t.is_active}"
#         )

#     print("=== 動作確認終了 ===")
#     print(os.getcwd())


# ==========================================
# 動作確認用のテストコード 02
# ==========================================
# if __name__ == "__main__":
#     print("=== Step 2: 動作確認開始 ===")

#     # テスト用の綺麗なCSVを用意
#     if os.path.exists("./data/tasks_test.csv"):
#         os.remove("./data/tasks_test.csv")

#     repo = TaskRepository("./data/tasks_test.csv")
#     manager = TaskManager(repo)

#     # 1. タスクの追加テスト
#     manager.add_task("マイクの音量調整")
#     manager.add_task("スピーカーの位相チェック")
#     manager.add_task("3番めのタスク（テスト用）")
#     manager.add_task("4番めのタスク（テスト用）")

#     # 2. タスクの名前編集テスト
#     manager.edit_task(1, "マイクのゲイン・音量調整（修正版）")

#     # 3. 非アクティブ化（完了にして履歴へ飛ばす）
#     manager.toggle_active(2, is_active=False)

#     # 4. 現在の状態を表示（アクティブと非アクティブの仕分け確認）
#     print("\n--- 現在の通常タスク一覧 ---")
#     for t in manager.get_active_tasks():
#         print(f"ID:{t.task_id} | {t.title} | {t.status}")

#     print("\n--- 現在の完了タスク（履歴）一覧 ---")
#     for t in manager.get_inactive_tasks():
#         print(f"ID:{t.task_id} | {t.title} | {t.status}")

#     # 5. 再アクティブ化テスト
#     print("\n履歴からID:2を通常タスクに復帰させます...")
#     manager.toggle_active(2, is_active=True)

#     # 6. 完全削除テスト
#     print("\nID:4を完全に削除します...")
#     manager.delete_task(4)

#     print("\n--- 最終的なCSVの中身 ---")
#     for t in repo.load_all():
#         print(f"ID:{t.task_id} | {t.title} | アクティブ:{t.is_active}")

#     print("=== 動作確認終了 ===")

# ==========================================
# Step 3: 動作確認用のテストコード（非同期版に書き換え）
# ==========================================
# async def main():
#     print("=== Step 3: 非同期動作確認開始 ===")

#     # テスト用の綺麗なCSVを用意
#     if os.path.exists("./data/tasks_test.csv"):
#         os.remove("./data/tasks_test.csv")

#     repo = TaskRepository("./data/tasks_test.csv")
#     manager = TaskManager(repo)

#     # 1. テスト用のタスクを3つ登録
#     manager.add_task("音響デバイスの初期化")
#     manager.add_task("周波数応答の計測")
#     manager.add_task("スピーカーの極性チェック")

#     # 追加
#     print("\n--- ID:2 を実行 ---")
#     await manager._run_single_task(manager.get_active_tasks()[1])

#     # 2. タスクを【複数選択】して、非同期一括実行！
#     # ここでは ID:1 と ID:3 を選んだと仮定するわよ
#     print("\nID:1 と ID:3 を同時に実行します...")
#     await manager.run_pipeline_tasks([1, 3])

#     # 3. 実行後の通常タスク（まだ残ってるやつ）と、完了したやつ（履歴）を表示
#     print("--- 現在の通常タスク一覧（未実行のやつだけ残るはず） ---")
#     for t in manager.get_active_tasks():
#         print(f"ID:{t.task_id} | {t.title} | {t.status} ({t.progress}%)")

#     print("\n--- 現在の完了タスク（非同期で自動でここに移動したはず） ---")
#     for t in manager.get_inactive_tasks():
#         print(f"ID:{t.task_id} | {t.title} | {t.status} ({t.progress}%)")

#     print("=== 非同期動作確認終了 ===")
# asyncio.run(main())








