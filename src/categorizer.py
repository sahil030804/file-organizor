"""Categorizer: extension -> folder name using rules.yaml + screenshot heuristic."""
from functools import lru_cache
from pathlib import Path
import yaml

RULES_PATH = Path(__file__).parent.parent / "rules.yaml"

@lru_cache(maxsize=8)
def load_rules(path=RULES_PATH):
    """Parsed once per path — scans call categorize() per file."""
    with open(path) as f:
        return yaml.safe_load(f)

def _ext_map(rules):
    """Lowercased extension -> folder. First rule wins (dict order)."""
    table = {}
    for folder, exts in rules.items():
        for e in exts or []:
            table.setdefault(e.lower(), folder)
    return table

def categorize(filename: str, rules=None):
    """Return (folder, reason). Falls back to Others/."""
    table = _ext_map(rules if rules is not None else load_rules())
    name_low = filename.lower()
    suffix = Path(filename).suffix.lower()

    # Heuristic: screenshot files go to Images/Screenshots even if .png
    if "screenshot" in name_low or "screen shot" in name_low:
        return "Images/Screenshots", "name contains screenshot"

    folder = table.get(suffix)
    if folder is not None:
        # .png is ambiguous: default Photos unless screenshot (handled above)
        return folder, f"{suffix} → {folder.split('/')[-1].lower()}"
    return "Others", "unknown → Others"

if __name__ == "__main__":
    for n in ["notes.md", "pic.jpg", "screenshot-12.png", "weird.xyz"]:
        print(n, categorize(n))
