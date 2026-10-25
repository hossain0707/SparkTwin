#!/usr/bin/env bash
set -euo pipefail
version=0.1.0
pkg="$(mktemp -d)"
trap 'rm -rf "$pkg"' EXIT
mkdir -p "$pkg/opt/sparktwin" "$pkg/usr/share/applications" "$pkg/DEBIAN"
cp -a dist/SparkTwin/. "$pkg/opt/sparktwin/"
cat > "$pkg/usr/share/applications/sparktwin.desktop" <<'DESKTOP'
[Desktop Entry]
Version=1.0
Type=Application
Name=SparkTwin
Comment=Local-first AI memory capacity planner
Exec=/opt/sparktwin/SparkTwin
Terminal=false
Categories=Development;Science;
DESKTOP
cat > "$pkg/DEBIAN/control" <<'CONTROL'
Package: sparktwin
Version: 0.1.0
Architecture: amd64
Maintainer: Md Najmul Hossain
Depends: libgtk-3-0, libwebkit2gtk-4.1-0
Description: SparkTwin private AI capacity planning developer preview
 Offline, memory-first capacity planning for DGX Spark and Linux inference hosts.
CONTROL
chmod -R a+rX "$pkg/opt" "$pkg/usr"
dpkg-deb --build "$pkg" SparkTwin-Linux-x64-preview.deb
