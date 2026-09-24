
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QScrollArea,
    QVBoxLayout, QHBoxLayout, QSizePolicy,
)
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QBrush, QColor, QPen
from PyQt6.QtCore import Qt, QSize, QRect, QRectF

from app.ui.theme import (
    BG_SIDEBAR, BG_HOVER, BG_ACTIVE, BG_PALE, BORDER,
    PRIMARY, PRIMARY_HOVER, ERROR, ERROR_BG,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    SIDEBAR_WIDTH, HEADER_HEIGHT,
    font, svg_icon, LOGO_GRADIENT,
)

NAV_ITEMS = [
    ("layout-dashboard", "dashboard",    "Inicio",         "PRINCIPAL"),
    ("graduation-cap",   "aprendices",   "Aprendices",     "PRINCIPAL"),
    ("shield",           "guardas",      "Guardas",        "PRINCIPAL"),
    ("clipboard-list",   "historial",    "Historial",      "PRINCIPAL"),
    ("ban",              "bloqueo",      "Bloqueados",     "PRINCIPAL"),
    ("file-text",        "reportes",     "Reportes",       "HERRAMIENTAS"),
    ("bar-chart-2",      "estadisticas", "Estadísticas",   "HERRAMIENTAS"),
    ("search",           "auditoria",    "Auditoría",      "PERFIL"),
    ("users",            "administradores", "Administradores", "PERFIL"),
    ("settings",         "ajustes",      "Editar perfil",  "PERFIL"),
]


class _AvatarWidget(QWidget):
 
    def __init__(self, color: str, icon_pixmap: QPixmap,
                 size: int = 36, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._icon  = icon_pixmap
        self._size  = size
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Círculo de fondo
        p.setBrush(QBrush(self._color))
        p.setPen(QPen(Qt.PenStyle.NoPen))
        p.drawEllipse(0, 0, self._size, self._size)
        # Ícono centrado
        iw = self._icon.width()
        ih = self._icon.height()
        ox = (self._size - iw) // 2
        oy = (self._size - ih) // 2
        p.drawPixmap(ox, oy, self._icon)
        p.end()

_EXTRA = ["layout-dashboard","graduation-cap","shield","clipboard-list",
          "ban","file-text","bar-chart-2","settings","log-out","user",
          "bell","calendar","package","users","building-2","clock",
          "circle-check","refresh-cw","bar-chart-2"]



class Sidebar(QFrame):
    def __init__(self, parent=None, on_navigate=None, admin_name: str = "Administrador",
                 is_superadmin: bool = False):
        super().__init__(parent)
        self.setFixedWidth(SIDEBAR_WIDTH)
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_SIDEBAR};
                border-right: 1px solid {BORDER};
            }}
        """)
        self._on_navigate = on_navigate or (lambda _: None)
        self._active_id   = None
        self._nav_items   = {}
        self._is_superadmin = is_superadmin
        self._build(admin_name)

    def _build(self, admin_name: str):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        logo_frame = QFrame()
        logo_frame.setFixedHeight(HEADER_HEIGHT)
        logo_frame.setStyleSheet(f"background:{BG_SIDEBAR}; border:none;")
        ll = QHBoxLayout(logo_frame)
        ll.setContentsMargins(14, 0, 14, 0)
        ll.setSpacing(6)

        if LOGO_GRADIENT.exists():
            pix = QPixmap(str(LOGO_GRADIENT)).scaled(
                28, 28,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            logo_img = QLabel()
            logo_img.setPixmap(pix)
            logo_img.setFixedSize(28, 28)
            logo_img.setScaledContents(True)
            logo_img.setStyleSheet("background:transparent; border:none;")
            ll.addWidget(logo_img)

        brand = QLabel("SAIA  <span style='color:#9CA3AF; font-weight:normal; font-size:11px;'>Admin</span>")
        brand.setFont(font(17, bold=True))
        brand.setStyleSheet(f"color:{PRIMARY}; background:transparent;")
        brand.setTextFormat(Qt.TextFormat.RichText)
        ll.addWidget(brand)
        ll.addStretch()
        root.addWidget(logo_frame)

        # Separador
        sep1 = QFrame(); sep1.setFixedHeight(1)
        sep1.setStyleSheet(f"background:{BORDER}; border:none;")
        root.addWidget(sep1)

        # Perfil 
        profile = QFrame()
        profile.setFixedHeight(70)

        profile.setStyleSheet(f"""
            QFrame {{
                background: {BG_HOVER};
                border-radius: 9px;
                border: none;
                margin: 8px 10px 2px 10px;
            }}
        """)

        pl = QHBoxLayout(profile)
        pl.setContentsMargins(12, 7, 12, 7)
        pl.setSpacing(10)

        # Avatar circular
        avatar = _AvatarWidget(PRIMARY, svg_icon("user", 18, "#FFFFFF"), size=36)
        pl.addWidget(avatar)


        # Información del administrador 
        info = QVBoxLayout()
        info.setSpacing(2)
        info.setContentsMargins(0, 0, 0, 0)

        self._name_label = QLabel(admin_name)
        self._name_label.setFont(font(10, bold=True))
        self._name_label.setStyleSheet(
            f"color:{TEXT_PRIMARY}; background:transparent;"
        )
        self._name_label.setWordWrap(False)

        info.addWidget(self._name_label)

        rol = QLabel("Superadministrador" if self._is_superadmin else "Administrador")
        rol.setFont(font(9))
        rol.setStyleSheet(
            f"color:{PRIMARY}; background:transparent;"
        )

        info.addWidget(rol)

        pl.addLayout(info, stretch=1)

        root.addWidget(profile)

        #  Nav
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { width: 4px; background: transparent; }
            QScrollBar::handle:vertical { background: #E5E7EB; border-radius: 2px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        nav_w = QWidget(); nav_w.setStyleSheet("background: transparent;")
        nl    = QVBoxLayout(nav_w)
        nl.setContentsMargins(0, 6, 0, 0)
        nl.setSpacing(0)

        current_sec = None
        for icon_name, view_id, label, section in NAV_ITEMS:
            if view_id == "auditoria" and not self._is_superadmin:
                continue
            if view_id == "administradores" and not self._is_superadmin:
                continue
            if section != current_sec:
                current_sec = section
                sec = QLabel(section)
                sec.setFont(font(8, bold=True))
                sec.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
                sec.setContentsMargins(14, 10, 0, 2)
                nl.addWidget(sec)

            item = self._make_item(nav_w, icon_name, view_id, label)
            nl.addWidget(item)

        nl.addStretch()
        scroll.setWidget(nav_w)
        root.addWidget(scroll, stretch=1)

        # Cerrar sesión 
        sep2 = QFrame(); sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background:{BORDER}; border:none;")
        root.addWidget(sep2)

        logout = QPushButton("  Cerrar sesión")
        logout.setFixedHeight(40)
        logout.setFont(font(11))
        logout.setCursor(Qt.CursorShape.PointingHandCursor)
        px_lo = svg_icon("log-out", 14, ERROR)
        logout.setIcon(QIcon(px_lo))
        logout.setIconSize(QSize(14, 14))
        logout.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {ERROR};
                border: none; border-radius: 6px;
                text-align: left; padding-left: 12px;
            }}
            QPushButton:hover {{ background: {ERROR_BG}; }}
        """)
        logout.clicked.connect(lambda: self._on_navigate("logout"))
        root.addWidget(logout)
        root.addSpacing(6)

    def _make_item(self, parent, icon_name, view_id, label) -> QFrame:
        frame = QFrame(parent)
        frame.setFixedHeight(36)
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        frame.setStyleSheet(
            "QFrame{background:transparent; border-radius:6px; border:none;}")

        lay = QHBoxLayout(frame)
        lay.setContentsMargins(6, 0, 8, 0)
        lay.setSpacing(0)

        # Barra de acento izquierda
        accent = QFrame()
        accent.setFixedSize(3, 22)
        accent.setStyleSheet("background:transparent; border-radius:2px; border:none;")
        lay.addWidget(accent)
        lay.addSpacing(6)

        # Icono
        px = svg_icon(icon_name, 15, TEXT_MUTED)
        ic = QLabel()
        ic.setPixmap(px)
        ic.setFixedSize(16, 16)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ic.setStyleSheet("background:transparent;")
        lay.addWidget(ic)
        lay.addSpacing(8)

        # Label
        lbl = QLabel(label)
        lbl.setFont(font(12))
        lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; background:transparent;")
        lay.addWidget(lbl, stretch=1)

        self._nav_items[view_id] = {
            "frame": frame, "accent": accent,
            "label": lbl,   "icon":   ic,
            "icon_name": icon_name,
        }

        frame.mousePressEvent = lambda e, v=view_id: self._click(v)
        frame.enterEvent      = lambda e, v=view_id: self._hover_in(v)
        frame.leaveEvent      = lambda e, v=view_id: self._hover_out(v)
        for child in [ic, lbl, accent]:
            child.mousePressEvent = lambda e, v=view_id: self._click(v)

        return frame

    def _click(self, view_id):
        self.set_active(view_id)
        self._on_navigate(view_id)

    def _hover_in(self, view_id):
        if view_id != self._active_id:
            self._nav_items[view_id]["frame"].setStyleSheet(
                f"QFrame{{background:{BG_HOVER}; border-radius:6px; border:none;}}")

    def _hover_out(self, view_id):
        if view_id != self._active_id:
            self._nav_items[view_id]["frame"].setStyleSheet(
                "QFrame{background:transparent; border-radius:6px; border:none;}")

    def set_active(self, view_id: str):
        if self._active_id and self._active_id in self._nav_items:
            old = self._nav_items[self._active_id]
            old["frame"].setStyleSheet(
                "QFrame{background:transparent; border-radius:6px; border:none;}")
            old["accent"].setStyleSheet(
                "background:transparent; border-radius:2px; border:none;")
            old["label"].setStyleSheet(
                f"color:{TEXT_SECONDARY}; background:transparent;")
            old["label"].setFont(font(12))
            old["icon"].setPixmap(svg_icon(old["icon_name"], 15, TEXT_MUTED))

        self._active_id = view_id
        if view_id in self._nav_items:
            item = self._nav_items[view_id]
            item["frame"].setStyleSheet(
                f"QFrame{{background:{BG_ACTIVE}; border-radius:6px; border:none;}}")
            item["accent"].setStyleSheet(
                f"background:{PRIMARY}; border-radius:2px; border:none;")
            item["label"].setStyleSheet(
                f"color:{PRIMARY}; background:transparent;")
            item["label"].setFont(font(12, bold=True))
            item["icon"].setPixmap(svg_icon(item["icon_name"], 15, PRIMARY))

    def update_admin_name(self, name: str):
        self._name_label.setText(name)
