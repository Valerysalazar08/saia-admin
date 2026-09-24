"""
VISTA Qt — Edición del perfil del administrador.
"""
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QScrollArea,
    QVBoxLayout, QHBoxLayout, QGridLayout,
)
from PyQt6.QtCore import Qt, QTimer
import re

from app.ui.theme import (
    BG_APP, BG_CARD, BORDER, PRIMARY,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ERROR, SUCCESS, SUCCESS_TEXT,
    CARD_RADIUS, font, svg_icon,
)
from app.ui.atoms.inputs  import LabeledInput, PasswordInput, Dropdown
from app.ui.atoms.labels  import Heading, Divider
from app.models.persona_model import PersonaModel, CuentaModel

TIPOS_DOC    = ["Cédula de Ciudadanía","Tarjeta de Identidad","Pasaporte","Cédula Extranjera"]
TIPOS_SANGRE = ["","O+","O-","A+","A-","B+","B-","AB+","AB-"]
SEXOS        = ["","Masculino","Femenino","Otro"]


class AjustesView(QScrollArea):
    def __init__(self, parent=None, session_user: dict = None, on_profile_update=None):
        super().__init__(parent)
        self._user = session_user or {}
        self._on_profile_update = on_profile_update
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"background:{BG_APP};")

        content = QWidget()
        content.setStyleSheet(f"background:{BG_APP};")
        self.setWidget(content)

        self._lay = QVBoxLayout(content)
        self._lay.setContentsMargins(24, 20, 24, 24)
        self._lay.setSpacing(0)
        self._build()
        self._load_profile()

    def _build(self):
        hero = QWidget()
        hero.setStyleSheet("background:transparent;")
        hero_lay = QHBoxLayout(hero)
        hero_lay.setContentsMargins(0, 0, 0, 0)
        hero_lay.setSpacing(12)
        # El encabezado usa el icono de ajustes; "user" queda reservado para Datos personales.
        hero_lay.addWidget(self._icon_badge("settings"), alignment=Qt.AlignmentFlag.AlignVCenter)

        title_box = QWidget()
        title_box.setStyleSheet("background:transparent;")
        title_lay = QVBoxLayout(title_box)
        title_lay.setContentsMargins(0, 1, 0, 0)
        title_lay.setSpacing(2)
        title_lay.addWidget(Heading("Editar perfil", level=2))
        sub = QLabel("Edita tu perfil y credenciales de acceso.")
        sub.setFont(font(11))
        sub.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        title_lay.addWidget(sub)
        hero_lay.addWidget(title_box)
        hero_lay.addStretch()
        self._lay.addWidget(hero)
        self._lay.addSpacing(20)

        self._build_personal_card()
        self._lay.addSpacing(16)
        self._build_password_card()
        self._lay.addStretch()

   
    def _build_personal_card(self):
        card, inner = self._make_card("Datos personales", "user")

        self._profile_reminder = QLabel()
        self._profile_reminder.setWordWrap(True)
        self._profile_reminder.setFont(font(10))
        self._profile_reminder.setStyleSheet(
            "background:#FFF7E6; color:#8A5A00; border:1px solid #F5CF7A; "
            "border-radius:8px; padding:9px 11px;")
        self._profile_reminder.hide()
        inner.layout().addWidget(self._profile_reminder)

        grid = QWidget(); grid.setStyleSheet("background:transparent;")
        gl   = QGridLayout(grid)
        gl.setContentsMargins(0, 0, 0, 0)
        gl.setHorizontalSpacing(24)
        gl.setVerticalSpacing(14)
        gl.setColumnStretch(0, 1)
        gl.setColumnStretch(1, 1)

        # Tipo doc
        td_w = QWidget(); td_w.setStyleSheet("background:transparent;")
        tdl  = QVBoxLayout(td_w); tdl.setContentsMargins(0,0,0,0); tdl.setSpacing(4)
        lbl = QLabel("Tipo documento"); lbl.setFont(font(11,bold=True))
        lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; background:transparent;")
        tdl.addWidget(lbl)
        self._tip_doc_dd = Dropdown(TIPOS_DOC, width=200)
        self._tip_doc_dd.setEnabled(False)
        tdl.addWidget(self._tip_doc_dd)
        tdl.addSpacing(14)
        gl.addWidget(td_w, 0, 0)

        self._num_doc_inp = LabeledInput("N° Documento", width=200)
        self._num_doc_inp.entry.setEnabled(False)
        self._num_doc_inp.entry.setStyleSheet(
            f"background:transparent; border:none; color:{TEXT_MUTED}; font-size:13px;")
        gl.addWidget(self._num_doc_inp, 0, 1)

        self._nombres   = LabeledInput("Nombres",  required=True, width=200)
        self._apellidos = LabeledInput("Apellidos", required=True, width=200)
        self._nombres.set_editable(False)
        self._apellidos.set_editable(False)
        gl.addWidget(self._nombres,   1, 0)
        gl.addWidget(self._apellidos, 1, 1)

        self._tel   = LabeledInput("Teléfono", width=200)
        self._email = LabeledInput("Email",    width=200)
        gl.addWidget(self._tel,   2, 0)
        gl.addWidget(self._email, 2, 1)

        # Tipo sangre
        ts_w = QWidget(); ts_w.setStyleSheet("background:transparent;")
        tsl  = QVBoxLayout(ts_w); tsl.setContentsMargins(0,0,0,0); tsl.setSpacing(4)
        lbl2 = QLabel("Tipo de sangre"); lbl2.setFont(font(11,bold=True))
        lbl2.setStyleSheet(f"color:{TEXT_SECONDARY}; background:transparent;")
        tsl.addWidget(lbl2)
        self._tip_sang_dd = Dropdown(TIPOS_SANGRE, width=200)
        tsl.addWidget(self._tip_sang_dd)
        gl.addWidget(ts_w, 3, 0)

        # Sexo
        sx_w = QWidget(); sx_w.setStyleSheet("background:transparent;")
        sxl  = QVBoxLayout(sx_w); sxl.setContentsMargins(0,0,0,0); sxl.setSpacing(4)
        lbl3 = QLabel("Sexo"); lbl3.setFont(font(11,bold=True))
        lbl3.setStyleSheet(f"color:{TEXT_SECONDARY}; background:transparent;")
        sxl.addWidget(lbl3)
        self._sexo_dd = Dropdown(SEXOS, width=200)
        sxl.addWidget(self._sexo_dd)
        gl.addWidget(sx_w, 3, 1)

        inner.layout().addWidget(grid)

        # Footer botones
        fb = QWidget(); fb.setStyleSheet("background:transparent;")
        fbl = QHBoxLayout(fb); fbl.setContentsMargins(0, 8, 0, 0)
        self._status_personal = QLabel("")
        self._status_personal.setFont(font(11))
        self._status_personal.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        fbl.addWidget(self._status_personal, stretch=1)
        save = self._action_button("Guardar cambios", self._save_personal)
        fbl.addWidget(save)
        inner.layout().addWidget(fb)

    # Card contraseña 
    def _build_password_card(self):
        card, inner = self._make_card("Seguridad — Cambiar contraseña", "shield")

        pw_row = QWidget(); pw_row.setStyleSheet("background:transparent;")
        pwl    = QHBoxLayout(pw_row); pwl.setContentsMargins(0,0,0,0); pwl.setSpacing(12)

        def pwd_col(label):
            col = QWidget(); col.setStyleSheet("background:transparent;")
            vl  = QVBoxLayout(col); vl.setContentsMargins(0,0,0,0); vl.setSpacing(4)
            lbl = QLabel(label); lbl.setFont(font(11,bold=True))
            lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; background:transparent;")
            vl.addWidget(lbl)
            inp = PasswordInput(width=200)
            vl.addWidget(inp)
            pwl.addWidget(col, stretch=1)
            return inp

        self._pwd_actual  = pwd_col("Contraseña actual")
        self._pwd_nueva   = pwd_col("Nueva contraseña")
        self._pwd_confirm = pwd_col("Confirmar contraseña")
        inner.layout().addWidget(pw_row)

        fb2 = QWidget(); fb2.setStyleSheet("background:transparent;")
        fb2l = QHBoxLayout(fb2); fb2l.setContentsMargins(0, 8, 0, 0)
        self._status_pwd = QLabel("")
        self._status_pwd.setFont(font(11))
        self._status_pwd.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        fb2l.addWidget(self._status_pwd, stretch=1)
        save2 = self._action_button("Actualizar contraseña", self._save_password)
        fb2l.addWidget(save2)
        inner.layout().addWidget(fb2)

    
    def _icon_badge(self, icon_name: str) -> QLabel:
        badge = QLabel()
        badge.setFixedSize(44, 44)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setPixmap(svg_icon(icon_name, 22, PRIMARY))
        badge.setStyleSheet("background:#E8F8FC; border:none; border-radius:22px;")
        return badge

    def _action_button(self, text: str, callback) -> QPushButton:
        button = QPushButton(text)
        button.setFixedHeight(40)
        button.setMinimumWidth(174)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setFont(font(12, bold=True))
        button.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0 20px;
            }}
            QPushButton:hover {{ background: #16A9C3; }}
            QPushButton:pressed {{ background: #0E99B2; }}
        """)
        button.clicked.connect(callback)
        return button

    def _make_card(self, title: str, icon_name: str):
        card = QFrame()
        card.setObjectName("SettingsCard")
        card.setStyleSheet(f"""
            QFrame#SettingsCard {{
                background:{BG_CARD};
                border-radius:{CARD_RADIUS}px;
                border:1px solid {BORDER};
            }}
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(10)

        head = QWidget()
        head.setStyleSheet("background:transparent;")
        head_lay = QHBoxLayout(head)
        head_lay.setContentsMargins(0, 0, 0, 0)
        head_lay.setSpacing(10)
        head_lay.addWidget(self._icon_badge(icon_name))
        tl = QLabel(title); tl.setFont(font(14, bold=True))
        tl.setStyleSheet(f"color:{TEXT_PRIMARY}; background:transparent;")
        head_lay.addWidget(tl)
        head_lay.addStretch()
        cl.addWidget(head)
        cl.addWidget(Divider())

        inner = QWidget(); inner.setStyleSheet("background:transparent;")
        il    = QVBoxLayout(inner); il.setContentsMargins(0, 6, 0, 0); il.setSpacing(12)
        cl.addWidget(inner)
        self._lay.addWidget(card)
        return card, inner


    def _load_profile(self):
        num_doc = self._user.get("num_doc")
        if not num_doc: return
        try:
            p = PersonaModel.get_by_doc(num_doc)
            if not p: return
            self._num_doc_inp.set(str(p.get("num_doc","")))
            self._nombres.set(p.get("nombres",""))
            self._apellidos.set(p.get("p_ape",""))
            self._tel.set(p.get("tel","") or "")
            self._email.set(p.get("email","") or "")
            td = p.get("tip_doc","")
            if td in TIPOS_DOC: self._tip_doc_dd.set(td)
            ts = p.get("tip_sang","") or ""
            if ts in TIPOS_SANGRE: self._tip_sang_dd.set(ts)
            sx = p.get("sexo","") or ""
            if sx in SEXOS: self._sexo_dd.set(sx)
            missing = []
            if not ts: missing.append("tipo de sangre")
            if not sx: missing.append("sexo")
            is_admin = self._user.get("id_rol") == 2 or self._user.get("nom_rol") == "Administrador"
            if missing and is_admin:
                self._profile_reminder.setText(
                    "Completa tus datos personales: falta " + " y ".join(missing)
                    + ". Esta información es necesaria para mantener tu perfil actualizado.")
                self._profile_reminder.show()
        except Exception as e:
            self._show_status(self._status_personal, f"Error: {e}", error=True)


    def _save_personal(self):
        nombres   = self._nombres.get().strip()
        apellidos = self._apellidos.get().strip()
        if not nombres or not apellidos:
            self._show_status(self._status_personal,
                              "⚠ Nombres y apellidos son obligatorios.", error=True)
            return
        tel = self._tel.get().strip()
        email = self._email.get().strip()
        if tel and not re.fullmatch(r"\d{7,15}", tel):
            self._show_status(self._status_personal, "⚠ El teléfono debe tener entre 7 y 15 dígitos.", error=True)
            return
        if email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            self._show_status(self._status_personal, "⚠ El correo electrónico no es válido.", error=True)
            return
        num_doc = self._user.get("num_doc")
        data = {
            "tip_doc":   self._tip_doc_dd.get(),
            "nombres":   nombres,
            "p_ape":     apellidos,
            "tel":       tel or None,
            "email":     email or None,
            "tip_sang":  self._tip_sang_dd.get() or None,
            "sexo":      self._sexo_dd.get() or None,
            "fecha_nac": None,
        }
        try:
            PersonaModel.update(num_doc, data)
            self._show_status(self._status_personal, "✓ Datos guardados correctamente.")
            if data["tip_sang"] and data["sexo"]:
                self._profile_reminder.hide()
            if self._on_profile_update:
                self._on_profile_update({"nombres": nombres, "p_ape": apellidos})
        except Exception as e:
            self._show_status(self._status_personal, f"⚠ Error: {e}", error=True)

    def _save_password(self):
        actual  = self._pwd_actual.get()
        nueva   = self._pwd_nueva.get()
        confirm = self._pwd_confirm.get()
        if not actual or not nueva or not confirm:
            self._show_status(self._status_pwd, "⚠ Completa los tres campos.", error=True); return
        if nueva != confirm:
            self._show_status(self._status_pwd, "⚠ Las contraseñas no coinciden.", error=True); return
        if (len(nueva) < 6 or not re.search(r"[A-Z]", nueva)
                or not re.search(r"[a-z]", nueva) or not re.search(r"\d", nueva)
                or not re.search(r"[^A-Za-z0-9]", nueva)):
            self._show_status(
                self._status_pwd,
                "⚠ Debe tener 6+ caracteres, mayúscula, minúscula, número y símbolo.",
                error=True)
            return
        num_doc = self._user.get("num_doc")
        if not CuentaModel.verify_password(num_doc, actual):
            self._show_status(self._status_pwd, "⚠ La contraseña actual es incorrecta.", error=True); return
        try:
            cuenta = CuentaModel.get_by_doc(num_doc)
            CuentaModel.update_password(cuenta["id_cuenta"], nueva)
            for inp in [self._pwd_actual, self._pwd_nueva, self._pwd_confirm]:
                inp.clear()
            self._show_status(self._status_pwd, "✓ Contraseña actualizada correctamente.")
        except Exception as e:
            self._show_status(self._status_pwd, f"⚠ Error: {e}", error=True)

    def _show_status(self, lbl: QLabel, text: str, error: bool = False):
        lbl.setStyleSheet(
            f"color:{ERROR if error else SUCCESS_TEXT}; background:transparent;")
        lbl.setText(text)
        def clear_status():
            try:
                lbl.setText("")
                lbl.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
            except RuntimeError:
                pass

        QTimer.singleShot(5000, clear_status)
