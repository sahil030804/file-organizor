# Windows one-file .exe bundle. Paths relative to REPO ROOT (CI runs pyinstaller from root).
#   pyinstaller packaging/pyinstaller-win.spec
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
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='FileOrganizer',
    console=False,  # windowed app, no terminal
    icon='assets/icon.svg',
)
