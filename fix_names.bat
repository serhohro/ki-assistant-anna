@echo off
chcp 65001 >nul
cd /d "C:\Users\sergo\AI_Anna" REM Поставьте папку, с которой будет запускаться ИИ Анна

echo 🔧 Виправлення назв файлів...
echo.

:: Спроба перейменувати головний файл
if exist "анна.py" (
    ren "анна.py" anna.py
    echo ✅ анна.py → anna.py
) else if exist "anna.py.txt" (
    ren "anna.py.txt" anna.py
    echo ✅ anna.py.txt → anna.py
) else if exist "anna.py" (
    echo ✅ anna.py вже існує
) else (
    echo ❌ Файл anna.py не знайдено!
)

:: Виправити подвійні розширення
if exist "girl.png.png" (
    ren "girl.png.png" girl.png
    echo ✅ girl.png.png → girl.png
)

if exist "girl.png.mp4" (
    ren "girl.png.mp4" girl.mp4
    echo ✅ girl.png.mp4 → girl.mp4
)

echo.
echo ============================================
dir /b
echo ============================================
pause