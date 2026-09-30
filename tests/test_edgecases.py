"""Edge cases: long names, unicode, spaces, no-ext, uppercase, duplicates, empty."""
from pathlib import Path
from src.categorizer import categorize
from src.scanner import scan_loose_files
from src.mover import unique_target, move_files, undo_last
from src import mover


def test_very_long_filename_no_crash(tmp_path):
    long_name = "a" * 200 + ".pdf"
    folder, _ = categorize(long_name)
    assert folder == "Documents/PDF"
    (tmp_path / long_name).write_text("x")
    assert len(scan_loose_files(tmp_path)) == 1


def test_unicode_and_spaces(tmp_path):
    for n in ["my résumé final .PDF", "फोटो sunset.JPG", "name with  spaces .txt", "SCREENSHOT 1.PNG"]:
        (tmp_path / n).write_text("x")
    found = {f["name"] for f in scan_loose_files(tmp_path)}
    assert len(found) == 4
    assert categorize("my résumé final .PDF")[0] == "Documents/PDF"
    assert categorize("SCREENSHOT 1.PNG")[0] == "Images/Screenshots"


def test_no_extension_and_uppercase(tmp_path):
    assert categorize("README")[0] == "Others"
    assert categorize("PHOTO.JPG")[0] == "Images/Wallpapers"
    assert categorize("Notes.MD")[0] == "Documents/Markdown"


def test_hidden_and_subfolders_ignored(tmp_path):
    (tmp_path / ".hidden").write_text("x")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "inner.txt").write_text("x")
    (tmp_path / "loose.txt").write_text("x")
    names = [f["name"] for f in scan_loose_files(tmp_path)]
    assert names == ["loose.txt"]


def test_unique_target_never_overwrites(tmp_path):
    (tmp_path / "a.jpg").write_text("orig")
    assert unique_target(tmp_path, "a.jpg").name == "a (1).jpg"
    (tmp_path / "a (1).jpg").write_text("x")
    assert unique_target(tmp_path, "a.jpg").name == "a (2).jpg"


def test_move_and_undo_unicode_long(tmp_path, monkeypatch):
    monkeypatch.setattr(mover, "LOG_PATH", tmp_path / "moves.json")
    demo = tmp_path / "dl"
    demo.mkdir()
    names = ["a" * 150 + ".md", "café song.mp3", "SCREENSHOT x.png"]
    for n in names:
        (demo / n).write_text("data")
    scanned = scan_loose_files(demo)
    assert len(scanned) == 3
    from src.categorizer import categorize as cat
    plans = [{"src": f["path"], "dest_folder": str(demo / cat(f["name"])[0])} for f in scanned]
    moved = move_files(plans)
    assert len(moved) == 3
    assert len([p for p in demo.iterdir() if p.is_file()]) == 0
    restored = undo_last()
    assert len(restored) == 3


def test_empty_folder(tmp_path):
    assert scan_loose_files(tmp_path) == []
