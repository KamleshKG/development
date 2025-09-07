@echo off
echo.
echo ----------------------------------------
echo    WELCOME TO YOUR DEV WORKSTATION
echo ----------------------------------------
echo.

:menu
echo What would you like to do?
echo.
echo   [1] WORK on Unified DevOps Portal
echo   [2] Exit
echo.

set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" goto portal
if "%choice%"=="2" goto exit

echo Invalid choice. Please try again.
echo.
goto menu

:portal
echo.
echo "Loading your DevOps Portal environment..."
echo.

set VENV_PATH=E:\PYTHON_VENVS\py311_streamlit
set PROJECT_PATH=E:\development\development\unified_devops_portal

REM Check if venv exists, if not, create it
if not exist "%VENV_PATH%" (
    echo Creating a new environment for you...
    "C:\Users\admin\AppData\Local\Programs\Python\Python311\python.exe" -m venv "%VENV_PATH%"
)

REM Activate the environment
call "%VENV_PATH%\Scripts\activate.bat"

REM Navigate to the project
cd /d "%PROJECT_PATH%"

REM Install the project in editable mode (if not done already)
echo Making sure everything is installed...
pip install -e .

REM Check if requirements are met
echo Checking packages...
pip install -r requirements.txt

echo.
echo Environment is READY!
echo You are in the project folder: %PROJECT_PATH%
echo Type 'streamlit run core/app.py' to start.
echo.
cmd /k
goto exit

:exit
echo Goodbye!
pause