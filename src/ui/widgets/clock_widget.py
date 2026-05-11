"""
Relógio digital estilo HUD com data e efeito glow.
"""
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtGui     import QFont, QColor, QPainter, QPen, QLinearGradient, QBrush
from src.config.settings import COLORS

WEEKDAYS_PT = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
MONTHS_PT   = ["", "JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
                "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]


class ClockWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._setup_ui()

        timer = QTimer(self)
        timer.timeout.connect(self._update_time)
        timer.start(500)
        self._update_time()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Time label
        self._time_label = QLabel("00:00:00", self)
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Courier New", 52, QFont.Weight.Bold)
        self._time_label.setFont(font)
        self._time_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['accent']};
                letter-spacing: 4px;
            }}
        """)

        # Date label
        self._date_label = QLabel("", self)
        self._date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_font = QFont("Courier New", 13)
        self._date_label.setFont(date_font)
        self._date_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                letter-spacing: 6px;
            }}
        """)

        # Seconds bar
        self._seconds_bar = _SecondsBar(self)

        layout.addWidget(self._time_label)
        layout.addWidget(self._date_label)
        layout.addWidget(self._seconds_bar)

    def _update_time(self):
        now = datetime.now()
        self._time_label.setText(now.strftime("%H:%M:%S"))
        wd  = WEEKDAYS_PT[now.weekday()]
        mo  = MONTHS_PT[now.month]
        self._date_label.setText(f"{wd}  {now.day:02d} {mo} {now.year}")
        self._seconds_bar.set_seconds(now.second)


class _SecondsBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._seconds = 0
        self.setFixedHeight(4)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_seconds(self, s: int):
        self._seconds = s
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()

        # track
        p.setBrush(QBrush(QColor(COLORS["text_dim"])))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, w, 4, 2, 2)

        # fill
        fill = int(w * self._seconds / 59)
        if fill > 0:
            grad = QLinearGradient(0, 0, fill, 0)
            grad.setColorAt(0, QColor(COLORS["accent2"]))
            grad.setColorAt(1, QColor(COLORS["accent"]))
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(0, 0, fill, 4, 2, 2)
        p.end()
