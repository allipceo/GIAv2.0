@echo off
REM GIA MVP1.0 자동화 시스템 실행 배치 파일
REM 작성일: 2025년 1월 12일
REM 작성자: 서대리 (Lead Developer)

echo ================================================
echo    GIA MVP1.0 자동화 시스템 시작
echo    작성자: 서대리 (Lead Developer)
echo    일시: %date% %time%
echo ================================================

REM 현재 디렉토리를 스크립트 위치로 변경
cd /d "%~dp0"

echo [INFO] 작업 디렉토리: %cd%

REM Python 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Python 가상환경 활성화 중...
    call venv\Scripts\activate.bat
) else (
    echo [INFO] 가상환경이 없습니다. 시스템 Python 사용
)

REM Python 버전 확인
echo [INFO] Python 버전 확인:
python --version

REM 필요한 라이브러리 설치 확인
echo [INFO] 필요한 라이브러리 설치 확인 중...
if exist "requirements_mvp1.txt" (
    pip install -r requirements_mvp1.txt --quiet
    if %errorlevel% neq 0 (
        echo [ERROR] 라이브러리 설치 실패
        pause
        exit /b 1
    )
) else (
    echo [WARNING] requirements_mvp1.txt 파일을 찾을 수 없습니다.
)

REM 로그 디렉토리 생성
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "backup" mkdir backup

echo [INFO] 필요한 디렉토리 생성 완료

REM MVP1.0 자동화 실행
echo ================================================
echo    MVP1.0 자동화 파이프라인 실행 시작
echo ================================================

python mvp1_automation.py

REM 실행 결과 확인
if %errorlevel% equ 0 (
    echo ================================================
    echo    ✅ MVP1.0 자동화 성공적 완료
    echo    생성된 파일들을 확인해주세요:
    echo    - logs/mvp1_automation.log (실행 로그)
    echo    - data/ (처리된 뉴스 데이터)
    echo    - backup/ (백업 파일)
    echo ================================================
) else (
    echo ================================================
    echo    ❌ MVP1.0 자동화 실행 실패
    echo    logs/mvp1_automation.log 파일을 확인해주세요.
    echo ================================================
)

REM 로그 파일 마지막 50줄 표시
echo [INFO] 최근 로그 (마지막 20줄):
echo ────────────────────────────────────────────────
if exist "logs\mvp1_automation.log" (
    powershell "Get-Content 'logs\mvp1_automation.log' | Select-Object -Last 20"
) else (
    echo 로그 파일이 없습니다.
)
echo ────────────────────────────────────────────────

echo.
echo [완료] MVP1.0 자동화 실행이 완료되었습니다.
echo 조대표님께서 노션에서 결과를 확인하실 수 있습니다.
echo.

REM 사용자 입력 대기 (배치 창이 자동으로 닫히지 않도록)
pause 