$ErrorActionPreference = "Stop"
$base = "http://127.0.0.1:8000"
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

function Post($path, $body) {
	Invoke-RestMethod -Uri "$base$path" -Method POST -WebSession $session -Body $body -TimeoutSec 60
}

$login = Post "/api/method/login" @{ usr = "Administrator"; pwd = "admin" }
Write-Output ("LOGIN " + ($login.message -join " "))
$csrf = ($session.Cookies.GetCookies([uri]$base) | Where-Object { $_.Name -eq "csrf_token" }).Value
$headers = @{ "X-Frappe-CSRF-Token" = $csrf; "Accept" = "application/json" }
Write-Output ("CSRF " + [bool]$csrf)

$cmd = Invoke-RestMethod -Uri "$base/api/method/erpatlas.command.board.get_command" -WebSession $session -TimeoutSec 60
$m = $cmd.message
Write-Output ("COMMAND cash=" + $m.shows_cash + " money=" + $m.shows_money + " pending=" + $m.approvals.pending + " available=" + $m.units.Available)

$funnel = Invoke-RestMethod -Uri "$base/api/method/erpatlas.analytics.board.get_sales_analytics" -WebSession $session -TimeoutSec 60
Write-Output ("FUNNEL " + (($funnel.message.funnel | ForEach-Object { "$($_.stage)=$($_.count)" }) -join " "))

$cmdPage = Invoke-WebRequest -Uri "$base/app/command" -WebSession $session -UseBasicParsing -TimeoutSec 60
Write-Output ("DESK_COMMAND status=" + $cmdPage.StatusCode + " len=" + $cmdPage.Content.Length)

$co = (Invoke-RestMethod -Uri "$base/api/resource/Company" -WebSession $session).data
Write-Output ("COMPANY " + (($co | ForEach-Object { $_.name }) -join ", "))

$projBody = @{
	doctype = "Project"
	project_name = "UAT Lake"
	company = "MOCK ATLAS3 LLP"
} | ConvertTo-Json
try {
	$proj = Invoke-RestMethod -Uri "$base/api/resource/Project" -Method POST -WebSession $session -Headers $headers -ContentType "application/json" -Body $projBody
	$pname = $proj.data.name
	Write-Output ("PROJECT created " + $pname)
} catch {
	$pname = "UAT Lake"
	Write-Output ("PROJECT exists_or_fail")
}

$parcel = @{
	doctype = "Atlas Parcel"
	project = $pname
	title = "Muhana Mandi khasra 41/2"
	khasra = "41/2"
	area = "3600 sq yd"
} | ConvertTo-Json
$pdoc = Invoke-RestMethod -Uri "$base/api/resource/Atlas Parcel" -Method POST -WebSession $session -Headers $headers -ContentType "application/json" -Body $parcel
Write-Output ("PARCEL " + $pdoc.data.name + " status=" + $pdoc.data.status)

$pack = Invoke-RestMethod -Uri "$base/api/method/erpatlas.land.doctype.atlas_parcel.atlas_parcel.start_title_pack" -Method POST -WebSession $session -Headers $headers -Body @{ parcel = $pdoc.data.name }
Write-Output ("PACK added=" + $pack.message.added.Count + " status=" + $pack.message.status)

$ch = @{
	doctype = "Atlas Channel Company"
	company_name = "UAT Pink City"
	city = "Jaipur"
	status = "Active"
} | ConvertTo-Json
try {
	$cc = Invoke-RestMethod -Uri "$base/api/resource/Atlas Channel Company" -Method POST -WebSession $session -Headers $headers -ContentType "application/json" -Body $ch
	Write-Output ("CHANNEL " + $cc.data.name)
} catch {
	Write-Output ("CHANNEL skip")
}

Write-Output "UAT_OK"
