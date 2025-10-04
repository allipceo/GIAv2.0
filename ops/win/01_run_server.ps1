$ErrorActionPreference = "Stop"

$env:PORT = '8080'
$cmd = 'python -X utf8 -u webhook_server.py'
Write-Output "PORT=$($env:PORT)"
Write-Output "START: $cmd (PORT=$($env:PORT))"

# Run in current session so env propagates
& python -X utf8 -u webhook_server.py



