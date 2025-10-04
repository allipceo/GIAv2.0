$ErrorActionPreference = "Stop"

function CurlTime($url){
    $(curl.exe -w "%{time_total}`n" -o NUL -s $url)
}

$t0 = CurlTime("http://127.0.0.1:8080/healthz")
Start-Sleep -Milliseconds 150
$t1 = CurlTime("http://127.0.0.1:8080/healthz")
Start-Sleep -Milliseconds 150
$t2 = CurlTime("http://127.0.0.1:8080/healthz")

$h  = curl.exe -i -s http://127.0.0.1:8080/health | findstr /R "^HTTP/1.1 200"

Write-Output ("t0=" + $t0 + " s ; t1=" + $t1 + " s ; t2=" + $t2 + " s")
Write-Output ("HEALTH: " + $h)



