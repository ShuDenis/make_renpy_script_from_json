@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "LOG_DIR=%SCRIPT_DIR%logs"
set "LOG_FILE=%LOG_DIR%\run.log"
set "VENV_DIR=%SCRIPT_DIR%.venv"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

pushd "%SCRIPT_DIR%"

powershell -NoProfile -Command "Write-Output (Get-Date -Format 'u' + ' – Starting scenegen') | Tee-Object -FilePath '%LOG_FILE%' -Append"

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment not found. Run setup.bat first.
    popd
    exit /b 1
)

call "%VENV_DIR%\Scripts\activate.bat"

powershell -NoProfile -Command "python -m scenegen.cli %* 2>&1 | Tee-Object -FilePath '%LOG_FILE%' -Append"

popd
endlocal
