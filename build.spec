# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['text_extractor_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.ini', '.'),
        ('icon.ico', '.')
    ],
    hiddenimports=[
        'importlib_metadata',
        'pandas._libs.tslibs.np_datetime',
        'pandas._libs.tslibs.nattype',
        'win32timezone'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'tkinter', 'matplotlib', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='text_extractor_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)