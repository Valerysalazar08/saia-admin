"""
VISTA Qt — Usuarios bloqueados.
"""
import threading
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import QObject, pyqtSignal

from app.ui.theme import BG_APP, TEXT_MUTED, font
from app.ui.atoms.buttons  import TableActionButton, SecondaryButton
from app.ui.atoms.inputs   import SearchInput, Dropdown
from app.ui.atoms.labels   import Heading, Badge
from app.ui.molecules.data_table import DataTable
from app.ui.molecules.modal      import ConfirmModal
from app.models.persona_model       import CuentaModel
from app.config.database            import db_saia
from app.config.settings            import is_superadmin


class _Sig(QObject):
    done = pyqtSignal(list)


class BloqueoView(QWidget):
    def __init__(self, parent=None, session_user: dict = None):
        super().__init__(parent)
        self._session_user = session_user or {}
        self._is_superadmin = is_superadmin(self._session_user.get("num_doc"))
        self._all_data = []
        self.setStyleSheet(f"background:{BG_APP};")
        self._build()
        self.load_data()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 8)
        lay.setSpacing(0)

        tb = QWidget(); tb.setStyleSheet("background:transparent;")
        tbl = QHBoxLayout(tb); tbl.setContentsMargins(0,0,0,0)
        tbl.addWidget(Heading("Usuarios Bloqueados", level=2), stretch=1)
        ref = SecondaryButton("↺ Actualizar", width=120, height=34)
        ref.clicked.connect(self.load_data)
        tbl.addWidget(ref)
        lay.addWidget(tb)
        lay.addSpacing(12)

        fr = QWidget(); fr.setStyleSheet("background:transparent;")
        frl = QHBoxLayout(fr); frl.setContentsMargins(0,0,0,8); frl.setSpacing(12)
        self._search = SearchInput("Buscar nombre o documento...", width=280,
                                   on_change=self._filter)
        frl.addWidget(self._search)
        lbl = QLabel("Rol:"); lbl.setFont(font(11))
        lbl.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        frl.addWidget(lbl)
        roles = ["Todos", "Guarda", "Aprendiz"]
        if self._is_superadmin:
            roles.append("Administrador")
        self._rol_dd = Dropdown(roles, width=130,
                                command=lambda _: self._filter())
        frl.addWidget(self._rol_dd)
        frl.addStretch()
        lay.addWidget(fr)

        cols = [
            {"key":"num_doc", "header":"Documento", "width":120},
            {"key":"nombres", "header":"Nombre",    "width":160},
            {"key":"p_ape",   "header":"Apellido",  "width":140},
            {"key":"email",   "header":"Email",     "width":200},
            {"key":"rol",     "header":"Rol",       "width":90,
             "renderer":self._render_rol},
            {"key":"_acc",    "header":"Acciones",  "width":40,
             "renderer":self._render_acc},
        ]
        self._table = DataTable(columns=cols)
        lay.addWidget(self._table, stretch=1)
        lay.addSpacing(4)

        self._status = QLabel("")
        self._status.setFont(font(11))
        self._status.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        lay.addWidget(self._status)

    def _render_rol(self, parent, row, val):
        w = QWidget(parent); w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w); h.setContentsMargins(4,0,0,0)
        role = str(val).lower()
        preset = "guarda" if role == "guarda" else "admin" if role == "administrador" else "aprendiz"
        h.addWidget(Badge(preset=preset)); h.addStretch(); return w

    def _render_acc(self, parent, row, _val):
        w = QWidget(parent); w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w); h.setContentsMargins(2,0,2,0)
        b = TableActionButton("check-circle", "Habilitar cuenta", color="success")
        b.clicked.connect(lambda: self._habilitar(row))
        h.addWidget(b); h.addStretch(); return w

    def load_data(self, search: str = ""):
        sig = _Sig(self); sig.done.connect(self._on_data)
        def fetch():
            try:
                q = """SELECT p.num_doc, p.nombres, p.p_ape, p.email,
                              r.nom_rol AS rol, c.id_cuenta
                       FROM persona p JOIN cuenta c ON p.num_doc=c.num_doc
                       JOIN rol r ON c.id_rol=r.id_rol
                       WHERE c.estado=0"""
                if not self._is_superadmin:
                    q += " AND c.id_rol <> 2"
                q += " ORDER BY p.nombres"
                rows = db_saia.fetch_all(q)
                for row in rows:
                    n = str(row.get("rol","")).lower()
                    if n == "guarda":
                        row["rol"] = "Guarda"
                    elif n == "administrador":
                        row["rol"] = "Administrador"
                    else:
                        row["rol"] = "Aprendiz"
            except Exception: rows = []
            sig.done.emit(rows)
        threading.Thread(target=fetch, daemon=True).start()

    def _on_data(self, data):
        self._all_data = data
        self._filter()

    def _filter(self, search: str = None):
        s   = search if search is not None else self._search.get()
        rol = self._rol_dd.get()
        out = []
        for row in self._all_data:
            nombre = f"{row.get('nombres','')} {row.get('p_ape','')}".lower()
            doc    = str(row.get("num_doc",""))
            if s and s.lower() not in nombre and s not in doc: continue
            if rol != "Todos" and row.get("rol") != rol: continue
            out.append(row)
        self._table.load(out)
        self._status.setText(f"{len(out)} usuario(s) bloqueado(s)")

    def _habilitar(self, row: dict):
        if row.get("rol") == "Administrador" and not self._is_superadmin:
            self._status.setText("No tienes permiso para habilitar administradores.")
            return
        nombre = f"{row.get('nombres','')} {row.get('p_ape','')}".strip()
        dlg = ConfirmModal(self, "Habilitar cuenta",
            f"¿Habilitar la cuenta de {nombre}?", confirm_text="Habilitar")
        if dlg.confirmed:
            try:
                CuentaModel.toggle_estado(row["id_cuenta"], 1)
                try:
                    from app.models.auditoria_model import AuditoriaModel, ACCION_HABILITAR, ENTIDAD_GUARDA, ENTIDAD_APRENDIZ
                    entidad = ENTIDAD_GUARDA if row.get("rol")=="Guarda" else ENTIDAD_APRENDIZ
                    AuditoriaModel.registrar(ACCION_HABILITAR, entidad, row["num_doc"],
                        f"Cuenta habilitada: {nombre}",
                        realizado_por=self._session_user.get("num_doc") if self._session_user else None)
                except Exception: pass
                self.load_data()
                self._refresh_cached_view("guardas")
                self._refresh_cached_view("aprendices")
            except Exception as e:
                self._status.setText(f"Error: {e}")

    def _refresh_cached_view(self, view_id: str):
        parent = self.parentWidget()
        while parent:
            refresh = getattr(parent, "refresh_view", None)
            if callable(refresh):
                refresh(view_id)
                return
            parent = parent.parentWidget()
