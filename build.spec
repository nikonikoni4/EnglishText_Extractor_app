# -*- mode: python ; coding: utf-8 -*-
# pyinstaller build.spec --clean --noconfirm
block_cipher = None

a = Analysis(
    ['text_extractor_app.py'],
    pathex=['D:/desktop/英语单词提取app', 'D:/program/language'],
    binaries=[],
    datas=[('config.ini', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'unittest', 'pytest', 'test',
        'numpy', 'matplotlib', 'scipy',
        'django', 'flask',
        'pandas', 'sqlalchemy'
    ],  # 修正后的排除项（保留tkinter）
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
