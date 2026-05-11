"""
Janela principal — gerencia transição boot → dashboard.
"""
import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore    import Qt, QTimer, pyqtSlot
from PyQt6.QtGui     import QPainter, QColor, QBrush, QPen, QFont, QKeySequence, QShortcut

from src.config.settings         import COLORS
from src.ui.boot_sequence        import BootSequenceWidget
from src.ui.dashboard            import DashboardWidget
from src.ui.widgets.hud_elements import ScanlineOverlay, CornerBracket
from src.services.greeting       import get_greeting_text, get_ready_message
from src.services.tts_service    import TTSService


class JarvisWindow(QMainWindow):
    def __init__(self, config: dict):
        super().__init__()
        self._config = config
        self._tts    = TTSService(
            engine=config.get("tts_engine", "auto"),
            speed=config.get("voice_speed", 1.0),
        )

        self._setup_window()
        self._setup_ui()
        self._setup_shortcuts()

    # ------------------------------------------------------------------ #
    def _setup_window(self):
        self.setWindowTitle("J.A.R.V.I.S")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Full screen
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

    def _setup_ui(self):
        central = QWidget(self)
        central.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Top bar
        self._topbar = _TopBar(self._config)
        root_layout.addWidget(self._topbar)

        # Stacked: boot → dashboard
        self._stack = QStackedWidget()
        self._stack.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._boot      = BootSequenceWidget()
        self._dashboard = DashboardWidget(self._config)

        self._stack.addWidget(self._boot)       # index 0
        self._stack.addWidget(self._dashboard)  # index 1
        self._stack.setCurrentIndex(0)

        root_layout.addWidget(self._stack)

        # Bottom bar
        self._bottombar = _BottomBar()
        root_layout.addWidget(self._bottombar)

        # Scanlines overlay
        if self._config.get("scanlines", True):
            self._scanlines = ScanlineOverlay(self)
            self._scanlines.setGeometry(self.rect())

        # Corner brackets
        self._add_corner_brackets(central)

        # Wire boot → dashboard transition
        self._boot.boot_finished.connect(self._on_boot_finished)

    def _add_corner_brackets(self, parent: QWidget):
        size = 28
        CornerBracket(parent, size=size, corner="tl").move(8, 8)
        QTimer.singleShot(0, lambda: CornerBracket(parent, size=size, corner="tr").move(parent.width() - size - 8, 8))
        QTimer.singleShot(0, lambda: CornerBracket(parent, size=size, corner="bl").move(8, parent.height() - size - 8))
        QTimer.singleShot(0, lambda: CornerBracket(parent, size=size, corner="br").move(parent.width() - size - 8, parent.height() - size - 8))

    def _setup_shortcuts(self):
        # Escape to exit
        esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc.activated.connect(self.close)

        # F11 toggle fullscreen
        f11 = QShortcut(QKeySequence(Qt.Key.Key_F11), self)
        f11.activated.connect(self._toggle_fullscreen)

    # ------------------------------------------------------------------ #
    @pyqtSlot()
    def _on_boot_finished(self):
        self._stack.setCurrentIndex(1)
        user = self._config.get("user_name", "usuário")
        greeting = get_greeting_text(user)
        self._dashboard.set_greeting(greeting)

        if self._config.get("voice_enabled", True):
            full_text = greeting + " " + get_ready_message(user)
            self._tts.speak(full_text)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_scanlines"):
            self._scanlines.setGeometry(self.rect())

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(COLORS["bg_primary"]))
        p.end()

    def closeEvent(self, event):
        self._tts.stop()
        event.accept()


# ─────────────────────────────────────────────
class _TopBar(QWidget):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self._config = config
        self.setFixedHeight(36)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(0)

        # Left
        lbl_left = QLabel("◈ J.A.R.V.I.S  v3.0")
        lbl_left.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        lbl_left.setStyleSheet(f"color: {COLORS['accent']}; letter-spacing: 3px; background: transparent;")

        # Center
        lbl_center = QLabel("JUST A RATHER VERY INTELLIGENT SYSTEM")
        lbl_center.setFont(QFont("Courier New", 7))
        lbl_center.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_center.setStyleSheet(f"color: {COLORS['text_dim']}; letter-spacing: 4px; background: transparent;")

        # Right
        user = config.get("user_name", "USER")
        lbl_right = QLabel(f"USER: {user.upper()}  ◈")
        lbl_right.setFont(QFont("Courier New", 9))
        lbl_right.setAlignment(Qt.AlignmentFlag.AlignRight)
        lbl_right.setStyleSheet(f"color: {COLORS['text_secondary']}; letter-spacing: 2px; background: transparent;")

        layout.addWidget(lbl_left)
        layout.addStretch()
        layout.addWidget(lbl_center)
        layout.addStretch()
        layout.addWidget(lbl_right)

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(COLORS["bg_secondary"]))
        pen = QPen(QColor(COLORS["border"]))
        pen.setWidth(1)
        p.setPen(pen)
        p.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        p.end()


class _BottomBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(26)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)

        hints = [
            "[ESC] Fechar",
            "[F11] Tela cheia",
        ]

        for hint in hints:
            lbl = QLabel(hint)
            lbl.setFont(QFont("Courier New", 7))
            lbl.setStyleSheet(
                f"color: {COLORS['text_dim']}; letter-spacing: 1px; background: transparent;"
            )
            layout.addWidget(lbl)
            layout.addSpacing(20)

        layout.addStretch()

        self._status = QLabel("SISTEMA OPERACIONAL  ●")
        self._status.setFont(QFont("Courier New", 7))
        self._status.setStyleSheet(
            f"color: {COLORS['accent3']}; letter-spacing: 2px; background: transparent;"
        )
        layout.addWidget(self._status)

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(COLORS["bg_secondary"]))
        pen = QPen(QColor(COLORS["border"]))
        p.setPen(pen)
        p.drawLine(0, 0, self.width(), 0)
        p.end()
