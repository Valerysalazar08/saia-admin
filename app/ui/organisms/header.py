"""
ORGANISMO Qt — Header superior SAIA.
"""
from datetime import datetime
from PyQt6.QtWidgets import QFrame, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer

from app.ui.theme import (
    BG_CARD, BORDER, TEXT_PRIMARY, TEXT_MUTED,
    HEADER_HEIGHT, font, svg_icon,
)


class Header(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(HEADER_HEIGHT)
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border-bottom: 1px solid {BORDER};
            }}
        """)
        self._build()
        self._start_clock()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 0, 20, 0)
        lay.setSpacing(12)

        lay.addStretch(1)

        # Ícono calendario
        cal_ic = QLabel()
        cal_ic.setPixmap(svg_icon("calendar", 16, TEXT_MUTED))
        cal_ic.setFixedSize(18, 18)
        cal_ic.setScaledContents(True)
        cal_ic.setStyleSheet("background:transparent;")
        lay.addWidget(cal_ic)

        # Separador
        sep = QFrame()
        sep.setFixedSize(1, 22)
        sep.setStyleSheet(f"background:{BORDER}; border:none;")
        lay.addWidget(sep)

        # Reloj
        self._clock = QLabel()
        self._clock.setFont(font(11))
        self._clock.setStyleSheet(
            f"color:{TEXT_MUTED}; background:transparent;")
        lay.addWidget(self._clock)

    def set_title(self, title: str):
        """Se conserva la API para las navegaciones, sin duplicar el título visible."""
        return

    def _start_clock(self):
        self._update_clock()
        t = QTimer(self)
        t.timeout.connect(self._update_clock)
        t.start(1000)

    def _update_clock(self):
        self._clock.setText(datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))
