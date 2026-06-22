import asyncio
import csv
from dataclasses import dataclass, asdict
import os
import pathlib
from turtle import title
from typing import List

import streamlit as st


@dataclass
class Task:
    task_id: int
    title: str
    progress: int = 0
    status: str = "未着手"
    is_active: bool = True


class TaskRepository:
    """tasks.csvからタスクを読み込み、保存するクラス"""
    def __init__(self, file_path: str = pathlib.Path.cwd() / "./data/tasks.csv"):
        self.file_path = file_path

    def load_all(self):
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


class TaskManager:
    def __init__(self, repository: TaskRepository):
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


    # def get_task_by_id(self, task_id):
    #     for task in self.tasks:
    #         if task.task_id == task_id:
    #             return task
    #     return None

    # def display_all_tasks(self):
    #     for task in self.tasks:
    #         task.display_task()
    #         print("-" * 20)




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




# ==========================================
# フェーズ2：Streamlit Web画面の実装
# ==========================================

# 1. ページの設定（ブラウザのタブに表示されるタイトルよ）
st.set_page_config(page_title="非同期タスクマネージャー", layout="wide")
st.title(" 映える！非同期一括処理型タスク管理マネージャー")

# 2. バックエンドロジックの初期化
# Streamlitは画面が動くたびにコードが上から再実行される特性があるから、
# データの管理クラス（TaskManager）が毎回リセットされないように「セッション状態」に保存するの。
if "manager" not in st.session_state:
    repo = TaskRepository("./data/tasks_streamlit.csv")
    st.session_state.manager = TaskManager(repo)

manager: TaskManager = st.session_state.manager

# ==========================================
# 画面レイアウト：お兄ちゃんの指摘通り「1画面に並記」するわよ！
# ==========================================
col1, col2 = st.columns(2)

# ------------------------------------------
# 左半分：現在の通常（アクティブ）タスク
# ------------------------------------------
with col1:
    st.header(" 現在の通常タスク")
    active_tasks = manager.get_active_tasks()

    if not active_tasks:
        st.info("有効な通常タスクはありません。下のフォームから追加してね！")
    else:
        # タスクの一覧を綺麗なテーブル（データフレーム）で表示
        # 画面切り替えなんてしなくても一目でわかるわね
        task_data = [
            {
                "ID": t.task_id,
                "タスク名": t.title,
                "進捗": f"{t.progress}%",
                "ステータス": t.status,
            }
            for t in active_tasks
        ]
        st.dataframe(task_data, use_container_width=True, hide_index=True)

# ------------------------------------------
# 右半分：完了したタスク（履歴）
# ------------------------------------------
with col2:
    st.header(" 完了したタスク（履歴）")
    inactive_tasks = manager.get_inactive_tasks()

    if not inactive_tasks:
        st.write("ここに完了したタスクが溜まっていくわよ。")
    else:
        inactive_data = [
            {"ID": t.task_id, "タスク名": t.title, "ステータス": t.status}
            for t in inactive_tasks
        ]
        st.dataframe(inactive_data, use_container_width=True, hide_index=True)

st.write("---")

# ==========================================
# 操作フォームエリア
# ==========================================
c_add, c_edit, c_history = st.columns(3)

# ① タスクの登録フォーム
with c_add:
    st.subheader("➕ タスクの新規登録")
    new_title = st.text_input("タスク名を入力", key="add_input")
    if st.button("タスクを登録", use_container_width=True):
        if new_title:
            manager.add_task(new_title)
            st.rerun()  # 画面を再描画して表を更新するの

# ② タスクの編集・完全削除フォーム
with c_edit:
    st.subheader(" 登録タスクの編集・削除")
    all_task_ids = [t.task_id for t in manager.tasks]

    if all_task_ids:
        selected_edit_id = st.selectbox("対象のタスクIDを選択", all_task_ids)
        new_name = st.text_input("新しいタスク名（編集用）")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("名前を変更", use_container_width=True):
                if new_name:
                    manager.edit_task(selected_edit_id, new_name)
                    st.rerun()
        with col_btn2:
            if st.button("🗑️ 完全削除", use_container_width=True):
                manager.delete_task(selected_edit_id)
                st.rerun()

# ③ 履歴タスクの再アクティブ化フォーム
with c_history:
    st.subheader(" 完了タスクの操作")
    inactive_ids = [t.task_id for t in inactive_tasks]

    if inactive_ids:
        selected_inactive_id = st.selectbox("履歴のタスクIDを選択", inactive_ids)
        if st.button("↩️ 通常タスクに復帰", use_container_width=True):
            manager.toggle_active(selected_inactive_id, is_active=True)
            st.rerun()
    else:
        st.caption("現在、操作できる履歴タスクはありません。")

st.write("---")

# ==========================================
# ★最重要：非同期一括実行フォーム（Step 6）
# ==========================================
st.subheader("⚡ 複数タスクの非同期一括実行")
executable_tasks = [t for t in active_tasks if t.progress < 100]

if not executable_tasks:
    st.info("現在、実行できる通常タスクはありません。")
else:
    # 複数選択（マルチセレクト）のUIを1行で作るわよ！
    selected_titles = st.multiselect(
        "実行したいタスクを複数選んでね（一斉に動き出すわよ！）",
        options=[t.title for t in executable_tasks],
    )

    # 選択されたタイトルのIDを抽出
    selected_ids = [
        t.task_id for t in executable_tasks if t.title in selected_titles
    ]

    if st.button("🚀 選択したタスクを一括実行！", type="primary"):
        if selected_ids:
            st.write("### ── パイプライン処理を実行中 ──")

            # 画面上に「タスクごとの進捗バー」用のプレースホルダー（置き場所）を動的に作る
            progress_bars = {}
            status_texts = {}
            targets = [t for t in manager.tasks if t.task_id in selected_ids]

            for t in targets:
                st.write(f"**[ID:{t.task_id}] {t.title}**")
                status_texts[t.task_id] = st.empty()
                progress_bars[t.task_id] = st.progress(0)

            # --- ここでバックエンドの非同期ロジックをハックするわよ ---
            # Streamlitの画面上でバーをアニメーションさせるために、
            # さっき作った「_execute_single_task」を画面用に少しだけ上書きして並行実行させるの
            async def _execute_single_task_for_ui(task: Task):
                task.status = "実行中"
                status_texts[task.task_id].text(" 処理中...")

                for i in range(1, 11):
                    task.progress = i * 10
                    # 画面の進捗バーとテキストをリアルタイムに更新（ここが映えポイント！）
                    progress_bars[task.task_id].progress(task.progress)
                    await asyncio.sleep(0.3)  # 非同期ウェイト

                task.status = "完了"
                task.is_active = False
                status_texts[task.task_id].text(" 完了しました！ ✅")

            # 複数タスクを同時に走らせる魔法の呪文（CLIの時と全く同じ！）
            async def run_ui_pipeline():
                await asyncio.gather(
                    *[_execute_single_task_for_ui(t) for t in targets]
                )

            # Streamlitの中で非同期関数を実行する呪文よ
            asyncio.run(run_ui_pipeline())

            # 処理が終わったらCSVに一括保存して、画面をリフレッシュ
            manager.repository.save_all(manager.tasks)
            st.success("すべてのタスクが完了しました！")
            st.rerun()



