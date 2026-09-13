"""
TEMPLATE Qt — Ventana principal post-login.
Shell: Sidebar izquierdo + Header + área de contenido intercambiable.
"""
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QHBoxLayout, QVBoxLayout,
    QStackedWidget,
)
from PyQt6.QtCore import Qt

from app.ui.organisms.sidebar import Sidebar
from app.ui.organisms.header  import Header
from app.ui.theme import BG_APP, font
from app.config.settings import is_superadmin

VIEW_TITLES = {
    "dashboard":    "Dashboard",
    "aprendices":   "Aprendices",
    "guardas":      "Guardas de Seguridad",
    "historial":    "Historial de Ingresos",
    "insumos":      "Insumos y Equipos",
    "reportes":     "Generador de Reportes",
    "estadisticas": "Estadísticas",
    "auditoria":    "Historial de Auditoría",
    "bloqueo":      "Usuarios Bloqueados",
    "ajustes":      "Editar perfil",
    "administradores": "Administradores",
}


class MainWindow(QWidget):
    """
    Frame principal post-login.
    on_logout se llama cuando el usuario cierra sesión.
    """

    def __init__(self, parent=None, user_data: dict = None, on_logout=None):
        super().__init__(parent)
        self._user      = user_data or {}
        self._on_logout = on_logout or (lambda: None)
        self._view_cache: dict[str, QWidget] = {}
        self._current_id: str | None = None
        self._is_superadmin = is_superadmin(self._user.get("num_doc"))

        self.setStyleSheet(f"background:{BG_APP};")
        self._build()
        self._navigate("dashboard")

    # ─────────────────────────────────────────────────────────────────────────
    # Construcción del shell
    # ─────────────────────────────────────────────────────────────────────────

    def _build(self):
        nombre = (
            f"{self._user.get('nombres','').strip()} "
            f"{self._user.get('p_ape','').strip()}"
        ).strip() or "Administrador"

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar(
            self, on_navigate=self._navigate, admin_name=nombre,
            is_superadmin=self._is_superadmin)
        root.addWidget(self._sidebar)

        # Columna derecha: header + contenido
        right = QWidget()
        right.setStyleSheet(f"background:{BG_APP};")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(0)

        self._header = Header(right)
        right_lay.addWidget(self._header)

        # Área de contenido con stack para cachear vistas
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background:{BG_APP};")
        right_lay.addWidget(self._stack, stretch=1)

        root.addWidget(right, stretch=1)

    # ─────────────────────────────────────────────────────────────────────────
    # Navegación
    # ─────────────────────────────────────────────────────────────────────────

    def _navigate(self, view_id: str):
        if view_id == "logout":
            self._do_logout()
            return
        if view_id in {"administradores", "auditoria"} and not self._is_superadmin:
            return

        if self._current_id == view_id:
            self.refresh_view(view_id)
            return

        # Crear vista si no existe
        is_cached = view_id in self._view_cache
        if not is_cached:
            view = self._create_view(view_id)
            if view is None:
                return
            self._view_cache[view_id] = view
            self._stack.addWidget(view)

        self._stack.setCurrentWidget(self._view_cache[view_id])
        self._current_id = view_id
        self._sidebar.set_active(view_id)
        self._header.set_title(VIEW_TITLES.get(view_id, view_id.title()))
        if is_cached:
            self.refresh_view(view_id)

    def refresh_view(self, view_id: str):
        """Recarga una vista ya creada, sin perder su lugar en el stack."""
        view = self._view_cache.get(view_id)
        refresh = getattr(view, "load_data", None)
        if callable(refresh):
            refresh()

    def _create_view(self, view_id: str) -> QWidget | None:
        """Importa y crea la vista bajo demanda (lazy loading)."""
        try:
            if view_id == "dashboard":
                from app.ui.views.dashboard_view import DashboardView
                return DashboardView()
            elif view_id == "aprendices":
                from app.ui.views.aprendices_view import AprendicesView
                return AprendicesView(session_user=self._user)
            elif view_id == "guardas":
                from app.ui.views.guardas_view import GuardasView
                return GuardasView(session_user=self._user)
            elif view_id == "historial":
                from app.ui.views.historial_view import HistorialView
                return HistorialView()
            elif view_id == "estadisticas":
                from app.ui.views.estadisticas_view import EstadisticasView
                return EstadisticasView()
            elif view_id == "reportes":
                from app.ui.views.reportes_view import ReportesView
                return ReportesView()
            elif view_id == "auditoria":
                from app.ui.views.auditoria_view import AuditoriaView
                return AuditoriaView()
            elif view_id == "bloqueo":
                from app.ui.views.bloqueo_view import BloqueoView
                return BloqueoView(session_user=self._user)
            elif view_id == "insumos":
                from app.ui.views.insumos_view import InsumosView
                return InsumosView()
            elif view_id == "ajustes":
                from app.ui.views.ajustes_view import AjustesView
                return AjustesView(
                    session_user=self._user,
                    on_profile_update=self._on_profile_update)
            elif view_id == "administradores" and self._is_superadmin:
                from app.ui.views.administradores_view import AdministradoresView
                return AdministradoresView(session_user=self._user)
        except Exception as e:
            print(f"[MainWindow] Error cargando vista '{view_id}': {e}")
            return self._placeholder(view_id)
        return None

    def _placeholder(self, view_id: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{BG_APP};")
        lay = QVBoxLayout(w)
        lbl = QLabel(f"Vista '{view_id}' en construcción…")
        lbl.setFont(font(16))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color:#9CA3AF;")
        lay.addWidget(lbl)
        return w

    # ─────────────────────────────────────────────────────────────────────────
    # Callbacks
    # ─────────────────────────────────────────────────────────────────────────

    def _on_profile_update(self, nuevos_datos: dict):
        self._user.update(nuevos_datos)
        nombre = (
            f"{self._user.get('nombres','').strip()} "
            f"{self._user.get('p_ape','').strip()}"
        ).strip()
        self._sidebar.update_admin_name(nombre)

    def _do_logout(self):
        try:
            from app.models.auditoria_model import (
                AuditoriaModel, ACCION_LOGOUT, ENTIDAD_SESION)
            nombre = (
                f"{self._user.get('nombres','').strip()} "
                f"{self._user.get('p_ape','').strip()}"
            ).strip()
            AuditoriaModel.registrar(
                ACCION_LOGOUT, ENTIDAD_SESION, self._user["num_doc"],
                f"Cierre de sesión del administrador {nombre} "
                f"(Doc: {self._user['num_doc']})",
                realizado_por=self._user["num_doc"],
            )
        except Exception:
            pass

        # Destruir vistas cacheadas
        for view in self._view_cache.values():
            view.deleteLater()
        self._view_cache.clear()
        self._on_logout()
