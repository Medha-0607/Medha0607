@echo off
setlocal EnableDelayedExpansion
title RECTRA - Digital Companion for Field Drug Testing (SIH26231)

echo ===============================================================================
echo                      RECTRA FIELD RUNTIME INITIALIZATION
echo       Calibrated Field-Test Intelligence and Presumptive Evidence System
echo ===============================================================================
echo.

:: 1. Check Python Availability
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not found on your PATH.
    echo Please install Python 3.11 and ensure "Add Python to PATH" is checked.
    echo.
    pause
    exit /b 1
)

:: 2. Activate Virtual Environment if present
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment (.venv)...
    call .venv\Scripts\activate.bat
) else (
    echo [WARN] Virtual environment .venv not found. Using system Python.
)

:: 3. Check / Initialize Cryptographic Keys
if not exist "runtime\keys\rectra_demo.key" (
    echo [INFO] Initializing Ed25519 cryptographic keypair...
    python scripts\generate_demo_keys.py
)

:: 4. Check / Initialize Local Database
if not exist "runtime\rectra.db" (
    echo [INFO] Initializing SQLite local database and schema...
    python scripts\init_database.py
)

:: 5. Check / Generate Reference Card & Demo Data
if not exist "assets\reference_cards\RECTRA_DEMO_REFERENCE_CARD.png" (
    echo [INFO] Generating reference card...
    python scripts\generate_reference_card.py
)

if not exist "data\demo\ground_truth.json" (
    echo [INFO] Generating deterministic synthetic demonstration dataset...
    python scripts\generate_demo_data.py
)

:: 6. Launch Browser and Start Streamlit Server
echo.
echo ===============================================================================
echo [SUCCESS] Runtime initialized. Launching RECTRA Field Application...
echo Local Application URL: http://localhost:8501
echo Press Ctrl+C in this terminal window to stop the server.
echo ===============================================================================
echo.

start "" "http://localhost:8501"
streamlit run app.py --server.port 8501

pause
