#!/usr/bin/env python3
"""
JARVIS Linux Assistant — Entry point
"""
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore    import Qt, QCoreApplication
from PyQt6.QtGui     import QIcon

from src.config.settings import load_config, BASE_DIR
from src.ui.main_window  import JarvisWindow


def main():
    # High DPI support
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS Linux Assistant")
    app.setOrganizationName("JarvisAI")

    # Dark application palette (fallback)
    app.setStyle("Fusion")

    config = load_config()

    window = JarvisWindow(config)
    window.show()
    window.showFullScreen()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
