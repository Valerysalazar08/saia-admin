"""
ÁTOMOS Qt — Labels, badges, stat cards, dividers.
"""
from PyQt6.QtWidgets import (
    QLabel, QFrame, QWidget, QVBoxLayout, QHBoxLayout,
    QSizePolicy,
)
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen
from PyQt6.QtCore import Qt, QRectF

from app.ui.theme import (
    PRIMARY, SECONDARY, INFO, INFO_BG,
    BG_CARD, BG_INPUT, BG_PALE, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ERROR, ERROR_BG, WARNING, WARNING_BG,
    SUCCESS, SUCCESS_BG,
    CARD_RADIUS, BADGE_RADIUS,
    font, svg_icon,
)


class Heading(QLabel):
    """Título con nivel 1–3."""

    _SIZES = {1: (28, True), 2: (22, True), 3: (18, True)}

    def __init__(self, text: str = "", level: int = 2, parent=None):
        super().__init__(text, parent)
        size, bold = self._SIZES.get(level, (22, True))
        self.setFont(font(size, bold=bold))
        self.setStyleSheet(f"color:{TEXT_PRIMARY}; background:transparent;")


class BodyLabel(QLabel):
    """Texto de cuerpo con opción muted."""

    def __init__(self, text: str = "", muted: bool = False, parent=None):
        super().__init__(text, parent)
        self.setFont(font(13))
        color = TEXT_MUTED if muted else TEXT_SECONDARY
        self.setStyleSheet(f"color:{color}; background:transparent;")


class Badge(QFrame):
    """Pastilla de estado con colores predefinidos."""

    PRESETS = {
        "activo":    ("#ECFDF5", "#15803D", "Activo"),
        "inactivo":  ("#FEF2F2", "#DC2626", "Inactivo"),
        "pendiente": ("#FFFBEB", "#B45309", "Pendiente"),
        "aprendiz":  (INFO_BG,   INFO,      "Aprendiz"),
        "guarda":    ("#FFFBEB", "#A16207", "Guarda"),
        "admin":     ("#F3E8FF", "#7E22CE", "Admin"),
        "ingreso":   ("#ECFDF5", "#15803D", "Ingreso"),
        "salida":    ("#FFFBEB", "#B45309", "Salida"),
        "info":      (INFO_BG,   INFO,      "Info"),
    }

    def __init__(self, text: str = None, preset: str = None,
                 bg: str = None, color: str = None, parent=None):
        super().__init__(parent)

        if preset and preset.lower() in self.PRESETS:
            bg, color, default_text = self.PRESETS[preset.lower()]
            text = text or default_text

        bg    = bg    or BG_INPUT
        color = color or TEXT_PRIMARY
        text  = text  or ""

        self.setFixedHeight(24)
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border-radius: {BADGE_RADIUS}px;
                border: none;
            }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(7, 0, 7, 0)
        lay.setSpacing(3)

        dot = QLabel("●")
        dot.setFont(font(8, bold=True))
        dot.setStyleSheet(f"color:{color}; background:transparent;")
        lay.addWidget(dot)

        lbl = QLabel(text)
        lbl.setFont(font(10, bold=True))
        lbl.setStyleSheet(f"color:{color}; background:transparent;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(lbl)
        # Al renderizarse en una columna ancha, el espacio sobrante queda al
        # final y no entre el indicador y el texto de la etiqueta.
        lay.addStretch()


class StatCard(QFrame):
    """Tarjeta de estadística grande con número y título."""

    def __init__(self, title: str = "", value=0,
                 icon: str = "", color: str = None, parent=None):
        super().__init__(parent)
        accent = color or PRIMARY

        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border-radius: {CARD_RADIUS}px;
                border: 1px solid {BORDER};
            }}
        """)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(120)

        root_lay = QVBoxLayout(self)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        # Barra superior de acento (3px)
        bar = QFrame()
        bar.setFixedHeight(4)
        bar.setStyleSheet(f"background:{accent}; border-radius:0; border:none;")
        root_lay.addWidget(bar)

        body = QWidget()
        body.setStyleSheet("background:transparent;")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(16, 12, 16, 12)
        body_lay.setSpacing(4)
        root_lay.addWidget(body)

        # Icono
        if icon:
            icon_box = QFrame()
            icon_box.setFixedSize(44, 44)
            icon_box.setStyleSheet(f"""
                QFrame {{
                    background: {BG_PALE};
                    border-radius: 10px;
                    border: none;
                }}
            """)
            ib_lay = QHBoxLayout(icon_box)
            ib_lay.setContentsMargins(0, 0, 0, 0)
            ic_lbl = QLabel(icon)
            ic_lbl.setFont(font(18))
            ic_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ic_lbl.setStyleSheet(f"color:{accent}; background:transparent;")
            ib_lay.addWidget(ic_lbl)
            body_lay.addWidget(icon_box)

        # Valor
        self._value_lbl = QLabel(str(value))
        self._value_lbl.setFont(font(22, bold=True))
        self._value_lbl.setStyleSheet(
            f"color:{TEXT_PRIMARY}; background:transparent;")
        body_lay.addWidget(self._value_lbl)

        # Título
        title_lbl = QLabel(title)
        title_lbl.setFont(font(11))
        title_lbl.setStyleSheet(
            f"color:{TEXT_MUTED}; background:transparent;")
        body_lay.addWidget(title_lbl)

    def update_value(self, new_value):
        self._value_lbl.setText(str(new_value))


class Divider(QFrame):
    """Separador horizontal de 1px."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background:{BORDER}; border:none;")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
