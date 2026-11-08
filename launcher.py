

import sys
from pathlib import Path

from streamlit.web import cli as stcli


def get_app_path():

    # Normal Python execution
    if not getattr(sys, "frozen", False):
        return Path(__file__).resolve().parent / "app.py"

    # PyInstaller packaged execution
    bundle_dir = Path(sys._MEIPASS)

    return bundle_dir / "app.py"


def main():

    app_path = get_app_path()

    if not app_path.exists():
        raise FileNotFoundError(
            f"Application file not found: {app_path}"
        )

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),

        "--server.address=127.0.0.1",
        "--server.port=8501",
        "--server.headless=false",

        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false",
    ]

    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
