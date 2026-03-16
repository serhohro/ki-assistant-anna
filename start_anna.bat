@echo off
title 🤖 Анна PRO v3
chcp 65001 >nul
cd /d "C:\Users\sergo\AI_Anna" REM Поставьте папку, с которой будет запускаться ИИ Анна

color 0A
cls

echo ============================================
echo           🤖 Анна PRO v3 — Запуск
echo ============================================
echo.

:: Перевірка Python
echo 🔍 Перевірка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не знайдено! Встановіть Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python знайдено
echo.

:: Перевірка Ollama
echo 🔍 Перевірка Ollama...
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Ollama не запущено. Запускаю...
    start "" ollama serve
    echo   Зачекайте 5 секунд...
    timeout /t 5 /nobreak >nul
    echo ✅ Ollama запущено
) else (
    echo ✅ Ollama вже працює
)
echo.

:: Перевірка файлів
echo 🔍 Перевірка файлів...
if exist "anna.py" (
    echo ✅ anna.py знайдено
) else (
    echo ❌ anna.py не знайдено!
    pause
    exit /b 1
)

if exist "girl.mp4" (
    echo ✅ girl.mp4 знайдено (відео)
) else if exist "girl.png" (
    echo ✅ girl.png знайдено (зображення)
) else (
    echo ⚠️  Медіа файли не знайдено
)
echo.

echo ============================================
echo   🚀 Запуск Анна PRO...
echo   Браузер відкриється автоматично
echo   URL: http://localhost:8501
echo ============================================
echo.
echo   💡 Для зупинки натисніть Ctrl+C
echo   💡 Для виходу закрийте це вікно
echo ============================================
echo.

:: Запуск Streamlit
streamlit run anna.py

pause