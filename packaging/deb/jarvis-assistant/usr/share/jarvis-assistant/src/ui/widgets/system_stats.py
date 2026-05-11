"""
Painel de estatísticas do sistema em tempo real.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtGui     import QFont
from src.config.settings import COLORS
from src.ui.widgets.hud_elements import NeonProgressBar, GlowPanel


def _label(text: str, size: int = 9, color: str | None = None, bold: bool = False) -> QLabel:
    lbl = QLabel(text)
    font = QFont("Courier New", size)
    if bold:
        font.setBold(True)
    lbl.setFont(font)
    c = color or COLORS["text_secondary"]
    lbl.setStyleSheet(f"color: {c}; background: transparent;")
    return lbl


class StatRow(QWidget):
    """Uma linha de métrica: título + barra + valor."""
    def __init__(self, title: str, color: str | None = None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._color = color or COLORS["accent"]
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(3)

        header = QHBoxLayout()
        self._title_lbl = _label(title, 9, COLORS["text_secondary"])
        self._value_lbl = _label("—", 9, self._color, bold=True)
        header.addWidget(self._title_lbl)
        header.addStretch()
        header.addWidget(self._value_lbl)

        self._bar = NeonProgressBar(color=self._color, height=5)

        layout.addLayout(header)
        layout.addWidget(self._bar)

    def update_stat(self, value: float, label: str):
        self._bar.set_value(value)
        self._value_lbl.setText(label)
        # color threshold
        if value >= 90:
            c = COLORS["accent_danger"]
        elif value >= 70:
            c = COLORS["accent_warn"]
        else:
            c = self._color
        self._value_lbl.setStyleSheet(f"color: {c}; background: transparent;")


class SystemStatsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._setup_ui()
        self._start_updates()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        title = _label("◈  SISTEMA", 10, COLORS["accent"], bold=True)
        title.setStyleSheet(f"color: {COLORS['accent']}; letter-spacing: 3px; background: transparent;")
        layout.addWidget(title)

        self._cpu_row  = StatRow("CPU", COLORS["accent"])
        self._ram_row  = StatRow("RAM", COLORS["accent2"])
        self._disk_row = StatRow("DISCO", COLORS["accent3"])

        layout.addWidget(self._cpu_row)
        layout.addWidget(self._ram_row)
        layout.addWidget(self._disk_row)
        layout.addSpacing(4)

        # Info grid
        grid = QGridLayout()
        grid.setSpacing(4)
        self._info_labels: dict[str, QLabel] = {}

        rows = [
            ("HOST",      "hostname"),
            ("IP",        "ip"),
            ("UPTIME",    "uptime"),
            ("TEMP",      "temp"),
            ("PROCS",     "procs"),
            ("NET",       "internet"),
        ]

        for i, (k, key) in enumerate(rows):
            key_lbl = _label(f"{k}:", 8, COLORS["text_dim"])
            val_lbl = _label("—", 8, COLORS["text_primary"])
            self._info_labels[key] = val_lbl
            grid.addWidget(key_lbl, i, 0, Qt.AlignmentFlag.AlignLeft)
            grid.addWidget(val_lbl, i, 1, Qt.AlignmentFlag.AlignRight)

        layout.addLayout(grid)

    def _start_updates(self):
        # Lazy import to avoid blocking init
        from src.services import system_info as si
        self._si = si

        # Primeiro update imediato
        QTimer.singleShot(500, self._update)

        timer = QTimer(self)
        timer.timeout.connect(self._update)
        timer.start(3000)

    def _update(self):
        si = self._si
        try:
            cpu = si.get_cpu_percent()
            self._cpu_row.update_stat(cpu, f"{cpu:.0f}%")

            ram = si.get_ram_info()
            self._ram_row.update_stat(ram["percent"], f"{ram['used_gb']:.1f}/{ram['total_gb']:.1f} GB")

            disk = si.get_disk_info()
            self._disk_row.update_stat(disk["percent"], f"{disk['used_gb']:.0f}/{disk['total_gb']:.0f} GB")

            self._info_labels["hostname"].setText(si.get_hostname())
            self._info_labels["ip"].setText(si.get_ip_address())
            self._info_labels["uptime"].setText(si.get_uptime())

            temp = si.get_cpu_temperature()
            self._info_labels["temp"].setText(f"{temp:.0f}°C" if temp else "N/A")

            self._info_labels["procs"].setText(str(si.get_process_count()))

            online = si.get_internet_status()
            color  = COLORS["accent3"] if online else COLORS["accent_danger"]
            status = "ONLINE" if online else "OFFLINE"
            self._info_labels["internet"].setText(status)
            self._info_labels["internet"].setStyleSheet(
                f"color: {color}; background: transparent;"
            )
        except Exception as e:
            print(f"[Stats] {e}")
