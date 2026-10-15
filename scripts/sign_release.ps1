param(
  [Parameter(Mandatory=$true)][string]$PfxPath,
  [Parameter(Mandatory=$true)][SecureString]$PfxPassword,
  [string]$ExePath = "$PSScriptRoot\..\dist\Win11NetSpeedCompact.exe",
  [string]$TimestampUrl = "http://timestamp.digicert.com"
)
$ErrorActionPreference='Stop'
if(-not (Test-Path $ExePath)){throw "Build the EXE first: $ExePath"}
$signtool=Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin" -Filter signtool.exe -Recurse -ErrorAction SilentlyContinue | Where-Object {$_.FullName -match '\\x64\\'} | Sort-Object FullName -Descending | Select-Object -First 1
if(-not $signtool){throw 'SignTool was not found. Install the Windows SDK.'}
$plain=[Runtime.InteropServices.Marshal]::PtrToStringBSTR([Runtime.InteropServices.Marshal]::SecureStringToBSTR($PfxPassword))
try {
  & $signtool.FullName sign /f $PfxPath /p $plain /fd SHA256 /tr $TimestampUrl /td SHA256 $ExePath
  if($LASTEXITCODE -ne 0){throw "SignTool sign failed: $LASTEXITCODE"}
  & $signtool.FullName verify /pa /v $ExePath
  if($LASTEXITCODE -ne 0){throw "SignTool verify failed: $LASTEXITCODE"}
  $h=(Get-FileHash $ExePath -Algorithm SHA256).Hash.ToLower()
  Set-Content -Encoding ASCII "$ExePath.sha256.txt" "$h  $([IO.Path]::GetFileName($ExePath))"
  Write-Host "Signed and verified: $ExePath"
} finally {$plain=$null}
