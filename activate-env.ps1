$env:HF_HOME = "F:\stitchlab-cache\hf"
$env:PIP_CACHE_DIR = "F:\stitchlab-cache\pip"
$env:TEMP = "F:\stitchlab-cache\tmp"
$env:TMP = "F:\stitchlab-cache\tmp"
$env:ANONYMIZED_TELEMETRY = "False"
$env:GRADIO_ANALYTICS_ENABLED = "False"

if (Test-Path "$PSScriptRoot\.venv\Scripts\Activate.ps1") {
    . "$PSScriptRoot\.venv\Scripts\Activate.ps1"
} elseif (Test-Path "F:\stitchlab-ai\.venv\Scripts\Activate.ps1") {
    . "F:\stitchlab-ai\.venv\Scripts\Activate.ps1"
}
