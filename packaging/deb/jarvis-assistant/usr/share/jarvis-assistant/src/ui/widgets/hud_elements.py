"""
Widgets de decoração e efeitos visuais estilo HUD/JARVIS.
"""
import math
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore    import Qt, QTimer, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui     import (
    QPainter, QPen, QColor, QBrush, QConicalGradient,
    QRadialGradient, QLinearGradient, QFont, QPainterPath,
    QFontMetrics,
)
from src.config.settings import COLORS


# ─────────────────────────────────────────────
#  Anel giratório (spinner decorativo)
# ─────────────────────────────────────────────
class SpinnerRing(QWidget):
    def __init__(self, parent=None, size: int = 120, rings: int = 3):
        super().__init__(parent)
        self._size   = size
        self._rings  = rings
        self._angles = [0.0] * rings
        self._speeds = [0.8, -0.5, 0.3][:rings]
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        timer = QTimer(self)
        timer.timeout.connect(self._tick)
        timer.start(16)

    def _tick(self):
        for i in range(self._rings):
            self._angles[i] = (self._angles[i] + self._speeds[i]) % 360
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx = self._size / 2
        cy = self._size / 2

        colors = [
            QColor(COLORS["accent"]),
            QColor(COLORS["accent2"]),
            QColor(COLORS["accent3"]),
        ]

        for i in range(self._rings):
            r      = (cx - 4) - i * 14
            margin = cx - r
            rect   = QRectF(margin, margin, r * 2, r * 2)
            c      = colors[i % len(colors)]
            c.setAlpha(180 - i * 40)

            pen = QPen(c, 1.5, Qt.PenStyle.DashLine)
            pen.setDashPattern([4, 6])
            p.setPen(pen)
            p.drawEllipse(rect)

            # bright arc
            arc_pen = QPen(colors[i % len(colors)], 2.5)
            p.setPen(arc_pen)
            start = int(self._angles[i] * 16)
            p.drawArc(rect, start, 90 * 16)

        p.end()


# ─────────────────────────────────────────────
#  Barra de progresso neon
# ─────────────────────────────────────────────
class NeonProgressBar(QWidget):
    def __init__(self, parent=None, color: str | None = None, height: int = 6):
        super().__init__(parent)
        self._value  = 0.0   # 0–100
        self._color  = color or COLORS["accent"]
        self._height = height
        self.setFixedHeight(height + 6)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_value(self, v: float):
        self._value = max(0.0, min(100.0, v))
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self._height
        y = (self.height() - h) // 2

        # track
        track_color = QColor(COLORS["border"])
        p.setBrush(QBrush(track_color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, y, w, h, h // 2, h // 2)

        # fill
        fill_w = int(w * self._value / 100)
        if fill_w > 0:
            grad = QLinearGradient(0, 0, fill_w, 0)
            base = QColor(self._color)
            bright = QColor(base)
            bright.setAlpha(255)
            base.setAlpha(200)
            grad.setColorAt(0.0, base)
            grad.setColorAt(1.0, bright)
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(0, y, fill_w, h, h // 2, h // 2)

            # glow
            glow = QColor(self._color)
            glow.setAlpha(60)
            glow_pen = QPen(glow, h + 4)
            glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(glow_pen)
            p.drawLine(0, y + h // 2, fill_w, y + h // 2)

        p.end()


# ─────────────────────────────────────────────
#  Painel com borda neon animada
# ─────────────────────────────────────────────
class GlowPanel(QWidget):
    def __init__(self, parent=None, color: str | None = None):
        super().__init__(parent)
        self._color  = color or COLORS["accent"]
        self._pulse  = 0.0
        self._dir    = 1
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        timer = QTimer(self)
        timer.timeout.connect(self._tick)
        timer.start(50)

    def _tick(self):
        self._pulse += 0.04 * self._dir
        if self._pulse >= 1.0:
            self._pulse = 1.0
            self._dir   = -1
        elif self._pulse <= 0.0:
            self._pulse = 0.0
            self._dir   = 1
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(2, 2, -2, -2)

        # background
        bg = QColor(COLORS["bg_panel"])
        bg.setAlpha(220)
        p.setBrush(QBrush(bg))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(rect, 6, 6)

        # border glow
        alpha = int(60 + 100 * self._pulse)
        border_color = QColor(self._color)
        border_color.setAlpha(alpha)
        pen = QPen(border_color, 1.5)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(rect, 6, 6)

        p.end()


# ─────────────────────────────────────────────
#  Label com efeito scanline
# ─────────────────────────────────────────────
class ScanlineOverlay(QWidget):
    """Overlay de scanlines — colocar sobre toda a janela."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

    def paintEvent(self, _):
        p = QPainter(self)
        line_color = QColor(0, 0, 0, 18)
        p.setPen(QPen(line_color, 1))
        for y in range(0, self.height(), 3):
            p.drawLine(0, y, self.width(), y)
        p.end()


# ─────────────────────────────────────────────
#  Decoração de canto (corner bracket)
# ─────────────────────────────────────────────
class CornerBracket(QWidget):
    def __init__(self, parent=None, size: int = 20, corner: str = "tl", color: str | None = None):
        super().__init__(parent)
        self._size   = size
        self._corner = corner   # tl tr bl br
        self._color  = color or COLORS["accent"]
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(self._color), 2)
        p.setPen(pen)
        s = self._size - 2
        if self._corner == "tl":
            p.drawLine(1, s, 1, 1); p.drawLine(1, 1, s, 1)
        elif self._corner == "tr":
            p.drawLine(s, s, s, 1); p.drawLine(s, 1, 1, 1)
        elif self._corner == "bl":
            p.drawLine(1, 1, 1, s); p.drawLine(1, s, s, s)
        elif self._corner == "br":
            p.drawLine(s, 1, s, s); p.drawLine(s, s, 1, s)
        p.end()
