from pathlib import Path
import shutil

from PyQt5.QtWidgets import QApplication

from pyvisor.GUI.main_gui import MovScoreGUI
from pyvisor.paths import ensure_tmp_icon_dir, ensure_user_data_dir


def reset_directory(directory: Path) -> None:
    """Remove all contents from *directory* while keeping it available."""
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)


def main():
    import sys

    ensure_user_data_dir()
    tmp_icon_dir = ensure_tmp_icon_dir()
    reset_directory(tmp_icon_dir)

    app = QApplication(sys.argv)

    def _cleanup_tmp_icons() -> None:
        reset_directory(tmp_icon_dir)

    app.aboutToQuit.connect(_cleanup_tmp_icons)

    gui = MovScoreGUI()
    gui.show()

    code = app.exec_()
    _cleanup_tmp_icons()
    sys.exit(code)


if __name__ == "__main__":
    main()
