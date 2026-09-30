#!/usr/bin/env bash
# Rebuild the .deb (no root needed to build, root needed to install).
# Run from project root:  bash packaging/build-deb.sh
# Install on Debian/Ubuntu:  sudo apt install ./dist/file-organizer_1.0.0_all.deb
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Assemble payload from the LIVE tree so rebuilds never ship stale code.
rm -rf "$ROOT/packaging/deb/usr/share/fileorganizer"
mkdir -p "$ROOT/packaging/deb/usr/share/fileorganizer/assets"
cp -r "$ROOT/src" "$ROOT/packaging/deb/usr/share/fileorganizer/"
cp "$ROOT/rules.yaml" "$ROOT/packaging/deb/usr/share/fileorganizer/"
cp "$ROOT/requirements.txt" "$ROOT/packaging/deb/usr/share/fileorganizer/"
cp "$ROOT/assets/arrow-down.svg" "$ROOT/packaging/deb/usr/share/fileorganizer/assets/"
find "$ROOT/packaging/deb/usr/share/fileorganizer" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
chmod 755 "$ROOT/packaging/deb/usr/bin/file-organizer" \
  "$ROOT/packaging/deb/DEBIAN/postinst" "$ROOT/packaging/deb/DEBIAN/prerm"
chmod 644 "$ROOT/packaging/deb/DEBIAN/control"
sed -i '/^Installed-Size:/d' "$ROOT/packaging/deb/DEBIAN/control"
echo "Installed-Size: $(du -sk "$ROOT/packaging/deb/usr" | cut -f1)" >> "$ROOT/packaging/deb/DEBIAN/control"
rm -rf /tmp/opencode/debbuild && mkdir -p /tmp/opencode/debbuild
tar -czf /tmp/opencode/debbuild/control.tar.gz -C "$ROOT/packaging/deb/DEBIAN" control postinst prerm
tar -czf /tmp/opencode/debbuild/data.tar.gz -C "$ROOT/packaging/deb" usr
echo -n "2.0" > /tmp/opencode/debbuild/debian-binary
mkdir -p "$ROOT/dist"
ar rcs "$ROOT/dist/file-organizer_1.0.0_all.deb" \
  /tmp/opencode/debbuild/debian-binary \
  /tmp/opencode/debbuild/control.tar.gz \
  /tmp/opencode/debbuild/data.tar.gz
echo "Built $ROOT/dist/file-organizer_1.0.0_all.deb"
ar t "$ROOT/dist/file-organizer_1.0.0_all.deb"
