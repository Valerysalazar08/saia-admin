"""
VISTA Qt — Estadísticas con gráficas matplotlib embebidas.
IMPORTANTE: usar backend Agg (off-screen) + FigureCanvasQTAgg.
NO usar plt.* (pyplot) — provoca ventanas emergentes en Qt.
"""
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QScrollArea,
    QVBoxLayout, QHBoxLayout, QGridLayout,
)
from PyQt6.QtCore import Qt

# Backend off-screen — forzado desde main.py antes de todo
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from app.ui.theme import (
    BG_APP, BG_CARD, BORDER, PRIMARY, SECONDARY, WARNING,
    TEXT_PRIMARY, TEXT_MUTED,
    CARD_RADIUS, font,
)
from app.ui.atoms.buttons import SecondaryButton
from app.ui.atoms.labels  import Heading, Divider
from app.models.historial_model import HistorialModel


class EstadisticasView(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
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

    def _build(self):
        tb = QWidget(); tb.setStyleSheet("background:transparent;")
        tbl = QHBoxLayout(tb); tbl.setContentsMargins(0, 0, 0, 0)
        tbl.addWidget(Heading("Estadísticas", level=2), stretch=1)
        ref = SecondaryButton("↺ Actualizar", width=120, height=34)
        ref.clicked.connect(self._load_charts)
        tbl.addWidget(ref)
        self._lay.addWidget(tb)
        self._lay.addSpacing(16)

        self._grid_widget = QWidget()
        self._grid_widget.setStyleSheet("background:transparent;")
        self._grid_lay = QGridLayout(self._grid_widget)
        self._grid_lay.setContentsMargins(0, 0, 0, 0)
        self._grid_lay.setSpacing(16)
        self._lay.addWidget(self._grid_widget)

        self._load_charts()

    def _load_charts(self):
        # Limpiar gráficas anteriores
        while self._grid_lay.count():
            item = self._grid_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._chart_linea(0, 0, "Ingresos últimos 30 días")
        self._chart_dona(0, 1, "Ingresos por portería")
        self._chart_barras(1, 0, "Distribución por hora del día")
        self._chart_placeholder(1, 1)

    # ── Card contenedor ───────────────────────────────────────────────────────
    def _make_card(self, title: str, row: int, col: int) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border-radius: {CARD_RADIUS}px;
                border: 1px solid {BORDER};
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)

        lbl = QLabel(title)
        lbl.setFont(font(14, bold=True))
        lbl.setStyleSheet(f"color:{TEXT_PRIMARY}; background:transparent;")
        lay.addWidget(lbl)
        lay.addWidget(Divider())

        self._grid_lay.addWidget(card, row, col)
        return card

    def _new_fig(self) -> Figure:
        """Crea una figura con estilo SAIA, sin tocar pyplot."""
        fig = Figure(figsize=(5, 3), dpi=90)
        fig.patch.set_facecolor(BG_CARD)
        return fig

    def _style_ax(self, ax):
        """Aplica el estilo SAIA a un eje."""
        ax.set_facecolor(BG_CARD)
        ax.tick_params(colors=TEXT_MUTED, labelsize=8)
        for sp in ax.spines.values():
            sp.set_edgecolor(BORDER)
        ax.grid(True, alpha=0.3, color=BORDER, linestyle="--")

    def _embed(self, fig: Figure, card: QFrame):
        """Embebe la figura en la tarjeta como widget Qt."""
        canvas = FigureCanvasQTAgg(fig)
        canvas.setMinimumHeight(260)
        card.layout().addWidget(canvas)

    # ── Gráfica 1: Línea — ingresos por día ──────────────────────────────────
    def _chart_linea(self, row: int, col: int, title: str):
        card = self._make_card(title, row, col)
        try:
            data = HistorialModel.ingresos_por_dia(30)
        except Exception:
            data = []

        fig = self._new_fig()
        ax  = fig.add_subplot(111)
        self._style_ax(ax)

        if data:
            fechas  = [str(r["fecha"])[-5:] for r in data]
            totales = [r["total"] for r in data]
            ax.plot(fechas, totales, color=PRIMARY, linewidth=2,
                    marker="o", markersize=4, markerfacecolor=SECONDARY)
            ax.fill_between(range(len(fechas)), totales,
                            alpha=0.15, color=PRIMARY)
            step = max(1, len(fechas) // 6)
            ax.set_xticks(range(0, len(fechas), step))
            ax.set_xticklabels(fechas[::step], rotation=30, fontsize=8,
                               color=TEXT_MUTED)
        else:
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                    color=TEXT_MUTED, transform=ax.transAxes)
            ax.grid(False)

        fig.tight_layout(pad=1.5)
        self._embed(fig, card)

    # ── Gráfica 2: Dona — ingresos por portería ───────────────────────────────
    def _chart_dona(self, row: int, col: int, title: str):
        card = self._make_card(title, row, col)
        try:
            data = HistorialModel.ingresos_por_porteria()
        except Exception:
            data = []

        fig = self._new_fig()
        ax  = fig.add_subplot(111)
        ax.set_facecolor(BG_CARD)

        if data:
            labels  = [r["porteria"] or "Sin portería" for r in data]
            sizes   = [r["total"] for r in data]
            palette = [PRIMARY, SECONDARY, WARNING, "#9B7AFF", "#FF8C5C"]
            colors  = palette[:len(labels)]
            _, texts, autotexts = ax.pie(
                sizes, labels=labels, colors=colors,
                autopct="%1.0f%%", startangle=90,
                wedgeprops={"linewidth": 2, "edgecolor": BG_CARD},
                textprops={"color": TEXT_PRIMARY, "fontsize": 8},
            )
            for at in autotexts:
                at.set_color(TEXT_PRIMARY)
                at.set_fontsize(7)
        else:
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                    color=TEXT_MUTED, transform=ax.transAxes)

        fig.tight_layout(pad=1.5)
        self._embed(fig, card)

    # ── Gráfica 3: Barras — ingresos por hora ────────────────────────────────
    def _chart_barras(self, row: int, col: int, title: str):
        card = self._make_card(title, row, col)
        try:
            data = HistorialModel.ingresos_por_hora()
        except Exception:
            data = []

        fig = self._new_fig()
        ax  = fig.add_subplot(111)
        self._style_ax(ax)
        ax.grid(True, alpha=0.3, axis="y", color=BORDER, linestyle="--")

        if data:
            horas   = [r["hora"] for r in data]
            totales = [r["total"] for r in data]
            bars = ax.bar(horas, totales, color=SECONDARY,
                          edgecolor=BG_CARD, linewidth=0.5)
            for b in bars:
                b.set_alpha(0.85)
            ax.set_xlabel("Hora del día", color=TEXT_MUTED, fontsize=8)
            ax.set_ylabel("Ingresos",     color=TEXT_MUTED, fontsize=8)
            ax.set_xticks(range(0, 24, 2))
        else:
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center",
                    color=TEXT_MUTED, transform=ax.transAxes)
            ax.grid(False)

        fig.tight_layout(pad=1.5)
        self._embed(fig, card)

    # ── Gráfica 4: Placeholder ────────────────────────────────────────────────
    def _chart_placeholder(self, row: int, col: int):
        card = self._make_card("Más métricas próximamente", row, col)
        lbl = QLabel("📊\n\nAquí se mostrarán más gráficas\ncuando haya datos suficientes.")
        lbl.setFont(font(13))
        lbl.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.layout().addWidget(lbl, stretch=1)
