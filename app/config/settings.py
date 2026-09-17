"""
Configuración central de la aplicación SAIA Admin.
Paleta de diseño: modo claro, Work Sans, gradiente celeste→verde menta.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ── Rutas base ─────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"
load_dotenv(ENV_FILE)
print("[DEBUG] ROOT_DIR:", ROOT_DIR)
print("[DEBUG] ENV_FILE:", ENV_FILE)
print("[DEBUG] .env existe:", ENV_FILE.exists())
print("[DEBUG] DB_SAIA_PORT:", repr(os.getenv("DB_SAIA_PORT")))
print("[DEBUG] DB_SAIA_PASSWORD:", repr(os.getenv("DB_SAIA_PASSWORD")))

# ── Base de datos ───────────────────────────────────────────────────────────────
DB_SAIA = {
    "host":     os.getenv("DB_SAIA_HOST", "127.0.0.1"),
    "port":     int(os.getenv("DB_SAIA_PORT", "3307")),
    "user":     os.getenv("DB_SAIA_USER", "root"),
    "password": os.getenv("DB_SAIA_PASSWORD", ""),
    "database": os.getenv("DB_SAIA_NAME", "saia"),
    "charset":  "utf8mb4",
    "autocommit": True,
}

DB_SENA = {
    "host":     os.getenv("DB_SENA_HOST", "127.0.0.1"),
    "port":     int(os.getenv("DB_SENA_PORT", "3307")),
    "user":     os.getenv("DB_SENA_USER", "root"),
    "password": os.getenv("DB_SENA_PASSWORD", ""),
    "database": os.getenv("DB_SENA_NAME", "sena"),
    "charset":  "utf8mb4",
    "autocommit": True,
}

# ── Paleta de colores — MODO CLARO ──────────────────────────────────────────────
# Gradiente principal: #33BEDC (celeste) → #42EDB5 (verde menta)
COLORS = {
    # Primarios
    "primary":          "#33BEDC",
    "primary_hover":    "#28A8C8",
    "primary_dark":     "#1E8FAA",
    "secondary":        "#42EDB5",
    "secondary_hover":  "#35D4A0",
    "gradient_start":   "#33BEDC",
    "gradient_end":     "#42EDB5",

    # Fondos — CLAROS
    "bg_app":           "#F5F7FA",   # fondo general de la app
    "bg_sidebar":       "#FFFFFF",   # sidebar blanco
    "bg_card":          "#FFFFFF",   # tarjetas blancas
    "bg_header":        "#FFFFFF",   # header blanco
    "bg_input":         "#F8FAFC",   # inputs
    "bg_input_focus":   "#FFFFFF",
    "bg_hover":         "#EBF9FC",   # hover suave celeste
    "bg_active":        "#E0F7FA",   # ítem activo sidebar
    "bg_primary_pale":  "#E8F8FC",   # fondo badge primario

    # Texto
    "text_primary":     "#1A1A2E",   # casi negro
    "text_secondary":   "#4B5563",   # gris oscuro
    "text_muted":       "#9CA3AF",   # gris claro
    "text_on_gradient": "#FFFFFF",   # texto sobre botón gradiente
    "text_primary_color":"#33BEDC",  # texto en color primario

    # Estados
    "success":          "#42EDB5",
    "success_bg":       "#E8FBF5",
    "success_text":     "#0D7A54",
    "warning":          "#F59E0B",
    "warning_bg":       "#FEF3C7",
    "warning_text":     "#92400E",
    "error":            "#EF4444",
    "error_bg":         "#FEE2E2",
    "error_text":       "#991B1B",
    "info":             "#33BEDC",
    "info_bg":          "#E8F8FC",
    "info_text":        "#1E6B8A",

    # Bordes y separadores
    "border":           "#E5E7EB",
    "border_focus":     "#33BEDC",
    "divider":          "#F3F4F6",
    "shadow":           "#00000014",  # sombra suave

    # Tabla
    "table_header_bg":  "#F8FAFC",
    "table_header_text":"#6B7280",
    "table_row_even":   "#FFFFFF",
    "table_row_odd":    "#F9FAFB",
    "table_row_hover":  "#EBF9FC",
    "table_selected":   "#E0F7FA",
    "table_border":     "#F3F4F6",
}

# ── Tipografía — Work Sans ──────────────────────────────────────────────────────
# Work Sans no viene con Windows, se usa Segoe UI como fallback
FONTS = {
    "family":        "Segoe UI",       # fallback; en el código intentamos Work Sans
    "heading1":      ("Segoe UI", 28, "bold"),
    "heading2":      ("Segoe UI", 22, "bold"),
    "heading3":      ("Segoe UI", 18, "bold"),
    "subtitle":      ("Segoe UI", 14, "bold"),
    "body":          ("Segoe UI", 13),
    "body_bold":     ("Segoe UI", 13, "bold"),
    "small":         ("Segoe UI", 11),
    "small_bold":    ("Segoe UI", 11, "bold"),
    "tiny":          ("Segoe UI", 10),
    "button":        ("Segoe UI", 13, "bold"),
    "input":         ("Segoe UI", 13),
    "table_header":  ("Segoe UI", 11, "bold"),
    "table_cell":    ("Segoe UI", 12),
    "badge":         ("Segoe UI", 10, "bold"),
    "nav_item":      ("Segoe UI", 13),
    "nav_item_bold": ("Segoe UI", 13, "bold"),
}

# ── Dimensiones ─────────────────────────────────────────────────────────────────
SIZES = {
    "window_width":      1280,
    "window_height":     780,
    "window_min_width":  1024,
    "window_min_height": 640,

    "sidebar_width":     240,
    "header_height":     60,

    "btn_height":        40,
    "btn_height_sm":     32,
    "btn_height_lg":     46,
    "btn_radius":        20,       # píldora
    "btn_radius_sm":     16,
    "input_height":      42,
    "input_radius":      10,
    "card_radius":       16,
    "card_radius_sm":    10,
    "badge_radius":      12,

    "pad_xs":  4,
    "pad_sm":  8,
    "pad_md":  16,
    "pad_lg":  24,
    "pad_xl":  32,

    "table_row_height":    38,
    "table_header_height": 40,
}

# ── Información de la app ───────────────────────────────────────────────────────
APP = {
    "name":          "SAIA Admin",
    "version":       "1.0.0",
    "full_name":     "Sistema de Autogestión de Ingreso y Acceso",
    "logo_gradient": str(ROOT_DIR / "src" / "logos" / "LogoGradiente.png"),
    "logo_white":    str(ROOT_DIR / "src" / "logos" / "LogoBlanco.png"),
    "exports_dir":   str(ROOT_DIR / "exports"),
}

# Único administrador autorizado para administrar cuentas administradoras.
SUPERADMIN_DOC = 71654321


def is_superadmin(num_doc) -> bool:
    """True únicamente para la cuenta administradora principal."""
    try:
        return int(num_doc) == SUPERADMIN_DOC
    except (TypeError, ValueError):
        return False

Path(APP["exports_dir"]).mkdir(exist_ok=True)
