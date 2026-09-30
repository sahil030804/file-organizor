#!/usr/bin/env bash
# Install File Organizer as a real Fedora (GNOME) app.
# What it does, step by step for learning:
# 1. Copies project to ~/.local/share/fileorganizer (system app dir for user apps)
# 2. Creates venv there + pip installs requirements (isolated, no sudo, no system break)
# 3. Creates wrapper ~/.local/bin/file-organizer (so Exec + terminal can launch it)
# 4. Installs .desktop to ~/.local/share/applications (this is what GNOME shows in app grid)
# 5. Installs icon to ~/.local/share/icons/... (what you see in grid)
set -e
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$HOME/.local/share/fileorganizer"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"

echo "[1/5] Copying files to $APP_DIR"
mkdir -p "$APP_DIR"
cp -r "$SRC_DIR/src" "$SRC_DIR/rules.yaml" "$SRC_DIR/requirements.txt" "$APP_DIR/"
mkdir -p "$APP_DIR/assets"
cp "$SRC_DIR"/assets/*.svg "$APP_DIR/assets/" 2>/dev/null || true

echo "[2/5] Creating venv + installing deps (no sudo)"
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip -q
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

echo "[3/5] Creating launcher $BIN_DIR/file-organizer"
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/file-organizer" <<EOF
#!/usr/bin/env bash
cd "$APP_DIR"
exec "$APP_DIR/venv/bin/python" -m src "\$@"
EOF
chmod +x "$BIN_DIR/file-organizer"

echo "[4/5] Installing .desktop entry"
mkdir -p "$DESKTOP_DIR"
cat > "$DESKTOP_DIR/file-organizer.desktop" <<EOF
[Desktop Entry]
Name=File Organizer
Comment=Organize Downloads/Desktop in-place with approve + undo
Exec=$HOME/.local/bin/file-organizer
Icon=file-organizer
Terminal=false
Type=Application
Categories=Utility;FileTools;
StartupWMClass=file-organizer
EOF

echo "[5/5] Installing icon"
mkdir -p "$ICON_DIR"
cp "$SRC_DIR/assets/icon.svg" "$ICON_DIR/file-organizer.svg"

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$DESKTOP_DIR" || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" || true
fi

echo ""
echo "Done. Search 'File Organizer' in GNOME Activities."
echo "Run from terminal too: ~/.local/bin/file-organizer"
echo "Ensure ~/.local/bin is in PATH: export PATH=\"\$HOME/.local/bin:\$PATH\""
