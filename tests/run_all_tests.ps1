$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$job = Start-Job -ScriptBlock {
    param($root)
    Set-Location $root
    python manage.py runserver 127.0.0.1:8000 --noreload
} -ArgumentList $projectRoot
$showServerLog = $false

try {
    $ready = $false
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        $tcp = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue
        if ($tcp.TcpTestSucceeded) {
            $ready = $true
            break
        }
        if ($job.State -ne "Running") {
            break
        }
    }

    if (-not $ready) {
        $showServerLog = $true
        Receive-Job $job
        throw "Django service did not start on 127.0.0.1:8000."
    }

    python -m unittest tests.test_function_whitebox -v
    if ($LASTEXITCODE -ne 0) {
        $showServerLog = $true
        exit $LASTEXITCODE
    }

    python -m unittest tests.test_api_blackbox -v
    if ($LASTEXITCODE -ne 0) {
        $showServerLog = $true
    }
    exit $LASTEXITCODE
}
finally {
    Stop-Job $job -ErrorAction SilentlyContinue
    if ($showServerLog) {
        Receive-Job $job -ErrorAction SilentlyContinue | Select-Object -Last 40
    } else {
        Receive-Job $job -ErrorAction SilentlyContinue | Out-Null
    }
    Remove-Job $job -ErrorAction SilentlyContinue
}
