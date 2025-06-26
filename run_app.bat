@echo off
chcp 65001 >nul
cd /d "C:\Users\jaewonchoi\Desktop\KDT\finance\Customs\airconditioner"

REM Conda activate
call C:\Users\jaewonchoi\miniconda3\Scripts\activate.bat Aitest

REM Install packages
echo Installing required packages...
pip install streamlit requests geocoder

REM Run Streamlit
echo.
echo Starting Airconditioner Calculator...
echo.
streamlit run Airconditioner.py

pause