"""
Assistente de configuração — aparece na primeira execução.
Pergunta nome, gênero da voz e apps preferidos.
"""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QButtonGroup, QRadioButton, QWidget, QComboBox,
    QCheckBox, QFrame,
)
from PyQt6.QtCore  import Qt, QTimer
from PyQt6.QtGui   import QFont, QColor, QPainter, QPen, QLinearGradient, QBrush

from src.config.settings import COLORS, save_config


class SetupWizard(QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self._config  = config
        self._current = 0          # página atual
        self._pages   : list[QWidget] = []
        self._setup_window()
        self._build_pages()
        self._show_page(0)

    # ── janela ────────────────────────────────────────────────────────── #
    def _setup_window(self):
        self.setWindowTitle("J.A.R.V.I.S — Configuração Inicial")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(560, 480)

        # Centralizar na tela
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2,
        )

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Fundo
        p.setBrush(QBrush(QColor(COLORS["bg_secondary"])))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(self.rect(), 12, 12)
        # Borda cyan
        pen = QPen(QColor(COLORS["accent"]))
        pen.setWidth(1)
        p.setPen(pen)
        p.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 12, 12)
        p.end()

    # ── páginas ───────────────────────────────────────────────────────── #
    def _build_pages(self):
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        # Header fixo
        self._root.addWidget(self._make_header())

        # Container de páginas
        self._page_container = QWidget()
        self._page_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._page_layout = QVBoxLayout(self._page_container)
        self._page_layout.setContentsMargins(40, 20, 40, 0)
        self._root.addWidget(self._page_container, stretch=1)

        # Botões de navegação
        self._root.addWidget(self._make_nav_bar())

        # Definir páginas
        self._pages = [
            self._page_welcome(),
            self._page_identity(),
            self._page_voice(),
            self._page_apps(),
            self._page_done(),
        ]

    def _show_page(self, idx: int):
        # Limpar container
        while self._page_layout.count():
            item = self._page_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        self._current = idx
        self._page_layout.addWidget(self._pages[idx])
        self._pages[idx].show()

        # Atualizar botões
        self._btn_back.setVisible(idx > 0)
        is_last = idx == len(self._pages) - 1
        self._btn_next.setText("CONFIRMAR" if is_last else "PRÓXIMO  ›")
        # Indicadores
        for i, dot in enumerate(self._dots):
            dot.setProperty("active", i == idx)
            dot.style().unpolish(dot)
            dot.style().polish(dot)

    # ── widgets de navegação ─────────────────────────────────────────── #
    def _make_header(self) -> QWidget:
        w = QWidget()
        w.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        w.setFixedHeight(52)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(24, 0, 16, 0)

        title = QLabel("◈  J.A.R.V.I.S  —  CONFIGURAÇÃO INICIAL")
        title.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']}; letter-spacing: 3px; background: transparent;")
        lay.addWidget(title)
        lay.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(28, 28)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_dim']};
                border: 1px solid {COLORS['text_dim']};
                border-radius: 14px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                color: {COLORS['accent_danger']};
                border-color: {COLORS['accent_danger']};
            }}
        """)
        btn_close.clicked.connect(self.reject)
        lay.addWidget(btn_close)
        return w

    def _make_nav_bar(self) -> QWidget:
        w = QWidget()
        w.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        w.setFixedHeight(64)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(40, 0, 40, 12)

        self._btn_back = QPushButton("‹  VOLTAR")
        self._btn_back.setFixedHeight(36)
        self._btn_back.setVisible(False)
        self._btn_back.clicked.connect(lambda: self._show_page(self._current - 1))
        self._btn_back.setStyleSheet(self._btn_style(primary=False))
        lay.addWidget(self._btn_back)

        # Dots indicadores
        dot_row = QHBoxLayout()
        dot_row.setSpacing(6)
        self._dots = []
        for i in range(len(self._pages) if hasattr(self, '_pages') else 5):
            dot = QLabel("●")
            dot.setFont(QFont("Courier New", 8))
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dot.setFixedWidth(18)
            dot.setStyleSheet(f"color: {COLORS['text_dim']}; background: transparent;")
            dot.setProperty("active", False)
            self._dots.append(dot)
            dot_row.addWidget(dot)
        lay.addStretch()
        lay.addLayout(dot_row)
        lay.addStretch()

        self._btn_next = QPushButton("PRÓXIMO  ›")
        self._btn_next.setFixedHeight(36)
        self._btn_next.clicked.connect(self._on_next)
        self._btn_next.setStyleSheet(self._btn_style(primary=True))
        lay.addWidget(self._btn_next)

        return w

    def _btn_style(self, primary: bool) -> str:
        if primary:
            return f"""
                QPushButton {{
                    background: transparent;
                    color: {COLORS['accent']};
                    border: 1px solid {COLORS['accent']};
                    border-radius: 4px;
                    padding: 0 20px;
                    font-family: 'Courier New';
                    font-size: 10px;
                    letter-spacing: 2px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: rgba(0,212,255,0.12);
                }}
            """
        return f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['text_dim']};
                border-radius: 4px;
                padding: 0 20px;
                font-family: 'Courier New';
                font-size: 10px;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                color: {COLORS['text_primary']};
                border-color: {COLORS['text_secondary']};
            }}
        """

    # ── navegação ────────────────────────────────────────────────────── #
    def _on_next(self):
        self._collect_current_page()
        if self._current < len(self._pages) - 1:
            self._show_page(self._current + 1)
        else:
            save_config(self._config)
            self.accept()

    def _collect_current_page(self):
        idx = self._current
        if idx == 1:  # identidade
            name = self._input_name.text().strip()
            if name:
                self._config["user_name"] = name
        elif idx == 2:  # voz
            self._config["voice_gender"]       = "male" if self._radio_male.isChecked() else "female"
            self._config["voice_enabled"]      = self._check_voice.isChecked()
            self._config["voice_recognition"]  = self._check_voicerec.isChecked()
        elif idx == 3:  # apps
            terminal = self._combo_terminal.currentText()
            browser  = self._combo_browser.currentText()
            editor   = self._combo_editor.currentText()
            if terminal != "— padrão —":
                self._config["terminal"] = terminal
            if browser != "— padrão —":
                self._config["browser"] = browser
            if editor != "— padrão —":
                self._config["editor"] = editor

    # ── conteúdo das páginas ─────────────────────────────────────────── #
    def _page_welcome(self) -> QWidget:
        w = _Page()
        w.add_title("BEM-VINDO")
        w.add_spacer(12)
        w.add_text(
            "J.A.R.V.I.S é seu assistente pessoal sci-fi para Linux.\n\n"
            "Em menos de 1 minuto vamos configurar tudo para você.\n\n"
            "Clique em PRÓXIMO para começar."
        )
        w.add_spacer(20)
        w.add_badge("◈  JUST A RATHER VERY INTELLIGENT SYSTEM")
        return w

    def _page_identity(self) -> QWidget:
        w = _Page()
        w.add_title("IDENTIFICAÇÃO")
        w.add_spacer(8)
        w.add_text("Como devo chamá-lo? O JARVIS usará este nome nas saudações.")
        w.add_spacer(20)

        lbl = QLabel("SEU NOME")
        lbl.setFont(QFont("Courier New", 8))
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; letter-spacing: 2px; background: transparent;")
        w.layout().addWidget(lbl)

        w.add_spacer(6)

        self._input_name = QLineEdit()
        self._input_name.setPlaceholderText("Ex: João, Maria, Dev...")
        self._input_name.setText(self._config.get("user_name", ""))
        self._input_name.setFixedHeight(40)
        self._input_name.setStyleSheet(f"""
            QLineEdit {{
                background: {COLORS['bg_panel']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 0 12px;
                font-family: 'Courier New';
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
            }}
        """)
        w.layout().addWidget(self._input_name)
        w.add_spacer(12)
        w.add_text("Deixe em branco para usar o padrão.")
        return w

    def _page_voice(self) -> QWidget:
        w = _Page()
        w.add_title("VOZ DO ASSISTENTE")
        w.add_spacer(8)
        w.add_text("Escolha o gênero da voz. Usamos vozes neurais Microsoft (Antonio / Francisca).")
        w.add_spacer(20)

        radio_row = QHBoxLayout()
        radio_row.setSpacing(16)

        self._radio_male   = _RadioCard("MASCULINO", "Antonio Neural", self._config.get("voice_gender","male") == "male")
        self._radio_female = _RadioCard("FEMININO",  "Francisca Neural", self._config.get("voice_gender","male") == "female")

        self._radio_male.toggled.connect(lambda on: self._radio_female.setChecked(not on) if on else None)
        self._radio_female.toggled.connect(lambda on: self._radio_male.setChecked(not on) if on else None)

        radio_row.addWidget(self._radio_male)
        radio_row.addWidget(self._radio_female)
        w.layout().addLayout(radio_row)

        w.add_spacer(20)

        checkbox_style = f"""
            QCheckBox {{ color: {COLORS['text_primary']}; background: transparent; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {COLORS['border']}; border-radius: 3px; }}
            QCheckBox::indicator:checked {{ background: {COLORS['accent']}; border-color: {COLORS['accent']}; }}
        """

        self._check_voice = QCheckBox("  Narração por voz (JARVIS fala)")
        self._check_voice.setChecked(self._config.get("voice_enabled", True))
        self._check_voice.setFont(QFont("Courier New", 9))
        self._check_voice.setStyleSheet(checkbox_style)
        w.layout().addWidget(self._check_voice)

        w.add_spacer(10)

        self._check_voicerec = QCheckBox("  Reconhecimento de voz — diga \"Jarvis\" para ativar")
        self._check_voicerec.setChecked(self._config.get("voice_recognition", False))
        self._check_voicerec.setFont(QFont("Courier New", 9))
        self._check_voicerec.setStyleSheet(checkbox_style)
        w.layout().addWidget(self._check_voicerec)

        w.add_spacer(8)
        w.add_text("Requer microfone e pacote python3-pyaudio instalado.")
        return w

    def _page_apps(self) -> QWidget:
        w = _Page()
        w.add_title("APLICATIVOS PADRÃO")
        w.add_spacer(8)
        w.add_text("Defina quais apps o JARVIS abrirá nas ações rápidas.")
        w.add_spacer(16)

        def _combo(label_text, options, current):
            row = QHBoxLayout()
            lbl = QLabel(f"{label_text}:")
            lbl.setFixedWidth(100)
            lbl.setFont(QFont("Courier New", 9))
            lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent; letter-spacing: 1px;")
            combo = QComboBox()
            combo.addItems(options)
            idx = combo.findText(current)
            combo.setCurrentIndex(idx if idx >= 0 else 0)
            combo.setFixedHeight(34)
            combo.setStyleSheet(f"""
                QComboBox {{
                    background: {COLORS['bg_panel']};
                    color: {COLORS['text_primary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 4px;
                    padding: 0 10px;
                    font-family: 'Courier New';
                    font-size: 11px;
                }}
                QComboBox:focus {{ border-color: {COLORS['accent']}; }}
                QComboBox QAbstractItemView {{
                    background: {COLORS['bg_panel']};
                    color: {COLORS['text_primary']};
                    selection-background-color: rgba(0,212,255,0.2);
                }}
            """)
            row.addWidget(lbl)
            row.addWidget(combo, stretch=1)
            return row, combo

        row_t, self._combo_terminal = _combo("TERMINAL",
            ["gnome-terminal", "xterm", "konsole", "xfce4-terminal", "tilix", "alacritty", "— padrão —"],
            self._config.get("terminal", "gnome-terminal"))

        row_b, self._combo_browser = _combo("NAVEGADOR",
            ["firefox", "google-chrome", "chromium-browser", "brave-browser", "— padrão —"],
            self._config.get("browser", "firefox"))

        row_e, self._combo_editor = _combo("EDITOR",
            ["code", "gedit", "kate", "subl", "nvim", "vim", "— padrão —"],
            self._config.get("editor", "code"))

        w.layout().addLayout(row_t)
        w.add_spacer(10)
        w.layout().addLayout(row_b)
        w.add_spacer(10)
        w.layout().addLayout(row_e)
        return w

    def _page_done(self) -> QWidget:
        w = _Page()
        w.add_spacer(10)
        w.add_title("TUDO PRONTO")
        w.add_spacer(16)
        w.add_text(
            "Configuração concluída.\n\n"
            "Clique em CONFIRMAR para iniciar o J.A.R.V.I.S."
        )
        w.add_spacer(20)
        w.add_badge(f"◈  BEM-VINDO, {self._config.get('user_name','USUÁRIO').upper()}")
        w.add_spacer(12)
        w.add_text("Você pode alterar qualquer configuração editando:\n~/.config/jarvis-assistant/jarvis.json")
        return w


# ── widgets auxiliares ──────────────────────────────────────────────── #
class _Page(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)
        self._lay.setAlignment(Qt.AlignmentFlag.AlignTop)

    def layout(self):
        return self._lay

    def add_title(self, text: str):
        lbl = QLabel(text)
        lbl.setFont(QFont("Courier New", 15, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['accent']}; letter-spacing: 4px; background: transparent;")
        self._lay.addWidget(lbl)

    def add_text(self, text: str):
        lbl = QLabel(text)
        lbl.setFont(QFont("Courier New", 9))
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent; line-height: 160%;")
        self._lay.addWidget(lbl)

    def add_spacer(self, h: int):
        sp = QWidget()
        sp.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        sp.setFixedHeight(h)
        self._lay.addWidget(sp)

    def add_badge(self, text: str):
        lbl = QLabel(text)
        lbl.setFont(QFont("Courier New", 8))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setFixedHeight(34)
        lbl.setStyleSheet(f"""
            color: {COLORS['accent3']};
            background: rgba(0,255,136,0.06);
            border: 1px solid rgba(0,255,136,0.3);
            border-radius: 4px;
            letter-spacing: 3px;
        """)
        self._lay.addWidget(lbl)


class _RadioCard(QPushButton):
    def __init__(self, title: str, subtitle: str, checked: bool = False):
        super().__init__()
        self._checked  = checked
        self._title    = title
        self._subtitle = subtitle
        self.setCheckable(True)
        self.setChecked(checked)
        self.setFixedHeight(72)
        self.toggled.connect(self._on_toggle)
        self._refresh_style()

    def _on_toggle(self, on: bool):
        self._checked = on
        self._refresh_style()
        label = self.findChild(QLabel)

    def _refresh_style(self):
        border = COLORS["accent"] if self._checked else COLORS["border"]
        bg     = "rgba(0,212,255,0.08)" if self._checked else COLORS["bg_panel"]
        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 6px;
                text-align: left;
                padding: 0 16px;
                font-family: 'Courier New';
            }}
        """)
        self.setText(f"  {self._title}\n  {self._subtitle}")
        self.setFont(QFont("Courier New", 9))
