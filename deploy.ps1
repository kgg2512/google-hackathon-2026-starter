[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[a-z][a-z0-9-]{4,28}[a-z0-9]$')][string]$ProjectId,
    [string]$Account,
    [ValidatePattern('^[a-z][a-z0-9-]{0,47}[a-z0-9]$')][string]$ServiceName = 'hackathon-app',
    [ValidatePattern('^[a-z]+-[a-z]+[0-9]$')][string]$Region = 'asia-northeast3',
    [switch]$PlanOnly
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$sourceDir = $PSScriptRoot
$plan = [ordered]@{project=$ProjectId; source=$sourceDir; region=$Region; service=$ServiceName; public=$true; reserved_env_overrides=$false}
if ($PlanOnly) {
    $plan | ConvertTo-Json
    exit 0
}
if ($Account -notmatch '^[^@\s]+@gcplab\.me$') { throw 'The event @gcplab.me account is required; personal projects are not used.' }
Get-Command gcloud -ErrorAction Stop | Out-Null
function Invoke-Gcloud {
    param([string[]]$Arguments)
    $result = & gcloud @Arguments
    if ($LASTEXITCODE -ne 0) { throw ('gcloud failed: ' + ($Arguments[0..([Math]::Min(1,$Arguments.Length-1))] -join ' ')) }
    return $result
}
$active = ((Invoke-Gcloud -Arguments @('auth','list','--filter=status:ACTIVE','--format=value(account)','--quiet')) -join '').Trim()
if ($active -cne $Account) { throw 'Active gcloud account does not match the supplied event account. No project was changed.' }
Invoke-Gcloud -Arguments @('projects','describe',$ProjectId,'--account',$Account,'--format=value(projectId)','--quiet') | Out-Null
Invoke-Gcloud -Arguments @('services','enable','run.googleapis.com','cloudbuild.googleapis.com','artifactregistry.googleapis.com','--project',$ProjectId,'--account',$Account,'--quiet') | Out-Null
Invoke-Gcloud -Arguments @('run','deploy',$ServiceName,'--source',$sourceDir,'--region',$Region,'--project',$ProjectId,'--account',$Account,'--allow-unauthenticated','--port','8080','--quiet') | Out-Null
$url = ((Invoke-Gcloud -Arguments @('run','services','describe',$ServiceName,'--region',$Region,'--project',$ProjectId,'--account',$Account,'--format=value(status.url)','--quiet')) -join '').Trim()
if ($url -notmatch '^https://[a-zA-Z0-9.-]+\.run\.app$') { throw 'Deployment returned no valid Cloud Run HTTPS URL.' }
$response = Invoke-RestMethod -Uri ($url + '/health') -TimeoutSec 30
if ($response.status -ne 'ok') { throw 'Deployed health check failed.' }
Write-Output ('DEPLOYMENT_VERIFIED ' + $url)
