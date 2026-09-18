"""
VISTA Qt — Historial de ingresos con filtros de fecha.
"""
import threading
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QHBoxLayout, QVBoxLayout,
)
from PyQt6.QtCore import QObject, pyqtSignal

from app.ui.theme import (
    BG_APP, BG_CARD, BORDER, PRIMARY, TEXT_PRIMARY, TEXT_MUTED, CARD_RADIUS, font,
)
from app.ui.atoms.buttons  import SecondaryButton, PrimaryButton
from app.ui.atoms.inputs   import SearchInput, TextInput
from app.ui.atoms.labels   import Heading, Badge
from app.ui.molecules.data_table import DataTable
from app.models.historial_model     import HistorialModel


class _Sig(QObject):
    done = pyqtSignal(list)


class HistorialView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{BG_APP};")
        self._build()
        self.load_data()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 8)
        lay.setSpacing(0)

        # Toolbar
        tb = QWidget(); tb.setStyleSheet("background:transparent;")
        tbl = QHBoxLayout(tb); tbl.setContentsMargins(0,0,0,0)
        tbl.addWidget(Heading("Historial de Ingresos", level=2), stretch=1)
        ref = SecondaryButton("↺ Actualizar", width=120, height=34)
        ref.clicked.connect(self.load_data)
        tbl.addWidget(ref)
        lay.addWidget(tb)
        lay.addSpacing(12)

        # Filtros
        filt = QFrame()
        filt.setObjectName("HistoryFilters")
        filt.setStyleSheet(f"""
            QFrame#HistoryFilters {{background:{BG_CARD}; border-radius:{CARD_RADIUS}px;
                                   border:1px solid {BORDER};}}
        """)
        fl = QHBoxLayout(filt); fl.setContentsMargins(12, 8, 12, 8); fl.setSpacing(8)

        lbl_f = QLabel("Filtros"); lbl_f.setFont(font(11, bold=True))
        lbl_f.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        fl.addWidget(lbl_f)

        self._search = SearchInput("Buscar nombre o documento...", width=240,
                                   on_change=self._on_search)
        fl.addWidget(self._search)

        fl.addWidget(self._lbl("Desde:"))
        self._fecha_ini = TextInput("YYYY-MM-DD", width=115, height=36)
        fl.addWidget(self._fecha_ini)

        fl.addWidget(self._lbl("Hasta:"))
        self._fecha_fin = TextInput("YYYY-MM-DD", width=115, height=36)
        fl.addWidget(self._fecha_fin)

        btn_f = PrimaryButton("Filtrar", width=80, height=36)
        btn_f.clicked.connect(self.load_data)
        fl.addWidget(btn_f)
        fl.addStretch()
        lay.addWidget(filt)
        lay.addSpacing(8)

        # Tabla
        cols = [
            {"key":"fecha_hora_ingreso", "header":"Ingreso",   "width":145},
            {"key":"fecha_hora_salida",  "header":"Salida",    "width":145},
            {"key":"nombres",            "header":"Nombre",    "width":160},
            {"key":"p_ape",              "header":"Apellido",  "width":130},
            {"key":"num_doc",            "header":"Documento", "width":120},
            {"key":"porteria_mostrada",  "header":"Portería",  "width":100},
            {"key":"estado_movimiento",  "header":"Estado",    "width":90,
             "renderer": self._render_estado},
            {"key":"guarda_nombres",     "header":"Guarda",    "width":170,
             "renderer": self._render_guarda},
        ]
        self._table = DataTable(columns=cols)
        lay.addWidget(self._table, stretch=1)
        lay.addSpacing(4)

        self._status = QLabel("")
        self._status.setFont(font(11))
        self._status.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        lay.addWidget(self._status)

    def _lbl(self, text):
        l = QLabel(text); l.setFont(font(11))
        l.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;"); return l

    def _render_estado(self, parent, row, val):
        w = QWidget(parent); w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w); h.setContentsMargins(4,0,0,0)
        estado = str(val or "1").upper()
        h.addWidget(Badge(preset="ingreso" if estado in ("1", "INGRESO") else "salida"))
        h.addStretch(); return w

    def _render_guarda(self, parent, row, _val):
        """Muestra el nombre completo del guarda responsable del movimiento."""
        w = QLabel(parent)
        nombre = " ".join(filter(None, [
            str(row.get("guarda_nombres") or "").strip(),
            str(row.get("guarda_ape") or "").strip(),
        ])) or "—"
        w.setText(nombre)
        w.setFont(font(12))
        w.setStyleSheet(f"color:{TEXT_PRIMARY}; background:transparent;")
        return w

    def load_data(self, search: str = None):
        s  = search if search is not None else self._search.get()
        fi = self._fecha_ini.get().strip() or None
        ff = self._fecha_fin.get().strip() or None
        sig = _Sig(self); sig.done.connect(self._on_data)
        def fetch():
            try: data = HistorialModel.get_all(search=s, fecha_inicio=fi, fecha_fin=ff)
            except Exception: data = []
            sig.done.emit(data)
        threading.Thread(target=fetch, daemon=True).start()

    def _on_data(self, data):
        self._table.load(data)
        self._status.setText(f"{len(data)} registro(s) encontrado(s)")

    def _on_search(self, text): self.load_data(text)
