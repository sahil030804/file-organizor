from src.categorizer import categorize

def test_basic():
    assert categorize("notes.md")[0] == "Documents/Markdown"
    assert categorize("pic.jpg")[0] == "Images/Wallpapers"

def test_screenshot_heuristic():
    assert categorize("screenshot-12.png")[0] == "Images/Screenshots"

def test_unknown_goes_others():
    assert categorize("weird.xyz")[0] == "Others"
