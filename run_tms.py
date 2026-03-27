"""
run_tms.py  –  EXE entry-point for the Traffic Management System
Place this file in: C:\Potpot System\myproject\

PyInstaller compiles THIS file into TMS.exe
"""

import sys
import os


def resource_path(relative_path):
    """
    Return the absolute path to a bundled resource.
    Works both when running as a script and as a frozen EXE.
    """
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller EXE – files are extracted to _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    # Running normally (dev)
    return os.path.join(os.path.abspath('.'), relative_path)


def setup_environment():
    """Configure Django paths before importing anything Django-related."""

    # ── 1. Tell Django where settings live ───────────────────────────────────
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

    # ── 2. Add the bundle root to sys.path so imports resolve ────────────────
    base = resource_path('.')
    if base not in sys.path:
        sys.path.insert(0, base)

    # ── 3. Resolve writable paths for DB and media ───────────────────────────
    #    When installed on a user's PC the EXE may live in Program Files (read-only).
    #    We store mutable data next to the EXE instead.
    if hasattr(sys, '_MEIPASS'):
        # Folder that contains TMS.exe  (e.g.  dist\TMS\)
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.abspath('.')

    # ── 4. Patch settings at runtime ─────────────────────────────────────────
    #    Import settings and override the paths that must be writable / correct.
    import django.conf as _conf

    # We must configure before accessing settings
    # Use a tiny wrapper so we only patch after Django loads the module
    _original_setup = _conf.LazySettings.__getattr__

    def _patched_getattr(self, name):
        value = _original_setup(self, name)
        return value

    # Better approach: just set env vars Django settings already reads
    os.environ['TMS_EXE_DIR'] = exe_dir
    os.environ['TMS_STATIC_ROOT'] = resource_path('staticfiles')
    os.environ['TMS_MEDIA_ROOT'] = os.path.join(exe_dir, 'media')
    os.environ['TMS_DB_PATH'] = os.path.join(exe_dir, 'db.sqlite3')
    os.environ['TMS_TEMPLATES_DIR'] = resource_path('templates')
    os.environ['TMS_STATIC_DIR'] = resource_path('static')

    # ── 5. Copy DB from bundle to exe_dir on first run ────────────────────────
    db_dest = os.path.join(exe_dir, 'db.sqlite3')
    db_src  = resource_path('db.sqlite3')
    if not os.path.exists(db_dest) and os.path.exists(db_src):
        import shutil
        shutil.copy2(db_src, db_dest)

    # Ensure media directory exists
    os.makedirs(os.path.join(exe_dir, 'media'), exist_ok=True)


def main():
    setup_environment()

    # ── Run Django dev server (suitable for local/offline desktop use) ────────
    from django.core.management import execute_from_command_line

    port = '8000'
    # Allow custom port via command-line:  TMS.exe 9000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = sys.argv[1]

    print("=" * 55)
    print("  Traffic Management System")
    print(f"  Open your browser at:  http://127.0.0.1:{port}/")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 55)

    # Optionally auto-open browser
    import threading, webbrowser, time

    def _open_browser():
        time.sleep(2)           # wait for server to start
        webbrowser.open(f'http://127.0.0.1:{port}/')

    threading.Thread(target=_open_browser, daemon=True).start()

    execute_from_command_line(['manage.py', 'runserver', f'127.0.0.1:{port}', '--noreload'])


if __name__ == '__main__':
    main()