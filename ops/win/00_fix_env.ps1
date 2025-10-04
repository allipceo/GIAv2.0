$ErrorActionPreference = "Stop"

chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

# Cleanup listeners on 8000 and 8080
$ports = @(8000, 8080)
foreach ($pt in $ports) {
    $cons = Get-NetTCPConnection -LocalPort $pt -ErrorAction SilentlyContinue
    if ($cons) {
        $pids = $cons | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($procId in $pids) { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue }
        Write-Output ("Stopped PIDs on port ${pt}: " + ($pids -join ','))
    } else {
        Write-Output "No process found on port ${pt}"
    }
}

$env:PORT = "8080"
Write-Output ("ENV READY: PORT=8080, UTF-8 ON")



