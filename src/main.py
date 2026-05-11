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

from src.config.settings import load_config, save_config, BASE_DIR, CONFIG_FILE
from src.ui.main_window  import JarvisWindow
from src.ui.setup_wizard import SetupWizard


def _is_first_run(config: dict) -> bool:
    """Primeira execução: flag explícita ou config ainda não foi personalizado."""
    if config.get("first_run", True):
        return True
    return False


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS Linux Assistant")
    app.setOrganizationName("JarvisAI")
    app.setStyle("Fusion")

    config = load_config()

    # Abrir wizard de configuração na primeira execução
    if _is_first_run(config):
        wizard = SetupWizard(config)
        result = wizard.exec()
        if result != SetupWizard.DialogCode.Accepted:
            # Usuário fechou o wizard — salvar mesmo assim para não perguntar de novo
            pass
        config["first_run"] = False
        save_config(config)
        # Recarregar para pegar valores salvos
        config = load_config()

    window = JarvisWindow(config)
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
