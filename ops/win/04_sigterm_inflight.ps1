$ErrorActionPreference = "Stop"

Write-Output "서버를 재기동하세요. 다른 창에서:"
Write-Output "curl.exe \"http://127.0.0.1:8080/sleep?ms=3000\""
Write-Output "바로 서버 창에서 Ctrl+C → 종료 총 소요(ms)를 기록해 주세요."


