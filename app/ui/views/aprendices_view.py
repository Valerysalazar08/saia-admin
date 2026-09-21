"""VISTA Qt — Gestión de aprendices registrados en SAIA y SENA."""
import logging
import threading
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QScrollArea, QSizePolicy,
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal

from app.ui.theme import (
    BG_APP, BG_CARD, BG_INPUT, BORDER, PRIMARY, SECONDARY,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ERROR, WARNING,
    SUCCESS_BG, SUCCESS_TEXT, INFO_BG, INFO,
    CARD_RADIUS, font, svg_icon,
)
from app.ui.atoms.buttons import PrimaryButton, SecondaryButton, TableActionButton
from app.ui.atoms.inputs  import SearchInput, Dropdown
from app.ui.atoms.labels  import Heading, Badge, Divider
from app.ui.molecules.data_table import DataTable
from app.ui.molecules.modal      import BaseModal, ConfirmModal
from app.models.aprendiz_model      import AprendizSaiaModel, AprendizSenaModel
from app.models.persona_model       import PersonaModel, CuentaModel
from app.models.historial_model     import HistorialModel


class _Sig(QObject):
    done = pyqtSignal(list)


class AprendicesView(QWidget):
    def __init__(self, parent=None, session_user: dict = None):
        super().__init__(parent)
        self._session_user = session_user or {}
        self._tab = "saia"
        self.setStyleSheet(f"background:{BG_APP};")
        self._build()
        logging.getLogger("saia.aprendices").info("Vista Aprendices creada")

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 8)
        lay.setSpacing(0)

        # Toolbar
        toolbar = QWidget(); toolbar.setStyleSheet("background:transparent;")
        tb = QHBoxLayout(toolbar); tb.setContentsMargins(0,0,0,0)
        tb.addWidget(Heading("Personas", level=2), stretch=1)
        refresh = SecondaryButton("↺ Actualizar", width=120, height=34)
        refresh.clicked.connect(self.load_data)
        tb.addWidget(refresh)
        lay.addWidget(toolbar)

        # Búsqueda
        self._search = SearchInput(
            "Buscar por nombre o documento...", width=320,
            on_change=self._on_search)
        filtro_row = QWidget(); filtro_row.setStyleSheet("background:transparent;")
        fr = QHBoxLayout(filtro_row); fr.setContentsMargins(0,0,0,0); fr.setSpacing(10)
        fr.addWidget(self._search)
        self._filtro_formacion = Dropdown(
            ["Todas", "Con formación", "Sin formación"], width=190,
            command=self._on_filtro_formacion)
        fr.addWidget(self._filtro_formacion)
        fr.addStretch()
        lay.addSpacing(12)
        lay.addWidget(filtro_row)

        # Tabs
        tab_row = QWidget(); tab_row.setStyleSheet("background:transparent;")
        tr = QHBoxLayout(tab_row); tr.setContentsMargins(0,8,0,4); tr.setSpacing(0)
        self._tab_saia = self._mk_tab("Personas registradas en SAIA", "saia")
        self._tab_sena = self._mk_tab("Personas en formación SENA", "sena")
        tr.addWidget(self._tab_saia); tr.addWidget(self._tab_sena); tr.addStretch()
        lay.addWidget(tab_row)

        # Columnas por tab
        self._cols_saia = [
            {"key":"num_doc",       "header":"Documento",  "width":120},
            {"key":"nombres",       "header":"Nombre",     "width":160},
            {"key":"p_ape",         "header":"Apellido",   "width":140},
            {"key":"email",         "header":"Email",      "width":200},
            # El ancho reserva separación visual entre la etiqueta QR y las
            # acciones de la siguiente columna.
            {"key":"cuenta_estado", "header":"Cuenta",     "width":100,
             "renderer":self._render_qr},
            {"key":"_acc",          "header":"Acciones",   "width":88,
             "renderer":self._render_acc},
        ]
        self._cols_sena = [
            {"key":"num_doc",          "header":"Documento", "width":120},
            {"key":"nombre_programa",  "header":"Programa",  "width":240},
            {"key":"carrera",          "header":"Tipo",      "width":90},
            {"key":"nombre_centro",    "header":"Centro",    "width":160},
            {"key":"fecha_inicio",     "header":"Inicio",    "width":110},
            {"key":"estado",           "header":"Estado",    "width":80,
             "renderer":self._render_estado_sena},
        ]
        self._table = DataTable(columns=self._cols_saia)
        lay.addWidget(self._table, stretch=1)
        lay.addSpacing(4)

        self._status = QLabel("")
        self._status.setFont(font(11))
        self._status.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        lay.addWidget(self._status)

        # _set_tab carga los datos iniciales; no duplicar la consulta desde
        # __init__, porque al abrir por primera vez se iniciaban dos hilos.
        self._set_tab("saia")

    def _mk_tab(self, text: str, tab_id: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(34)
        btn.setFont(font(12))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setCheckable(True)
        btn.setStyleSheet(f"""
            QPushButton {{
                background:transparent; border:none; border-bottom:2px solid transparent;
                color:{TEXT_MUTED}; padding:0 16px;
            }}
            QPushButton:checked {{
                color:{PRIMARY}; border-bottom:2px solid {PRIMARY};
                font-weight:bold;
            }}
        """)
        btn.clicked.connect(lambda: self._set_tab(tab_id))
        return btn

    def _set_tab(self, tab_id: str):
        self._tab = tab_id
        self._tab_saia.setChecked(tab_id == "saia")
        self._tab_sena.setChecked(tab_id == "sena")
        if tab_id == "saia":
            self._table._columns = self._cols_saia
            self._filtro_formacion.show()
        else:
            self._table._columns = self._cols_sena
            self._filtro_formacion.hide()
        self._table._build_header()
        self._search.clear()
        logging.getLogger("saia.aprendices").info("Pestaña seleccionada: %s", tab_id)
        self.load_data()

    # ── Renderers ─────────────────────────────────────────────────────────────
    def _render_qr(self, parent, row, val):
        w = QWidget(parent); w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w); h.setContentsMargins(4,0,0,0)
        h.addWidget(Badge(preset="activo" if val == 1 else "inactivo"))
        h.addStretch(); return w

    def _render_estado_sena(self, parent, row, val):
        w = QWidget(parent); w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w); h.setContentsMargins(4,0,0,0)
        h.addWidget(Badge(preset="activo" if val==1 else "inactivo"))
        h.addStretch(); return w

    def _render_acc(self, parent, row, _val):
        w = QWidget(parent); w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w); h.setContentsMargins(2,0,2,0); h.setSpacing(6)
        estado = row.get("cuenta_estado", 0)
        if estado == 1:
            b = TableActionButton("lock", "Bloquear cuenta", color="warning")
            b.clicked.connect(lambda: self._bloquear(row))
        else:
            b = TableActionButton("check-circle", "Activar cuenta", color="success")
            b.clicked.connect(lambda: self._desbloquear(row))
        h.addWidget(b)
        ver = TableActionButton("eye", "Ver detalle", color="ghost")
        ver.clicked.connect(lambda: self._ver(row))
        h.addWidget(ver); h.addStretch(); return w

    # ── Datos ─────────────────────────────────────────────────────────────────
    def load_data(self, search: str = None):
        search = self._search.get() if search is None else search
        sig = _Sig(self)
        sig.done.connect(self._on_data)
        tab = self._tab
        filtro_formacion = self._filtro_formacion.get()
        logging.getLogger("saia.aprendices").info(
            "Iniciando carga: pestaña=%s, búsqueda=%r", tab, search)
        def fetch():
            try:
                if tab == "saia":
                    data = AprendizSaiaModel.get_all(search, filtro_formacion)
                else:
                    data = AprendizSenaModel.get_all(search)
                logging.getLogger("saia.aprendices").info(
                    "Carga completada: pestaña=%s, registros=%d", tab, len(data))
            except Exception:
                logging.getLogger("saia.aprendices").exception(
                    "Falló la carga de aprendices: pestaña=%s, búsqueda=%r", tab, search)
                data = []
            sig.done.emit(data)
        threading.Thread(target=fetch, daemon=True).start()

    def _on_data(self, data: list):
        self._table.load(data)
        etiqueta = "persona(s)" if self._tab == "saia" else "persona(s) en formación"
        self._status.setText(f"{len(data)} {etiqueta} encontrada(s)")

    def _on_search(self, text: str):
        self.load_data(text)

    def _on_filtro_formacion(self, _filtro: str):
        if self._tab == "saia":
            self.load_data()

    # ── Acciones ──────────────────────────────────────────────────────────────
    def _bloquear(self, row: dict):
        nombre = f"{row.get('nombres','')} {row.get('p_ape','')}".strip()
        try:
            if HistorialModel.esta_dentro(row["num_doc"]):
                ConfirmModal(
                    self, "No se puede bloquear",
                    "No se puede bloquear a este aprendiz ya que se encuentra dentro de la institución.",
                    confirm_text="Entendido", cancel_text=None,
                )
                return
        except Exception as e:
            self._status.setText(f"Error verificando el ingreso: {e}")
            return
        dlg = ConfirmModal(self, "Bloquear cuenta",
            f"¿Bloquear la cuenta de {nombre}?\nNo podrá iniciar sesión ni usar el QR.",
            confirm_text="Bloquear", danger=True)
        if dlg.confirmed:
            try:
                CuentaModel.toggle_estado(row["id_cuenta"], 0)
                try:
                    from app.models.auditoria_model import AuditoriaModel, ACCION_BLOQUEAR, ENTIDAD_APRENDIZ
                    AuditoriaModel.registrar(ACCION_BLOQUEAR, ENTIDAD_APRENDIZ, row["num_doc"],
                        f"Cuenta bloqueada: {nombre}", realizado_por=self._session_user.get("num_doc"))
                except Exception: pass
                self.load_data()
                self._refresh_cached_view("bloqueo")
            except Exception as e:
                self._status.setText(f"Error: {e}")

    def _desbloquear(self, row: dict):
        nombre = f"{row.get('nombres','')} {row.get('p_ape','')}".strip()
        dlg = ConfirmModal(self, "Desbloquear cuenta",
            f"¿Desbloquear la cuenta de {nombre}?", confirm_text="Desbloquear")
        if dlg.confirmed:
            try:
                CuentaModel.toggle_estado(row["id_cuenta"], 1)
                try:
                    from app.models.auditoria_model import AuditoriaModel, ACCION_HABILITAR, ENTIDAD_APRENDIZ
                    AuditoriaModel.registrar(ACCION_HABILITAR, ENTIDAD_APRENDIZ, row["num_doc"],
                        f"Cuenta habilitada: {nombre}", realizado_por=self._session_user.get("num_doc"))
                except Exception: pass
                self.load_data()
                self._refresh_cached_view("bloqueo")
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

    def _ver(self, row: dict):
        # Crear el diálogo no lo muestra por sí solo. ``exec`` lo abre de
        # forma modal y mantiene la instancia viva hasta que se cierre.
        dlg = AprendizDetalleModal(self, row)
        dlg.exec()


class AprendizDetalleModal(BaseModal):
    def __init__(self, parent, data: dict):
        nombre = f"{data.get('nombres','')} {data.get('p_ape','')}".strip()
        super().__init__(parent, f"Detalle — {nombre}", width=520, height=580)
        c = self.content
        c_lay = c.layout()
        num_doc = data.get("num_doc")

        def fila(label, value):
            row = QFrame()
            row.setStyleSheet(f"QFrame{{background:{BG_INPUT};border-radius:6px;border:none;}}")
            rh = QHBoxLayout(row); rh.setContentsMargins(10,6,10,6)
            l = QLabel(label); l.setFont(font(11,bold=True))
            l.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;"); l.setFixedWidth(140)
            rh.addWidget(l)
            v = QLabel(str(value) if value else "—"); v.setFont(font(11))
            v.setStyleSheet(f"color:{TEXT_PRIMARY}; background:transparent;")
            rh.addWidget(v, stretch=1)
            c_lay.insertWidget(c_lay.count()-1, row)

        sec = QLabel("Datos personales"); sec.setFont(font(12,bold=True))
        sec.setStyleSheet(f"color:{PRIMARY}; background:transparent;")
        c_lay.insertWidget(c_lay.count()-1, sec)
        fila("N° Documento", num_doc); fila("Nombre", nombre)
        fila("Email", data.get("email")); fila("Teléfono", data.get("tel"))
        fila("Estado cuenta", "Activa" if data.get("cuenta_estado")==1 else "Bloqueada")

        try:
            sena = AprendizSenaModel.get_by_doc(num_doc)
        except Exception:
            sena = None

        if sena:
            sec2 = QLabel("Datos SENA"); sec2.setFont(font(12,bold=True))
            sec2.setStyleSheet(f"color:{SECONDARY}; background:transparent;")
            c_lay.insertWidget(c_lay.count()-1, sec2)
            fila("Programa", sena.get("nombre_programa")); fila("Tipo", sena.get("carrera"))
            fila("Centro", sena.get("nombre_centro")); fila("Inicio", sena.get("fecha_inicio"))
        else:
            warn = QLabel("⚠ No encontrado en BD SENA"); warn.setFont(font(11))
            warn.setStyleSheet(f"color:{WARNING}; background:{BG_APP}; border-radius:6px; padding:6px;")
            c_lay.insertWidget(c_lay.count()-1, warn)

        self.add_footer_buttons(confirm_text="Cerrar", confirm_cmd=self.accept)
