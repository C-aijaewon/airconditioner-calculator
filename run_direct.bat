@echo off
cd /d "C:\Users\jaewonchoi\Desktop\KDT\finance\Customs\airconditioner"

echo Installing packages...
C:\Users\jaewonchoi\miniconda3\envs\Aitest\Scripts\pip.exe install streamlit requests geocoder

echo.
echo Starting application...
C:\Users\jaewonchoi\miniconda3\envs\Aitest\Scripts\streamlit.exe run Airconditioner.py

pause