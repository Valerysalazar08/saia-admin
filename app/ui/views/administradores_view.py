"""Vista de cuentas administradoras; solo accesible al superadministrador."""
import re
import threading
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QObject, pyqtSignal

from app.config.settings import is_superadmin
from app.models.administrador_model import AdministradorModel
from app.models.persona_model import PersonaModel, CuentaModel
from app.ui.theme import BG_APP, TEXT_MUTED, ERROR, font
from app.ui.atoms.buttons import SecondaryButton, TableActionButton
from app.ui.atoms.inputs import SearchInput, LabeledInput, Dropdown
from app.ui.atoms.labels import Heading, Badge
from app.ui.molecules.data_table import DataTable
from app.ui.molecules.modal import BaseModal, ConfirmModal


class _Sig(QObject):
    done = pyqtSignal(list)


class AdministradoresView(QWidget):
    def __init__(self, parent=None, session_user=None):
        super().__init__(parent)
        self._session_user = session_user or {}
        self._allowed = is_superadmin(self._session_user.get("num_doc"))
        self.setStyleSheet(f"background:{BG_APP};")
        self._build()
        self.load_data()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(24, 20, 24, 8); lay.setSpacing(0)
        bar = QWidget(); row = QHBoxLayout(bar); row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(Heading("Administradores", level=2), stretch=1)
        add = SecondaryButton("＋ Nuevo administrador", width=190, height=34)
        add.clicked.connect(self._open_create); row.addWidget(add); lay.addWidget(bar)
        lay.addSpacing(4)
        hint = QLabel("Solo el superadministrador puede crear o desactivar cuentas administradoras.")
        hint.setFont(font(10)); hint.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        lay.addWidget(hint); lay.addSpacing(12)
        self._search = SearchInput("Buscar por nombre o documento...", width=320, on_change=self.load_data)
        lay.addWidget(self._search); lay.addSpacing(8)
        cols = [
            {"key":"num_doc", "header":"Documento", "width":120},
            {"key":"nombres", "header":"Nombres", "width":165},
            {"key":"p_ape", "header":"Apellidos", "width":165},
            {"key":"email", "header":"Email", "width":220},
            {"key":"estado", "header":"Estado", "width":90, "renderer":self._estado},
            {"key":"_acc", "header":"Acciones", "width":88, "renderer":self._acciones},
        ]
        self._table = DataTable(columns=cols, row_height=44); lay.addWidget(self._table, stretch=1)
        self._status = QLabel(""); self._status.setFont(font(11)); self._status.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        lay.addWidget(self._status)

    def _estado(self, parent, _row, _value): return Badge(preset="activo", parent=parent)

    def _acciones(self, parent, row, _value):
        w = QWidget(parent); h = QHBoxLayout(w); h.setContentsMargins(2, 0, 2, 0); h.setSpacing(6)
        edit = TableActionButton("pencil", "Editar administrador", color="primary")
        edit.clicked.connect(lambda: self._open_edit(row)); h.addWidget(edit)
        if row.get("num_doc") != self._session_user.get("num_doc"):
            block = TableActionButton("ban", "Desactivar administrador", color="danger")
            block.clicked.connect(lambda: self._deactivate(row)); h.addWidget(block)
        h.addStretch(); return w

    def load_data(self, search=""):
        if not self._allowed: return
        text = search if isinstance(search, str) else self._search.get()
        signal = _Sig(self); signal.done.connect(self._on_data)
        def fetch():
            try: data = AdministradorModel.get_all(text)
            except Exception: data = []
            signal.done.emit(data)
        threading.Thread(target=fetch, daemon=True).start()

    def _on_data(self, data):
        self._table.load(data); self._status.setText(f"{len(data)} administrador(es) activo(s)")

    def _open_create(self): AdminFormModal(self, on_save=self.load_data)
    def _open_edit(self, row): AdminFormModal(self, admin=row, on_save=self.load_data)

    def _deactivate(self, row):
        name = f"{row.get('nombres','')} {row.get('p_ape','')}".strip()
        dlg = ConfirmModal(self, "Desactivar administrador", f"¿Desactivar la cuenta de {name}?\n\nNo podrá ingresar al panel hasta que sea habilitada nuevamente.", confirm_text="Desactivar", danger=True)
        if dlg.confirmed:
            try:
                CuentaModel.toggle_estado(row["id_cuenta"], 0); self.load_data()
            except Exception as exc: self._status.setText(f"Error: {exc}")


class AdminFormModal(BaseModal):
 
    TIPOS_DOCUMENTO = ["Cédula de Ciudadanía", "Cédula de Extranjería", "Pasaporte"]

    def __init__(self, parent, admin=None, on_save=None):
        self._admin, self._on_save = admin, on_save
        self._editing = admin is not None
        super().__init__(parent, "Editar administrador" if admin else "Nuevo administrador", width=540, height=540)
        lay = self.content.layout()
        def add(widget): lay.insertWidget(lay.count() - 1, widget)
        self._doc = LabeledInput("N° Documento", required=True, width=230)
        self._tip_doc = Dropdown(self.TIPOS_DOCUMENTO, width=230)
        self._names = LabeledInput("Nombres", required=True, width=230)
        self._last = LabeledInput("Apellidos", required=True, width=230)
        self._email = LabeledInput("Email", required=True, width=230)
        self._tel = LabeledInput("Teléfono", required=True, width=230)
        type_doc = QWidget()
        type_doc.setStyleSheet("background:transparent;")
        type_doc_lay = QVBoxLayout(type_doc)
        type_doc_lay.setContentsMargins(0, 0, 0, 0)
        type_doc_lay.setSpacing(4)
        type_doc_label = QLabel("Tipo de documento *")
        type_doc_label.setFont(font(11, bold=True))
        type_doc_lay.addWidget(type_doc_label)
        type_doc_lay.addWidget(self._tip_doc)
        # LabeledInput reserva una línea para mensajes de validación; esta
        # separación mantiene alineadas ambas columnas de la fila.
        type_doc_lay.addSpacing(14)

        for left, right in [
            (self._doc, type_doc),
            (self._names, self._last),
            (self._email, self._tel),
        ]:
            row = QWidget(); rlay = QHBoxLayout(row); rlay.setContentsMargins(0, 0, 0, 0); rlay.setSpacing(12)
            rlay.addWidget(left)
            if right: rlay.addWidget(right)
            else: rlay.addStretch()
            add(row)
        if not self._editing:
            self._password = LabeledInput("Contraseña inicial", required=True, password=True, width=230); add(self._password)
        else:
            self._password = None; self._doc.set(self._admin["num_doc"]); self._doc.entry.setReadOnly(True)
            saved_type = self._admin.get("tip_doc", "")
            if saved_type in self.TIPOS_DOCUMENTO:
                self._tip_doc.set(saved_type)
            self._names.set(self._admin.get("nombres")); self._last.set(self._admin.get("p_ape")); self._email.set(self._admin.get("email")); self._tel.set(self._admin.get("tel"))
        self.add_footer_buttons(confirm_text="Guardar", confirm_cmd=self._save)
        self.show()

    def _save(self):
        doc, names, last = self._doc.get().strip(), self._names.get().strip(), self._last.get().strip()
        email, tel = self._email.get().strip(), self._tel.get().strip()
        if not re.fullmatch(r"[1-9]\d{5,11}", doc) or not names or not last or not email or not tel:
            self.show_error("Completa los campos obligatorios correctamente."); return
        name_pattern = r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ]+(?: [a-zA-ZáéíóúÁÉÍÓÚüÜñÑ]+)*$"
        if not re.fullmatch(name_pattern, names) or not re.fullmatch(name_pattern, last):
            self.show_error("Nombres y apellidos solo pueden contener letras y espacios."); return
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email): self.show_error("Email inválido."); return
        if not re.fullmatch(r"\d{7,15}", tel):
            self.show_error("El teléfono debe tener entre 7 y 15 dígitos."); return
        if self._tip_doc.get() not in self.TIPOS_DOCUMENTO:
            self.show_error("Selecciona un tipo de documento válido."); return
        if not self._editing:
            password = self._password.get()
            if (len(password) < 6 or not re.search(r"[A-Z]", password)
                    or not re.search(r"[a-z]", password) or not re.search(r"\d", password)
                    or not re.search(r"[^A-Za-z0-9]", password)):
                self.show_error("La contraseña requiere 6+ caracteres, mayúscula, minúscula, número y símbolo."); return
        person = {"num_doc":int(doc), "tip_doc":self._tip_doc.get(), "nombres":names, "p_ape":last, "email":email, "tel":tel, "sexo":None, "tip_sang":None, "fecha_nac":None}
        try:
            if self._editing: AdministradorModel.update(self._admin["num_doc"], person)
            else:
                if PersonaModel.exists(int(doc)): self.show_error("Ya existe una persona con ese documento."); return
                AdministradorModel.create(person, self._password.get())
        except Exception as exc: self.show_error(f"No se pudo guardar: {exc}"); return
        if self._on_save: self._on_save()
        self.accept()
