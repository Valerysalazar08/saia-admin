
import threading
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout,
    QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal

from app.ui.theme import (
    BG_APP, BG_CARD, BG_INPUT, BG_PALE, BORDER,
    PRIMARY, SECONDARY, WARNING, TEXT_PRIMARY, TEXT_MUTED,
    CARD_RADIUS, font, svg_icon,
)
from app.ui.atoms.buttons import SecondaryButton
from app.ui.atoms.labels  import Divider
from app.models.aprendiz_model  import AprendizSaiaModel
from app.models.guarda_model    import GuardaModel
from app.models.historial_model import HistorialModel
from app.config.database        import db_saia


class _Sig(QObject):
    recent_ready  = pyqtSignal(list)
    guardas_ready = pyqtSignal(list)
    stats_ready   = pyqtSignal(dict)


def _shadow(widget, blur=20, offset=4, alpha=18):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(blur)
    fx.setOffset(0, offset)
    fx.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(fx)



class _StatCard(QFrame):
    def __init__(self, title, value=0, icon_name="", color=PRIMARY):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border-radius: 12px;
                border: none;
            }}
        """)
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        _shadow(self, blur=16, offset=3, alpha=14)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Barra de acento top (4px, solo esquinas superiores)
        bar = QFrame()
        bar.setFixedHeight(4)
        bar.setStyleSheet(f"""
            background: {color};
            border: none;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        """)
        root.addWidget(bar)

        # Contenido
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(16, 12, 16, 14)
        bl.setSpacing(4)

        if icon_name:
            ic_box = QFrame()
            ic_box.setFixedSize(32, 32)
            ic_box.setStyleSheet(f"""
                background: {BG_PALE};
                border-radius: 8px;
                border: none;
            """)
            ib = QHBoxLayout(ic_box)
            ib.setContentsMargins(0, 0, 0, 0)
            ic_lbl = QLabel()
            ic_lbl.setPixmap(svg_icon(icon_name, 16, color))
            ic_lbl.setFixedSize(16, 16)
            ic_lbl.setScaledContents(True)
            ic_lbl.setStyleSheet("background: transparent;")
            ic_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ib.addWidget(ic_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
            bl.addWidget(ic_box)

        # Número grande
        self._val = QLabel(str(value))
        self._val.setFont(font(26, bold=True))
        self._val.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        bl.addWidget(self._val)

        # Título pequeño
        ttl = QLabel(title)
        ttl.setFont(font(11))
        ttl.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        bl.addWidget(ttl)

        root.addWidget(body)

    def update_value(self, v):
        self._val.setText(str(v))


class DashboardView(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"background: {BG_APP};")

        self._sig = _Sig()
        self._sig.recent_ready.connect(self._render_recent)
        self._sig.guardas_ready.connect(self._render_guardas)
        self._sig.stats_ready.connect(self._update_stats)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        # Mantiene los datos del inicio al día sin exigir navegación manual.
        self._timer.start(10000)

        content = QWidget()
        content.setStyleSheet(f"background: {BG_APP};")
        self.setWidget(content)

        self._lay = QVBoxLayout(content)
        self._lay.setContentsMargins(24, 20, 24, 24)
        self._lay.setSpacing(0)

        self._build()
        self.refresh()

    def _build(self):
        top = QWidget(); top.setStyleSheet("background: transparent;")
        tl  = QHBoxLayout(top); tl.setContentsMargins(0, 0, 0, 0)

        h_lbl = QLabel("Bienvenido al Panel SAIA")
        h_lbl.setFont(font(18, bold=True))
        h_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        tl.addWidget(h_lbl, stretch=1)

        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        ref = SecondaryButton("Actualizar", width=120, height=32)
        ref.clicked.connect(self.refresh)
        tl.addWidget(ref)
        self._lay.addWidget(top)

        sub = QLabel("Resumen del sistema — se actualiza automáticamente cada 10 segundos")
        sub.setFont(font(11))
        sub.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent;")
        sub.setContentsMargins(0, 4, 0, 20)
        self._lay.addWidget(sub)

        row1 = QWidget(); row1.setStyleSheet("background: transparent;")
        r1l  = QHBoxLayout(row1); r1l.setContentsMargins(0,0,0,0); r1l.setSpacing(12)

        self._cards = []
        for title, icon, color in [
            ("Aprendices registrados", "users",          PRIMARY),
            ("Guardas activos",        "shield",         SECONDARY),
            ("Ingresos hoy",           "clipboard-list", WARNING),
        ]:
            c = _StatCard(title, "—", icon, color)
            self._cards.append(c)
            r1l.addWidget(c)
        self._lay.addWidget(row1)
        self._lay.addSpacing(12)

        row2 = QWidget(); row2.setStyleSheet("background: transparent;")
        r2l  = QHBoxLayout(row2); r2l.setContentsMargins(0,0,0,0); r2l.setSpacing(12)

        self._stat_mes     = _StatCard("Ingresos este mes",          "—", "calendar",     PRIMARY)
        self._stat_activos = _StatCard("Cuentas activas",            "—", "circle-check",  SECONDARY)
        self._stat_dentro  = _StatCard("Aprendices dentro del SENA", "—", "building-2",   "#33BEDC")
        for c in [self._stat_mes, self._stat_activos, self._stat_dentro]:
            r2l.addWidget(c)
        self._lay.addWidget(row2)
        self._lay.addSpacing(16)

        div = Divider()
        self._lay.addWidget(div)
        self._lay.addSpacing(14)

        cols = QWidget(); cols.setStyleSheet("background: transparent;")
        cl   = QHBoxLayout(cols); cl.setContentsMargins(0,0,0,0); cl.setSpacing(16)

        self._recent_card  = self._list_card("Accesos recientes",      "clock",  show_ver=True)
        self._recent_body, self._recent_lay = self._scroll_body(self._recent_card)
        cl.addWidget(self._recent_card, stretch=1)

        self._guardas_card = self._list_card("Guardas en turno activo","shield", show_ver=False)
        self._guardas_body, self._guardas_lay = self._scroll_body(self._guardas_card)
        cl.addWidget(self._guardas_card, stretch=1)

        # Las listas tienen una altura compacta; no deben estirarse para llenar
        # todo el espacio vertical de la ventana.
        self._lay.addWidget(cols)

    def _list_card(self, title, icon_name, show_ver=False) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border-radius: 12px;
                border: none;
            }}
        """)
        _shadow(card, blur=16, offset=3, alpha=14)

        lay = QVBoxLayout(card); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)

        hdr = QWidget(); hdr.setStyleSheet("background: transparent;")
        hl  = QHBoxLayout(hdr); hl.setContentsMargins(14, 8, 14, 6); hl.setSpacing(8)

        ic = QLabel()
        ic.setPixmap(svg_icon(icon_name, 15, PRIMARY))
        ic.setFixedSize(16, 16); ic.setScaledContents(True)
        ic.setStyleSheet("background: transparent;")
        hl.addWidget(ic)

        lbl = QLabel(title); lbl.setFont(font(13, bold=True))
        lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        hl.addWidget(lbl, stretch=1)

        if show_ver:
            ver = QPushButton("Ver todos")
            ver.setFlat(True)
            ver.setFont(font(11))
            ver.setCursor(Qt.CursorShape.PointingHandCursor)
            ver.setStyleSheet(f"""
                QPushButton {{ color: {PRIMARY}; background: transparent; border: none; }}
                QPushButton:hover {{ text-decoration: underline; }}
            """)
            hl.addWidget(ver)

        lay.addWidget(hdr)
        # Separador fino
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER}; border: none;")
        lay.addWidget(sep)
        return card

    def _scroll_body(self, card: QFrame):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setFixedHeight(150)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                margin: 4px 2px 4px 0;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 3px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #C8D0DC;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)

        body = QWidget(); body.setStyleSheet("background: transparent;")
        bl   = QVBoxLayout(body)
        bl.setContentsMargins(10, 8, 10, 8); bl.setSpacing(4)
        bl.addStretch()

        scroll.setWidget(body)
        card.layout().addWidget(scroll)
        return body, bl

    def refresh(self):
        threading.Thread(target=self._fetch_all, daemon=True).start()

    def _fetch_all(self):
        try:
            r1 = db_saia.fetch_one(
                "SELECT COUNT(*) AS total FROM historial "
                "WHERE fecha_hora_salida IS NULL")
            dentro = r1["total"] if r1 else 0
            r2 = db_saia.fetch_one("SELECT COUNT(*) AS total FROM cuenta WHERE estado=1")
            activas = r2["total"] if r2 else 0
            stats = {
                "aprendices":      AprendizSaiaModel.count(),
                "guardas":         GuardaModel.count(),
                "ingresos_hoy":    HistorialModel.count_hoy(),
                "ingresos_mes":    HistorialModel.count_mes(),
                "cuentas_activas": activas,
                "dentro_sena":     dentro,
            }
        except Exception:
            stats = {k: "—" for k in ["aprendices","guardas","ingresos_hoy",
                                        "ingresos_mes","cuentas_activas","dentro_sena"]}
        self._sig.stats_ready.emit(stats)

        try:    rows_r = HistorialModel.get_recientes(10)
        except: rows_r = []
        self._sig.recent_ready.emit(rows_r)

        try:
            rows_g = db_saia.fetch_all("""
                SELECT p.nombres, p.p_ape, ps.turno, ps.empresa_seg, htg.inicio_turno
                FROM historial_turno_guarda htg
                JOIN personal_seguridad ps ON htg.id_guarda=ps.id_guarda
                JOIN persona p ON ps.num_doc=p.num_doc
                WHERE htg.estado='ACTIVO' ORDER BY htg.inicio_turno DESC
            """)
        except: rows_g = []
        self._sig.guardas_ready.emit(rows_g)

    def _update_stats(self, s: dict):
        for card, v in zip(self._cards, [s["aprendices"],s["guardas"],s["ingresos_hoy"]]):
            card.update_value(v)
        self._stat_mes.update_value(s["ingresos_mes"])
        self._stat_activos.update_value(s["cuentas_activas"])
        self._stat_dentro.update_value(s["dentro_sena"])

    def _clear_body(self, bl: QVBoxLayout):
        while bl.count() > 1:
            item = bl.takeAt(0)
            if item.widget(): item.widget().deleteLater()

    def _render_recent(self, rows: list):
        self._clear_body(self._recent_lay)
        if not rows:
            lbl = QLabel("Sin registros recientes"); lbl.setFont(font(11))
            lbl.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._recent_lay.insertWidget(0, lbl); return

        for r in rows:
            item = QFrame()
            item.setStyleSheet(f"QFrame{{background:{BG_INPUT};border-radius:8px;border:none;}}")
            rl = QHBoxLayout(item); rl.setContentsMargins(10,6,10,6); rl.setSpacing(8)

            estado = str(r.get("estado_movimiento") or "1").upper()
            es_ingreso = estado in ("1", "INGRESO")
            dot = QLabel("●"); dot.setFont(font(10, bold=True))
            dot.setStyleSheet(f"color:{'#42EDB5' if es_ingreso else WARNING}; background:transparent;")
            dot.setFixedWidth(14); rl.addWidget(dot)

            nombre = f"{r.get('nombres','') or ''} {r.get('p_ape','') or ''}".strip()
            n = QLabel(nombre or str(r.get("num_doc",""))); n.setFont(font(11))
            n.setStyleSheet(f"color:{TEXT_PRIMARY}; background:transparent;")
            rl.addWidget(n, stretch=1)

            fecha = str(r.get("fecha_hora_ingreso",""))[:16]
            f = QLabel(fecha); f.setFont(font(10))
            f.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
            rl.addWidget(f)
            self._recent_lay.insertWidget(self._recent_lay.count()-1, item)

    def _render_guardas(self, rows: list):
        self._clear_body(self._guardas_lay)
        if not rows:
            lbl = QLabel("Sin guardas en turno activo"); lbl.setFont(font(11))
            lbl.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._guardas_lay.insertWidget(0, lbl); return

        for r in rows:
            item = QFrame()
            item.setStyleSheet(f"QFrame{{background:{BG_INPUT};border-radius:8px;border:none;}}")
            rl = QHBoxLayout(item); rl.setContentsMargins(10,6,10,6); rl.setSpacing(8)

            ic = QLabel(); ic.setPixmap(svg_icon("shield", 14, PRIMARY))
            ic.setFixedSize(16,16); ic.setScaledContents(True)
            ic.setStyleSheet("background:transparent;"); rl.addWidget(ic)

            nombre = f"{r.get('nombres','') or ''} {r.get('p_ape','') or ''}".strip()
            info = QVBoxLayout(); info.setSpacing(0)
            n = QLabel(nombre); n.setFont(font(11, bold=True))
            n.setStyleSheet(f"color:{TEXT_PRIMARY}; background:transparent;"); info.addWidget(n)
            s = QLabel(f"{r.get('turno','') or ''}  •  {r.get('empresa_seg','') or ''}")
            s.setFont(font(10))
            s.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;"); info.addWidget(s)
            rl.addLayout(info, stretch=1)

            t = QLabel(str(r.get("inicio_turno",""))[:16]); t.setFont(font(10))
            t.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;"); rl.addWidget(t)
            self._guardas_lay.insertWidget(self._guardas_lay.count()-1, item)

    def closeEvent(self, event):
        self._timer.stop(); super().closeEvent(event)

    # MainWindow utiliza load_data para refrescar las vistas que tiene en caché.
    def load_data(self):
        self.refresh()
