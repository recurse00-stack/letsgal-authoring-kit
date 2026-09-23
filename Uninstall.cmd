@echo off
setlocal
powershell.exe -NoLogo -NoProfile -STA -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0Import.ps1" -InitialAction Uninstall
exit /b %ERRORLEVEL%
