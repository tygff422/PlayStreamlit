import asyncio

import streamlit as st

from src.managers import TaskManager
from src.repositories import TaskRepository

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