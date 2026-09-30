#!/usr/bin/env bash
# Removes what install.sh created. Never touches ~/Downloads or organized files.
set -e
rm -rf "$HOME/.local/share/fileorganizer"
rm -f "$HOME/.local/bin/file-organizer"
rm -f "$HOME/.local/share/applications/file-organizer.desktop"
rm -f "$HOME/.local/share/icons/hicolor/scalable/apps/file-organizer.svg"
echo "Uninstalled. Your organized files stay as-is. Undo log kept at ~/.config/fileorganizer/moves.json"
