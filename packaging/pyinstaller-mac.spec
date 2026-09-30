# macOS .app bundle (CI wraps it into .dmg with create-dmg).
# Paths relative to REPO ROOT:  pyinstaller packaging/pyinstaller-mac.spec
a = Analysis(
    ['src/__main__.py'],
    binaries=[],
    datas=[
        ('rules.yaml', '.'),
        ('assets/arrow-down.svg', 'assets'),
        ('assets/icon.svg', 'assets'),
    ],
    hiddenimports=['PySide6.QtSvg'],
    excludes=['pytest'],
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='FileOrganizer',
    console=False,
)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name='FileOrganizer')
app = BUNDLE(
    coll,
    name='FileOrganizer.app',
    icon='assets/icon.svg',
    bundle_identifier='com.example.fileorganizer',
)
