@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "LOG_DIR=%SCRIPT_DIR%logs"
set "LOG_FILE=%LOG_DIR%\setup.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

pushd "%SCRIPT_DIR%"

powershell -NoProfile -Command "Write-Output (Get-Date -Format 'u' + ' – Creating virtual environment in %VENV_DIR%') | Tee-Object -FilePath '%LOG_FILE%' -Append"

powershell -NoProfile -Command "python -m venv '%VENV_DIR%' 2>&1 | Tee-Object -FilePath '%LOG_FILE%' -Append"

call "%VENV_DIR%\Scripts\activate.bat"

powershell -NoProfile -Command "Write-Output (Get-Date -Format 'u' + ' – Upgrading pip') | Tee-Object -FilePath '%LOG_FILE%' -Append"

powershell -NoProfile -Command "pip install --upgrade pip 2>&1 | Tee-Object -FilePath '%LOG_FILE%' -Append"

if exist "%SCRIPT_DIR%requirements.txt" (
    powershell -NoProfile -Command "Write-Output (Get-Date -Format 'u' + ' – Installing packages from requirements.txt') | Tee-Object -FilePath '%LOG_FILE%' -Append"
    powershell -NoProfile -Command "pip install -r '%SCRIPT_DIR%requirements.txt' 2>&1 | Tee-Object -FilePath '%LOG_FILE%' -Append"
)

powershell -NoProfile -Command "Write-Output (Get-Date -Format 'u' + ' – Virtual environment created in %VENV_DIR%') | Tee-Object -FilePath '%LOG_FILE%' -Append"

popd
endlocal
