# -*- mode: python ; coding: utf-8 -*-
# TMS (Traffic Management System) - PyInstaller Spec File
# Place this file in: C:\Potpot System\myproject\

import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

datas = []
hiddenimports = []

django_apps = [
    'django',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
]

for app in django_apps:
    try:
        d, b, h = collect_all(app)
        datas += d
        hiddenimports += h
    except Exception:
        pass

hiddenimports += collect_submodules('django')
hiddenimports += collect_submodules('rest_framework')
hiddenimports += collect_submodules('myapp')
hiddenimports += collect_submodules('pandas')
hiddenimports += collect_submodules('numpy')

hiddenimports += [
    'django.template.defaulttags',
    'django.template.defaultfilters',
    'django.template.loader_tags',
    'django.contrib.admin.templatetags.admin_modify',
    'django.contrib.admin.templatetags.admin_list',
    'django.contrib.admin.templatetags.admin_urls',
    'sqlite3',
    'openpyxl',
    'openpyxl.cell._writer',
    'PIL',
    'PIL._imaging',
    'jazzmin',
    'whitenoise',
    'whitenoise.middleware',
    'pandas',
    'numpy',
]

datas += [
    ('myapp',                           'myapp'),
    ('myapp/templates',                 'myapp/templates'),
    ('static',                          'static'),
    ('staticfiles',                     'staticfiles'),
    ('media',                           'media'),
    ('db.sqlite3',                      '.'),
    ('manage.py',                       '.'),
    ('myproject',                       'myproject'),
]

a = Analysis(
    ['run_tms.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'pytest',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TMS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TMS',
)