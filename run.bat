@echo off
title HE THONG DAI THE KY ADVISOR (CRM V1.0)
color 0A

:: 1. Tự động chuyển đến thư mục gốc chứa file run.bat này
cd /d "%~dp0"

:: 2. Chạy Streamlit thông qua module Python để tránh lỗi 'not recognized'
echo [+] Dang khoi dong CRM Dashboard...
python -m streamlit run data\crm_app.py

pause