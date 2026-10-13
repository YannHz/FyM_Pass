param([Parameter(Mandatory=$true)][string]$Direccion)
$ErrorActionPreference = 'Stop'
$direccionIp = [System.Net.IPAddress]::Parse($Direccion)
$adaptadorFym = Get-NetIPAddress -InterfaceAlias 'Wi-Fi' -AddressFamily IPv4 | Where-Object IPAddress -eq $Direccion
if (-not $adaptadorFym -or $direccionIp.AddressFamily -ne 'InterNetwork') { throw 'La direccion debe pertenecer al Wi-Fi de esta PC.' }
$nombreRegla = 'FyM Pass API Wi-Fi demo'
Get-NetFirewallRule -DisplayName $nombreRegla -ErrorAction SilentlyContinue | Remove-NetFirewallRule
New-NetFirewallRule -DisplayName $nombreRegla -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8000 -LocalAddress $Direccion -RemoteAddress LocalSubnet -InterfaceAlias 'Wi-Fi' -Profile Any | Out-Null
'Regla Wi-Fi creada para ' + $Direccion | Set-Content -LiteralPath "$PSScriptRoot\.registros\firewall-red.log"
