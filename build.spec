# -*- mode: python ; coding: utf-8 -*-
# pyinstaller build.spec --clean --noconfirm
block_cipher = None

a = Analysis(
    ['text_extractor_app.py'],
    pathex=['D:/desktop/英语单词提取app/仓库/EnglishText_Extractor_app'],
    binaries=[],
    datas=[('config.ini', '.')],
    hiddenimports=['PySide6'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'unittest', 'pytest', 'test',
        # 'numpy', 'matplotlib', 'scipy',
        'django', 'flask', 'sqlalchemy',
        'pandas', 'openpyxl', 'xlrd',
        'psutil', 'chardet', 'html5lib'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='text_extractor_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='text_extractor_app',
)