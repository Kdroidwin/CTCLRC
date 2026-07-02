# -*- mode: python ; coding: utf-8 -*-

import os

from PyInstaller.utils.hooks import collect_all


datas = []
binaries = []
hiddenimports = []


for pkg in [
    "torch",
    "torchcodec",
    "transformers",
    "av",
    "ctc_forced_aligner",
    "uroman",
    "unidecode",
]:
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass


# Optional offline Hugging Face model bundle.
# Put the downloaded model here before building:
# models/mms-300m-1130-forced-aligner/
if os.path.isdir("models"):
    datas += [
        ("models", "models"),
    ]


a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    exclude_binaries=False,
    name="CTCLRC",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
