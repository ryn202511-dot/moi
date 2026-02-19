# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file cho Game Account Registrar Tool
"""
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

a = Analysis(
    ['gui_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('utils.py', '.'),
        ('game_account_registrar.py', '.'),
        ('accounts.txt', '.'),
    ],
    hiddenimports=[
        'selenium',
        'webdriver_manager',
        'PIL',
    ] + collect_submodules('selenium'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GameAccountRegistrar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
