@echo off
echo ============================================
echo   한국형 에어컨 가동률 예측기 설치 및 실행
echo ============================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python을 먼저 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 가상환경 생성 (없으면)
if not exist "venv" (
    echo 가상환경을 생성합니다...
    python -m venv venv
)

REM 가상환경 활성화
echo 가상환경을 활성화합니다...
call venv\Scripts\activate.bat

REM pip 업그레이드
python -m pip install --upgrade pip

REM 패키지 설치
echo.
echo 필요한 패키지를 설치합니다...
pip install -r requirements.txt

REM Streamlit 실행
echo.
echo ============================================
echo   설치가 완료되었습니다!
echo   웹 브라우저에서 자동으로 열립니다...
echo ============================================
echo.
streamlit run Airconditioner.py

pause