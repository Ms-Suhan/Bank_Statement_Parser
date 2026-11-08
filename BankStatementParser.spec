

# BankStatementParser.spec

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

project_root = Path(SPECPATH).resolve()

# Make sure PyInstaller can discover local project packages
sys.path.insert(0, str(project_root))

datas = [
    (str(project_root / "app.py"), "."),
]

binaries = []
hiddenimports = []

# Collect all runtime dependencies, including our custom parser package
packages = [
    "streamlit",
    "pandas",
    "openpyxl",
    "python_calamine",
    "parser",
]

for package in packages:

    package_datas, package_binaries, package_hidden = collect_all(package)

    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hidden


# Explicitly include the local parser modules
hiddenimports += [
    "parser",
    "parser.utils",

    "parser.icici",
    "parser.icici.dispatcher",
    "parser.icici.upi",
    "parser.icici.imps",
    "parser.icici.neft",
    "parser.icici.rtgs",
    "parser.icici.other",

    "parser.union_bank",
    "parser.union_bank.dispatcher",
    "parser.union_bank.upi",
    "parser.union_bank.imps",
    "parser.union_bank.neft",
    "parser.union_bank.rtgs",
    "parser.union_bank.other",
]


# Remove duplicate hidden imports
hiddenimports = list(set(hiddenimports))


# PyInstaller analysis
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BankStatementParser",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="BankStatementParser",
)
