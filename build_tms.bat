@echo off
REM ============================================================
REM  TMS - Build EXE Script
REM  Run this from:  C:\Potpot System\myproject\
REM  with your virtualenv ACTIVE  (myenv)
REM ============================================================

echo.
echo  === Step 1: Collect static files ===
python manage.py collectstatic --noinput --clear
if errorlevel 1 (
    echo ERROR: collectstatic failed. Check STATIC_ROOT in settings.py
    pause
    exit /b 1
)

echo.
echo  === Step 2: Remove old build artifacts ===
if exist "build\TMS" rmdir /s /q "build\TMS"
if exist "dist\TMS"  rmdir /s /q "dist\TMS"

echo.
echo  === Step 3: Build EXE with PyInstaller ===
pyinstaller tms.spec --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo  === Step 4: Copy database to dist folder ===
copy /y db.sqlite3 "dist\TMS\db.sqlite3"

echo.
echo  === Step 5: Create media folder in dist ===
if not exist "dist\TMS\media" mkdir "dist\TMS\media"

echo.
echo ============================================================
echo  BUILD COMPLETE!
echo  Your EXE is at:  dist\TMS\TMS.exe
echo  Double-click TMS.exe to start the server.
echo  Then open:  http://127.0.0.1:8000/
echo ============================================================
pause