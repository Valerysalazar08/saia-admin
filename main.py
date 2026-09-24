"""
SAIA Admin — Punto de entrada principal (PyQt6).
Ejecutar:  python main.py

Orden crítico en Windows con mysql-connector + PyQt6:
  1. Importar BD (mysql-connector) ANTES de QApplication
  2. Crear QApplication
  3. Recién entonces importar módulos de interfaz y vistas.
"""
import sys
import os
import logging
import ctypes
from pathlib import Path


import matplotlib
matplotlib.use("Agg")

# Forzar DPI 96 (100%) para que los tamaños sean exactos
os.environ["QT_SCALE_FACTOR"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"


from app.config.database import db_saia, db_sena
from app.config.settings import APP


def configure_diagnostics():
    """Registra errores de Python y Qt sin ocultarlos detrás de la UI."""
    log_path = Path(__file__).with_name("saia-debug.log")
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    def uncaught_exception(exc_type, exc_value, exc_traceback):
        logging.getLogger("saia").exception(
            "Excepción no controlada", exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = uncaught_exception
    logging.getLogger("saia").setLevel(logging.INFO)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)


def check_connections() -> bool:
    print("[SAIA] Verificando conexiones a la base de datos…")
    if not db_saia.test_connection():
        print("[SAIA] ✗ No se pudo conectar a la BD saia.")
        print("       Revisa .env — DB_SAIA_HOST, DB_SAIA_USER, DB_SAIA_PASSWORD")
        return False
    if not db_sena.test_connection():
        print("[SAIA] ✗ No se pudo conectar a la BD sena.")
        print("       Revisa .env — DB_SENA_HOST, DB_SENA_USER, DB_SENA_PASSWORD")
        return False
    print("[SAIA] ✓ Conexiones establecidas.")
    return True


if __name__ == "__main__":
    configure_diagnostics()
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "SENA.SAIA.Admin")
        except Exception:
            pass
  
    if not check_connections():
        print("\n[SAIA] La aplicación no puede iniciar sin conexión a la BD.")
        sys.exit(1)


    from PyQt6.QtWidgets import QApplication, QToolTip
    from PyQt6.QtCore import qInstallMessageHandler, QtMsgType
    from PyQt6.QtGui import QColor, QPalette
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    def qt_message_handler(mode, context, message):
        level = logging.WARNING if mode in (
            QtMsgType.QtWarningMsg, QtMsgType.QtCriticalMsg, QtMsgType.QtFatalMsg
        ) else logging.INFO
        logging.getLogger("qt").log(level, "%s", message)

    qInstallMessageHandler(qt_message_handler)


    tooltip_palette = QToolTip.palette()
    for color_group in (QPalette.ColorGroup.Active,
                        QPalette.ColorGroup.Inactive,
                        QPalette.ColorGroup.Disabled):
        tooltip_palette.setColor(
            color_group, QPalette.ColorRole.ToolTipBase, QColor("#FFFFFF"))
        tooltip_palette.setColor(
            color_group, QPalette.ColorRole.ToolTipText, QColor("#1A1A2E"))
    QToolTip.setPalette(tooltip_palette)


    app.setStyleSheet(f"""
        QScrollBar:vertical {{
            background: transparent;
            width: 6px;
            margin: 4px 2px 4px 0;
            border-radius: 3px;
        }}
        QScrollBar::handle:vertical {{
            background: #D1D5DB;
            border-radius: 3px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #9CA3AF;
        }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{ height: 0px; }}
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {{ background: transparent; }}
        QScrollBar:horizontal {{
            background: transparent;
            height: 6px;
            margin: 0 0 2px 4px;
            border-radius: 3px;
        }}
        QScrollBar::handle:horizontal {{
            background: #D1D5DB;
            border-radius: 3px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: #9CA3AF;
        }}
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{ width: 0px; }}
        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal {{ background: transparent; }}
        QToolTip {{
            background: #FFFFFF;
            color: #1A1A2E;
            border: 1px solid #33BEDC;
            border-radius: 6px;
            padding: 5px 8px;
            font-size: 11px;
        }}
    """)


    from PyQt6.QtWidgets import QWidget, QVBoxLayout
    from PyQt6.QtGui import QIcon
    from app.ui.theme import LOGO_GRADIENT, BG_APP
    from app.ui.views.login_view import LoginView


    try:
        from app.models.auditoria_model import AuditoriaModel
        if not AuditoriaModel.table_exists():
            AuditoriaModel.create_table()
            print("[SAIA] Tabla auditoria_actividad creada.")
    except Exception as e:
        print(f"[SAIA] Advertencia BD: {e}")


    win = QWidget()
    win.setWindowTitle(f"{APP['name']} — {APP['full_name']}")
    win.setMinimumSize(1024, 640)
    win.setStyleSheet(f"background:{BG_APP};")
    if LOGO_GRADIENT.exists():
        saia_icon = QIcon(str(LOGO_GRADIENT))
        app.setWindowIcon(saia_icon)
        win.setWindowIcon(saia_icon)

    root_layout = QVBoxLayout(win)
    root_layout.setContentsMargins(0, 0, 0, 0)
    root_layout.setSpacing(0)

    _current = {"widget": None}

    def swap_to(widget: QWidget):
        if _current["widget"]:
            root_layout.removeWidget(_current["widget"])
            _current["widget"].deleteLater()
        _current["widget"] = widget
        root_layout.addWidget(widget)

    def show_login():
        swap_to(LoginView(on_login_success=on_login))

    def on_login(user_data: dict):
        from app.ui.templates.main_window import MainWindow
        swap_to(MainWindow(user_data=user_data, on_logout=show_login))

    show_login()
    win.showMaximized()
    sys.exit(app.exec())
