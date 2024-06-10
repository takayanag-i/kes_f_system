import sys
from PyQt6.QtWidgets import QApplication

from pkgs.common.executor import Executor


def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    executor = Executor()
    executor.window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
