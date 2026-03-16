@echo off
chcp 65001 >nul
echo ============================================
echo   🔍 Перевірка налаштувань Анни
echo ============================================
echo.

cd /d C:\Users\sergo\AI_Anna REM Поставьте папку, с которой будет запускаться ИИ Анна

echo [1] Python:
python --version
echo.

echo [2] Streamlit:
pip show streamlit | findstr Version
echo.

echo [3] Файл anna.py:
if exist anna.py (echo ✅ anna.py знайдено) else (echo ❌ anna.py НЕ знайдено)
echo.

echo [4] Зображення/Відео:
dir /b *.png *.jpg *.mp4 2>nul
echo.

echo [5] Ollama:
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if errorlevel 1 (echo ⚠️ Ollama не працює) else (echo ✅ Ollama працює)
echo.

echo ============================================
pause