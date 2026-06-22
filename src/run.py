import sys
from pathlib import Path
# プロジェクトのルート（PlayStreamlit）をPythonの検索パスに強制登録する！
sys.path.append(str(Path(__file__).parent.parent))

import streamlit.web.bootstrap

if __name__ == "__main__":
    # run.pyがsrc/フォルダの中にある前提で、同じフォルダのapp.pyを指す
    app_path = Path(__file__).parent / "app.py"
    
    # 💡 要求されている3つの引数をデフォルト値でしっかり渡す！
    streamlit.web.bootstrap.run(
        main_script_path=str(app_path),
        is_hello=False,       # Streamlit公式のデモ画面じゃないからFalse
        args=[],              # コマンドライン引数は空
        flag_options={}       # オプション設定も空
    )