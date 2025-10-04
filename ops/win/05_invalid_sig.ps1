$ErrorActionPreference = "Stop"

curl.exe -s -X POST http://127.0.0.1:8080/webhook/case1 `
    -H "Content-Type: application/json" `
    -H "X-Signature: invalid" `
    -H "X-Timestamp: 0" `
    -H "X-Nonce: test" `
    -d "{}"

Write-Output "확인: stdout JSON은 server_stdout.log, 파일 로그는 logs/security_YYYYMMDD.log에서 발췌해 주세요."


