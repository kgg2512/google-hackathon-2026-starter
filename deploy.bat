@echo off
powershell.exe -NoProfile -File "%~dp0deploy.ps1" %*
exit /b %errorlevel%
