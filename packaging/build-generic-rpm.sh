#!/usr/bin/env bash
# Build the .rpm anywhere rpmbuild exists (Fedora: sudo dnf install rpm-build,
# Ubuntu CI: sudo apt-get install rpm). Run from project root.
set -e
VER=1.0.0
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
rm -rf /tmp/rpmbuild && mkdir -p /tmp/rpmbuild/{BUILD,RPMS,SRPMS,SOURCES,SPECS}
STAGE=/tmp/rpmbuild/stage
rm -rf "$STAGE" && mkdir -p "$STAGE/file-organizer-$VER"
cd "$ROOT"
git archive HEAD -- src rules.yaml assets requirements.txt packaging README.md install.sh uninstall.sh \
  | tar -x -C "$STAGE/file-organizer-$VER"
tar -czf /tmp/rpmbuild/SOURCES/file-organizer-$VER.tar.gz -C "$STAGE" file-organizer-$VER
cp "$ROOT/packaging/file-organizer.spec" /tmp/rpmbuild/SPECS/
rpmbuild -bb /tmp/rpmbuild/SPECS/file-organizer.spec --define "_topdir /tmp/rpmbuild"
mkdir -p "$ROOT/dist"
cp /tmp/rpmbuild/RPMS/noarch/*.rpm "$ROOT/dist/"
echo "RPMs in $ROOT/dist/"
ls "$ROOT/dist/"*.rpm
