"""Qt GUI v2 premium: matches mock, handles long names, empty states, large lists."""
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QLineEdit, QLabel, QMessageBox, QHeaderView, QAbstractItemView,
    QSizePolicy, QFileDialog
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QFont, QShortcut, QKeySequence, QDesktopServices

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.scanner import scan_loose_files
from src.categorizer import categorize
from src.mover import move_files, undo_last


def human_size(n: int) -> str:
    n = int(n)
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024 or unit == "GB":
            return f"{n} B" if unit == "B" else f"{n:.1f} {unit}".replace(".0 ", " ")
        n /= 1024
    return f"{n:.1f} GB"


ALL_CATEGORIES = "All categories"
NEEDS_REVIEW = "Others"  # must match categorizer fallback


APP_STYLE = """
QMainWindow, QWidget { font-family: "Cantarell", "Inter", "Segoe UI", "Roboto", sans-serif; font-size: 14px; }
QMainWindow { background: #eef0f4; }
QWidget#card { background: white; border: 1px solid #dfe3ea; border-radius: 14px; }
QLabel#title { background: #23272f; color: white; padding: 12px 18px; font-size: 16px;
               font-weight: 600; letter-spacing: 0.2px;
               border-top-left-radius: 14px; border-top-right-radius: 14px; }
QLabel#hint { background: #fffbe6; color: #5f5744; font-size: 13px; padding: 9px 16px;
              border-bottom: 1px solid #f0ead0; }
QLabel#chip { background: #f1f4f9; border: 1px solid #dde3ee; border-radius: 10px;
              padding: 5px 12px; font-size: 13px; color: #33415c; font-weight: 600; }
QLabel#chipWarn { background: #fff4e5; border: 1px solid #f5d9a8; border-radius: 10px;
                  padding: 5px 12px; font-size: 13px; color: #7a4a00; font-weight: 600; }
QLabel#empty { color: #8a94a6; font-size: 15px; padding: 36px; }
QLineEdit { padding: 9px 12px; border: 1px solid #cbd2dd; border-radius: 9px;
            font-size: 14px; background: white; color: #1e1e1e; }
QLineEdit:focus { border: 2px solid #0078d4; outline: none; }
/* Professional dropdown — closed state */
QComboBox { padding: 9px 36px 9px 12px; border: 1px solid #cbd2dd; border-radius: 9px;
            font-size: 14px; font-weight: 500; background: white; color: #1f2937; }
QComboBox:hover { border-color: #0078d4; background: #f8fbff; }
QComboBox:focus, QComboBox:on { border: 2px solid #0078d4; outline: none; background: white; }
QComboBox:editable { background: white; }
QComboBox QLineEdit { border: none; padding: 0; background: transparent; font-size: 14px; }
QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right;
                       width: 32px; border-left: 1px solid #e2e6ec;
                       border-top-right-radius: 9px; border-bottom-right-radius: 9px;
                       background: #f6f8fb; }
QComboBox::drop-down:hover { background: #eef4ff; }
QComboBox::down-arrow { image: url({ARROW}); width: 14px; height: 9px; }
QComboBox QAbstractItemView { background: white; border: 1px solid #cbd2dd;
                              border-radius: 10px; padding: 6px; outline: none;
                              font-size: 14px; color: #1f2937;
                              selection-background-color: #0078d4; selection-color: white; }
QComboBox QAbstractItemView::item { padding: 9px 12px; border-radius: 7px; min-height: 26px; }
QComboBox QAbstractItemView::item:hover { background: #eef4ff; color: #1a3a6b; }
QComboBox QAbstractItemView::item:selected { background: #0078d4; color: white; }
QPushButton:focus { border: 2px solid #0078d4; outline: none; }
QPushButton { padding: 9px 16px; border-radius: 9px; border: 1px solid #cbd2dd;
              background: white; font-size: 14px; font-weight: 600; }
QPushButton:hover { border-color: #0078d4; color: #0078d4; }
QPushButton[primary="true"] { background: #0078d4; color: white; border-color: #0078d4; }
QPushButton[primary="true"]:hover { background: #0062ad; color: white; }
QPushButton:disabled { color: #9aa3b2; background: #f2f4f7; border-color: #e2e6ec; }
QTableWidget { gridline-color: #eef1f6; border: none; font-size: 14px;
               alternate-background-color: #f8fafd; selection-background-color: #e3efff; }
QTableWidget::item { padding: 6px; }
QTableWidget::item:hover { background: #f2f7ff; }
QTableWidget::item:selected { background: #e3efff; color: #1f2937; }
QHeaderView::section { background: #f6f8fb; color: #5b6474; padding: 10px 8px; border: none;
                       border-bottom: 1px solid #e6eaf0; font-weight: 600; font-size: 13px; }
QLabel#status { color: #4b5563; font-size: 13px; font-weight: 600; }
"""


def app_style() -> str:
    """Same QSS, with real arrow asset path so Qt renders a chevron, not a grey box."""
    candidates = [
        Path(__file__).parent.parent / "assets" / "arrow-down.svg",  # dev + installed APP_DIR
        Path.home() / ".local" / "share" / "fileorganizer" / "assets" / "arrow-down.svg",
    ]
    arrow = next((str(p) for p in candidates if p.exists()), "")
    return APP_STYLE.replace("{ARROW}", arrow)


class OrganizerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Organizer — ~/Downloads")
        self.resize(1100, 680)
        self.rows = []
        self.setStyleSheet(app_style())

        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(18, 18, 18, 18)

        card = QWidget()
        card.setObjectName("card")
        outer.addWidget(card)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("File Organizer <span style='font-weight:400; opacity:0.75; font-size:13px;'>in-place organize · v2</span>")
        title.setObjectName("title")
        title.setTextFormat(Qt.RichText)
        title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout.addWidget(title)

        hint = QLabel("Only loose files are listed. Existing subfolders stay untouched. "
                      "Double-click a row to open it. Nothing moves until you press Move Selected.")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        hint.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout.addWidget(hint)

        toolbar = QWidget()
        toolbar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(12, 12, 12, 8)
        self.folderBox = QComboBox()
        self.folderBox.setAccessibleName("Folder to scan")
        self.folderBox.addItems([str(Path.home() / "Downloads"), str(Path.home() / "Desktop")])
        self.folderBox.setEditable(True)
        self.folderBox.setMinimumWidth(230)
        self.folderBox.setMaxVisibleItems(8)
        self.folderBox.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.folderBox.view().window().setWindowFlags(Qt.Popup | Qt.NoDropShadowWindowHint | Qt.FramelessWindowHint)
        self.folderBox.view().window().setAttribute(Qt.WA_TranslucentBackground)
        scanBtn = QPushButton("Scan")
        scanBtn.setAccessibleName("Scan folder")
        scanBtn.setProperty("primary", True)
        scanBtn.clicked.connect(self.do_scan)
        self.scanBtn = scanBtn
        browseBtn = QPushButton("Browse…")
        browseBtn.setAccessibleName("Browse for folder to scan")
        browseBtn.setToolTip("Pick any folder with a file dialog")
        browseBtn.clicked.connect(self.browse_folder)
        self.search = QLineEdit()
        self.search.setAccessibleName("Search files")
        self.search.setPlaceholderText("Search files…  (Ctrl+F)")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.refresh_table)
        self.catFilter = QComboBox()
        self.catFilter.setAccessibleName("Filter by category")
        self.catFilter.addItem(ALL_CATEGORIES)
        self.catFilter.currentTextChanged.connect(self.refresh_table)
        self.catFilter.setMinimumWidth(160)
        self.catFilter.setMaxVisibleItems(12)
        tb.addWidget(self.folderBox, 2)
        tb.addWidget(browseBtn)
        tb.addWidget(scanBtn)
        tb.addWidget(self.search, 3)
        tb.addWidget(self.catFilter, 1)
        layout.addWidget(toolbar)

        # Stat chips row
        chipbar = QWidget()
        chipbar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        cb = QHBoxLayout(chipbar)
        cb.setContentsMargins(12, 0, 12, 8)
        self.chipTotal = QLabel("Total: 0")
        self.chipTotal.setObjectName("chip")
        self.chipSel = QLabel("Selected: 0")
        self.chipSel.setObjectName("chip")
        self.chipReview = QLabel("Needs Review: 0")
        self.chipReview.setObjectName("chipWarn")
        cb.addWidget(self.chipTotal)
        cb.addWidget(self.chipSel)
        cb.addWidget(self.chipReview)
        cb.addStretch(1)
        layout.addWidget(chipbar)

        # Table — long names: elide middle + full tooltip so nothing breaks
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["", "File", "Size", "Proposed Folder", "Reason"])
        self.table.setTextElideMode(Qt.ElideMiddle)
        self.table.setWordWrap(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(2, 96)
        self.table.setColumnWidth(3, 210)
        self.table.horizontalHeader().setMinimumSectionSize(70)
        self.table.setColumnHidden(0, False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(36)
        table_font = QFont("Cantarell", 11)
        self.table.setFont(table_font)
        self.table.cellClicked.connect(self.on_row_clicked)
        self.table.cellDoubleClicked.connect(self.on_open_file)
        self.table.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        layout.addWidget(self.table, 1)

        # Empty state — dedicated expanding panel so header never stretches
        self.emptyWrap = QWidget()
        self.emptyWrap.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        ew = QVBoxLayout(self.emptyWrap)
        ew.setAlignment(Qt.AlignCenter)
        ew.setSpacing(8)
        ew.setContentsMargins(20, 40, 20, 40)
        self.emptyIcon = QLabel("○")
        self.emptyIcon.setAlignment(Qt.AlignCenter)
        self.emptyIcon.setStyleSheet("font-size:44px; color:#c3ccd8;")
        self.emptyTitle = QLabel("No files to show")
        self.emptyTitle.setAlignment(Qt.AlignCenter)
        self.emptyTitle.setStyleSheet("font-size:17px; font-weight:600; color:#33415c;")
        self.emptySub = QLabel("Pick a folder and press Scan…")
        self.emptySub.setObjectName("empty")
        self.emptySub.setAlignment(Qt.AlignCenter)
        self.emptySub.setWordWrap(True)
        self.emptyBtn = QPushButton("Scan Now")
        self.emptyBtn.setProperty("primary", True)
        self.emptyBtn.clicked.connect(self.do_scan)
        btnRow = QHBoxLayout()
        btnRow.setAlignment(Qt.AlignCenter)
        btnRow.addWidget(self.emptyBtn)
        ew.addWidget(self.emptyIcon)
        ew.addWidget(self.emptyTitle)
        ew.addWidget(self.emptySub)
        ew.addLayout(btnRow)
        layout.addWidget(self.emptyWrap, 1)

        footer = QWidget()
        footer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        fb = QHBoxLayout(footer)
        fb.setContentsMargins(12, 12, 12, 12)
        selAll = QPushButton("Select All")
        selAll.setAccessibleName("Select all visible files")
        selAll.clicked.connect(lambda: self.set_all(True))
        clearBtn = QPushButton("Clear")
        clearBtn.setAccessibleName("Clear selection")
        clearBtn.clicked.connect(lambda: self.set_all(False))
        self.moveBtn = QPushButton("Move Selected")
        self.moveBtn.setAccessibleName("Move selected files")
        self.moveBtn.setProperty("primary", True)
        self.moveBtn.clicked.connect(self.do_move)
        self.undoBtn = QPushButton("Undo Last")
        self.undoBtn.setAccessibleName("Undo last move")
        self.undoBtn.clicked.connect(self.do_undo)
        self.undoBtn.setEnabled(False)
        self.status = QLabel("Ready")
        self.status.setObjectName("status")
        fb.addWidget(selAll)
        fb.addWidget(clearBtn)
        fb.addWidget(self.moveBtn)
        fb.addWidget(self.undoBtn)
        fb.addWidget(self.status, 1, Qt.AlignRight)
        layout.addWidget(footer)

        # Keyboard: Ctrl+A select, Ctrl+F focus search, Space toggles focused row
        QShortcut(QKeySequence("Ctrl+A"), self, activated=lambda: self.set_all(True))
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self.search.setFocus)

        self.refresh_table()

    # ---- data ----
    def browse_folder(self):
        """Open native folder picker; remember choice in the dropdown."""
        picked = QFileDialog.getExistingDirectory(
            self, "Choose Folder to Organize", self.folderBox.currentText())
        if not picked:
            return
        if self.folderBox.findText(picked) == -1:
            self.folderBox.addItem(picked)
        self.folderBox.setCurrentText(picked)
        self.do_scan()  # auto-scan: picking a folder implies intent, skip extra click

    def do_scan(self):
        folder = self.folderBox.currentText()
        self.setWindowTitle(f"File Organizer — {folder}")
        self.scanBtn.setEnabled(False)
        self.scanBtn.setText("Scanning…")
        QApplication.processEvents()
        try:
            files = scan_loose_files(folder)
        except Exception as e:
            QMessageBox.warning(self, "Scan Failed", f"Cannot scan folder.\n\nFix: check the path and permissions.\n\n{e}")
            return
        finally:
            self.scanBtn.setEnabled(True)
            self.scanBtn.setText("Scan")
        self.rows = []
        cats = set()
        for f in files:
            folder_name, reason = categorize(f["name"])
            cats.add(folder_name)
            self.rows.append({**f, "folder": folder_name, "reason": reason, "checked": True})
        self.catFilter.blockSignals(True)
        self.catFilter.clear()
        self.catFilter.addItem(ALL_CATEGORIES)
        self.catFilter.addItems(sorted(cats))
        self.catFilter.blockSignals(False)
        self.refresh_table()

    def _table_fonts(self):
        base = QFont("Cantarell", 11)
        base.setWeight(QFont.Normal)
        name = QFont("Cantarell", 11)
        name.setWeight(QFont.Medium)
        pill = QFont("Cantarell", 11)
        pill.setWeight(QFont.DemiBold)
        mono = QFont("DejaVu Sans Mono", 11)
        mono.setStyleHint(QFont.Monospace)
        return base, name, pill, mono

    def _fill_row(self, row_idx, orig_i, r, fonts):
        base_font, name_font, pill_font, mono = fonts
        chk = QTableWidgetItem()
        chk.setFlags(chk.flags() | Qt.ItemIsUserCheckable)
        chk.setCheckState(Qt.Checked if r["checked"] else Qt.Unchecked)
        chk.setData(Qt.UserRole, orig_i)
        chk.setTextAlignment(Qt.AlignCenter)
        chk.setToolTip(f"{r['name']}\n{r['path']}")
        self.table.setItem(row_idx, 0, chk)

        # Long names: show full in tooltip, elide in cell — layout never breaks
        name_item = QTableWidgetItem(r["name"])
        name_item.setFont(name_font)
        name_item.setForeground(QColor("#1f2937"))
        name_item.setToolTip(f"{r['name']}\n{r['path']}\n{human_size(r['size'])}")
        self.table.setItem(row_idx, 1, name_item)

        size_item = QTableWidgetItem(human_size(r["size"]))
        size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        size_item.setFont(mono)  # tabular numbers, easy comparison
        size_item.setToolTip(f"{r['size']} bytes")
        self.table.setItem(row_idx, 2, size_item)

        pill = QTableWidgetItem(r["folder"] + "/")
        pill.setBackground(QColor("#eef4ff"))
        pill.setForeground(QColor("#1e3a5f"))
        pill.setFont(pill_font)
        pill.setToolTip(f"Will create/use: {r['folder']}/")
        self.table.setItem(row_idx, 3, pill)

        reason_item = QTableWidgetItem(r["reason"])
        reason_item.setForeground(QColor("#6b7280"))
        reason_item.setFont(base_font)
        reason_item.setToolTip(r["reason"])
        self.table.setItem(row_idx, 4, reason_item)

    def _update_counts(self, shown):
        sel = sum(r["checked"] for r in self.rows)
        need_review = sum(1 for r in self.rows if r["folder"] == NEEDS_REVIEW)
        self.chipTotal.setText(f"Total: {len(self.rows)}")
        self.chipSel.setText(f"Selected: {sel}")
        self.chipReview.setText(f"Needs Review: {need_review}")
        self.status.setText(f"{len(self.rows)} scanned, {sel} selected • showing {shown}")
        self.moveBtn.setEnabled(sel > 0)

    def visible_rows(self):
        q = self.search.text().strip().lower()
        cf = self.catFilter.currentText()
        out = []
        for i, r in enumerate(self.rows):
            if q and q not in r["name"].lower():
                continue
            if cf != ALL_CATEGORIES and r["folder"] != cf:
                continue
            out.append((i, r))
        return out

    def refresh_table(self):
        vis = self.visible_rows()
        self.table.setUpdatesEnabled(False)
        self.table.blockSignals(True)
        self.table.setRowCount(len(vis))
        fonts = self._table_fonts()
        for row_idx, (orig_i, r) in enumerate(vis):
            self._fill_row(row_idx, orig_i, r, fonts)
        self.table.blockSignals(False)
        self.table.setUpdatesEnabled(True)

        # Empty states — dedicated panel keeps header compact, table keeps grid lines
        has_rows = len(self.rows) > 0
        if not has_rows:
            self.emptyTitle.setText("Folder is tidy")
            self.emptySub.setText("No loose files to show.\nPick another folder and press Scan…")
            self.emptyBtn.setText("Scan Now")
            self.emptyBtn.setVisible(True)
            self.emptyWrap.setVisible(True)
            self.table.setVisible(False)
        elif not vis:
            self.emptyTitle.setText("No matches")
            self.emptySub.setText("Clear search or pick another category…")
            self.emptyBtn.setVisible(False)
            self.emptyWrap.setVisible(True)
            self.table.setVisible(False)
        else:
            self.emptyWrap.setVisible(False)
            self.table.setVisible(True)

        self._update_counts(len(vis))

    def on_row_clicked(self, row, col):
        if col == 0:
            item = self.table.item(row, 0)
            if item is None:
                return
            orig_i = item.data(Qt.UserRole)
            self.table.blockSignals(True)
            new_state = Qt.Unchecked if self.rows[orig_i]["checked"] else Qt.Checked
            item.setCheckState(new_state)
            self.rows[orig_i]["checked"] = new_state == Qt.Checked
            self.table.blockSignals(False)
            self._update_counts(self.table.rowCount())

    def set_all(self, val):
        targets = {orig for orig, _ in self.visible_rows()}
        for orig in targets:
            self.rows[orig]["checked"] = val
        self.refresh_table()

    def on_open_file(self, row, _col):
        vis = self.visible_rows()
        if row < len(vis):
            _, r = vis[row]
            # QDesktopServices works on Linux/Windows/macOS (xdg-open does not)
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(r["path"])):
                QMessageBox.warning(self, "Cannot Open File",
                                    "Fix: check the default app for this file type.")

    def do_move(self):
        base = Path(self.folderBox.currentText()).expanduser()
        selected = [r for r in self.rows if r["checked"]]
        if not selected:
            QMessageBox.information(self, "Nothing Selected", "Tick at least one file first.")
            return
        # Destructive guard: has undo, so confirm only for large batches
        if len(selected) > 50:
            ok = QMessageBox.question(self, "Move Files",
                                      f"Move {len(selected)} files? You can undo right after.")
            if ok != QMessageBox.Yes:
                return
        plans = [{"src": r["path"], "dest_folder": str(base / r["folder"])} for r in selected]
        try:
            moved = move_files(plans)
        except Exception as e:
            QMessageBox.warning(self, "Move Failed", f"Some files did not move.\n\nFix: check permissions and retry.\n\n{e}")
            return
        moved_names = {m["old"] for m in moved}
        self.rows = [r for r in self.rows if r["path"] not in moved_names]
        self.undoBtn.setEnabled(True)
        self.refresh_table()
        self.status.setText(f"Moved {len(moved)} files ✓ (Undo available)")

    def do_undo(self):
        try:
            restored = undo_last()
        except Exception as e:
            QMessageBox.warning(self, "Undo Failed", f"Fix: check files were not manually moved.\n\n{e}")
            return
        self.undoBtn.setEnabled(False)
        QMessageBox.information(self, "Undo Complete", f"Restored {len(restored)} files.")
        self.do_scan()


def main():
    app = QApplication(sys.argv)
    # Readable base font: Fedora Cantarell, 11pt ≈ 15px, fallback chain
    base = QFont("Cantarell", 11)
    base.setStyleHint(QFont.SansSerif)
    app.setFont(base)
    w = OrganizerWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
