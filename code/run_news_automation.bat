@echo off
chcp 65001 >nul
title 뉴스 클리핑 자동화 시스템 (인코딩 안전 버전)

echo ================================================
echo 🎯 뉴스 클리핑 완전 자동화 시스템 시작
echo ================================================
echo [INFO] Windows 인코딩 안전성 보장 모드
echo [INFO] UTF-8 코드페이지 활성화 완료
echo ================================================
echo.

REM Python UTF-8 모드로 실행 (인코딩 문제 완전 방지)
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8
python -X utf8 run_news_automation.py

echo.
echo ================================================
echo 자동화 프로세스 완료
echo ================================================
pause 