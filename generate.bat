@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "INPUT_DIR=%SCRIPT_DIR%input"
set "OUTPUT_DIR=%SCRIPT_DIR%output"
set "LOG_DIR=%SCRIPT_DIR%logs"

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "LOG_FILE=%LOG_DIR%\cmd_%%i.log"

pushd "%SCRIPT_DIR%"

if exist "%INPUT_DIR%\*.json" (
    for %%F in ("%INPUT_DIR%\*.json") do (
        powershell -NoProfile -Command "Write-Output ('Processing %%F') | Tee-Object -FilePath '%LOG_FILE%' -Append"
        powershell -NoProfile -Command "python -m scenegen.cli --in '%%F' --out-dir '%OUTPUT_DIR%' 2>&1 | Tee-Object -FilePath '%LOG_FILE%' -Append"
    )
) else (
    echo No JSON files found in %INPUT_DIR%
)

popd
endlocal
