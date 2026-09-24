
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QScrollArea, QSizePolicy,
)
from PyQt6.QtCore import Qt
from app.ui.theme import (
    BG_CARD, BG_INPUT, BG_HOVER, BORDER,
    TABLE_HEADER_BG, TABLE_HEADER_TEXT,
    TABLE_ROW_EVEN, TABLE_ROW_ODD, TABLE_SELECTED,
    TEXT_PRIMARY, TEXT_MUTED, TEXT_SECONDARY,
    PRIMARY, CARD_RADIUS,
    font,
)

PAGE_SIZE = 25


class DataTable(QWidget):
    
    def __init__(self, parent=None, columns: list = None,
                 on_select=None, on_double_click=None,
                 row_height: int = 52, page_size: int = PAGE_SIZE):
        super().__init__(parent)
        self._columns      = columns or []
        self._on_select    = on_select
        self._on_dbl       = on_double_click
        self._row_height   = row_height
        self._has_wrapped_columns = any(col.get("wrap", False) for col in self._columns)
        self._page_size    = page_size
        self._rows_data: list[dict] = []
        self._page         = 0
        self._selected_idx = None
        self._row_widgets: list[QFrame] = []

        self.setStyleSheet(f"""
            QWidget {{
                background: {BG_CARD};
                border-radius: {CARD_RADIUS}px;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Cabecera 
        self._header = QFrame()
        self._header.setFixedHeight(40)
        self._header.setStyleSheet(f"""
            QFrame {{
                background: {TABLE_HEADER_BG};
                border-bottom: 1px solid {BORDER};
                border-radius: 0;
            }}
        """)
        root.addWidget(self._header)
        self._build_header()

        # Cuerpo scrolleable 
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet("background: transparent;")

        self._body_widget = QWidget()
        self._body_widget.setStyleSheet("background: transparent;")
        self._body_layout = QVBoxLayout(self._body_widget)
        # Filas tipo tarjeta en todas las vistas: más aire, lectura más fácil.
        row_gap = 6
        self._body_layout.setContentsMargins(0, row_gap, 0, row_gap)
        self._body_layout.setSpacing(row_gap)
        self._body_layout.addStretch()

        self._scroll.setWidget(self._body_widget)
        root.addWidget(self._scroll, stretch=1)

        self._footer = QFrame()
        self._footer.setFixedHeight(38)
        self._footer.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border-top: 1px solid {BORDER};
            }}
        """)
        root.addWidget(self._footer)
        self._build_footer()


    def _build_header(self):
        # Limpiar
        old = self._header.layout()
        if old:
            while old.count():
                item = old.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(old)

        lay = QHBoxLayout(self._header)
        lay.setContentsMargins(8, 0, 8, 0)
        lay.setSpacing(0)

        n = QLabel("#")
        n.setFixedWidth(36)
        n.setAlignment(Qt.AlignmentFlag.AlignCenter)
        n.setFont(font(11, bold=True))
        n.setStyleSheet(f"color:{TABLE_HEADER_TEXT}; background:transparent;")
        lay.addWidget(n)

        for col in self._columns:
            lbl = QLabel(col["header"])
            # Algunas tablas pueden reservar un poco más de ancho visual en
            # la cabecera, sin sacrificar el área útil de la celda.
            lbl.setFixedWidth(col.get("header_width", col.get("width", 120)))
            lbl.setFont(font(11, bold=True))
            lbl.setStyleSheet(
                f"color:{TABLE_HEADER_TEXT}; background:transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter |
                             Qt.AlignmentFlag.AlignLeft)
            lay.addWidget(lbl)

        lay.addStretch()


    def _build_footer(self):
        old = self._footer.layout()
        if old:
            while old.count():
                item = old.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(old)

        lay = QHBoxLayout(self._footer)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(4)

        total = len(self._rows_data)
        total_pages = max(1, -(-total // self._page_size))
        start = self._page * self._page_size + 1
        end   = min(start + self._page_size - 1, total)

        info_text = f"{start}–{end} de {total}" if total > 0 else "Sin resultados"
        info = QLabel(info_text)
        info.setFont(font(10))
        info.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        lay.addWidget(info)
        lay.addStretch()

        page_lbl = QLabel(f"Pág. {self._page + 1}/{total_pages}")
        page_lbl.setFont(font(10))
        page_lbl.setStyleSheet(f"color:{TEXT_MUTED}; background:transparent;")
        lay.addWidget(page_lbl)

        btn_ss = f"""
            QPushButton {{
                background: {BG_INPUT};
                color: {TEXT_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{ background: {BG_HOVER}; }}
        """
        for sym, fn in [("«", self._first), ("‹", self._prev),
                        ("›", self._next),  ("»", self._last)]:
            b = QPushButton(sym)
            b.setFixedSize(28, 26)
            b.setStyleSheet(btn_ss)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(fn)
            lay.addWidget(b)


    def _total_pages(self):
        return max(1, -(-len(self._rows_data) // self._page_size))

    def _first(self):
        if self._page != 0:
            self._page = 0
            self._render_page()

    def _last(self):
        lp = self._total_pages() - 1
        if self._page != lp:
            self._page = lp
            self._render_page()

    def _next(self):
        if self._page < self._total_pages() - 1:
            self._page += 1
            self._render_page()

    def _prev(self):
        if self._page > 0:
            self._page -= 1
            self._render_page()



    def _render_page(self):
        for w in self._row_widgets:
            w.setParent(None)
            w.deleteLater()
        self._row_widgets.clear()
        self._selected_idx = None

        stretch = self._body_layout.takeAt(self._body_layout.count() - 1)

        start = self._page * self._page_size
        page_rows = self._rows_data[start: start + self._page_size]

        for local_i, row in enumerate(page_rows):
            global_i = start + local_i
            even = local_i % 2 == 0
            bg   = TABLE_ROW_EVEN if even else TABLE_ROW_ODD

            row_frame = QFrame()
            row_frame.setFixedHeight(self._row_height)
            radius = 10
            row_frame.setStyleSheet(
                f"QFrame{{background:{bg}; border:none; border-radius:{radius}px;}}")

            lay = QHBoxLayout(row_frame)
            vertical_padding = 7 if self._row_height >= 60 else 5
            lay.setContentsMargins(8, vertical_padding, 8, vertical_padding)
            lay.setSpacing(0)

            n_lbl = QLabel(str(global_i + 1))
            n_lbl.setFixedWidth(36)
            n_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            n_lbl.setFont(font(12))
            n_lbl.setStyleSheet(
                f"color:{TEXT_MUTED}; background:transparent;")
            lay.addWidget(n_lbl)

            # Columnas
            for col in self._columns:
                val = row.get(col["key"], "")
                w   = col.get("width", 120)

                if "renderer" in col and callable(col["renderer"]):
                    widget = col["renderer"](row_frame, row, val)
                    if widget:
                        widget.setFixedWidth(w)
                        lay.addWidget(widget)
                    else:
                        spacer = QLabel("")
                        spacer.setFixedWidth(w)
                        lay.addWidget(spacer)
                else:
                    cell = QLabel(str(val) if val is not None else "—")
                    cell.setFixedWidth(w)
                    cell.setFont(font(12))
                    cell.setStyleSheet(
                        f"color:{TEXT_PRIMARY}; background:transparent;")
                    wraps = col.get("wrap", False)
                    cell.setWordWrap(wraps)
                    cell.setAlignment(
                        (Qt.AlignmentFlag.AlignTop if wraps else Qt.AlignmentFlag.AlignVCenter) |
                        Qt.AlignmentFlag.AlignLeft
                    )
                    lay.addWidget(cell)

            lay.addStretch()

            row_frame.mousePressEvent = lambda e, idx=local_i: \
                self._select(idx)
            if self._on_dbl:
                row_frame.mouseDoubleClickEvent = lambda e, ri=global_i: \
                    self._on_dbl(self._rows_data[ri])

            self._body_layout.addWidget(row_frame)
            self._row_widgets.append(row_frame)

        # Devolver stretch
        self._body_layout.addStretch()
        self._build_footer()


    def _select(self, local_idx: int):
        if self._selected_idx is not None and \
                self._selected_idx < len(self._row_widgets):
            even = self._selected_idx % 2 == 0
            prev_bg = TABLE_ROW_EVEN if even else TABLE_ROW_ODD
            radius = 10
            self._row_widgets[self._selected_idx].setStyleSheet(
                f"QFrame{{background:{prev_bg}; border:none; border-radius:{radius}px;}}")

        self._selected_idx = local_idx
        radius = 10
        self._row_widgets[local_idx].setStyleSheet(
            f"QFrame{{background:{TABLE_SELECTED}; border:none; border-radius:{radius}px;}}")

        if self._on_select:
            global_idx = self._page * self._page_size + local_idx
            self._on_select(self._rows_data[global_idx])

 

    def load(self, data: list[dict]):
        self._rows_data      = data
        self._page           = 0
        self._selected_idx   = None
        self._render_page()

    def clear(self):
        self.load([])

    def get_selected(self) -> dict | None:
        if self._selected_idx is not None:
            global_idx = self._page * self._page_size + self._selected_idx
            return self._rows_data[global_idx]
        return None

    def get_row_count(self) -> int:
        return len(self._rows_data)
