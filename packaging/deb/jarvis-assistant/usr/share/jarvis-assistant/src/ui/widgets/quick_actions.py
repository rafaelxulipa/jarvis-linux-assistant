"""
Painel de ações rápidas do modo desenvolvedor.
"""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QGridLayout, QScrollArea, QTextEdit,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui  import QFont, QColor
from src.config.settings import COLORS
from src.services import dev_tools


def _label(text: str, size: int = 9, color: str | None = None) -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(QFont("Courier New", size))
    lbl.setStyleSheet(f"color: {color or COLORS['text_secondary']}; background: transparent;")
    return lbl


def _neon_button(text: str, color: str | None = None) -> QPushButton:
    c = color or COLORS["accent"]
    btn = QPushButton(text)
    btn.setFont(QFont("Courier New", 9))
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            color: {c};
            background: rgba(0,0,0,0);
            border: 1px solid {c};
            border-radius: 4px;
            padding: 6px 10px;
            letter-spacing: 1px;
        }}
        QPushButton:hover {{
            background: rgba(0,212,255,0.08);
            border-color: {COLORS['text_primary']};
            color: {COLORS['text_primary']};
        }}
        QPushButton:pressed {{
            background: rgba(0,212,255,0.18);
        }}
    """)
    return btn


class DevToolsPanel(QWidget):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self._config = config
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._setup_ui()
        QTimer.singleShot(800, self._detect_tools)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        title = _label("◈  DEV ENVIRONMENT", 10, COLORS["accent"])
        title.setStyleSheet(f"color: {COLORS['accent']}; letter-spacing: 3px; background: transparent;")
        layout.addWidget(title)

        # Tools grid
        self._tools_grid = QGridLayout()
        self._tools_grid.setSpacing(4)
        layout.addLayout(self._tools_grid)

        # Quick actions
        layout.addSpacing(6)
        act_title = _label("◈  AÇÕES RÁPIDAS", 9, COLORS["accent2"])
        act_title.setStyleSheet(f"color: {COLORS['accent2']}; letter-spacing: 3px; background: transparent;")
        layout.addWidget(act_title)

        btn_grid = QGridLayout()
        btn_grid.setSpacing(6)

        actions = [
            ("VS Code",     self._open_vscode,   COLORS["accent"]),
            ("Terminal",    self._open_terminal,  COLORS["accent2"]),
            ("Navegador",   self._open_browser,   COLORS["accent3"]),
            ("Docker PS",   self._docker_ps,      COLORS["accent_warn"]),
        ]

        for i, (label, slot, color) in enumerate(actions):
            btn = _neon_button(label, color)
            btn.clicked.connect(slot)
            btn_grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(btn_grid)

        # Output terminal mini
        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setMaximumHeight(90)
        self._output.setFont(QFont("Courier New", 8))
        self._output.setStyleSheet(f"""
            QTextEdit {{
                background: rgba(0,0,0,0.5);
                color: {COLORS['accent3']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self._output)

    def _detect_tools(self):
        tools = dev_tools.detect_tools()
        # Clear grid
        while self._tools_grid.count():
            item = self._tools_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, tool in enumerate(tools):
            icon  = "✔" if tool["found"] else "✖"
            color = COLORS["accent3"] if tool["found"] else COLORS["accent_danger"]
            name  = tool["name"]
            ver   = tool["version"][:20] if tool["version"] else ""

            icon_lbl = QLabel(f"{icon} {name}")
            icon_lbl.setFont(QFont("Courier New", 8))
            icon_lbl.setStyleSheet(f"color: {color}; background: transparent;")

            ver_lbl = QLabel(ver)
            ver_lbl.setFont(QFont("Courier New", 7))
            ver_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; background: transparent;")

            self._tools_grid.addWidget(icon_lbl, i, 0)
            self._tools_grid.addWidget(ver_lbl,  i, 1)

    def _open_vscode(self):
        dev_tools.open_vscode()
        self._output.append("→ Abrindo VS Code...")

    def _open_terminal(self):
        dev_tools.open_terminal()
        self._output.append("→ Abrindo terminal...")

    def _open_browser(self):
        dev_tools.open_browser()
        self._output.append("→ Abrindo navegador...")

    def _docker_ps(self):
        result = dev_tools.run_docker_ps()
        self._output.clear()
        self._output.setPlainText(result)
