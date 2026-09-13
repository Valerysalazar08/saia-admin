"""
Diálogos base y de confirmación de la aplicación.
"""
from PyQt6.QtWidgets import (
    QDialog, QWidget, QFrame, QLabel, QPushButton,
    QScrollArea, QHBoxLayout, QVBoxLayout, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont, QMouseEvent

from app.ui.theme import (
    BG_APP, BG_CARD, BG_HOVER, BG_PALE, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ERROR, ERROR_BG, SUCCESS, SUCCESS_BG, SUCCESS_TEXT,
    PRIMARY, PRIMARY_HOVER,
    BTN_HEIGHT, BTN_HEIGHT_SM, BTN_RADIUS, BTN_RADIUS_SM,
    font, svg_icon,
)


# ─────────────────────────────────────────────────────────────────────────────
# Botones inline (para no crear dependencia circular con atoms)
# ─────────────────────────────────────────────────────────────────────────────

def _mk_btn(text: str, bg: str, hover: str, tc: str,
            height: int = BTN_HEIGHT, radius: int = BTN_RADIUS,
            min_w: int = 110) -> QPushButton:
    b = QPushButton(text)
    b.setFixedHeight(height)
    b.setMinimumWidth(min_w)
    b.setFont(font(13, bold=True))
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{
            background: {bg};
            color: {tc};
            border: none;
            border-radius: {radius}px;
            padding: 0 16px;
        }}
        QPushButton:hover {{ background: {hover}; }}
    """)
    return b


def _primary_btn(text: str, min_w: int = 130) -> QPushButton:
    return _mk_btn(text, PRIMARY, PRIMARY_HOVER, "white", min_w=min_w)


def _secondary_btn(text: str, min_w: int = 110) -> QPushButton:
    b = QPushButton(text)
    b.setFixedHeight(BTN_HEIGHT)
    b.setMinimumWidth(min_w)
    b.setFont(font(13, bold=True))
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{
            background: transparent;
            color: {PRIMARY};
            border: 1.5px solid {PRIMARY};
            border-radius: {BTN_RADIUS}px;
            padding: 0 16px;
        }}
        QPushButton:hover {{ background: {BG_HOVER}; }}
    """)
    return b


def _danger_btn(text: str, min_w: int = 130) -> QPushButton:
    return _mk_btn(text, ERROR, "#DC2626", "white", min_w=min_w)


class _ModalHeader(QFrame):
    """Cabecera arrastrable para los diálogos sin marco nativo."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_origin: QPoint | None = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = event.globalPosition().toPoint()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_origin and event.buttons() & Qt.MouseButton.LeftButton:
            current = event.globalPosition().toPoint()
            self.window().move(self.window().pos() + current - self._drag_origin)
            self._drag_origin = current
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_origin = None
        super().mouseReleaseEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
# BaseModal
# ─────────────────────────────────────────────────────────────────────────────

class BaseModal(QDialog):
    """
    Ventana modal base para formularios CRUD.
    Expone:
        - self.content  → widget de contenido (scrolleable o no)
        - self.add_footer_buttons(...)
        - self.show_error(msg)
        - self.show_success(msg)
    """

    def __init__(self, parent, title: str,
                 width: int = 480, height: int = 520,
                 scrollable: bool = True):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle(title)
        # Evita duplicar el título con la barra de Windows; la cabecera de la
        # aplicación conserva el cierre y permite arrastrar el diálogo.
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(width, height)
        self.setStyleSheet("QDialog { background: transparent; }")

        # Centrar sobre el padre
        if parent:
            px = parent.window().x() + (parent.window().width()  - width)  // 2
            py = parent.window().y() + (parent.window().height() - height) // 2
            self.move(max(0, px), max(0, py))

        self._toast_timer: QTimer | None = None
        self._toast_widget: QWidget | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(0)

        surface = QFrame()
        surface.setObjectName("modalSurface")
        surface.setStyleSheet(f"""
            QFrame#modalSurface {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
        """)
        root.addWidget(surface)

        surface_layout = QVBoxLayout(surface)
        surface_layout.setContentsMargins(0, 0, 0, 0)
        surface_layout.setSpacing(0)

        # ── Header ───────────────────────────────────────────────────────────
        header = _ModalHeader()
        header.setFixedHeight(52)
        header.setObjectName("modalHeader")
        header.setStyleSheet(f"""
            QFrame#modalHeader {{
                background: {BG_CARD};
                border-bottom: 1px solid {BORDER};
                border-top-left-radius: 14px;
                border-top-right-radius: 14px;
            }}
        """)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(20, 0, 8, 0)

        title_lbl = QLabel(title)
        title_lbl.setFont(font(18, bold=True))
        title_lbl.setStyleSheet(
            f"color:{TEXT_PRIMARY}; background:transparent;")
        h_lay.addWidget(title_lbl, stretch=1)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(34, 34)
        close_btn.setFont(font(13, bold=True))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_MUTED};
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: {ERROR_BG};
                color: {ERROR};
            }}
        """)
        close_btn.clicked.connect(self.reject)
        h_lay.addWidget(close_btn)

        surface_layout.addWidget(header)

        # ── Zona de toast (se inserta aquí encima del contenido) ──────────────
        self._toast_anchor = surface_layout  # referencia para insertar toast

        # ── Contenido ────────────────────────────────────────────────────────
        if scrollable:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setStyleSheet("background: transparent;")

            self._content_inner = QWidget()
            self._content_inner.setStyleSheet("background: transparent;")
            self._content_layout = QVBoxLayout(self._content_inner)
            self._content_layout.setContentsMargins(20, 12, 20, 12)
            self._content_layout.setSpacing(6)
            self._content_layout.addStretch()

            scroll.setWidget(self._content_inner)
            surface_layout.addWidget(scroll, stretch=1)
            self._content_widget = self._content_inner
        else:
            self._content_widget = QWidget()
            self._content_widget.setStyleSheet("background: transparent;")
            self._content_layout = QVBoxLayout(self._content_widget)
            self._content_layout.setContentsMargins(20, 12, 20, 12)
            self._content_layout.setSpacing(6)
            surface_layout.addWidget(self._content_widget, stretch=1)

        # ── Footer ───────────────────────────────────────────────────────────
        self._footer = QFrame()
        self._footer.setFixedHeight(60)
        self._footer.setStyleSheet(f"""
            QFrame {{
                background: {BG_APP};
                border-top: 1px solid {BORDER};
                border-bottom-left-radius: 14px;
                border-bottom-right-radius: 14px;
            }}
        """)
        self._footer_lay = QHBoxLayout(self._footer)
        self._footer_lay.setContentsMargins(16, 0, 16, 0)
        self._footer_lay.setSpacing(8)
        surface_layout.addWidget(self._footer)

    # ── Propiedad content ─────────────────────────────────────────────────────
    @property
    def content(self) -> QWidget:
        """Widget de contenido al que las subclases añaden sus widgets."""
        return self._content_widget

    # ── Helpers para añadir al contenido ─────────────────────────────────────
    def _add_to_content(self, widget: QWidget):
        """Inserta un widget antes del stretch final (si scrollable)."""
        count = self._content_layout.count()
        last  = self._content_layout.itemAt(count - 1)
        if last and last.spacerItem():
            self._content_layout.insertWidget(count - 1, widget)
        else:
            self._content_layout.addWidget(widget)

    # ── Footer buttons ────────────────────────────────────────────────────────
    def add_footer_buttons(self,
                           confirm_text: str = "Guardar",
                           confirm_cmd=None,
                           cancel_text: str = "Cancelar",
                           danger_text: str = None,
                           danger_cmd=None):
        if danger_text and danger_cmd:
            db = _danger_btn(danger_text)
            db.clicked.connect(danger_cmd)
            self._footer_lay.addWidget(db)

        self._footer_lay.addStretch()

        cancel = _secondary_btn(cancel_text)
        cancel.clicked.connect(self.reject)
        self._footer_lay.addWidget(cancel)

        confirm = _primary_btn(confirm_text, min_w=130)
        if confirm_cmd:
            confirm.clicked.connect(confirm_cmd)
        else:
            confirm.clicked.connect(self.accept)
        self._footer_lay.addWidget(confirm)

    # ── Toast de error ────────────────────────────────────────────────────────
    def show_error(self, message: str):
        self._clear_toast()

        toast = QFrame(self)
        toast.setStyleSheet(f"""
            QFrame {{
                background: {ERROR_BG};
                border: 1px solid {ERROR};
                border-radius: 8px;
            }}
        """)
        tl = QHBoxLayout(toast)
        tl.setContentsMargins(12, 6, 6, 6)

        msg_lbl = QLabel(f"⚠  {message}")
        msg_lbl.setFont(font(11))
        msg_lbl.setStyleSheet(
            f"color:{ERROR}; background:transparent;")
        msg_lbl.setWordWrap(True)
        tl.addWidget(msg_lbl, stretch=1)

        x_btn = QPushButton("✕")
        x_btn.setFixedSize(22, 22)
        x_btn.setFont(font(11, bold=True))
        x_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        x_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none;
                color: {ERROR};
            }}
        """)
        x_btn.clicked.connect(self._clear_toast)
        tl.addWidget(x_btn)

        # Posicionar debajo del header (y=53)
        toast.setGeometry(24, 61, self.width() - 48, 42)
        toast.show()
        toast.raise_()
        self._toast_widget = toast

        self._toast_timer = QTimer(self)
        self._toast_timer.setSingleShot(True)
        self._toast_timer.timeout.connect(self._clear_toast)
        self._toast_timer.start(4000)

    def _clear_toast(self):
        if self._toast_timer:
            self._toast_timer.stop()
            self._toast_timer = None
        if self._toast_widget:
            self._toast_widget.hide()
            self._toast_widget.deleteLater()
            self._toast_widget = None

    def show_success(self, message: str):
        lbl = QLabel(f"✓  {message}")
        lbl.setFont(font(11))
        lbl.setStyleSheet(f"""
            color: {SUCCESS_TEXT};
            background: {SUCCESS_BG};
            border-radius: 6px;
            padding: 6px 10px;
        """)
        self._add_to_content(lbl)
        QTimer.singleShot(3000, lbl.deleteLater)


# ─────────────────────────────────────────────────────────────────────────────
# ConfirmModal — bloquea hasta que el usuario confirma o cancela
# ─────────────────────────────────────────────────────────────────────────────

class ConfirmModal(BaseModal):
    """
    Modal de confirmación modal y bloqueante.
    Uso:
        dlg = ConfirmModal(parent, title="...", message="...", danger=True)
        if dlg.confirmed:
            ...
    """

    def __init__(self, parent, title: str, message: str,
                 confirm_text: str = "Confirmar",
                 danger: bool = False,
                 cancel_text: str | None = "Cancelar"):
        # El contenido necesita al menos 316 px lógicos con el escalado de
        # Windows; una altura inferior provoca que Qt lo recorte hasta moverlo.
        super().__init__(parent, title, width=520, height=320,
                         scrollable=False)
        self._confirmed = False

        # La confirmación muestra contexto y gravedad sin dejar un bloque vacío.
        tone = ERROR if danger else PRIMARY
        tone_bg = ERROR_BG if danger else BG_PALE
        icon_name = "ban" if danger else "shield"

        notice = QFrame()
        notice.setStyleSheet(f"""
            QFrame {{
                background: {tone_bg};
                border: none;
                border-radius: 10px;
            }}
        """)
        notice_lay = QHBoxLayout(notice)
        notice_lay.setContentsMargins(16, 14, 16, 14)
        notice_lay.setSpacing(12)

        icon = QLabel()
        icon.setFixedSize(28, 28)
        icon.setPixmap(svg_icon(icon_name, 24, tone))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        notice_lay.addWidget(icon, alignment=Qt.AlignmentFlag.AlignTop)

        msg = QLabel(message)
        msg.setFont(font(13))
        msg.setStyleSheet(f"color:{TEXT_SECONDARY}; background:transparent;")
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        notice_lay.addWidget(msg, stretch=1)

        self._content_layout.setContentsMargins(24, 20, 24, 18)
        self._content_layout.addWidget(notice)
        self._content_layout.addStretch()

        # Botones
        self._footer_lay.addStretch()

        if cancel_text:
            cancel = _secondary_btn(cancel_text)
            cancel.clicked.connect(self.reject)
            self._footer_lay.addWidget(cancel)

        if danger:
            confirm = _danger_btn(confirm_text)
        else:
            confirm = _primary_btn(confirm_text)
        confirm.clicked.connect(self._confirm)
        self._footer_lay.addWidget(confirm)

        # Bloquear hasta cerrar.
        self.exec()

    def _confirm(self):
        self._confirmed = True
        self.accept()

    @property
    def confirmed(self) -> bool:
        return self._confirmed
