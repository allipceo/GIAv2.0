# GIA 일일 자동 실행 스케줄 설정 스크립트
# 작성자: 서대리 (Lead Developer)
# 작성일: 2025년 1월 13일
# 목적: 조대표님 맞춤 GIA 시스템 일일 자동 실행 스케줄 설정

Write-Host "🚀 GIA 일일 자동 실행 스케줄 설정 시작" -ForegroundColor Green
Write-Host "=" * 60

# 관리자 권한 확인
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ 관리자 권한이 필요합니다. PowerShell을 관리자로 실행해주세요." -ForegroundColor Red
    exit 1
}

# 현재 디렉토리 확인
$currentDir = Get-Location
Write-Host "📁 현재 작업 디렉토리: $currentDir" -ForegroundColor Yellow

# Python 실행 파일 확인
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "❌ Python이 설치되지 않았거나 PATH에 등록되지 않았습니다." -ForegroundColor Red
    exit 1
}
Write-Host "🐍 Python 경로: $($pythonPath.Source)" -ForegroundColor Green

# mvp1_automation.py 파일 존재 확인
$automationScript = "$currentDir\mvp1_automation.py"
if (-not (Test-Path $automationScript)) {
    Write-Host "❌ mvp1_automation.py 파일을 찾을 수 없습니다: $automationScript" -ForegroundColor Red
    exit 1
}
Write-Host "📄 자동화 스크립트 확인: mvp1_automation.py" -ForegroundColor Green

# 작업 스케줄러 태스크 생성
$taskName = "GIA_Daily_Automation"
$taskDescription = "GIA 지능형 정보 에이전트 일일 자동 실행"
$taskAction = New-ScheduledTaskAction -Execute $pythonPath.Source -Argument $automationScript -WorkingDirectory $currentDir

# 트리거 설정 (매일 오전 8시)
$taskTrigger = New-ScheduledTaskTrigger -Daily -At "08:00"

# 추가 트리거 (매일 오후 6시 - 저녁 업데이트)
$eveningTrigger = New-ScheduledTaskTrigger -Daily -At "18:00" 

# 설정 옵션
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 사용자 계정 설정 (현재 사용자)
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$taskPrincipal = New-ScheduledTaskPrincipal -UserId $currentUser -LogonType Interactive

# 기존 태스크 삭제 (있다면)
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "🗑️ 기존 태스크 삭제 완료" -ForegroundColor Yellow
} catch {
    Write-Host "ℹ️ 기존 태스크가 없음" -ForegroundColor Gray
}

# 새 태스크 등록
try {
    Register-ScheduledTask -TaskName $taskName -Description $taskDescription -Action $taskAction -Trigger @($taskTrigger, $eveningTrigger) -Settings $taskSettings -Principal $taskPrincipal -Force
    Write-Host "✅ 작업 스케줄러 태스크 등록 성공!" -ForegroundColor Green
    
    # 태스크 상태 확인
    $task = Get-ScheduledTask -TaskName $taskName
    Write-Host "📋 태스크 정보:" -ForegroundColor Cyan
    Write-Host "   - 이름: $($task.TaskName)" -ForegroundColor White
    Write-Host "   - 상태: $($task.State)" -ForegroundColor White
    Write-Host "   - 실행 시간: 매일 오전 8시, 오후 6시" -ForegroundColor White
    Write-Host "   - 실행 파일: $automationScript" -ForegroundColor White
    
} catch {
    Write-Host "❌ 작업 스케줄러 태스크 등록 실패: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 배치 파일 생성 (수동 실행용)
$batchContent = @"
@echo off
cd /d "$currentDir"
echo 🤖 GIA 시스템 수동 실행 시작
echo ====================================
python mvp1_automation.py
echo.
echo ✅ GIA 시스템 실행 완료
pause
"@

$batchFile = "$currentDir\run_gia_manual.bat"
$batchContent | Out-File -FilePath $batchFile -Encoding ascii
Write-Host "📄 수동 실행 배치 파일 생성: run_gia_manual.bat" -ForegroundColor Green

# 로그 디렉토리 생성
$logDir = "$currentDir\logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force
    Write-Host "📁 로그 디렉토리 생성: $logDir" -ForegroundColor Green
}

# 알림 설정 파일 생성
$notificationConfig = @{
    "notification_enabled" = $true
    "notification_methods" = @("notion", "log")
    "notion_notification_page_id" = "22ea613d25ff819698ccf55e84b650c8"
    "email_notification" = $false
    "slack_notification" = $false
    "telegram_notification" = $false
    "created_at" = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    "description" = "GIA 시스템 알림 설정"
}

$notificationConfigPath = "$currentDir\notification_config.json"
$notificationConfig | ConvertTo-Json -Depth 3 | Out-File -FilePath $notificationConfigPath -Encoding UTF8
Write-Host "📧 알림 설정 파일 생성: notification_config.json" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 GIA 일일 자동 실행 스케줄 설정 완료!" -ForegroundColor Green
Write-Host "⏰ 실행 시간: 매일 오전 8시, 오후 6시" -ForegroundColor Cyan
Write-Host "📊 대시보드는 자동으로 업데이트됩니다." -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 주요 파일들:" -ForegroundColor Yellow
Write-Host "   - 작업 스케줄러: $taskName" -ForegroundColor White
Write-Host "   - 수동 실행: run_gia_manual.bat" -ForegroundColor White
Write-Host "   - 설정 파일: notification_config.json" -ForegroundColor White
Write-Host "   - 로그 디렉토리: logs\" -ForegroundColor White
Write-Host ""
Write-Host "🔧 작업 스케줄러에서 '$taskName' 태스크를 확인하실 수 있습니다." -ForegroundColor Cyan
Write-Host "🔄 즉시 테스트하려면 'run_gia_manual.bat'을 실행하세요." -ForegroundColor Cyan 