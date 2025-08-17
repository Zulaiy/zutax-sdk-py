@echo off
REM Setup script for FIRS E-Invoice Python SDK on Windows

echo ===========================================
echo FIRS E-Invoice Python SDK Setup for Windows
echo ===========================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo   Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo Warning: Failed to upgrade pip
)
echo pip upgraded
echo.

REM Install Poetry
echo Installing Poetry...
pip install poetry --quiet
if %errorlevel% neq 0 (
    echo Error: Failed to install Poetry
    pause
    exit /b 1
)
echo Poetry installed
echo.

REM Configure Poetry to use the virtual environment
echo Configuring Poetry...
poetry config virtualenvs.in-project true
poetry config virtualenvs.create false
echo Poetry configured
echo.

REM Install dependencies
echo Installing dependencies with Poetry...
echo This may take a few minutes...
poetry install
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    echo Try running: poetry install --verbose
    pause
    exit /b 1
)
echo Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    if exist .env.example (
        echo Creating .env file from template...
        copy .env.example .env >nul
        echo .env file created - please update with your credentials
        echo.
    )
)

REM Create output directory
if not exist output (
    echo Creating output directory...
    mkdir output
    echo Output directory created
    echo.
)

REM Verify installation
echo Verifying installation...
python -c "import firs_einvoice; print(f'FIRS E-Invoice SDK v{firs_einvoice.__version__} installed successfully')" 2>nul
if %errorlevel% neq 0 (
    echo Warning: Could not verify installation. Try running: poetry install
)
echo.

echo ===========================================
echo Setup complete!
echo.
echo To activate the environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To run the example:
echo   poetry run python examples\simple_invoice.py
echo.
echo To deactivate when done:
echo   deactivate
echo ===========================================
pause