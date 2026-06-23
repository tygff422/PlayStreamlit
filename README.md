# PlayStreamlit
streamlitを使ったタスク管理アプリ(超最低限)を作成

## 概要
タスク管理をStreamlitを使って実現
WEBからタスク登録・確認、編集・削除、Active/DeActiveの切り替えを行うことが可能

## 実行コマンド
uv run python -m src.run

## テスト確認コマンド
uv run python -m pytest tests/test_models.py -sv
uv run python -m pytest tests/test_repositories.py -sv


