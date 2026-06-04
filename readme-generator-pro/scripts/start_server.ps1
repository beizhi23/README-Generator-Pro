$SkillDir = Split-Path -Parent $PSScriptRoot
$ProjectDir = Join-Path $SkillDir "assets\readme-generator-pro"

Set-Location $ProjectDir
python run.py
