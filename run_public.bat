@echo off
setlocal

echo ============================================
echo   Medley Lease Analysis ^& Management
echo   Public Access
echo ============================================
echo.

REM Set default password
set APP_PASSWORD=Medley2026
echo App password: %APP_PASSWORD%
echo.

REM Check for ngrok
where ngrok >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: ngrok is not installed!
    echo.
    echo Install ngrok using one of these methods:
    echo   1. winget install ngrok.ngrok
    echo   2. choco install ngrok
    echo   3. Download from https://ngrok.com/download
    echo.
    echo After installing, run: ngrok config add-authtoken YOUR_TOKEN
    pause
    exit /b 1
)

echo Starting Streamlit...
start /B streamlit run interfaces/chat_app.py --server.port 8501 --server.headless true

echo Waiting for Streamlit to start...
timeout /t 5 /nobreak >nul

echo.
echo ============================================
echo   Starting ngrok tunnel...
echo ============================================
echo.
echo Your public URL will appear below.
echo Password: %APP_PASSWORD%
echo.
echo Press Ctrl+C to stop.
echo.

ngrok http 8501
