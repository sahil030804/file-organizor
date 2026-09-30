Name:           file-organizer
Version:        1.0.0
Release:        1%{?dist}
Summary:        Organize files in-place with approve + undo
License:        MIT
URL:            https://example.com/file-organizer
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
Requires:       python3, python3-pyside6, python3-pyyaml

%description
Scan Downloads/Desktop, get category proposals
(Documents/Markdown, Images/Photos, …), approve moves,
and undo any batch. Safe by design: preview first,
never overwrites, ignores subfolders.

%prep
%autosetup -n %{name}-%{version}

%build
# pure python, nothing to compile

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -r src rules.yaml %{buildroot}%{_datadir}/%{name}/
mkdir -p %{buildroot}%{_datadir}/%{name}/assets
cp assets/arrow-down.svg %{buildroot}%{_datadir}/%{name}/assets/
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'EOF'
#!/usr/bin/python3
import sys
sys.path.insert(0, "/usr/share/fileorganizer")
from src.gui import main
if __name__ == "__main__":
    main()
EOF
chmod 755 %{buildroot}%{_bindir}/%{name}
mkdir -p %{buildroot}%{_datadir}/applications
cp packaging/file-organizer.desktop %{buildroot}%{_datadir}/applications/ 2>/dev/null || cat > %{buildroot}%{_datadir}/applications/%{name}.desktop <<'EOF'
[Desktop Entry]
Name=File Organizer
Comment=Organize Downloads/Desktop in-place with approve + undo
Exec=/usr/bin/file-organizer
Icon=file-organizer
Terminal=false
Type=Application
Categories=Utility;FileTools;
StartupWMClass=file-organizer
EOF
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
cp assets/icon.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

%files
%{_datadir}/%{name}/
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

%changelog
* Tue Sep 30 2026 Dev <you@example.com> - 1.0.0-1
- Initial package
