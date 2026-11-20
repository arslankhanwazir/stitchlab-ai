# StitchLab AI Client Environment Activation
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (Test-Path "$ScriptDir\.venv\Scripts\Activate.ps1") {
    & "$ScriptDir\.venv\Scripts\Activate.ps1"
}

# Offline and Telemetry Protection
$env:ANONYMIZED_TELEMETRY = "False"
$env:GRADIO_ANALYTICS_ENABLED = "False"
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"

Write-Host "StitchLab AI client environment active. Telemetry: OFF. Offline mode: ON." -ForegroundColor Green
