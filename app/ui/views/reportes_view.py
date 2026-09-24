import threading
from PyQt6.QtWidgets import QWidget, QLabel, QTextEdit, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QObject, pyqtSignal

from app.ui.theme import BG_APP, BG_INPUT, TEXT_PRIMARY, TEXT_MUTED, font
from app.ui.atoms.buttons import SecondaryButton, TableActionButton
from app.ui.atoms.inputs import SearchInput, Dropdown
from app.ui.atoms.labels import Heading, Badge
from app.ui.molecules.data_table import DataTable
from app.ui.molecules.modal import BaseModal
from app.models.rechazo_ingreso_model import RechazoIngresoModel


class _Sig(QObject):
    done = pyqtSignal(list)


class ReportesView(QWidget):
    def __init__(self, parent=None, session_user: dict = None):
        super().__init__(parent)
        self._session_user = session_user or {}
        self.setStyleSheet(f"background:{BG_APP};")
        self._build(); self.load_data()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(24, 20, 24, 8); lay.setSpacing(0)
        toolbar = QWidget(); toolbar.setStyleSheet("background:transparent;")
        tl = QHBoxLayout(toolbar); tl.setContentsMargins(0, 0, 0, 0)
        tl.addWidget(Heading("Reportes de rechazo", level=2), stretch=1)
        refresh = SecondaryButton("↺ Actualizar", width=120, height=34)
        refresh.clicked.connect(self.load_data); tl.addWidget(refresh); lay.addWidget(toolbar)
        sub = QLabel("Revisa los rechazos registrados por los guardas y deja un comentario al gestionarlos.")
        sub.setFont(font(11)); sub.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        sub.setContentsMargins(0, 4, 0, 12); lay.addWidget(sub)
        filters = QWidget(); filters.setStyleSheet("background:transparent;")
        fl = QHBoxLayout(filters); fl.setContentsMargins(0, 0, 0, 0); fl.setSpacing(10)
        self._search = SearchInput("Buscar por aprendiz o documento...", width=300, on_change=self._on_search)
        self._estado = Dropdown(["Todos", "PENDIENTE", "GESTIONADO"], width=170, command=self._on_estado)
        fl.addWidget(self._search); fl.addWidget(self._estado); fl.addStretch(); lay.addWidget(filters); lay.addSpacing(10)
        columns = [
            {"key":"fecha_hora", "header":"Fecha", "width":145},
            {"key":"num_doc", "header":"Documento", "width":120},
            {"key":"nombres", "header":"Aprendiz", "width":145, "renderer":self._render_aprendiz},
            {"key":"guarda", "header":"Guarda", "width":150},
            {"key":"motivo", "header":"Motivo del rechazo", "width":260},
            {"key":"estado_gestion", "header":"Estado", "width":110, "renderer":self._render_estado},
            {"key":"_accion", "header":"Acción", "width":80, "renderer":self._render_accion},
        ]
        self._table = DataTable(columns=columns, row_height=52); lay.addWidget(self._table, stretch=1); lay.addSpacing(4)
        self._status = QLabel(""); self._status.setFont(font(11)); self._status.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;"); lay.addWidget(self._status)

    def load_data(self, search: str = None):
        search = self._search.get() if search is None else search
        estado = self._estado.get(); sig = _Sig(self); sig.done.connect(self._on_data)
        def fetch():
            try: rows = RechazoIngresoModel.get_all(search, estado)
            except Exception: rows = []
            sig.done.emit(rows)
        threading.Thread(target=fetch, daemon=True).start()

    def _on_data(self, rows):
        self._table.load(rows); self._status.setText(f"{len(rows)} reporte(s) encontrado(s)")
    def _on_search(self, value): self.load_data(value)
    def _on_estado(self, _value): self.load_data()

    def _render_aprendiz(self, parent, row, _value):
        lbl = QLabel(f"{row.get('nombres','')} {row.get('p_ape','')}".strip() or "—", parent)
        lbl.setFont(font(12)); lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; background:transparent;"); return lbl

    def _render_estado(self, parent, row, value):
        pending = value == "PENDIENTE"
        return Badge(preset="pendiente" if pending else "activo", text="Pendiente" if pending else "Gestionado", parent=parent)

    def _render_accion(self, parent, row, _value):
        wrap = QWidget(parent); lay = QHBoxLayout(wrap); lay.setContentsMargins(2, 0, 2, 0)
        if row.get("estado_gestion") == "PENDIENTE":
            btn = TableActionButton("check-circle", "Gestionar reporte", color="success"); btn.clicked.connect(lambda: self._gestionar(row))
        else:
            btn = TableActionButton("eye", "Ver gestión", color="ghost"); btn.clicked.connect(lambda: self._ver_gestion(row))
        lay.addWidget(btn); lay.addStretch(); return wrap

    def _gestionar(self, row):
        dialog = GestionRechazoModal(self, row)
        if dialog.exec() and dialog.comentario:
            try:
                if RechazoIngresoModel.gestionar(row["id_rechazo"], dialog.comentario, self._session_user.get("num_doc")):
                    self.load_data()
            except Exception as exc: self._status.setText(f"Error al gestionar el reporte: {exc}")

    def _ver_gestion(self, row): GestionRechazoModal(self, row, solo_lectura=True).exec()


class GestionRechazoModal(BaseModal):
    def __init__(self, parent, row: dict, solo_lectura: bool = False):
        super().__init__(parent, "Gestión del reporte" if solo_lectura else "Gestionar reporte", width=560, height=490)
        self.comentario = ""; layout = self.content.layout()
        info = QLabel(f"<b>Aprendiz:</b> {row.get('nombres','')} {row.get('p_ape','')}<br><b>Documento:</b> {row.get('num_doc','')}<br><b>Guarda:</b> {row.get('guarda','')}<br><br><b>Motivo reportado:</b><br>{row.get('motivo','')}")
        info.setWordWrap(True); info.setFont(font(11)); info.setStyleSheet(f"color:{TEXT_PRIMARY}; background:{BG_INPUT}; border-radius:8px; padding:10px;")
        layout.insertWidget(layout.count() - 1, info)
        label = QLabel("Comentario registrado" if solo_lectura else "Comentario de gestión")
        label.setFont(font(11, bold=True)); label.setStyleSheet(f"color:{TEXT_PRIMARY}; background:transparent;"); layout.insertWidget(layout.count() - 1, label)
        self._comment = QTextEdit(); self._comment.setFixedHeight(110); self._comment.setPlaceholderText("Describe la gestión realizada…")
        self._comment.setPlainText(row.get("comentario_gestion") or ""); self._comment.setReadOnly(solo_lectura)
        self._comment.setStyleSheet(f"QTextEdit{{background:{BG_INPUT}; color:{TEXT_PRIMARY}; border:1px solid #D7DEE8; border-radius:8px; padding:8px;}}")
        layout.insertWidget(layout.count() - 1, self._comment)
        if solo_lectura: self.add_footer_buttons(confirm_text="Cerrar", confirm_cmd=self.accept, cancel_text="Cerrar")
        else: self.add_footer_buttons(confirm_text="Marcar gestionado", confirm_cmd=self._save)

    def _save(self):
        text = self._comment.toPlainText().strip()
        if not text: self.show_error("Debes escribir un comentario de gestión."); return
        self.comentario = text; self.accept()
