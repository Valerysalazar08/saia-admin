"""
VISTA Qt — CRUD de insumos y equipos.
"""
import threading
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import QObject, pyqtSignal

from app.ui.theme import BG_APP, TEXT_MUTED, font
from app.ui.atoms.buttons  import PrimaryButton, SmallButton
from app.ui.atoms.inputs   import SearchInput, LabeledInput, Dropdown
from app.ui.atoms.labels   import Heading, Badge
from app.ui.molecules.data_table import DataTable
from app.ui.molecules.modal      import BaseModal, ConfirmModal
from app.models.historial_model     import InsumoModel
from app.models.persona_model       import PersonaModel
import mysql.connector


class _Sig(QObject):
    done = pyqtSignal(list)


class InsumosView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{BG_APP};")
        self._build()
        self.load_data()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 8); lay.setSpacing(0)

        tb = QWidget(); tb.setStyleSheet("background:transparent;")
        tbl = QHBoxLayout(tb); tbl.setContentsMargins(0,0,0,0)
        tbl.addWidget(Heading("Insumos y Equipos", level=2), stretch=1)
        btn = PrimaryButton("+ Nuevo insumo", width=150, height=36)
        btn.clicked.connect(self._open_create)
        tbl.addWidget(btn)
        lay.addWidget(tb); lay.addSpacing(12)

        self._search = SearchInput("Buscar por nombre, serie o marca...", width=320,
                                   on_change=self._on_search)
        lay.addWidget(self._search); lay.addSpacing(8)

        cols = [
            {"key":"nom_insumo",     "header":"Nombre",      "width":180},
            {"key":"marca",          "header":"Marca",       "width":120},
            {"key":"num_serie",      "header":"N° Serie",    "width":140},
            {"key":"nombres",        "header":"Propietario", "width":160},
            {"key":"fecha_registro", "header":"Registro",    "width":130},
            {"key":"estado",         "header":"Estado",      "width":80,
             "renderer":self._render_estado},
            {"key":"_acc",           "header":"Acciones",    "width":170,
             "renderer":self._render_acc},
        ]
        self._table = DataTable(columns=cols)
        lay.addWidget(self._table, stretch=1); lay.addSpacing(4)

        self._status = QLabel("")
        self._status.setFont(font(11))
        self._status.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        lay.addWidget(self._status)

    def _render_estado(self, parent, row, val):
        w = QWidget(parent); w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w); h.setContentsMargins(4,0,0,0)
        h.addWidget(Badge(preset="activo" if val==1 else "inactivo"))
        h.addStretch(); return w

    def _render_acc(self, parent, row, _val):
        w = QWidget(parent); w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w); h.setContentsMargins(4,0,4,0); h.setSpacing(4)
        e = SmallButton("✏ Editar", color="primary")
        e.clicked.connect(lambda: self._open_edit(row))
        d = SmallButton("🗑 Eliminar", color="danger")
        d.clicked.connect(lambda: self._delete(row))
        h.addWidget(e); h.addWidget(d); h.addStretch(); return w

    def load_data(self, search: str = ""):
        sig = _Sig(self); sig.done.connect(lambda d: (self._table.load(d),
            self._status.setText(f"{len(d)} insumo(s)")))
        def fetch():
            try: data = InsumoModel.get_all(search)
            except Exception: data = []
            sig.done.emit(data)
        threading.Thread(target=fetch, daemon=True).start()

    def _on_search(self, text): self.load_data(text)
    def _open_create(self):     InsumoFormModal(self, on_save=self.load_data)
    def _open_edit(self, row):  InsumoFormModal(self, on_save=self.load_data, insumo_data=row)

    def _delete(self, row):
        dlg = ConfirmModal(self, "Eliminar insumo",
            f"¿Eliminar '{row.get('nom_insumo')}'?",
            confirm_text="Eliminar", danger=True)
        if dlg.confirmed:
            try:
                InsumoModel.delete(row["id_insumo"])
                self.load_data()
            except Exception as e:
                self._status.setText(f"Error: {e}")


class InsumoFormModal(BaseModal):
    def __init__(self, parent, on_save=None, insumo_data: dict = None):
        title = "Editar insumo" if insumo_data else "Nuevo insumo"
        super().__init__(parent, title, width=500, height=500)
        self._on_save = on_save
        self._data    = insumo_data
        self._is_edit = insumo_data is not None
        self._build_form()
        if self._is_edit: self._fill()
        self.add_footer_buttons(confirm_text="Guardar", confirm_cmd=self._save)

    def _build_form(self):
        c   = self.content
        lay = c.layout()

        def ins(w): lay.insertWidget(lay.count()-1, w)

        r1 = QWidget(); r1.setStyleSheet("background:transparent;")
        rh = QHBoxLayout(r1); rh.setContentsMargins(0,0,0,0); rh.setSpacing(8)
        self._nombre = LabeledInput("Nombre del insumo", required=True, width=200)
        self._marca  = LabeledInput("Marca", width=200)
        rh.addWidget(self._nombre); rh.addWidget(self._marca)
        ins(r1)

        self._serie   = LabeledInput("Número de serie", width=320); ins(self._serie)
        self._desc    = LabeledInput("Descripción", width=320);     ins(self._desc)
        self._num_doc = LabeledInput("N° documento del propietario", required=True, width=320)
        ins(self._num_doc)

        ef = QWidget(); ef.setStyleSheet("background:transparent;")
        el = QVBoxLayout(ef); el.setContentsMargins(0,0,0,0); el.setSpacing(4)
        lbl = QLabel("Estado"); lbl.setFont(__import__('app.ui.theme', fromlist=['font']).font(11, bold=True))
        from app.ui.theme import TEXT_SECONDARY
        lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; background:transparent;")
        el.addWidget(lbl)
        self._estado_dd = Dropdown(["Activo","Inactivo"], width=200)
        el.addWidget(self._estado_dd)
        ins(ef)

    def _fill(self):
        d = self._data
        self._nombre.set(d.get("nom_insumo",""))
        self._marca.set(d.get("marca",""))
        self._serie.set(d.get("num_serie",""))
        self._desc.set(d.get("desc_insumo",""))
        self._num_doc.set(d.get("num_doc",""))
        self._estado_dd.set("Activo" if d.get("estado",1)==1 else "Inactivo")

    def _save(self):
        nombre  = self._nombre.get().strip()
        nd_str  = self._num_doc.get().strip()
        if not nombre:
            self.show_error("El nombre del insumo es obligatorio."); return
        if not nd_str:
            self.show_error("El N° de documento del propietario es obligatorio."); return
        try:   num_doc = int(nd_str)
        except ValueError:
            self.show_error("El número de documento debe ser numérico."); return
        if not PersonaModel.exists(num_doc):
            self.show_error("No existe ninguna persona con ese número de documento."); return

        data = {"nom_insumo": nombre, "marca": self._marca.get().strip() or None,
                "num_serie": self._serie.get().strip() or None,
                "desc_insumo": self._desc.get().strip() or None,
                "estado": 1 if self._estado_dd.get()=="Activo" else 0, "num_doc": num_doc}
        try:
            if self._is_edit: InsumoModel.update(self._data["id_insumo"], data)
            else:             InsumoModel.create(data)
        except mysql.connector.Error as e:
            self.show_error(f"Error BD: {e.msg}"); return
        except Exception as e:
            self.show_error(str(e)); return
        if self._on_save: self._on_save()
        self.accept()
