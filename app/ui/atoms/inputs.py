
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLineEdit, QLabel, QHBoxLayout, QVBoxLayout,
    QPushButton, QComboBox, QSizePolicy,
)
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import Qt, QEvent, QSize

from app.ui.theme import (
    BG_INPUT, BG_HOVER, BORDER, BORDER_FOCUS, ERROR,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, PRIMARY, PRIMARY_HOVER,
    INPUT_HEIGHT, INPUT_RADIUS,
    font, svg_icon,
)



def _frame_ss(border: str) -> str:
    return (
        f"QFrame#FInput{{background:{BG_INPUT};"
        f"border:1.5px solid {border};"
        f"border-radius:{INPUT_RADIUS}px;}}"
        f"QFrame#FInput:disabled{{background:#F1F5F9;"
        f"border:1.5px solid {BORDER};}}"
    )


_SS_NORMAL = _frame_ss(BORDER)
_SS_FOCUS  = _frame_ss(BORDER_FOCUS)
_SS_ERROR  = _frame_ss(ERROR)

_ENTRY_SS = f"""
    QLineEdit {{
        background: transparent;
        border: none;
        color: {TEXT_PRIMARY};
        font-family: 'Segoe UI';
        font-size: 13px;
    }}
    QLineEdit:disabled {{ color: {TEXT_MUTED}; }}
"""



class TextInput(QFrame):
    """Campo de texto estilizado con borde que resalta al enfocar."""

    def __init__(self, placeholder: str = "", parent=None,
                 width: int = 220, height: int = None):
        super().__init__(parent)
        self.setObjectName("FInput")
        self.setFixedHeight(height or INPUT_HEIGHT)
        if width:
            self.setMinimumWidth(width)
        self.setStyleSheet(_SS_NORMAL)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(0)

        self._edit = QLineEdit()
        self._edit.setPlaceholderText(placeholder)
        self._edit.setStyleSheet(_ENTRY_SS)
        self._edit.installEventFilter(self)
        lay.addWidget(self._edit)

        self._has_error = False

    def eventFilter(self, obj, event):
        if obj is self._edit:
            if event.type() == QEvent.Type.FocusIn:
                if not self._has_error:
                    self.setStyleSheet(_SS_FOCUS)
            elif event.type() == QEvent.Type.FocusOut:
                if not self._has_error:
                    self.setStyleSheet(_SS_NORMAL)
        return super().eventFilter(obj, event)

    def text(self) -> str:
        return self._edit.text()

    def get(self) -> str:
        return self._edit.text()

    def setText(self, v: str):
        self._edit.setText(str(v) if v is not None else "")

    def set(self, v: str):
        self.setText(v)

    def clear(self):
        self._edit.clear()
        self.clear_error()

    def set_error(self, _msg: str = ""):
        self._has_error = True
        self.setStyleSheet(_SS_ERROR)

    def clear_error(self):
        self._has_error = False
        self.setStyleSheet(_SS_NORMAL)

    def setPlaceholder(self, text: str):
        self._edit.setPlaceholderText(text)

    @property
    def entry(self):
        return self._edit



class PasswordInput(QFrame):
    """Campo de contraseña con botón ojo."""

    def __init__(self, placeholder: str = "Contraseña", parent=None,
                 width: int = 220, height: int = None):
        super().__init__(parent)
        self.setObjectName("FInput")
        self.setFixedHeight(height or INPUT_HEIGHT)
        if width:
            self.setMinimumWidth(width)
        self.setStyleSheet(_SS_NORMAL)
        self._has_error = False
        self._visible = False

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 8, 0)
        lay.setSpacing(4)

        self._edit = QLineEdit()
        self._edit.setPlaceholderText(placeholder)
        self._edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._edit.setStyleSheet(_ENTRY_SS)
        self._edit.installEventFilter(self)
        lay.addWidget(self._edit, stretch=1)

        self._eye = QPushButton()
        self._eye.setFixedSize(28, 28)
        self._eye.setStyleSheet(
            f"background:transparent; border:none; color:{TEXT_MUTED};")
        self._eye.setCursor(Qt.CursorShape.PointingHandCursor)
        self._eye.clicked.connect(self._toggle)
        self._refresh_eye()
        lay.addWidget(self._eye)

    def _refresh_eye(self):
        px = svg_icon("eye-off" if self._visible else "eye", 18, TEXT_MUTED)
        self._eye.setIcon(QIcon(px))
        self._eye.setIconSize(QSize(18, 18))

    def _toggle(self):
        self._visible = not self._visible
        self._edit.setEchoMode(
            QLineEdit.EchoMode.Normal if self._visible
            else QLineEdit.EchoMode.Password)
        self._refresh_eye()

    def eventFilter(self, obj, event):
        if obj is self._edit:
            if event.type() == QEvent.Type.FocusIn:
                if not self._has_error:
                    self.setStyleSheet(_SS_FOCUS)
            elif event.type() == QEvent.Type.FocusOut:
                if not self._has_error:
                    self.setStyleSheet(_SS_NORMAL)
        return super().eventFilter(obj, event)

    def text(self) -> str:    return self._edit.text()
    def get(self) -> str:     return self._edit.text()
    def set(self, v: str):    self._edit.setText(str(v) if v else "")
    def delete(self, *_):     self._edit.clear()
    def clear(self):
        self._edit.clear()
        self.clear_error()

    def set_error(self, _msg=""):
        self._has_error = True
        self.setStyleSheet(_SS_ERROR)

    def clear_error(self):
        self._has_error = False
        self.setStyleSheet(_SS_NORMAL)

    def toggle_visibility(self):
        self._toggle()

    @property
    def entry(self):
        return self._edit



class SearchInput(QFrame):
    """Campo de búsqueda con icono de lupa."""

    def __init__(self, placeholder: str = "Buscar...", parent=None,
                 width: int = 280, on_change=None):
        super().__init__(parent)
        self.setObjectName("FInput")
        self.setFixedHeight(INPUT_HEIGHT)
        self.setMinimumWidth(width)
        self.setStyleSheet(_SS_NORMAL)
        self._on_change = on_change

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(6)

        # Icono lupa
        ic = QLabel()
        ic.setPixmap(svg_icon("search", 16, TEXT_MUTED))
        ic.setFixedSize(16, 16)
        ic.setStyleSheet("background:transparent;")
        lay.addWidget(ic)

        self._edit = QLineEdit()
        self._edit.setPlaceholderText(placeholder)
        self._edit.setStyleSheet(_ENTRY_SS)
        self._edit.installEventFilter(self)
        if on_change:
            self._edit.textChanged.connect(on_change)
        lay.addWidget(self._edit, stretch=1)

    def eventFilter(self, obj, event):
        if obj is self._edit:
            if event.type() == QEvent.Type.FocusIn:
                self.setStyleSheet(_SS_FOCUS)
            elif event.type() == QEvent.Type.FocusOut:
                self.setStyleSheet(_SS_NORMAL)
        return super().eventFilter(obj, event)

    def get(self) -> str:  return self._edit.text()
    def set(self, v: str): self._edit.setText(str(v) if v else "")
    def clear(self):       self._edit.clear()



class Dropdown(QComboBox):
    """QComboBox estilizado con la paleta SAIA."""

    def __init__(self, values: list = None, parent=None,
                 width: int = 200, command=None):
        super().__init__(parent)
        self.setFixedHeight(INPUT_HEIGHT)
        if width:
            self.setMinimumWidth(width)
        self.setFont(font(13))
        self.setStyleSheet(f"""
            QComboBox {{
                background: {BG_INPUT};
                color: {TEXT_PRIMARY};
                border: 1.5px solid {BORDER};
                border-radius: {INPUT_RADIUS}px;
                padding: 0 12px;
                font-size: 13px;
            }}
            QComboBox:focus {{
                border-color: {BORDER_FOCUS};
            }}
            QComboBox:disabled {{
                background: #F1F5F9;
                color: {TEXT_MUTED};
                border-color: {BORDER};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 28px;
            }}
            QAbstractItemView {{
                background: white;
                border: 1px solid {BORDER};
                border-radius: 8px;
                selection-background-color: {BG_HOVER};
                selection-color: {TEXT_PRIMARY};
                color: {TEXT_PRIMARY};
                padding: 4px;
            }}
        """)
        if values:
            self.addItems([str(v) for v in values])
        if command:
            self.currentTextChanged.connect(command)

    def get(self) -> str:
        return self.currentText()

    def set(self, value: str):
        idx = self.findText(str(value))
        if idx >= 0:
            self.setCurrentIndex(idx)

    def set_options(self, values: list):
        current = self.currentText()
        self.clear()
        self.addItems([str(v) for v in values])
        self.set(current)



class LabeledInput(QWidget):
    """Label + Input + error message, apilados verticalmente."""

    def __init__(self, label: str, placeholder: str = "",
                 parent=None, width: int = 220,
                 required: bool = False, password: bool = False):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        # Label
        lbl_text = f"{label} *" if required else label
        lbl = QLabel(lbl_text)
        lbl.setFont(font(11, bold=True))
        lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; background:transparent;")
        lay.addWidget(lbl)

        # Input
        if password:
            self._input: QFrame = PasswordInput(placeholder, width=width)
        else:
            self._input = TextInput(placeholder, width=width)
        lay.addWidget(self._input)

        # Error label
        self._err = QLabel("")
        self._err.setFont(font(10))
        self._err.setStyleSheet(f"color:{ERROR}; background:transparent;")
        self._err.setFixedHeight(14)
        lay.addWidget(self._err)


    def get(self) -> str:
        return self._input.get()

    def set(self, value: str):
        self._input.set(str(value) if value is not None else "")

    def clear(self):
        self._input.clear()
        self.clear_error()

    def set_error(self, message: str = ""):
        self._input.set_error()
        self._err.setText(f"  {message}" if message else "")

    def clear_error(self):
        self._input.clear_error()
        self._err.setText("")

    @property
    def entry(self):
        return self._input.entry

    def set_editable(self, editable: bool):
        self._input.setEnabled(editable)
