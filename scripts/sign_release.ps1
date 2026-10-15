<#
.SYNOPSIS
  Authenticode-signs the release EXE and regenerates its SHA-256 checksum.
.DESCRIPTION
  The PFX is imported into the current user's certificate store only for the
  duration of signing and SignTool selects it by thumbprint, so the password is
  never placed on a command line where other processes could read it. The
  imported certificate and its private key are removed afterwards.
#>
param(
  [Parameter(Mandatory=$true)][string]$PfxPath,
  [Parameter(Mandatory=$true)][SecureString]$PfxPassword,
  [string]$ExePath = "$PSScriptRoot\..\dist\Win11NetSpeedCompact.exe",
  # RFC 3161 timestamps are signed by the TSA, so plain HTTP is standard here.
  [string]$TimestampUrl = "http://timestamp.digicert.com"
)
$ErrorActionPreference='Stop'
if(-not (Test-Path -LiteralPath $ExePath)){throw "Build the EXE first: $ExePath"}
if(-not (Test-Path -LiteralPath $PfxPath)){throw "PFX not found: $PfxPath"}
$signtool=Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin" -Filter signtool.exe -Recurse -ErrorAction SilentlyContinue | Where-Object {$_.FullName -match '\\x64\\'} | Sort-Object FullName -Descending | Select-Object -First 1
if(-not $signtool){throw 'SignTool was not found. Install the Windows SDK.'}

$imported=@()
try {
  $imported=@(Import-PfxCertificate -FilePath $PfxPath -CertStoreLocation Cert:\CurrentUser\My -Password $PfxPassword)
  $cert=$imported | Where-Object {$_.HasPrivateKey} | Select-Object -First 1
  if(-not $cert){throw 'The PFX does not contain a private key.'}
  $eku=@($cert.EnhancedKeyUsageList | ForEach-Object {$_.ObjectId})
  if($eku.Count -gt 0 -and $eku -notcontains '1.3.6.1.5.5.7.3.3'){throw 'The certificate is not valid for code signing.'}
  if($cert.NotAfter -lt (Get-Date)){throw "The certificate expired on $($cert.NotAfter)."}

  & $signtool.FullName sign /sha1 $cert.Thumbprint /s My /fd SHA256 /tr $TimestampUrl /td SHA256 $ExePath
  if($LASTEXITCODE -ne 0){throw "SignTool sign failed: $LASTEXITCODE"}
  & $signtool.FullName verify /pa /v $ExePath
  if($LASTEXITCODE -ne 0){throw "SignTool verify failed: $LASTEXITCODE"}
  $h=(Get-FileHash -LiteralPath $ExePath -Algorithm SHA256).Hash.ToLower()
  Set-Content -Encoding ASCII -LiteralPath "$ExePath.sha256.txt" "$h  $([IO.Path]::GetFileName($ExePath))"
  Write-Host "Signed and verified: $ExePath"
} finally {
  foreach($c in $imported){
    Remove-Item -LiteralPath "Cert:\CurrentUser\My\$($c.Thumbprint)" -DeleteKey -ErrorAction SilentlyContinue
  }
}
