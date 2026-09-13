"""
VISTA Qt — Login. Diseño SAIA con círculos decorativos, tarjeta flotante
con sombra real y botón gradiente.
"""
import sys
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QHBoxLayout, QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import (
    QPixmap, QColor, QPainter, QBrush, QLinearGradient, QPen, QIcon,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QEvent, QSize

from app.ui.theme import (
    PRIMARY, PRIMARY_HOVER, SECONDARY,
    BG_APP, BG_CARD, BG_INPUT, BG_PALE, BG_HOVER,
    BORDER, BORDER_FOCUS, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ERROR, INPUT_RADIUS,
    font, svg_icon, LOGO_GRADIENT, ICONS_DIR,
    paint_gradient_btn,
)

_CIRCLE = "#B2F0DC"
_DOT    = "#C8F5E6"
_ACCOUNT_ICON = ICONS_DIR / "cuenta.png"


# ─────────────────────────────────────────────────────────────────────────────
# Worker de autenticación (hilo separado)
# ─────────────────────────────────────────────────────────────────────────────

class _LoginWorker(QThread):
    success = pyqtSignal(dict)
    error   = pyqtSignal(str)

    def __init__(self, num_doc: int, pwd: str):
        super().__init__()
        self._doc = num_doc
        self._pwd = pwd

    def run(self):
        try:
            import bcrypt
            from app.models.persona_model import CuentaModel
            user = CuentaModel.get_login_data(self._doc)
        except Exception:
            self.error.emit("Error de conexión a la base de datos.")
            return

        if not user:
            self.error.emit("Documento o contraseña incorrectos.")
            return
        if not user.get("estado"):
            self.error.emit("Tu cuenta está bloqueada. Contacta al administrador.")
            return
        if user.get("id_rol") != 2:
            self.error.emit("Acceso denegado. Solo administradores.")
            return

        try:
            import bcrypt
            valid = bcrypt.checkpw(
                self._pwd.encode(), user.get("password", "").encode())
        except Exception:
            valid = False

        if not valid:
            self.error.emit("Documento o contraseña incorrectos.")
            return

        try:
            from app.models.auditoria_model import (
                AuditoriaModel, ACCION_LOGIN, ENTIDAD_SESION)
            nombre = (f"{user.get('nombres','').strip()} "
                      f"{user.get('p_ape','').strip()}").strip()
            AuditoriaModel.registrar(
                ACCION_LOGIN, ENTIDAD_SESION, user["num_doc"],
                f"Inicio de sesión del administrador {nombre} "
                f"(Doc: {user['num_doc']})",
                realizado_por=user["num_doc"],
            )
        except Exception:
            pass

        self.success.emit(user)


# ─────────────────────────────────────────────────────────────────────────────
# Input con icono SVG izquierdo
# ─────────────────────────────────────────────────────────────────────────────

class _IconInput(QFrame):
    _SS_N = ""   # normal
    _SS_F = ""   # focus
    _SS_E = ""   # error

    def __init__(self, placeholder: str, icon_name: str,
                 password: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("II")
        self.setFixedHeight(48)

        _IconInput._SS_N = (f"QFrame#II{{background:{BG_INPUT};"
                            f"border:1.5px solid {BORDER};"
                            f"border-radius:{INPUT_RADIUS}px;}}")
        _IconInput._SS_F = (f"QFrame#II{{background:{BG_INPUT};"
                            f"border:1.5px solid {BORDER_FOCUS};"
                            f"border-radius:{INPUT_RADIUS}px;}}")
        _IconInput._SS_E = (f"QFrame#II{{background:{BG_INPUT};"
                            f"border:1.5px solid {ERROR};"
                            f"border-radius:{INPUT_RADIUS}px;}}")
        self.setStyleSheet(_IconInput._SS_N)
        self._has_error = False

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 10, 0)
        lay.setSpacing(8)

        ic = QLabel()
        ic.setPixmap(svg_icon(icon_name, 20, PRIMARY))
        ic.setFixedSize(22, 22)
        ic.setScaledContents(True)
        ic.setStyleSheet("background:transparent;")
        lay.addWidget(ic)

        self.edit = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        self.edit.setStyleSheet(f"""
            QLineEdit {{
                background:transparent; border:none;
                color:{TEXT_PRIMARY};
                font-family:'Segoe UI'; font-size:13px;
            }}
        """)
        if password:
            self.edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit.installEventFilter(self)
        lay.addWidget(self.edit, stretch=1)

        if password:
            self._eye_visible = False
            self._eye_btn = QPushButton()
            self._eye_btn.setFixedSize(30, 30)
            self._eye_btn.setStyleSheet(
                "background:transparent; border:none;")
            self._eye_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._update_eye()
            self._eye_btn.clicked.connect(self._toggle_eye)
            lay.addWidget(self._eye_btn)

    def eventFilter(self, obj, event):
        if obj is self.edit:
            if event.type() == QEvent.Type.FocusIn:
                if not self._has_error:
                    self.setStyleSheet(_IconInput._SS_F)
            elif event.type() == QEvent.Type.FocusOut:
                if not self._has_error:
                    self.setStyleSheet(_IconInput._SS_N)
        return super().eventFilter(obj, event)

    def _update_eye(self):
        px = svg_icon("eye-off" if self._eye_visible else "eye", 20, PRIMARY)
        self._eye_btn.setIcon(QIcon(px))
        self._eye_btn.setIconSize(QSize(20, 20))

    def _toggle_eye(self):
        self._eye_visible = not self._eye_visible
        self.edit.setEchoMode(
            QLineEdit.EchoMode.Normal if self._eye_visible
            else QLineEdit.EchoMode.Password)
        self._update_eye()

    def text(self) -> str:  return self.edit.text()
    def set_error(self):    self._has_error = True;  self.setStyleSheet(_IconInput._SS_E)
    def clear_error(self):  self._has_error = False; self.setStyleSheet(_IconInput._SS_N)


# ─────────────────────────────────────────────────────────────────────────────
# Botón gradiente
# ─────────────────────────────────────────────────────────────────────────────

class _GradBtn(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(font(13, bold=True))
        self.setStyleSheet(
            "color:white; border:none; border-radius:25px;")
        self._hover = False

    def enterEvent(self, e): self._hover = True;  self.update()
    def leaveEvent(self, e): self._hover = False; self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        paint_gradient_btn(p, self.rect(), self._hover, radius=25)
        p.setPen(QPen(QColor("white")))
        p.setFont(self.font())
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())


# ─────────────────────────────────────────────────────────────────────────────
# Vista de Login
# ─────────────────────────────────────────────────────────────────────────────

class LoginView(QWidget):
    """Pantalla de inicio de sesión con diseño SAIA completo."""

    def __init__(self, parent=None, on_login_success=None):
        super().__init__(parent)
        self._callback = on_login_success
        self._worker   = None
        self._build()

    # ── Fondo con círculos ────────────────────────────────────────────────────
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(BG_APP))

        c = QColor(_CIRCLE)
        p.setBrush(QBrush(c))
        p.setPen(QPen(Qt.PenStyle.NoPen))
        W, H = self.width(), self.height()
        p.drawEllipse(-90,     -90,      250, 250)
        p.drawEllipse(W - 115, -65,      175, 175)
        p.drawEllipse(-55,     H - 110,  160, 160)
        p.drawEllipse(W - 130, H - 130,  210, 210)

        dot = QColor(_DOT)
        p.setBrush(QBrush(dot))
        for r in range(5):
            for c_ in range(5):
                p.drawEllipse(58 + c_ * 14, H // 2 - 30 + r * 14, 5, 5)
        for r in range(5):
            for c_ in range(5):
                p.drawEllipse(W - 100 + c_ * 14, H // 2 + 20 + r * 14, 5, 5)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()
        if hasattr(self, "_footer"):
            self._footer.setGeometry(
                0, self.height() - 36, self.width(), 36)

    # ── Layout principal ──────────────────────────────────────────────────────
    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # El contenido vive en un bloque central: así las dos columnas mantienen
        # una relación consistente tanto en pantallas grandes como medianas.
        container = QWidget()
        container.setMaximumWidth(1150)
        container.setStyleSheet("background:transparent;")
        content = QHBoxLayout(container)
        content.setContentsMargins(10, 20, 30, 45)
        # content.setSpacing(220)

        left_wrap = QWidget()
        left_wrap.setMinimumWidth(430)
        left_wrap.setStyleSheet("background:transparent;")
        ll = QVBoxLayout(left_wrap)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.addStretch(1)
        ll.addWidget(self._make_left(), alignment=Qt.AlignmentFlag.AlignCenter)
        ll.addStretch(1)

        right_wrap = QWidget()
        right_wrap.setMinimumWidth(430)
        right_wrap.setStyleSheet("background:transparent;")
        rl = QVBoxLayout(right_wrap)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.addStretch(1)
        rl.addWidget(self._make_card(),
                     alignment=Qt.AlignmentFlag.AlignCenter)
        rl.addStretch(1)

        content.addWidget(left_wrap)
        content.addWidget(right_wrap)
        root.addStretch(1)
        root.addWidget(container)
        root.addStretch(1)

        # Footer flotante
        footer = QWidget(self)
        footer.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(0, 0, 0, 6)
        lbl = QLabel(
            "<b style='color:#33BEDC;'>SAIA</b>"
            "<span style='color:#9CA3AF;'> • Administración"
            "&nbsp;&nbsp;&nbsp;"
            "© 2025 SAIA. Todos los derechos reservados.</span>")
        lbl.setFont(font(9))
        lbl.setStyleSheet("background:transparent;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(lbl)
        self._footer = footer
        footer.setGeometry(0, self.height() - 36, self.width(), 36)

    # ── Panel izquierdo ───────────────────────────────────────────────────────
    def _make_left(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Logo
        logo = QLabel()
        logo.setStyleSheet("background:transparent;")
        if LOGO_GRADIENT.exists():
            pix = QPixmap(str(LOGO_GRADIENT)).scaled(
                110, 110,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pix)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(logo)
        lay.addSpacing(14)

        saia = QLabel("SAIA")
        saia.setFont(font(42, bold=True))
        saia.setStyleSheet(f"color:{PRIMARY}; background:transparent;")
        saia.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(saia)

        sub = QLabel("Sistema de Autogestión de\nIngreso y Acceso")
        sub.setFont(font(13))
        sub.setStyleSheet(
            f"color:{TEXT_SECONDARY}; background:transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(sub)
        lay.addSpacing(14)

        # Separador
        sep_row = QHBoxLayout()
        sep_row.setContentsMargins(0, 0, 0, 0)
        sep = QFrame()
        sep.setFixedSize(50, 3)
        sep.setStyleSheet(f"background:{PRIMARY}; border-radius:2px;")
        sep_row.addStretch()
        sep_row.addWidget(sep)
        sep_row.addStretch()
        lay.addLayout(sep_row)
        lay.addSpacing(24)

        # Features
        for icon, title, subtitle in [
            ("qr-code",    "Tecnología QR",    "Ingreso seguro y sin contacto."),
            ("zap",        "Validación rápida", "Procesos ágiles y eficientes."),
            ("headphones", "Soporte 24/7",     "Estamos siempre para ayudarte."),
        ]:
            lay.addWidget(self._make_feature(icon, title, subtitle))
            lay.addSpacing(10)

        return w

    def _make_feature(self, icon_name: str, title: str,
                      subtitle: str) -> QWidget:
        row = QWidget()
        row.setStyleSheet("background:transparent;")
        row.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(14)

        box = QWidget()
        box.setFixedSize(46, 46)
        box.setStyleSheet(
            f"background:{BG_CARD}; border:1px solid {BORDER}; "
            "border-radius:10px;")
        shadow = QGraphicsDropShadowEffect(box)
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 24))
        box.setGraphicsEffect(shadow)
        bl = QHBoxLayout(box)
        bl.setContentsMargins(0, 0, 0, 0)
        ic = QLabel()
        ic.setPixmap(svg_icon(icon_name, 22, PRIMARY))
        ic.setFixedSize(22, 22)
        ic.setScaledContents(True)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ic.setStyleSheet("background:transparent;")
        bl.addWidget(ic, alignment=Qt.AlignmentFlag.AlignCenter)
        h.addWidget(box, alignment=Qt.AlignmentFlag.AlignVCenter)

        col = QVBoxLayout()
        col.setSpacing(1)
        col.setContentsMargins(0, 0, 0, 0)
        t = QLabel(title)
        t.setFont(font(12, bold=True))
        t.setStyleSheet(f"color:{TEXT_PRIMARY}; background:transparent;")
        s = QLabel(subtitle)
        s.setFont(font(10))
        s.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        col.addWidget(t)
        col.addWidget(s)
        h.addLayout(col)
        h.addStretch()
        return row

    # ── Tarjeta del formulario ────────────────────────────────────────────────
    def _make_card(self) -> QFrame:
        card = QFrame()
        card.setFixedWidth(430)
        card.setStyleSheet(f"""
            QFrame {{
                background:{BG_CARD};
                border-radius:20px;
                border:none;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 45))
        card.setGraphicsEffect(shadow)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(38, 32, 38, 32)
        lay.setSpacing(0)

        # Icono de cuenta específico para el formulario, sin repetir el logo.
        account_icon = QLabel()
        account_icon.setStyleSheet("background:transparent;")
        if _ACCOUNT_ICON.exists():
            account_icon.setPixmap(QPixmap(str(_ACCOUNT_ICON)).scaled(
                82, 82,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        account_icon.setFixedSize(82, 82)
        account_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(account_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        lay.addSpacing(10)

        title = QLabel("INICIAR SESIÓN")
        title.setFont(font(18, bold=True))
        title.setStyleSheet(f"color:{PRIMARY}; background:transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        sub = QLabel("Panel de Administración")
        sub.setFont(font(11))
        sub.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(sub)
        lay.addSpacing(8)

        # Separador
        line_row = QHBoxLayout()
        line_row.setContentsMargins(0, 0, 0, 0)
        line = QFrame()
        line.setFixedSize(50, 2)
        line.setStyleSheet("background:#E5E7EB; border-radius:1px;")
        line_row.addStretch()
        line_row.addWidget(line)
        line_row.addStretch()
        lay.addLayout(line_row)
        lay.addSpacing(18)

        # — Documento —
        doc_lbl = QLabel("Número de documento")
        doc_lbl.setFont(font(11, bold=True))
        doc_lbl.setStyleSheet(
            f"color:{TEXT_SECONDARY}; background:transparent;")
        lay.addWidget(doc_lbl)
        lay.addSpacing(6)

        self._doc = _IconInput(
            "Ingresa tu número de documento", "user")
        lay.addWidget(self._doc)
        self._doc.edit.returnPressed.connect(
            lambda: self._pwd.edit.setFocus())
        lay.addSpacing(14)

        # — Contraseña —
        pwd_lbl = QLabel("Contraseña")
        pwd_lbl.setFont(font(11, bold=True))
        pwd_lbl.setStyleSheet(
            f"color:{TEXT_SECONDARY}; background:transparent;")
        lay.addWidget(pwd_lbl)
        lay.addSpacing(6)

        self._pwd = _IconInput(
            "Ingresa tu contraseña", "lock", password=True)
        lay.addWidget(self._pwd)
        self._pwd.edit.returnPressed.connect(self._do_login)
        lay.addSpacing(6)

        # — Mensaje de error/info —
        self._err = QLabel("")
        self._err.setFont(font(10))
        self._err.setStyleSheet(
            f"color:{ERROR}; background:transparent;")
        self._err.setFixedHeight(16)
        self._err.setWordWrap(True)
        lay.addWidget(self._err)
        lay.addSpacing(10)

        # — Botón ingresar —
        self._btn = _GradBtn("Ingresar  →")
        self._btn.clicked.connect(self._do_login)
        lay.addWidget(self._btn)
        return card

    # ── Lógica de login ───────────────────────────────────────────────────────
    def _do_login(self):
        doc = self._doc.text().strip()
        pwd = self._pwd.text()
        self._doc.clear_error()
        self._pwd.clear_error()

        if not doc or not pwd:
            self._show_error("Completa todos los campos.")
            if not doc: self._doc.set_error()
            if not pwd: self._pwd.set_error()
            return
        try:
            num_doc = int(doc)
        except ValueError:
            self._show_error("El número de documento debe ser numérico.")
            self._doc.set_error()
            return
        if len(pwd) < 6:
            self._show_error("La contraseña debe tener al menos 6 caracteres.")
            self._pwd.set_error()
            return

        self._btn.setEnabled(False)
        self._show_info("⏳  Verificando…")
        self._worker = _LoginWorker(num_doc, pwd)
        self._worker.success.connect(self._on_ok)
        self._worker.error.connect(self._on_err)
        self._worker.start()

    def _on_ok(self, user: dict):
        self._btn.setEnabled(True)
        self._err.setText("")
        if self._callback:
            self._callback(user)

    def _on_err(self, msg: str):
        self._btn.setEnabled(True)
        self._show_error(msg)

    def _show_error(self, msg: str):
        self._err.setStyleSheet(f"color:{ERROR}; background:transparent;")
        self._err.setText(f"⚠  {msg}")

    def _show_info(self, msg: str):
        self._err.setStyleSheet(f"color:{PRIMARY}; background:transparent;")
        self._err.setText(msg)
