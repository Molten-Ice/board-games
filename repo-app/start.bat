@echo off
echo Starting Foody Menu App...
echo.

REM Check if Tesseract is installed
where tesseract >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Tesseract OCR is not installed!
    echo Please install it from: https://github.com/UB-Mannheim/tesseract/wiki
    pause
    exit /b 1
)

echo Tesseract OCR found
echo.

REM Start backend
echo Starting backend server...
cd backend

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
if not exist "venv\installed" (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    echo. > venv\installed
)

REM Create .env if it doesn't exist
if not exist ".env" (
    copy .env.example .env
)

REM Start backend
start "Foody Backend" cmd /k python app.py

echo Backend started on http://localhost:5000
echo.

REM Start frontend
cd ..\frontend

echo Starting frontend server...

REM Install dependencies
if not exist "node_modules\" (
    echo Installing Node dependencies...
    call npm install
)

REM Create .env if it doesn't exist
if not exist ".env" (
    copy .env.example .env
)

echo.
echo Foody Menu App is ready!
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:5000
echo.

REM Start frontend
call npm start
