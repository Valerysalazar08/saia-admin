
from pathlib import Path
from PyQt6.QtGui import (
    QFont, QColor, QPixmap, QPainter, QBrush, QLinearGradient, QPen,
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtSvg import QSvgRenderer

# Rutas 
ROOT_DIR      = Path(__file__).resolve().parent.parent.parent
ICONS_DIR     = ROOT_DIR / "src" / "icons"
LOGO_GRADIENT = ROOT_DIR / "src" / "logos" / "LogoGradiente.png"
LOGO_WHITE    = ROOT_DIR / "src" / "logos" / "LogoBlanco.png"

# Colores 
PRIMARY         = "#33BEDC"
PRIMARY_HOVER   = "#28A8C8"
PRIMARY_DARK    = "#1E8FAA"
SECONDARY       = "#42EDB5"
SECONDARY_HOVER = "#35D4A0"

BG_APP          = "#F5F7FA"
BG_CARD         = "#FFFFFF"
BG_SIDEBAR      = "#FFFFFF"
BG_INPUT        = "#F8FAFC"
BG_HOVER        = "#EBF9FC"
BG_ACTIVE       = "#E0F7FA"
BG_PALE         = "#E8F8FC"

BORDER          = "#E5E7EB"
BORDER_FOCUS    = "#33BEDC"
DIVIDER         = "#F3F4F6"

TEXT_PRIMARY    = "#1A1A2E"
TEXT_SECONDARY  = "#4B5563"
TEXT_MUTED      = "#9CA3AF"

ERROR           = "#EF4444"
ERROR_BG        = "#FEE2E2"
ERROR_TEXT      = "#991B1B"
WARNING         = "#F59E0B"
WARNING_BG      = "#FEF3C7"
WARNING_TEXT    = "#92400E"
SUCCESS         = "#42EDB5"
SUCCESS_BG      = "#E8FBF5"
SUCCESS_TEXT    = "#0D7A54"
INFO            = "#33BEDC"
INFO_BG         = "#E8F8FC"
INFO_TEXT       = "#1E6B8A"

TABLE_HEADER_BG   = "#F8FAFC"
TABLE_HEADER_TEXT = "#6B7280"
TABLE_ROW_EVEN    = "#FFFFFF"
TABLE_ROW_ODD     = "#F9FAFB"
TABLE_ROW_HOVER   = "#EBF9FC"
TABLE_SELECTED    = "#E0F7FA"

SIDEBAR_WIDTH  = 240
HEADER_HEIGHT  = 60
BTN_HEIGHT     = 40
BTN_HEIGHT_SM  = 32
BTN_HEIGHT_LG  = 46
BTN_RADIUS     = 20
BTN_RADIUS_SM  = 16
INPUT_HEIGHT   = 42
INPUT_RADIUS   = 10
CARD_RADIUS    = 16
BADGE_RADIUS   = 12



def font(size: int = 13, bold: bool = False, family: str = "Segoe UI") -> QFont:
    """Devuelve un QFont. Tamaños reducidos para mejor densidad visual."""
    adjusted = max(8, size - 2)
    f = QFont(family, adjusted)
    if bold:
        f.setWeight(QFont.Weight.Bold)
    return f


def svg_icon(name: str, size: int, color: str) -> QPixmap:
    svg_path = ICONS_DIR / f"{name}.svg"
    if not svg_path.exists():
        px = QPixmap(size, size)
        px.fill(Qt.GlobalColor.transparent)
        return px

    svg_data = svg_path.read_text(encoding="utf-8")
    svg_data = svg_data.replace("currentColor", color)
    svg_data = svg_data.replace('stroke-width="2"', 'stroke-width="2.2"')

    render_size = size * 2
    px = QPixmap(render_size, render_size)
    px.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(svg_data.encode("utf-8"))
    painter = QPainter(px)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    renderer.render(painter, QRectF(0, 0, render_size, render_size))
    painter.end()

    return px.scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def paint_gradient_btn(
    painter: QPainter,
    rect,
    hovered: bool = False,
    radius: int = 25,
) -> None:
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    grad = QLinearGradient(0, 0, rect.width(), 0)
    if hovered:
        grad.setColorAt(0, QColor(PRIMARY_HOVER))
        grad.setColorAt(1, QColor(SECONDARY_HOVER))
    else:
        grad.setColorAt(0, QColor(PRIMARY))
        grad.setColorAt(1, QColor(SECONDARY))
    painter.setBrush(QBrush(grad))
    painter.setPen(QPen(Qt.PenStyle.NoPen))
    painter.drawRoundedRect(QRectF(rect), radius, radius)



def _input_ss(border_color: str) -> str:
    return (
        f"QFrame#SInput{{"
        f"background:{BG_INPUT};"
        f"border:1.5px solid {border_color};"
        f"border-radius:{INPUT_RADIUS}px;}}"
    )


SS_INPUT_NORMAL = _input_ss(BORDER)
SS_INPUT_FOCUS  = _input_ss(BORDER_FOCUS)
SS_INPUT_ERROR  = _input_ss(ERROR)

SS_CARD = (
    f"QFrame{{background:{BG_CARD};"
    f"border-radius:{CARD_RADIUS}px;"
    f"border:1px solid {BORDER};}}"
)
