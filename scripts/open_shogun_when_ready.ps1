param(
    [string]$Url = "http://localhost:8000",
    [string]$HealthUrl = "http://localhost:8000/api/v1/health",
    [int]$TimeoutSeconds = 120,
    [string]$LogPath = ""
)

if (-not $LogPath) {
    $scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    $projectRoot = Split-Path -Parent $scriptRoot
    $LogPath = Join-Path $projectRoot "logs\launcher-browser.log"
}

function Write-LauncherLog {
    param([string]$Message)
    try {
        $dir = Split-Path -Parent $LogPath
        if ($dir -and -not (Test-Path $dir)) {
            New-Item -ItemType Directory -Force -Path $dir | Out-Null
        }
        $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -Path $LogPath -Value "[$stamp] $Message" -Encoding UTF8
    } catch {
        # Logging must never block browser launch.
    }
}

function Open-ShogunUrl {
    param([string]$TargetUrl)

    try {
        Write-LauncherLog "Opening via Start-Process URL: $TargetUrl"
        Start-Process -FilePath $TargetUrl
        return $true
    } catch {
        Write-LauncherLog "Start-Process URL failed: $($_.Exception.Message)"
    }

    try {
        Write-LauncherLog "Opening via ShellExecute: $TargetUrl"
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $TargetUrl
        $psi.UseShellExecute = $true
        [System.Diagnostics.Process]::Start($psi) | Out-Null
        return $true
    } catch {
        Write-LauncherLog "ShellExecute failed: $($_.Exception.Message)"
    }

    try {
        Write-LauncherLog "Opening via rundll32 fallback: $TargetUrl"
        Start-Process -FilePath "rundll32.exe" -ArgumentList @("url.dll,FileProtocolHandler", $TargetUrl)
        return $true
    } catch {
        Write-LauncherLog "rundll32 fallback failed: $($_.Exception.Message)"
    }

    return $false
}

Write-LauncherLog "Waiting for Shogun. Url=$Url HealthUrl=$HealthUrl TimeoutSeconds=$TimeoutSeconds"

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$ready = $false

while ((Get-Date) -lt $deadline) {
    foreach ($probe in @($HealthUrl, $Url)) {
        try {
            $response = Invoke-WebRequest -Uri $probe -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                $ready = $true
                Write-LauncherLog "Ready probe succeeded: $probe HTTP $($response.StatusCode)"
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

if (-not $ready) {
    Write-LauncherLog "Timed out waiting for readiness; opening URL anyway."
}

if (-not (Open-ShogunUrl $Url)) {
    Write-LauncherLog "All browser open methods failed."
}
