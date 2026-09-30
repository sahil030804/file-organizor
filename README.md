# File Organizer v1

In-place organizer: scans loose files, proposes `Category/` folders, you approve, undo available.

## Run
```
cd file-organizer
python3 -m pip install pyyaml PySide6 pytest
python3 -m pytest -q
python3 -m src.gui
```

## How it works (for learning)
- `src/scanner.py` — `Path.iterdir()`, skips dirs/hidden. No recursion = safe.
- `src/categorizer.py` — loads `rules.yaml` once (cached), screenshot heuristic, else Others.
- `src/mover.py` — `mkdir + shutil.move`, `unique_target()` avoids overwrite, JSON log at `~/.config/fileorganizer/moves.json` for undo.
- `src/gui.py` — Qt signals/slots: `clicked -> do_scan/do_move`, `textChanged -> refresh_table`. GUI never does I/O directly, calls core functions.

## Packaging
- Debian/Ubuntu: `bash packaging/build-deb.sh` → `dist/*.deb` (assembles from live tree, never stale).
- Fedora: `bash packaging/build-rpm.sh` (needs `rpm-build`, one sudo).
- Windows/macOS: push a `v*` tag to GitHub → Actions builds `.exe` / `.dmg` via PyInstaller.
