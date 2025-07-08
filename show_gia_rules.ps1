# GIA 협업헌장 및 RULES 자동 출력 스크립트 (PowerShell)
$rules = "D:\AI_Project\GIAv2.0\GIA_Rules.md"
if (Test-Path $rules) {
    Write-Host "=== GIA 협업헌장 및 RULES (요약) ===" -ForegroundColor Cyan
    Get-Content $rules -TotalCount 50
    Write-Host "\n↑ 위는 GIA 협업헌장 및 RULES 요약입니다. 반드시 숙지 후 작업을 시작하세요!" -ForegroundColor Yellow
} else {
    Write-Host "GIA_Rules.md 파일을 찾을 수 없습니다." -ForegroundColor Red
} 