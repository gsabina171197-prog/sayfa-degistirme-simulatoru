@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul && (set "PY=py") || (set "PY=python")
echo === BIM361 - Bireysel Ara Teslim - 11.11.2026 ===
%PY% --version
%PY% -m unittest discover -s tests
if errorlevel 1 (echo Testler basarisiz. & pause & exit /b 1)
echo.
echo Demo Enter ile ilerler, a Enter ile sona kadar ilerler.
%PY% main.py -f data/ornek.txt -k 3 --step
pause
