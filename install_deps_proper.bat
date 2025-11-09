@echo off
echo Activating virtual environment...
call backend\.venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

echo Installing backend dependencies...
cd backend
python -m pip install -r requirements_basic.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo Dependencies installed successfully!
cd ..
echo Running backend tests...
python -m pytest backend/tests/ -v --tb=short
if %errorlevel% neq 0 (
    echo Some tests failed
    pause
    exit /b 1
)

echo All backend tests passed!
echo.
echo Now checking frontend...
cd frontend
echo Installing Flutter dependencies...
flutter pub get
if %errorlevel% neq 0 (
    echo Failed to install Flutter dependencies
    pause
    exit /b 1
)

echo Running Flutter tests...
flutter test
if %errorlevel% neq 0 (
    echo Some Flutter tests failed
    pause
    exit /b 1
)

echo All Flutter tests passed!
cd ..
echo.
echo ============================================
echo ALL TESTS PASSED SUCCESSFULLY!
echo ============================================
echo.
echo Ready to commit and push to GitHub...
echo.
pause
