"""
Dashboard principal — layout HUD com relógio, stats, dev tools e ações.
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QScrollArea, QFrame, QSizePolicy, QLineEdit,
)
from PyQt6.QtCore  import Qt, QTimer, pyqtSignal
from PyQt6.QtGui   import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient

from src.config.settings          import COLORS
from src.ui.widgets.clock_widget  import ClockWidget
from src.ui.widgets.system_stats  import SystemStatsPanel
from src.ui.widgets.quick_actions import DevToolsPanel
from src.ui.widgets.hud_elements  import SpinnerRing, GlowPanel, ScanlineOverlay, CornerBracket


def _divider(vertical: bool = False) -> QFrame:
    line = QFrame()
    if vertical:
        line.setFrameShape(QFrame.Shape.VLine)
    else:
        line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"color: {COLORS['border']}; background: {COLORS['border']};")
    line.setFixedWidth(1) if vertical else line.setFixedHeight(1)
    return line


class DashboardWidget(QWidget):
    command_submitted = pyqtSignal(str)

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self._config = config
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._setup_ui()

    def _setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Left panel ──────────────────────────────────────────────────
        left = self._build_left_panel()
        root.addWidget(left, stretch=2)

        root.addWidget(_divider(vertical=True))

        # ── Center panel ────────────────────────────────────────────────
        center = self._build_center_panel()
        root.addWidget(center, stretch=3)

        root.addWidget(_divider(vertical=True))

        # ── Right panel ─────────────────────────────────────────────────
        right = self._build_right_panel()
        root.addWidget(right, stretch=2)

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        stats = SystemStatsPanel()
        layout.addWidget(stats)
        layout.addStretch()

        # Battery (if available)
        self._battery_label = QLabel("")
        self._battery_label.setFont(QFont("Courier New", 8))
        self._battery_label.setStyleSheet(
            f"color: {COLORS['text_dim']}; background: transparent; padding: 8px;"
        )
        layout.addWidget(self._battery_label)
        QTimer.singleShot(1500, self._update_battery)

        return panel

    def _build_center_panel(self) -> QWidget:
        panel = QWidget()
        panel.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Spinner rings
        ring_row = QHBoxLayout()
        ring_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._spinner = SpinnerRing(size=140, rings=3)
        ring_row.addWidget(self._spinner)
        layout.addLayout(ring_row)

        # Clock
        self._clock = ClockWidget()
        layout.addWidget(self._clock)

        # Greeting label
        self._greeting_label = QLabel("")
        self._greeting_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._greeting_label.setFont(QFont("Courier New", 10))
        self._greeting_label.setWordWrap(True)
        self._greeting_label.setStyleSheet(
            f"color: {COLORS['text_primary']}; background: transparent; "
            f"letter-spacing: 1px; padding: 0 20px;"
        )
        layout.addWidget(self._greeting_label)

        layout.addStretch()

        # Command input
        self._cmd_input = _CommandInput()
        self._cmd_input.command_submitted.connect(self.command_submitted)
        layout.addWidget(self._cmd_input)

        # Status bar
        self._status_bar = _StatusBar()
        layout.addWidget(self._status_bar)

        return panel

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        panel.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        dev = DevToolsPanel(self._config)
        layout.addWidget(dev)
        layout.addStretch()

        return panel

    def set_greeting(self, text: str):
        self._greeting_label.setText(text)

    def set_status(self, text: str):
        self._status_bar.set_status(text)

    def _update_battery(self):
        from src.services.system_info import get_battery_info
        bat = get_battery_info()
        if bat:
            icon = "⚡" if bat["plugged"] else "🔋"
            self._battery_label.setText(f"{icon}  {bat['percent']:.0f}%")


class _StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._pulse = 0.0
        self._dir   = 1

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._dot = _PulseDot()
        self._lbl = QLabel("SISTEMA OPERACIONAL")
        self._lbl.setFont(QFont("Courier New", 8))
        self._lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; background: transparent; letter-spacing: 3px;"
        )
        layout.addStretch()
        layout.addWidget(self._dot)
        layout.addWidget(self._lbl)
        layout.addStretch()

    def set_status(self, text: str):
        self._lbl.setText(text)


class _CommandInput(QWidget):
    command_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(8)

        prompt = QLabel(">_")
        prompt.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        prompt.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        layout.addWidget(prompt)

        self._field = QLineEdit()
        self._field.setPlaceholderText("Digite um comando...")
        self._field.setFont(QFont("Courier New", 10))
        self._field.setStyleSheet(
            f"QLineEdit {{"
            f"  background: rgba(0,0,0,0.4);"
            f"  color: {COLORS['text_primary']};"
            f"  border: 1px solid {COLORS['border']};"
            f"  border-radius: 2px;"
            f"  padding: 4px 8px;"
            f"  letter-spacing: 1px;"
            f"}}"
            f"QLineEdit:focus {{"
            f"  border: 1px solid {COLORS['accent']};"
            f"}}"
        )
        self._field.returnPressed.connect(self._submit)
        layout.addWidget(self._field)

    def _submit(self):
        text = self._field.text().strip()
        if text:
            self.command_submitted.emit(text)
            self._field.clear()


class _PulseDot(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._alpha = 255
        self._dir   = -8
        self.setFixedSize(10, 10)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        timer = QTimer(self)
        timer.timeout.connect(self._tick)
        timer.start(40)

    def _tick(self):
        self._alpha += self._dir
        if self._alpha <= 80:
            self._dir = 8
        elif self._alpha >= 255:
            self._dir = -8
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QColor(COLORS["accent3"])
        c.setAlpha(self._alpha)
        p.setBrush(QBrush(c))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(2, 2, 6, 6)
        p.end()
