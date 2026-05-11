"""
Tela de boot cinematográfico — animação de inicialização estilo JARVIS.
"""
import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore    import Qt, QTimer, pyqtSignal
from PyQt6.QtGui     import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient
from src.config.settings import COLORS
from src.services.greeting import get_boot_lines


class BootSequenceWidget(QWidget):
    boot_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._lines       = get_boot_lines()
        self._shown_lines : list[str] = []
        self._progress    = 0
        self._step        = 0
        self._total_steps = len(self._lines) + 10
        self._glitch_chars = "█▓▒░|/\\-+*#@&%$!?"
        self._setup_ui()
        QTimer.singleShot(600, self._start_boot)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Cabeçalho
        header = QLabel("J.A.R.V.I.S  —  JUST A RATHER VERY INTELLIGENT SYSTEM")
        header.setFont(QFont("Courier New", 11, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"color: {COLORS['accent']}; letter-spacing: 4px;")
        layout.addWidget(header)

        sub = QLabel("Personal Development Assistant  ·  v3.0")
        sub.setFont(QFont("Courier New", 8))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {COLORS['text_secondary']}; letter-spacing: 3px; margin-bottom: 30px;")
        layout.addWidget(sub)

        layout.addSpacing(30)

        # Log de boot
        self._log_widget = _BootLog(self)
        layout.addWidget(self._log_widget)

        layout.addStretch()

        # Barra de progresso
        self._progress_label = QLabel("INITIALIZING  0%")
        self._progress_label.setFont(QFont("Courier New", 8))
        self._progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._progress_label.setStyleSheet(f"color: {COLORS['text_secondary']}; letter-spacing: 2px;")
        layout.addWidget(self._progress_label)

        layout.addSpacing(8)

        self._progress_bar = _NeonBootBar(self)
        self._progress_bar.setFixedHeight(8)
        layout.addWidget(self._progress_bar)

        layout.addSpacing(20)

        # Anel central decorativo
        self._ring = _BootRing(self)
        self._ring.setFixedSize(200, 200)
        self._ring.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _start_boot(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(180)

    def _tick(self):
        self._step += 1
        pct = int(self._step / self._total_steps * 100)
        pct = min(pct, 100)
        self._progress = pct
        self._progress_bar.set_value(pct)
        self._progress_label.setText(f"LOADING SYSTEMS  {pct}%")

        # Add a log line every few ticks
        line_idx = int(self._step / self._total_steps * len(self._lines))
        line_idx = min(line_idx, len(self._lines) - 1)
        line     = self._lines[line_idx]
        if line not in self._shown_lines:
            self._shown_lines.append(line)
            self._log_widget.add_line(line)

        if pct >= 100:
            self._timer.stop()
            QTimer.singleShot(800, self.boot_finished.emit)

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(COLORS["bg_primary"]))
        p.end()


class _BootLog(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._lines: list[str] = []
        self.setFont(QFont("Courier New", 9))
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        self.setWordWrap(True)
        self.setFixedHeight(240)

    def add_line(self, line: str):
        self._lines.append(f"[OK]  {line}")
        if len(self._lines) > 14:
            self._lines = self._lines[-14:]
        html_lines = []
        for i, l in enumerate(self._lines):
            alpha = 60 + int(195 * (i / len(self._lines)))
            color = f"rgba(0,212,255,{alpha/255:.2f})"
            html_lines.append(f'<span style="color:{color}">{l}</span>')
        self.setText("<br>".join(html_lines))


class _NeonBootBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_value(self, v: int):
        self._value = v
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width(); h = self.height()

        # Track
        p.setBrush(QBrush(QColor(COLORS["text_dim"])))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, w, h, 3, 3)

        fw = int(w * self._value / 100)
        if fw > 0:
            grad = QLinearGradient(0, 0, fw, 0)
            grad.setColorAt(0.0, QColor(COLORS["accent2"]))
            grad.setColorAt(0.6, QColor(COLORS["accent"]))
            grad.setColorAt(1.0, QColor("#ffffff"))
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(0, 0, fw, h, 3, 3)

            # glow
            glow = QColor(COLORS["accent"])
            glow.setAlpha(50)
            p.setBrush(QBrush(glow))
            p.drawRoundedRect(0, -3, fw, h + 6, 3, 3)
        p.end()


class _BootRing(QLabel):
    """Placeholder — replaced by SpinnerRing in layout if needed."""
    pass
