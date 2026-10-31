@echo off
setlocal
title CRM
color 0E
cd /d "%~dp0"
if not exist "logs" mkdir "logs" >nul 2>&1
set PYTHONUTF8=1
cls
echo.
echo.
echo.
echo     ####  ####   #   #
echo    #      #   #  ## ##
echo    #      ####   # # #
echo    #      #  #   #   #
echo     ####  #   #  #   #
echo.
echo.
echo.
python -m streamlit run data\crm_app.py --server.port 8504
pause >nul
endlocal
