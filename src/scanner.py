"""Scanner: list loose files in a folder, ignore subfolders for v1."""
from pathlib import Path


def scan_loose_files(folder: str | Path):
    """Return list of dicts for files directly inside folder (no recursion)."""
    folder = Path(folder).expanduser()
    results = []
    for entry in folder.iterdir():
        # v1 rule: ignore subfolders, hidden files
        if entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        stat = entry.stat()
        results.append({
            "name": entry.name,
            "path": str(entry),
            "size": stat.st_size,
            "suffix": entry.suffix.lower(),
        })
    return results


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "~/Downloads"
    for f in scan_loose_files(target):
        print(f["name"], f["size"], f["suffix"])
