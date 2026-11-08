

# BankStatementParser.spec

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

project_root = Path(SPECPATH)

datas = [
    (str(project_root / "app.py"), "."),
]

binaries = []
hiddenimports = []

# Collect package data, binaries and hidden imports
packages = [
    "streamlit",
    "pandas",
    "openpyxl",
    "python_calamine",
]

for package in packages:
    package_datas, package_binaries, package_hidden = collect_all(package)

    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hidden

# Include both bank parser packages
hiddenimports += collect_submodules("parser")

# Analysis
a = Analysis(
    [str(project_root / "launcher.py")],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

# Executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BankStatementParser",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console visible during initial testing
    disable_windowed_traceback=False,
)

# Collect all dependencies into one folder
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="BankStatementParser",
)
