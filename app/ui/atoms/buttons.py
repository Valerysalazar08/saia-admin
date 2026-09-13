"""
ÁTOMOS Qt — Botones reutilizables SAIA.
"""
from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtGui import QPainter, QColor, QFont, QIcon, QCursor
from PyQt6.QtCore import Qt, QSize, QPoint
from app.ui.theme import (
    PRIMARY, PRIMARY_HOVER, SECONDARY, SECONDARY_HOVER,
    ERROR, BG_INPUT, BG_HOVER, TEXT_SECONDARY, TEXT_PRIMARY,
    WARNING, SUCCESS, SUCCESS_TEXT,
    BTN_HEIGHT, BTN_HEIGHT_SM, BTN_RADIUS, BTN_RADIUS_SM,
    font, paint_gradient_btn,
    svg_icon,
)


class GradientButton(QPushButton):
    """Botón principal con gradiente celeste→verde. Usa paintEvent custom."""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(BTN_HEIGHT_SM + 10)  # 42px  (entre SM y normal)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(font(13, bold=True))
        self.setStyleSheet("color: white; border: none; border-radius: 21px;")
        self._hover = False

    def enterEvent(self, e):
        self._hover = True
        self.update()

    def leaveEvent(self, e):
        self._hover = False
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        paint_gradient_btn(p, self.rect(), self._hover, radius=BTN_RADIUS)
        p.setPen(QColor("white"))
        p.setFont(self.font())
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

    def sizeHint(self):
        sh = super().sizeHint()
        sh.setHeight(BTN_HEIGHT)
        return sh


class PrimaryButton(QPushButton):
    """Botón sólido color primario."""

    def __init__(self, text: str = "", parent=None, width: int = 140, height: int = None):
        super().__init__(text, parent)
        h = height or BTN_HEIGHT
        self.setFixedHeight(h)
        if width:
            self.setMinimumWidth(width)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFont(font(13, bold=True))
        self.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                border: none;
                border-radius: {BTN_RADIUS}px;
                padding: 0 16px;
                outline: none;
            }}
            QPushButton:hover {{ background: {PRIMARY_HOVER}; }}
            QPushButton:pressed {{ background: {PRIMARY_HOVER}; }}
            QPushButton:focus {{ outline: none; }}
            QPushButton:disabled {{ background: #B0D8E8; color: #FFFFFF; }}
        """)


class SecondaryButton(QPushButton):
    """Acción secundaria ligera, alineada con el estilo de Auditoría."""

    def __init__(self, text: str = "", parent=None, width: int = 140, height: int = None):
        super().__init__(text, parent)
        h = height or BTN_HEIGHT
        self.setFixedHeight(h)
        if width:
            self.setMinimumWidth(width)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFont(font(13, bold=True))
        self.setStyleSheet(f"""
            QPushButton {{
                background: #F0FAFD;
                color: {PRIMARY};
                border: 1px solid #D5EDF5;
                border-radius: 7px;
                padding: 0 16px;
                outline: none;
            }}
            QPushButton:hover {{ background: {BG_HOVER}; border-color: {PRIMARY}; }}
            QPushButton:pressed {{ background: #E7F7FB; border-color: {PRIMARY}; }}
            QPushButton:focus {{ outline: none; border-color: {PRIMARY}; }}
        """)


class DangerButton(QPushButton):
    """Botón destructivo rojo."""

    def __init__(self, text: str = "", parent=None, width: int = 140, height: int = None):
        super().__init__(text, parent)
        h = height or BTN_HEIGHT
        self.setFixedHeight(h)
        if width:
            self.setMinimumWidth(width)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFont(font(13, bold=True))
        self.setStyleSheet(f"""
            QPushButton {{
                background: {ERROR};
                color: white;
                border: none;
                border-radius: {BTN_RADIUS}px;
                padding: 0 16px;
            }}
            QPushButton:hover {{ background: #DC2626; }}
        """)


class SuccessButton(QPushButton):
    """Botón verde menta."""

    def __init__(self, text: str = "", parent=None, width: int = 140, height: int = None):
        super().__init__(text, parent)
        h = height or BTN_HEIGHT
        self.setFixedHeight(h)
        if width:
            self.setMinimumWidth(width)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFont(font(13, bold=True))
        self.setStyleSheet(f"""
            QPushButton {{
                background: {SUCCESS};
                color: {TEXT_PRIMARY};
                border: none;
                border-radius: {BTN_RADIUS}px;
                padding: 0 16px;
            }}
            QPushButton:hover {{ background: {SECONDARY_HOVER}; }}
        """)


class SmallButton(QPushButton):
    """Botón pequeño para acciones en tablas."""

    _PRESETS = {
        "primary": (PRIMARY,   PRIMARY_HOVER, "white"),
        "danger":  (ERROR,     "#DC2626",     "white"),
        "success": (SUCCESS,   SECONDARY_HOVER, TEXT_PRIMARY),
        "warning": (WARNING,   "#D97706",     "white"),
        "ghost":   (BG_INPUT,  BG_HOVER,      TEXT_SECONDARY),
    }

    def __init__(self, text: str = "", parent=None,
                 color: str = "primary", width: int = 88):
        super().__init__(text, parent)
        self.setFixedHeight(BTN_HEIGHT_SM)
        self.setMinimumWidth(width)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFont(font(11, bold=True))
        bg, hv, tc = self._PRESETS.get(color, self._PRESETS["primary"])
        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {tc};
                border: none;
                border-radius: {BTN_RADIUS_SM}px;
                padding: 0 10px;
            }}
            QPushButton:hover {{ background: {hv}; }}
        """)


class TableActionButton(QPushButton):
    """Acción compacta para tablas con icono y ayuda visual al pasar."""

    _PRESETS = {
        "primary": ("#E8F8FC", PRIMARY, "#C6ECF5", PRIMARY_HOVER),
        "danger":  ("#FEF2F2", ERROR, "#FECACA", "#DC2626"),
        "success": ("#E8FBF5", SUCCESS_TEXT, "#BCEEDC", "#0D7A54"),
        "warning": ("#FFF7E6", "#C76A00", "#F9D9A6", "#A95500"),
        "ghost":   (BG_INPUT, TEXT_SECONDARY, "#D8E0E8", TEXT_PRIMARY),
    }

    def __init__(self, icon_name: str, label: str, parent=None,
                 color: str = "primary"):
        super().__init__(parent)
        bg, fg, border, hover_fg = self._PRESETS.get(color, self._PRESETS["primary"])
        self.setFixedSize(32, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAccessibleName(label)
        self.setAccessibleDescription(label)
        # No usamos QToolTip: su aspecto puede ser reemplazado por el tema de
        # Windows. Esta etiqueta propia mantiene siempre la paleta SAIA clara.
        self._hint = QLabel(label, None, Qt.WindowType.ToolTip)
        self._hint.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self._hint.setFont(font(10))
        self._hint.setContentsMargins(10, 5, 10, 5)
        self._hint.setStyleSheet(f"""
            QLabel {{
                background: #FFFFFF;
                color: {TEXT_PRIMARY};
                border: 1px solid {PRIMARY};
                border-radius: 6px;
            }}
        """)
        self.setIcon(QIcon(svg_icon(icon_name, 16, fg)))
        self.setIconSize(QSize(16, 16))
        self.setStyleSheet(f"""
            QPushButton {{
                background:{bg}; color:{fg}; border:1px solid {border};
                border-radius:9px; padding:0;
            }}
            QPushButton:hover {{ background:white; border-color:{hover_fg}; }}
            QPushButton:pressed {{ background:{bg}; }}
        """)

    def enterEvent(self, event):
        self._hint.adjustSize()
        self._hint.move(QCursor.pos() + QPoint(10, 14))
        self._hint.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hint.hide()
        super().leaveEvent(event)
