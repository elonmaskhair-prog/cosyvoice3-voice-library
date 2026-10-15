$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
foreach ($voiceTool in @('uv', 'git', 'ffmpeg')) {
    if (-not (Get-Command $voiceTool -ErrorAction SilentlyContinue)) {
        throw "Install $voiceTool and add it to PATH before running setup. See README.md."
    }
}
if (-not (Test-Path -LiteralPath .venv\Scripts\python.exe)) {
    & uv venv --python 3.12 .venv
    if ($LASTEXITCODE -ne 0) { throw 'Could not create Python environment.' }
}
& .\.venv\Scripts\python.exe scripts\fetch_source.py
if ($LASTEXITCODE -ne 0) { throw 'Could not fetch pinned upstream source.' }
& uv pip install --python .venv\Scripts\python.exe --index-strategy unsafe-best-match -r requirements-resolved-win.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& .\.venv\Scripts\python.exe scripts\download_model.py
if ($LASTEXITCODE -ne 0) { throw 'Base model download or verification failed.' }
& .\.venv\Scripts\python.exe scripts\verify_assets.py
if ($LASTEXITCODE -ne 0) { throw 'Voice asset verification failed.' }
Write-Host 'Ready. Run start.cmd and open http://127.0.0.1:7861.'
