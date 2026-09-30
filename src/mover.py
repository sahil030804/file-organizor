"""Mover: move loose files in-place + JSON undo log."""
import json
import shutil
from datetime import datetime
from pathlib import Path

LOG_PATH = Path.home() / ".config" / "fileorganizer" / "moves.json"

def _load_log():
    if LOG_PATH.exists():
        return json.loads(LOG_PATH.read_text())
    return []

def _save_log(data):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(data, indent=2))

def unique_target(folder: Path, name: str) -> Path:
    """If photo.jpg exists, return photo (1).jpg — never overwrite."""
    target = folder / name
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    i = 1
    while True:
        cand = folder / f"{stem} ({i}){suffix}"
        if not cand.exists():
            return cand
        i += 1

def move_files(plans):
    """plans: list of {src, dest_folder}. Returns list of {old, new}."""
    moved = []
    for p in plans:
        src = Path(p["src"])
        dest_folder = Path(p["dest_folder"])
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest = unique_target(dest_folder, src.name)
        shutil.move(str(src), str(dest))
        moved.append({"old": str(src), "new": str(dest), "time": datetime.now().isoformat()})
    log = _load_log()
    log.append({"batch": moved, "time": datetime.now().isoformat()})
    _save_log(log)
    return moved

def undo_last():
    """Undo most recent batch. Returns list of restored paths."""
    log = _load_log()
    if not log:
        return []
    last = log.pop()
    restored = []
    for m in reversed(last["batch"]):
        src = Path(m["new"])
        dst = Path(m["old"])
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            restored.append(str(dst))
    _save_log(log)
    return restored
