param(
    [string]$Url = "http://localhost:8000",
    [string]$HealthUrl = "http://localhost:8000/api/v1/health",
    [int]$TimeoutSeconds = 120
)

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$ready = $false

while ((Get-Date) -lt $deadline) {
    foreach ($probe in @($HealthUrl, $Url)) {
        try {
            $response = Invoke-WebRequest -Uri $probe -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                $ready = $true
                break
            }
        } catch {
            Start-Sleep -Milliseconds 250
        }
    }

    if ($ready) {
        break
    }

    Start-Sleep -Seconds 1
}

Start-Process $Url
