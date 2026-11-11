@echo off
rem MMAN: cut + Change status. MMAN_*.txt + status list (.xls/.xlsx/.csv) in input\  ->  output\MMAN_<POD>.txt
rem Keep this file ASCII only: Thai text in a .bat breaks cmd. The questions (Thai) come from mman_vn.py --ask.
setlocal
cd /d "%~dp0"
chcp 65001 >nul <nul
set PYTHONIOENCODING=utf-8

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (where python >nul 2>nul && set "PY=python")
if not defined PY (
  echo [ERROR] Python not found - install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH"
  pause
  exit /b 1
)

%PY% -c "import pandas, xlrd, openpyxl" 2>nul || (
  echo Installing pandas, xlrd, openpyxl - first run only...
  %PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt || (
    echo [ERROR] install failed - check the internet connection
    pause
    exit /b 1
  )
)

%PY% mman_vn.py --ask
if errorlevel 1 (
  echo.
  echo [ERROR] not done - read the message above
) else (
  echo.
  echo Done: open the file in the output folder
)
pause
