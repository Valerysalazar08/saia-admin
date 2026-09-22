"""
VISTA Qt — CRUD completo de guardas de seguridad.
"""
import re, os, shutil, time, threading
from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QFileDialog,
    QCalendarWidget, QDialog,
    QVBoxLayout, QHBoxLayout, QGridLayout,
)
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QColor
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QDate, QRectF

from app.ui.theme import (
    BG_APP, BG_INPUT, BG_HOVER, BG_PALE, BORDER,
    PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ERROR, SUCCESS_TEXT, WARNING,
    CARD_RADIUS, font, svg_icon,
)
from app.ui.atoms.buttons  import SecondaryButton, TableActionButton
from app.ui.atoms.inputs   import SearchInput, LabeledInput, Dropdown
from app.ui.atoms.labels   import Heading, Badge
from app.ui.molecules.data_table import DataTable
from app.ui.molecules.modal      import BaseModal, ConfirmModal
from app.models.guarda_model        import GuardaModel
from app.models.persona_model       import PersonaModel, CuentaModel
import mysql.connector

# Las tres apps están en el mismo computador: el Escritorio copia las fotos
# directamente a la carpeta que el Backend expone al Móvil.
BACKEND_PERFILES_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..", "..", "saia_backend", "uploads", "perfiles"
))


class _Sig(QObject):
    done = pyqtSignal(list)


class _CircularPhoto(QFrame):
    """Foto circular con recorte centrado y borde antialias, sin QBitmap."""

    SIZE = 110

    def __init__(self, parent=None):
        super().__init__(parent)
        self._photo = QPixmap()
        self.setFixedSize(self.SIZE, self.SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("background:transparent; border:none;")

    def set_photo(self, path: str):
        self._photo = QPixmap(path)
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        circle = QPainterPath()
        circle.addEllipse(QRectF(0, 0, self.SIZE, self.SIZE))
        painter.setClipPath(circle)

        if self._photo.isNull():
            painter.fillPath(circle, QColor(BG_PALE))
            painter.setPen(QColor(PRIMARY))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "👤")
        else:
            # KeepAspectRatioByExpanding llena el círculo y copy recorta el
            # excedente desde el centro, como un avatar profesional.
            scaled = self._photo.scaled(
                self.SIZE, self.SIZE,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = max(0, (scaled.width() - self.SIZE) // 2)
            y = max(0, (scaled.height() - self.SIZE) // 2)
            painter.drawPixmap(0, 0, scaled.copy(x, y, self.SIZE, self.SIZE))
        painter.end()


class _DatePickerField(QWidget):

    def __init__(self, parent=None, width: int = 236):
        super().__init__(parent)
        self.setFixedWidth(width)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        label = QLabel("Fecha de nacimiento *")
        label.setFont(font(11, bold=True))
        label.setStyleSheet(f"color:{TEXT_SECONDARY}; background:transparent;")
        lay.addWidget(label)

        self._date = QDate.currentDate().addYears(-18)
        self._picker = QFrame()
        self._picker.setObjectName("DatePickerSurface")
        self._picker.setFixedHeight(42)
        self._picker.setCursor(Qt.CursorShape.PointingHandCursor)
        self._picker.setStyleSheet(f"""
            QFrame#DatePickerSurface {{ background:{BG_INPUT}; color:{TEXT_PRIMARY};
                border:1.5px solid {BORDER}; border-radius:10px;
            }}
            QFrame#DatePickerSurface:hover {{ border-color:{PRIMARY}; background:{BG_PALE}; }}
        """)
        self._normal_picker_style = self._picker.styleSheet()
        picker_lay = QHBoxLayout(self._picker)
        picker_lay.setContentsMargins(12, 0, 12, 0)
        picker_lay.setSpacing(8)
        self._date_text = QLabel()
        self._date_text.setFont(font(13))
        self._date_text.setStyleSheet(f"color:{TEXT_PRIMARY}; background:transparent;")
        self._date_text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        picker_lay.addWidget(self._date_text)
        picker_lay.addStretch()
        calendar_icon = QLabel()
        calendar_icon.setPixmap(svg_icon("calendar", 18, PRIMARY))
        calendar_icon.setFixedSize(22, 22)
        calendar_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        calendar_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        picker_lay.addWidget(calendar_icon)
        self._picker.mousePressEvent = lambda _event: self._open_calendar()
        self._refresh_date_text()
        lay.addWidget(self._picker)
        self._error = QLabel("")
        self._error.setFixedHeight(14)
        self._error.setFont(font(10))
        self._error.setStyleSheet(f"color:{ERROR}; background:transparent;")
        lay.addWidget(self._error)

    def _open_calendar(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Seleccionar fecha de nacimiento")
        dialog.setModal(True)
        # El tamaño fijo evita que el diálogo crezca al cambiar de mes o año.
        dialog.setFixedSize(390, 324)
        dialog.setStyleSheet(f"background:white; border:1px solid {BORDER}; border-radius:12px;")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(12, 12, 12, 12)

        calendar = QCalendarWidget(dialog)
        calendar.setSelectedDate(self._date)
        calendar.setMinimumDate(QDate.currentDate().addYears(-70))
        calendar.setMaximumDate(QDate.currentDate().addYears(-18))
        calendar.setGridVisible(False)
        calendar.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        calendar.setHorizontalHeaderFormat(
            QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        calendar.setNavigationBarVisible(True)
        calendar.setFixedSize(366, 300)
        calendar.setStyleSheet(f"""
            QCalendarWidget {{
                background:white; color:{TEXT_PRIMARY};
                border:1px solid {BORDER}; border-radius:10px;
            }}
            QCalendarWidget QToolButton {{
                color:{TEXT_PRIMARY}; background:transparent; border:none;
                border-radius:6px; font-weight:bold; font-size:12px;
                min-height:28px; padding:3px 8px;
            }}
            QCalendarWidget QToolButton:hover {{ background:{BG_HOVER}; }}
            QCalendarWidget QToolButton#qt_calendar_monthbutton,
            QCalendarWidget QToolButton#qt_calendar_yearbutton {{
                background:transparent; margin:0 3px;
            }}
            QCalendarWidget QToolButton#qt_calendar_prevmonth,
            QCalendarWidget QToolButton#qt_calendar_nextmonth {{
                min-width:28px; max-width:28px; min-height:28px; max-height:28px;
                padding:0; color:{PRIMARY}; font-size:16px;
            }}
            QCalendarWidget QMenu {{ background:white; color:{TEXT_PRIMARY}; border:1px solid {BORDER}; }}
            QCalendarWidget QMenu::item:selected {{ background:#D9F0FF; color:#0F6B99; }}
            QCalendarWidget QSpinBox {{ color:{TEXT_PRIMARY}; background:white; border:none; padding:2px; }}
            QCalendarWidget QWidget#qt_calendar_calendarview {{
                background:white; alternate-background-color:white;
            }}
            QCalendarWidget QHeaderView::section {{
                background:#D9F0FF; color:#1677A8; border:none;
                font-weight:bold; padding:6px 0;
            }}
            QCalendarWidget QAbstractItemView {{
                background:white; color:{TEXT_PRIMARY}; selection-background-color:{PRIMARY};
                selection-color:white; outline:0; font-size:12px; gridline-color:{BORDER};
            }}
        """)
        layout.addWidget(calendar)

        def select_date(selected):
            self._date = selected
            self._refresh_date_text()
            dialog.accept()

        calendar.clicked.connect(select_date)
        calendar.activated.connect(select_date)
        dialog.exec()

    def _refresh_date_text(self):
        self._date_text.setText(self._date.toString("yyyy-MM-dd"))

    def get(self) -> str:
        return self._date.toString("yyyy-MM-dd")

    def set(self, value):
        parsed = QDate.fromString(str(value)[:10], "yyyy-MM-dd")
        if parsed.isValid():
            self._date = parsed
            self._refresh_date_text()

    def set_error(self, message=""):
        self._error.setText(message)
        self._picker.setStyleSheet(self._normal_picker_style.replace(
            f"border:1.5px solid {BORDER}", f"border:1.5px solid {ERROR}"))

    def clear_error(self):
        self._error.setText("")
        self._picker.setStyleSheet(self._normal_picker_style)


class GuardasView(QWidget):
    def __init__(self, parent=None, session_user: dict = None):
        super().__init__(parent)
        self._session_user = session_user or {}
        self.setStyleSheet(f"background:{BG_APP};")
        self._build()
        self.load_data()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 8); lay.setSpacing(0)

        tb = QWidget(); tb.setStyleSheet("background:transparent;")
        tbl = QHBoxLayout(tb); tbl.setContentsMargins(0,0,0,0)
        tbl.addWidget(Heading("Guardas de Seguridad", level=2), stretch=1)
        # Misma acción ligera usada por los controles de Auditoría.
        new_btn = SecondaryButton("＋ Nuevo guarda", width=148, height=34)
        new_btn.clicked.connect(self._open_create)
        tbl.addWidget(new_btn)
        lay.addWidget(tb); lay.addSpacing(12)

        self._search = SearchInput("Buscar por nombre o documento...", width=320,
                                   on_change=self._on_search)
        lay.addWidget(self._search); lay.addSpacing(8)

        cols = [
            {"key":"num_doc",     "header":"Documento",  "width":110},
            {"key":"nombres",     "header":"Nombre",     "width":130},
            {"key":"p_ape",       "header":"Apellido",   "width":130},
            {"key":"turno",       "header":"Turno",      "width":80},
            {"key":"empresa_seg", "header":"Empresa",    "width":130},
            {"key":"tel",         "header":"Teléfono",   "width":110},
            {"key":"turno_activo", "header":"Turno activo", "width":112,
             "renderer":self._render_turno_activo},
            {"key":"cuenta_estado", "header":"Estado",   "width":92,
             "renderer":self._render_estado},
            {"key":"_acc",        "header":"Acciones",   "width":88,
             "renderer":self._render_acc},
        ]
        self._table = DataTable(columns=cols, row_height=44)
        lay.addWidget(self._table, stretch=1); lay.addSpacing(4)

        self._status = QLabel("")
        self._status.setFont(font(11))
        self._status.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        lay.addWidget(self._status)

    def _render_acc(self, parent, row, _val):
        w = QWidget(parent); w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w); h.setContentsMargins(2,0,2,0); h.setSpacing(6)
        e = TableActionButton("pencil", "Editar guarda", color="primary")
        e.clicked.connect(lambda: self._open_edit(row))
        h.addWidget(e)

        # Una cuenta ya inactiva se habilita únicamente desde Bloqueados;
        # no se ofrece una desactivación repetida en la lista principal.
        if row.get("cuenta_estado") in (1, True, "1"):
            d = TableActionButton("ban", "Desactivar guarda", color="danger")
            d.clicked.connect(lambda: self._confirm_delete(row))
            h.addWidget(d)

        h.addStretch()
        return w

    def _render_estado(self, parent, row, _val):
        activo = row.get("cuenta_estado") in (1, True, "1")
        return Badge(preset="activo" if activo else "inactivo", parent=parent)

    def _render_turno_activo(self, parent, row, _val):
        activo = row.get("turno_activo") in (1, True, "1")
        return Badge(
            text="En turno" if activo else "Sin turno",
            preset="activo" if activo else "inactivo", parent=parent)

    def load_data(self, search: str = ""):
        sig = _Sig(self); sig.done.connect(self._on_data)
        def fetch():
            try: data = GuardaModel.get_all(search)
            except Exception: data = []
            sig.done.emit(data)
        threading.Thread(target=fetch, daemon=True).start()

    def _on_data(self, data):
        self._table.load(data)
        self._status.setText(f"{len(data)} guarda(s) encontrado(s)")
        self._status.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")

    def _on_search(self, text): self.load_data(text)
    def _open_create(self): GuardaFormModal(self, on_save=self.load_data,
                                            session_user=self._session_user)
    def _open_edit(self, row): GuardaFormModal(self, on_save=self.load_data,
                                               guarda_data=row,
                                               session_user=self._session_user)

    def _confirm_delete(self, row: dict):
        nombre = f"{row.get('nombres','')} {row.get('p_ape','')}".strip()
        try:
            if GuardaModel.tiene_turno_activo(row["id_guarda"]):
                ConfirmModal(
                    self, "No se puede desactivar",
                    "No se puede bloquear a este guarda porque tiene un turno activo. Debe finalizarlo antes de desactivar su cuenta.",
                    confirm_text="Entendido", cancel_text=None,
                )
                return
        except Exception as e:
            self._show_status(f"Error verificando el turno: {e}", error=True)
            return
        dlg = ConfirmModal(
            self, "Desactivar guarda",
            f"¿Desactivar la cuenta de {nombre}?\n\n"
            "No podrá iniciar sesión ni registrar nuevos ingresos. "
            "Sus datos y su historial se conservarán para auditoría.",
            confirm_text="Desactivar", danger=True,
        )
        if dlg.confirmed:
            try:
                GuardaModel.delete(row["id_guarda"])
                try:
                    from app.models.auditoria_model import AuditoriaModel, ENTIDAD_GUARDA
                    AuditoriaModel.registrar(
                        "BLOQUEAR", ENTIDAD_GUARDA, row["num_doc"],
                        f"Desactivado guarda {nombre}; se conserva su historial.",
                        realizado_por=self._session_user.get("num_doc"))
                except Exception: pass
                self.load_data()
                self._refresh_cached_view("bloqueo")
                self._refresh_cached_view("dashboard")
                ConfirmModal(
                    self, "Guarda desactivado",
                    "La cuenta fue desactivada y sus registros históricos se conservaron.",
                    confirm_text="Entendido", cancel_text=None,
                )
            except Exception as e:
                self._show_status(str(e), error=True)

    def _show_status(self, message: str, error: bool = False):
        color = ERROR if error else WARNING
        self._status.setText(message)
        self._status.setStyleSheet(f"color:{color}; background:transparent;")

    def _refresh_cached_view(self, view_id: str):
        parent = self.parentWidget()
        while parent:
            refresh = getattr(parent, "refresh_view", None)
            if callable(refresh):
                refresh(view_id)
                return
            parent = parent.parentWidget()


class GuardaFormModal(BaseModal):
    TIPOS_DOC    = ["Cédula de Ciudadanía","Cédula Extranjera","Permiso por Protección Temporal"]
    SEXOS        = ["Masculino","Femenino","Otro"]
    TIPOS_SANGRE = ["O+","O-","A+","A-","B+","B-","AB+","AB-"]
    PAIR_FIELD_WIDTH = 236

    def __init__(self, parent, on_save=None, guarda_data: dict = None,
                 session_user: dict = None):
        title = "Editar guarda" if guarda_data else "Nuevo guarda"
        super().__init__(parent, title, width=560, height=740)
        self._on_save      = on_save
        self._guarda_data  = guarda_data
        self._is_edit      = guarda_data is not None
        self._original_num_doc = guarda_data.get("num_doc") if guarda_data else None
        self._foto_path    = None
        self._session_user = session_user or {}
        self._build_form()
        if self._is_edit: self._fill()
        self.add_footer_buttons(confirm_text="Guardar", confirm_cmd=self._save)
        # A diferencia de ConfirmModal (que usa exec), los formularios no son
        # bloqueantes: deben mostrarse explícitamente al terminar de crearse.
        self.show()

    def _build_form(self):
        c   = self.content
        lay = c.layout()

        def ins(w):
            lay.insertWidget(lay.count()-1, w)

        # ── Avatar ────────────────────────────────────────────────────────────
        av = QWidget(); av.setStyleSheet("background:transparent;")
        avl = QVBoxLayout(av); avl.setContentsMargins(0,0,0,0); avl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._foto_preview = _CircularPhoto()
        self._foto_preview.mousePressEvent = lambda e: self._sel_foto()
        avl.addWidget(self._foto_preview, alignment=Qt.AlignmentFlag.AlignCenter)

        foto_btn = QPushButton("📷  Cargar foto")
        foto_btn.setFixedHeight(28); foto_btn.setMinimumWidth(120)
        foto_btn.setFont(font(11)); foto_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        foto_btn.setStyleSheet(f"""
            QPushButton {{background:{BG_INPUT}; color:{PRIMARY};
                          border:1px solid {BORDER}; border-radius:14px; padding:0 12px;}}
            QPushButton:hover {{background:{BG_HOVER};}}
        """)
        foto_btn.clicked.connect(self._sel_foto)
        avl.addWidget(foto_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._foto_lbl = QLabel("Sin foto (obligatoria al crear)")
        self._foto_lbl.setFont(font(10))
        self._foto_lbl.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        self._foto_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avl.addWidget(self._foto_lbl)
        ins(av)
        ins(self._hsep())

        # ── Datos personales ──────────────────────────────────────────────────
        ins(self._sec_label("Datos personales"))

        r1 = self._row2()
        self._num_doc = LabeledInput("N° Documento", required=True, width=200)
        self._num_doc.setFixedWidth(self.PAIR_FIELD_WIDTH)
        r1.layout().addWidget(self._num_doc)

        td_w = QWidget(); td_w.setStyleSheet("background:transparent;")
        td_w.setFixedWidth(self.PAIR_FIELD_WIDTH)
        tdl  = QVBoxLayout(td_w); tdl.setContentsMargins(0,0,0,0); tdl.setSpacing(4)
        tl   = QLabel("Tipo documento"); tl.setFont(font(11,bold=True))
        tl.setStyleSheet(f"color:{TEXT_SECONDARY}; background:transparent;")
        tdl.addWidget(tl)
        self._tip_doc_dd = Dropdown(self.TIPOS_DOC, width=200)
        tdl.addWidget(self._tip_doc_dd)
        # Igual que LabeledInput: reserva el espacio del mensaje de validación
        # para que un Dropdown tenga exactamente la misma altura que un input.
        tdl.addSpacing(19)
        r1.layout().addWidget(td_w)
        ins(r1)

        r2 = self._row2()
        self._nombres   = LabeledInput("Nombres",   required=True, width=200)
        self._apellidos = LabeledInput("Apellidos", required=True, width=200)
        self._nombres.setFixedWidth(self.PAIR_FIELD_WIDTH)
        self._apellidos.setFixedWidth(self.PAIR_FIELD_WIDTH)
        r2.layout().addWidget(self._nombres); r2.layout().addWidget(self._apellidos)
        ins(r2)

        # Cada fila mantiene exactamente dos campos del mismo ancho.
        # Tipo de sangre deja de ocupar toda la fila y queda junto a email.
        sang_w = QWidget(); sang_w.setStyleSheet("background:transparent;")
        sang_w.setFixedWidth(self.PAIR_FIELD_WIDTH)
        sgl    = QVBoxLayout(sang_w); sgl.setContentsMargins(0,0,0,0); sgl.setSpacing(4)
        sgl2   = QLabel("Tipo de sangre"); sgl2.setFont(font(11,bold=True))
        sgl2.setStyleSheet(f"color:{TEXT_SECONDARY}; background:transparent;")
        sgl.addWidget(sgl2)
        self._tip_sang_dd = Dropdown(self.TIPOS_SANGRE, width=200)
        sgl.addWidget(self._tip_sang_dd)
        sgl.addSpacing(19)

        r3 = self._row2()
        self._email = LabeledInput("Email", required=True, width=200)
        self._email.setFixedWidth(self.PAIR_FIELD_WIDTH)
        r3.layout().addWidget(sang_w); r3.layout().addWidget(self._email)
        ins(r3)

        r4 = self._row2()
        self._tel = LabeledInput("Teléfono", required=True, width=200)
        self._fecha_nac = _DatePickerField(width=self.PAIR_FIELD_WIDTH)
        self._tel.setFixedWidth(self.PAIR_FIELD_WIDTH)
        r4.layout().addWidget(self._tel); r4.layout().addWidget(self._fecha_nac)
        ins(r4)

        sexo_w = QWidget(); sexo_w.setStyleSheet("background:transparent;")
        sexo_w.setFixedWidth(self.PAIR_FIELD_WIDTH)
        sexo_lay = QVBoxLayout(sexo_w); sexo_lay.setContentsMargins(0,0,0,0); sexo_lay.setSpacing(4)
        sexo_lbl = QLabel("Sexo"); sexo_lbl.setFont(font(11,bold=True))
        sexo_lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; background:transparent;")
        sexo_lay.addWidget(sexo_lbl)
        self._sexo_dd = Dropdown(self.SEXOS, width=200)
        sexo_lay.addWidget(self._sexo_dd)
        sexo_lay.addSpacing(19)
        sexo_row = self._row2()
        sexo_row.layout().addWidget(sexo_w)
        sexo_row.layout().addStretch()
        ins(sexo_row)

        # ── Info seguridad ────────────────────────────────────────────────────
        ins(self._sec_label("Información de seguridad"))

        self._empresa = LabeledInput("Empresa de seguridad", required=True, width=200)
        self._empresa.setFixedWidth(self.PAIR_FIELD_WIDTH)
        empresa_row = self._row2()
        empresa_row.layout().addWidget(self._empresa)
        empresa_row.layout().addStretch()
        ins(empresa_row)

        if not self._is_edit:
            ins(self._sec_label("Contraseña de acceso"))
            self._pwd = LabeledInput("Contraseña inicial", required=True, password=True)
            ins(self._pwd)
            note = QLabel("El guarda usará esta contraseña en la app móvil.")
            note.setFont(font(10))
            note.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
            ins(note)
        else:
            self._pwd = None

    # ── Helpers UI ────────────────────────────────────────────────────────────
    def _row2(self):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w); h.setContentsMargins(0,0,0,0); h.setSpacing(12)
        h.setAlignment(Qt.AlignmentFlag.AlignLeft)
        return w

    def _hsep(self):
        from app.ui.atoms.labels import Divider
        return Divider()

    def _sec_label(self, text: str) -> QLabel:
        lbl = QLabel(text); lbl.setFont(font(12, bold=True))
        lbl.setStyleSheet(f"color:{PRIMARY}; background:transparent;")
        lbl.setContentsMargins(0, 8, 0, 2)
        return lbl

    # ── Foto ──────────────────────────────────────────────────────────────────
    def _sel_foto(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar foto de perfil", "",
            "Imágenes (*.jpg *.jpeg *.png *.webp)")
        if not path: return
        self._foto_path = path
        self._foto_lbl.setText(f"✓ {os.path.basename(path)}")
        self._foto_lbl.setStyleSheet(f"color:{SUCCESS_TEXT}; background:transparent;")
        self._foto_preview.set_photo(path)

    # ── Fill ──────────────────────────────────────────────────────────────────
    def _fill(self):
        d = self._guarda_data
        self._num_doc.set(d.get("num_doc",""))
        # El documento es la llave que conecta cuenta, persona e historial.
        # Cambiarlo aquí podía hacer que el UPDATE no encontrara la persona.
        self._num_doc.entry.setReadOnly(True)
        self._num_doc.setToolTip("El documento no puede cambiarse al editar una cuenta.")
        self._nombres.set(d.get("nombres",""))
        self._apellidos.set(d.get("p_ape",""))
        self._email.set(d.get("email",""))
        self._tel.set(d.get("tel",""))
        self._fecha_nac.set(str(d.get("fecha_nac","")) if d.get("fecha_nac") else "")
        self._empresa.set(d.get("empresa_seg",""))
        if d.get("tip_doc") in self.TIPOS_DOC: self._tip_doc_dd.set(d["tip_doc"])
        if d.get("sexo") in self.SEXOS:       self._sexo_dd.set(d["sexo"])
        if d.get("tip_sang") in self.TIPOS_SANGRE: self._tip_sang_dd.set(d["tip_sang"])
        img = d.get("imagen")
        if img:
            local = os.path.join(BACKEND_PERFILES_DIR, os.path.basename(img))
            if os.path.exists(local):
                self._foto_preview.set_photo(local)
                self._foto_lbl.setText("✓ Foto actual — clic para cambiar")
                self._foto_lbl.setStyleSheet(f"color:{SUCCESS_TEXT}; background:transparent;")

    # ── Save ──────────────────────────────────────────────────────────────────
    def _save(self):
        for f in [self._num_doc, self._nombres, self._apellidos,
                  self._email, self._tel, self._fecha_nac, self._empresa]:
            f.clear_error()

        nd_str   = self._num_doc.get().strip()
        nombres  = self._nombres.get().strip()
        apellidos = self._apellidos.get().strip()
        email    = self._email.get().strip()
        tel      = self._tel.get().strip()
        empresa  = self._empresa.get().strip()
        fecha    = self._fecha_nac.get().strip()
        tip_doc  = self._tip_doc_dd.get()

        # Validaciones
        if not nd_str or not re.match(r"^\d{6,12}$", nd_str) or nd_str.startswith("0"):
            self._num_doc.set_error("6-12 dígitos, sin cero inicial")
            self.show_error("Número de documento inválido."); return
        num_doc = int(nd_str)

        if not nombres or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ]+([ ][a-zA-ZáéíóúÁÉÍÓÚüÜñÑ]+)*$", nombres):
            self._nombres.set_error("Solo letras"); self.show_error("Nombres inválidos."); return
        if not apellidos or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ]+([ ][a-zA-ZáéíóúÁÉÍÓÚüÜñÑ]+)*$", apellidos):
            self._apellidos.set_error("Solo letras"); self.show_error("Apellidos inválidos."); return
        if not email or not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$", email):
            self._email.set_error("Email inválido"); self.show_error("Email inválido."); return
        if not tel or not re.match(r"^\d{7,15}$", tel):
            self._tel.set_error("7-15 dígitos"); self.show_error("Teléfono inválido."); return
        if not fecha:
            self._fecha_nac.set_error("Obligatorio"); self.show_error("Fecha de nacimiento requerida."); return
        try:
            parts = fecha.split("-")
            if len(parts)!=3: raise ValueError
            fnac = date(int(parts[0]),int(parts[1]),int(parts[2]))
            hoy  = date.today()
            edad = (hoy-fnac).days//365
            if fnac >= hoy or edad < 18 or edad > 70:
                raise ValueError
        except ValueError:
            self._fecha_nac.set_error("Formato o edad inválida")
            self.show_error("Fecha de nacimiento inválida (debe tener 18-70 años)."); return
        if not empresa:
            self._empresa.set_error("Obligatorio"); self.show_error("Empresa requerida."); return
        if not self._is_edit and (not self._foto_path or not os.path.isfile(self._foto_path)):
            self._foto_lbl.setStyleSheet(f"color:{ERROR}; background:transparent;")
            self.show_error("La foto de perfil es obligatoria."); return
        if not self._is_edit:
            pwd = self._pwd.get() if self._pwd else ""
            if len(pwd) < 6 or not re.search(r"[a-zA-Z]",pwd) or not re.search(r"\d",pwd):
                if self._pwd: self._pwd.set_error("Mín 6 chars, letras y números")
                self.show_error("Contraseña: mínimo 6 caracteres con letras y números."); return
            if PersonaModel.exists(num_doc):
                self._num_doc.set_error("Ya registrado")
                self.show_error(f"Ya existe una persona con el documento {num_doc}."); return

        persona_data = {"num_doc":num_doc,"tip_doc":tip_doc,"nombres":nombres,
                        "p_ape":apellidos,"email":email,"tel":tel,
                        "sexo":self._sexo_dd.get(),"tip_sang":self._tip_sang_dd.get(),"fecha_nac":fecha}
        guarda_data = {"empresa_seg":empresa}

        # La foto debe copiarse correctamente antes de crear la cuenta. Así no
        # queda un guarda nuevo sin la imagen de perfil obligatoria.
        foto_ruta = None
        if not self._is_edit:
            foto_ruta = self._guardar_foto(num_doc)
            if not foto_ruta:
                self.show_error("No se pudo guardar la foto de perfil. Inténtalo de nuevo.")
                return

        try:
            if self._is_edit:
                PersonaModel.update(self._original_num_doc, persona_data)
                GuardaModel.update(self._guarda_data["id_guarda"], guarda_data)
                if self._foto_path:
                    ruta = self._guardar_foto(num_doc)
                    if not ruta:
                        self.show_error("No se pudo actualizar la foto de perfil.")
                        return
                    cuenta = CuentaModel.get_by_doc(num_doc)
                    if cuenta:
                        CuentaModel.update_imagen(cuenta["id_cuenta"], ruta)
                try:
                    from app.models.auditoria_model import AuditoriaModel, ACCION_ACTUALIZAR, ENTIDAD_GUARDA
                    AuditoriaModel.registrar(ACCION_ACTUALIZAR, ENTIDAD_GUARDA, num_doc,
                        f"Actualizado guarda {nombres} {apellidos}",
                        realizado_por=self._session_user.get("num_doc"))
                except Exception: pass
            else:
                PersonaModel.create(persona_data)
                GuardaModel.create(num_doc, empresa_seg=guarda_data["empresa_seg"])
                if not CuentaModel.get_by_doc(num_doc):
                    CuentaModel.create(num_doc, id_rol=3, password_plain=self._pwd.get())
                cuenta = CuentaModel.get_by_doc(num_doc)
                if cuenta:
                    CuentaModel.update_imagen(cuenta["id_cuenta"], foto_ruta)
                try:
                    from app.models.auditoria_model import AuditoriaModel, ACCION_CREAR, ENTIDAD_GUARDA
                    AuditoriaModel.registrar(ACCION_CREAR, ENTIDAD_GUARDA, num_doc,
                        f"Creado guarda {nombres} {apellidos} (Empresa: {empresa})",
                        realizado_por=self._session_user.get("num_doc"))
                except Exception: pass
        except mysql.connector.Error as e:
            self.show_error(f"Error de base de datos: {e.msg}"); return
        except Exception as e:
            self.show_error(str(e)); return

        if self._on_save: self._on_save()
        self.accept()

    def _guardar_foto(self, num_doc: int) -> str | None:
        if not self._foto_path or not os.path.exists(self._foto_path): return None
        try:
            ext = os.path.splitext(self._foto_path)[1].lower()
            nombre = f"perfil_{num_doc}_{int(time.time() * 1000)}{ext}"
            os.makedirs(BACKEND_PERFILES_DIR, exist_ok=True)
            shutil.copy2(self._foto_path, os.path.join(BACKEND_PERFILES_DIR, nombre))
            return f"/uploads/perfiles/{nombre}"
        except Exception as e:
            print(f"[Guardas] Error copiando foto: {e}")
        return None


# Necesario para que QPushButton funcione en el módulo
from PyQt6.QtWidgets import QPushButton as _QPB
QPushButton = _QPB
