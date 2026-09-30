#!/usr/bin/env bash
# Build the .rpm on Fedora (needs sudo once for rpm-build).
# Run from the project root:  bash packaging/build-rpm.sh
set -e
VER=1.0.0
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
sudo dnf install -y rpm-build
rm -rf /tmp/rpmbuild && mkdir -p /tmp/rpmbuild/{BUILD,RPMS,SRPMS,SOURCES,SPECS}
TARBALL=/tmp/rpmbuild/SOURCES/file-organizer-$VER.tar.gz
tar --exclude=__pycache__ --exclude=.pytest_cache --exclude=dist \
    -czf "$TARBALL" -C "$(dirname "$ROOT")" "$(basename "$ROOT")"
# rename top dir inside tarball to file-organizer-1.0.0
mkdir -p /tmp/rpmbuild/tmpsrc && tar -xzf "$TARBALL" -C /tmp/rpmbuild/tmpsrc
mv /tmp/rpmbuild/tmpsrc/file-organizer /tmp/rpmbuild/tmpsrc/file-organizer-$VER
tar -czf "$TARBALL" -C /tmp/rpmbuild/tmpsrc file-organizer-$VER
cp "$ROOT/packaging/file-organizer.spec" /tmp/rpmbuild/SPECS/
rpmbuild -bb /tmp/rpmbuild/SPECS/file-organizer.spec --define "_topdir /tmp/rpmbuild"
echo "RPMs in /tmp/rpmbuild/RPMS/noarch/"
ls /tmp/rpmbuild/RPMS/noarch/
