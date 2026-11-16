@echo off
setlocal
if exist "%~dp0workbench_server.py" (
  python -B -X utf8 "%~dp0workbench_server.py" --user-area "%~dp0.."
) else (
  python -B -X utf8 "%~dp0maintenance\workbench_runtime.py" setup --source "%~dp0." --user-area "%USERPROFILE%\.letsgal-authoring"
  if errorlevel 1 goto failed
  python -B -X utf8 "%USERPROFILE%\.letsgal-authoring\workbench\workbench_server.py" --user-area "%USERPROFILE%\.letsgal-authoring"
)
if errorlevel 1 goto failed
exit /b 0
:failed
echo Workbench could not start. Python 3.10+ is required. Details are shown above.
pause
exit /b 1
