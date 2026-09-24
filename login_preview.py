"""
Preview del login SAIA en PyQt6.
    python -B login_preview.py
"""
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QLineEdit, QVBoxLayout, QHBoxLayout, QFrame,
    QSizePolicy, QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import (
    QPixmap, QFont, QColor, QPainter, QBrush,
    QLinearGradient, QPen, QIcon,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QEvent, QSize, QRectF
from PyQt6.QtSvg import QSvgRenderer

ROOT          = Path(__file__).resolve().parent
LOGO_GRADIENT = ROOT / "src" / "logos" / "LogoGradiente.png"

PRIMARY        = "#33BEDC"
PRIMARY_HOVER  = "#28A8C8"
SECONDARY      = "#42EDB5"
BG_APP         = "#F5F7FA"
BG_CARD        = "#FFFFFF"
BG_INPUT       = "#F8FAFC"
BG_PALE        = "#E8F8FC"
BORDER         = "#E5E7EB"
BORDER_FOCUS   = "#33BEDC"
TEXT_PRIMARY   = "#1A1A2E"
TEXT_SECONDARY = "#4B5563"
TEXT_MUTED     = "#9CA3AF"
ERROR          = "#EF4444"
CIRCLE         = "#B2F0DC"
DOT            = "#C8F5E6"


ICONS_DIR = ROOT / "src" / "icons"


def _svg_icon(name: str, size: int, color: str) -> QPixmap:
    """Carga un SVG de Lucide, colorea los strokes y retorna QPixmap.
    Renderiza al doble del tamaño pedido para evitar pixelado en HiDPI."""
    svg_path = ICONS_DIR / f"{name}.svg"
    if not svg_path.exists():
        px = QPixmap(size, size)
        px.fill(Qt.GlobalColor.transparent)
        return px

    svg_data = svg_path.read_text(encoding="utf-8")
    svg_data = svg_data.replace("currentColor", color)
    svg_data = svg_data.replace('stroke-width="2"', 'stroke-width="2.2"')
    svg_bytes = svg_data.encode("utf-8")

    render_size = size * 2
    px = QPixmap(render_size, render_size)
    px.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(svg_bytes)
    painter = QPainter(px)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(painter, QRectF(0, 0, render_size, render_size))
    painter.end()

    return px.scaled(size, size,
                     Qt.AspectRatioMode.KeepAspectRatio,
                     Qt.TransformationMode.SmoothTransformation)



def _icon_user(size=20, color=TEXT_MUTED) -> QPixmap:
    return _svg_icon("user", size, color)

def _icon_lock(size=20, color=TEXT_MUTED) -> QPixmap:
    return _svg_icon("lock", size, color)

def _icon_eye(size=20, color=TEXT_MUTED, closed=False) -> QPixmap:
    return _svg_icon("eye-off" if closed else "eye", size, color)



class _IconInput(QFrame):
    _SS_NORMAL = ""
    _SS_FOCUS  = ""
    _SS_ERROR  = ""

    def __init__(self, placeholder, icon_pixmap: QPixmap,
                 password=False, parent=None):
        super().__init__(parent)
        self.setObjectName("II")
        self.setFixedHeight(48)
        _IconInput._SS_NORMAL = (
            f"QFrame#II{{background:{BG_INPUT};"
            f"border:1.5px solid {BORDER};border-radius:10px;}}")
        _IconInput._SS_FOCUS = (
            f"QFrame#II{{background:{BG_INPUT};"
            f"border:1.5px solid {BORDER_FOCUS};border-radius:10px;}}")
        _IconInput._SS_ERROR = (
            f"QFrame#II{{background:{BG_INPUT};"
            f"border:1.5px solid {ERROR};border-radius:10px;}}")
        self.setStyleSheet(_IconInput._SS_NORMAL)

        h = QHBoxLayout(self)
        h.setContentsMargins(12, 0, 10, 0)
        h.setSpacing(8)

        # Icono vectorial
        ic_lbl = QLabel()
        ic_lbl.setPixmap(icon_pixmap)
        ic_lbl.setFixedSize(22, 22)
        ic_lbl.setStyleSheet("background:transparent;")
        ic_lbl.setScaledContents(True)
        h.addWidget(ic_lbl)

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
        h.addWidget(self.edit, stretch=1)


        if password:
            self._eye_visible = False
            self._eye_btn = QPushButton()
            self._eye_btn.setFixedSize(30, 30)
            self._eye_btn.setStyleSheet(
                "background:transparent; border:none;")
            self._eye_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._update_eye_icon()
            self._eye_btn.clicked.connect(self._toggle_eye)
            h.addWidget(self._eye_btn)

    def _update_eye_icon(self):
        px = _icon_eye(20, TEXT_SECONDARY, closed=self._eye_visible)
        self._eye_btn.setIcon(QIcon(px))
        self._eye_btn.setIconSize(QSize(20, 20))

    def eventFilter(self, obj, event):
        if obj is self.edit:
            if event.type() == QEvent.Type.FocusIn:
                self.setStyleSheet(_IconInput._SS_FOCUS)
            elif event.type() == QEvent.Type.FocusOut:
                self.setStyleSheet(_IconInput._SS_NORMAL)
        return super().eventFilter(obj, event)

    def _toggle_eye(self):
        self._eye_visible = not self._eye_visible
        self.edit.setEchoMode(
            QLineEdit.EchoMode.Normal if self._eye_visible
            else QLineEdit.EchoMode.Password)
        self._update_eye_icon()

    def text(self): return self.edit.text()
    def set_error(self): self.setStyleSheet(_IconInput._SS_ERROR)
    def clear_error(self): self.setStyleSheet(_IconInput._SS_NORMAL)



# Botón gradiente


class _GradientButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.setStyleSheet("color:white; border:none; border-radius:25px;")
        self._hover = False

    def enterEvent(self, e): self._hover = True;  self.update()
    def leaveEvent(self, e): self._hover = False; self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        g = QLinearGradient(0, 0, self.width(), 0)
        g.setColorAt(0, QColor("#28A8C8" if self._hover else PRIMARY))
        g.setColorAt(1, QColor("#35D4A0" if self._hover else SECONDARY))
        p.setBrush(QBrush(g))
        p.setPen(QPen(Qt.PenStyle.NoPen))
        p.drawRoundedRect(self.rect(), 25, 25)
        p.setPen(QPen(QColor("white")))
        p.setFont(self.font())
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())



class _LoginWorker(QThread):
    success = pyqtSignal(dict)
    error   = pyqtSignal(str)

    def __init__(self, num_doc, pwd):
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
            self.error.emit("Cuenta bloqueada. Contacta al administrador.")
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
                f"Login administrador {nombre}",
                realizado_por=user["num_doc"])
        except Exception:
            pass
        self.success.emit(user)



# Ventana principal


class LoginWindow(QWidget):
    def __init__(self, on_login_success=None):
        super().__init__()
        self._callback = on_login_success
        self._worker   = None
        self.setWindowTitle(
            "SAIA Admin — Sistema de Autogestión de Ingreso y Acceso")
        self.setMinimumSize(960, 600)

        # ── Ícono de la ventana (taskbar + titlebar)
        if LOGO_GRADIENT.exists():
            self.setWindowIcon(QIcon(str(LOGO_GRADIENT)))

        self._build()

   # Fondo
       def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(BG_APP))
        c = QColor(CIRCLE)
        p.setBrush(QBrush(c))
        p.setPen(QPen(Qt.PenStyle.NoPen))
        W, H = self.width(), self.height()
        p.drawEllipse(-90,      -90,      250, 250)   # sup-izq
        p.drawEllipse(W - 115,  -65,      175, 175)   # sup-der
        p.drawEllipse(-55,      H - 110,  160, 160)   # inf-izq
        p.drawEllipse(W - 130,  H - 130,  210, 210)   # inf-der
        # Puntos
        dot_c = QColor(DOT)
        p.setBrush(QBrush(dot_c))
        for r in range(5):
            for c_ in range(5):
                p.drawEllipse(58 + c_*14, H//2 - 30 + r*14, 5, 5)
        for r in range(5):
            for c_ in range(5):
                p.drawEllipse(W - 100 + c_*14, H//2 + 20 + r*14, 5, 5)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()
        if hasattr(self, "_footer"):
            self._footer.setGeometry(0, self.height()-36, self.width(), 36)

    #  Layout 
    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Contenedor central
        container = QWidget()
        container.setMaximumWidth(1150)
        container.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(container)
        layout.setContentsMargins(30, 20, 30, 45)
        layout.setSpacing(80)


        # IZQUIERDA


        left = QWidget()
        left.setMinimumWidth(430)
        left.setStyleSheet("background: transparent;")

        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_layout.addStretch()
        left_layout.addWidget(
            self._make_left(),
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        left_layout.addStretch()


        # DERECHA


        right = QWidget()
        right.setMinimumWidth(430)
        right.setStyleSheet("background: transparent;")

        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_layout.addStretch()
        right_layout.addWidget(
            self._make_card(),
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        right_layout.addStretch()

        layout.addWidget(left)
        layout.addWidget(right)

        root.addStretch()
        root.addWidget(container)
        root.addStretch()

        # Footer
        footer = QWidget(self)
        footer.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        fl = QHBoxLayout(footer)
        fl.setContentsMargins(0, 0, 0, 6)

        lbl = QLabel(
            "<b style='color:#33BEDC;'>SAIA</b>"
            "<span style='color:#9CA3AF;'> • Administración"
            "&nbsp;&nbsp;&nbsp;"
            "© 2025 SAIA. Todos los derechos reservados.</span>"
        )

        lbl.setFont(QFont("Segoe UI", 9))
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

        # SAIA
        saia = QLabel("SAIA")
        saia.setFont(QFont("Segoe UI", 42, QFont.Weight.Bold))
        saia.setStyleSheet(f"color:{PRIMARY}; background:transparent;")
        saia.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(saia)

        sub = QLabel("Sistema de Autogestión de\nIngreso y Acceso")
        sub.setFont(QFont("Segoe UI", 13))
        sub.setStyleSheet(f"color:{TEXT_SECONDARY}; background:transparent;")
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
            ("qr",      "Tecnología QR",    "Ingreso seguro y sin contacto."),
            ("bolt",    "Validación rápida", "Procesos ágiles y eficientes."),
            ("headset", "Soporte 24/7",     "Estamos siempre para ayudarte."),
        ]:
            lay.addWidget(self._make_feature(icon, title, subtitle))
            lay.addSpacing(10)

        return w

    def _make_feature(self, icon_name, title, subtitle) -> QWidget:
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
            f"background:{BG_PALE}; border-radius:10px;")
        bl = QHBoxLayout(box)
        bl.setContentsMargins(0, 0, 0, 0)

        # Icono vectorial según nombre
        ic_px = self._feature_icon(icon_name, 22, PRIMARY)
        ic_lbl = QLabel()
        ic_lbl.setPixmap(ic_px)
        ic_lbl.setFixedSize(22, 22)
        ic_lbl.setScaledContents(True)
        ic_lbl.setStyleSheet("background:transparent;")
        ic_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bl.addWidget(ic_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        h.addWidget(box, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Textos
        col = QVBoxLayout()
        col.setSpacing(1)
        col.setContentsMargins(0, 0, 0, 0)
        t = QLabel(title)
        t.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{TEXT_PRIMARY}; background:transparent;")
        s = QLabel(subtitle)
        s.setFont(QFont("Segoe UI", 10))
        s.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        col.addWidget(t)
        col.addWidget(s)
        h.addLayout(col)
        h.addStretch()
        return row

    def _feature_icon(self, name: str, size: int, color: str) -> QPixmap:
        lucide_map = {
            "qr":      "qr-code",
            "bolt":    "zap",
            "headset": "headphones",
        }
        return _svg_icon(lucide_map.get(name, name), size, color)

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

        # Logo pequeño
        logo_sm = QLabel()
        logo_sm.setStyleSheet("background:transparent;")
        if LOGO_GRADIENT.exists():
            pix = QPixmap(str(LOGO_GRADIENT)).scaled(
                70, 70,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            logo_sm.setPixmap(pix)
        logo_sm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(logo_sm)
        lay.addSpacing(10)

        title = QLabel("INICIAR SESIÓN")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{PRIMARY}; background:transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        sub = QLabel("Panel de Administración")
        sub.setFont(QFont("Segoe UI", 11))
        sub.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(sub)
        lay.addSpacing(8)

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

        # Campo documento
        doc_lbl = QLabel("Número de documento")
        doc_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        doc_lbl.setStyleSheet(
            f"color:{TEXT_SECONDARY}; background:transparent;")
        lay.addWidget(doc_lbl)
        lay.addSpacing(6)

        self._doc_input = _IconInput(
            "Ingresa tu número de documento",
            _icon_user(20, TEXT_SECONDARY))
        lay.addWidget(self._doc_input)
        self._doc_input.edit.returnPressed.connect(
            lambda: self._pwd_input.edit.setFocus())
        lay.addSpacing(14)

        # Campo contraseña
        pwd_lbl = QLabel("Contraseña")
        pwd_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        pwd_lbl.setStyleSheet(
            f"color:{TEXT_SECONDARY}; background:transparent;")
        lay.addWidget(pwd_lbl)
        lay.addSpacing(6)

        self._pwd_input = _IconInput(
            "Ingresa tu contraseña",
            _icon_lock(20, TEXT_SECONDARY),
            password=True)
        lay.addWidget(self._pwd_input)
        self._pwd_input.edit.returnPressed.connect(self._do_login)
        lay.addSpacing(6)

        # Error label
        self._err = QLabel("")
        self._err.setFont(QFont("Segoe UI", 10))
        self._err.setStyleSheet(f"color:{ERROR}; background:transparent;")
        self._err.setFixedHeight(16)
        self._err.setWordWrap(True)
        lay.addWidget(self._err)
        lay.addSpacing(10)

        # Botón ingresar
        self._btn = _GradientButton("Ingresar  →")
        self._btn.clicked.connect(self._do_login)
        lay.addWidget(self._btn)
        lay.addSpacing(14)

        # ¿Olvidaste tu contraseña?
        forgot = QPushButton("¿Olvidaste tu contraseña?")
        forgot.setFlat(True)
        forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot.setFont(QFont("Segoe UI", 11))
        forgot.setStyleSheet(f"""
            QPushButton {{
                color:{PRIMARY}; background:transparent;
                border:none; text-decoration:underline;
            }}
            QPushButton:hover {{ color:{PRIMARY_HOVER}; }}
        """)
        lay.addWidget(forgot, alignment=Qt.AlignmentFlag.AlignCenter)
        return card


    def _do_login(self):
        doc = self._doc_input.text().strip()
        pwd = self._pwd_input.text()
        self._doc_input.clear_error()
        self._pwd_input.clear_error()
        if not doc or not pwd:
            self._show_error("Completa todos los campos.")
            if not doc: self._doc_input.set_error()
            if not pwd: self._pwd_input.set_error()
            return
        try:
            num_doc = int(doc)
        except ValueError:
            self._show_error("El número de documento debe ser numérico.")
            self._doc_input.set_error()
            return
        if len(pwd) < 6:
            self._show_error("La contraseña debe tener al menos 6 caracteres.")
            self._pwd_input.set_error()
            return
        self._btn.setEnabled(False)
        self._show_info("⏳  Verificando...")
        self._worker = _LoginWorker(num_doc, pwd)
        self._worker.success.connect(self._on_success)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_success(self, user):
        self._btn.setEnabled(True)
        self._err.setText("")
        if self._callback:
            self._callback(user)

    def _on_error(self, msg):
        self._btn.setEnabled(True)
        self._show_error(msg)

    def _show_error(self, msg):
        self._err.setStyleSheet(f"color:{ERROR}; background:transparent;")
        self._err.setText(f"⚠  {msg}")

    def _show_info(self, msg):
        self._err.setStyleSheet(f"color:{PRIMARY}; background:transparent;")
        self._err.setText(msg)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = LoginWindow(on_login_success=lambda u: print(f"Login OK: {u}"))
    win.showMaximized()
    sys.exit(app.exec())
