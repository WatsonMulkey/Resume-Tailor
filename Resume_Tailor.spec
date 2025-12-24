# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['resume_tailor_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('import_career_data.py', '.'), ('generator.py', '.'), ('pdf_generator.py', '.'), ('html_template.py', '.'), ('docx_generator.py', '.'), ('conflict_detector.py', '.'), ('config.py', '.'), ('.env', '.')],
    hiddenimports=['anthropic', 'dotenv', 'docx', 'reportlab'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Resume_Tailor',
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
)
