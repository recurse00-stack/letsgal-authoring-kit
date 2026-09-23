@echo off
setlocal
powershell.exe -NoLogo -NoProfile -STA -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0Import.ps1" -InitialAction Check
exit /b %ERRORLEVEL%
