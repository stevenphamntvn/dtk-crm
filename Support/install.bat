@echo off
title CAI DAT MOI TRUONG CRM (PYTHON 3.13)
color 0B

:: 1. Kiểm tra xem Python đã được cài chưa
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Python. Vui long cai Python 3.13 va tich vao 'Add Python to PATH'.
    pause
    exit
)

echo [+] Dang khoi tao moi truong ao (env_crm)...
python -m venv env_crm

echo [+] Dang kich hoat moi truong va cai dat thu vien...
:: Gọi pip của môi trường ảo để cài đặt
env_crm\Scripts\python.exe -m pip install --upgrade pip
env_crm\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo [OK] Moi truong da san sang!
echo [!] Luu y: Hay dung file run.bat moi de chay App.
pause