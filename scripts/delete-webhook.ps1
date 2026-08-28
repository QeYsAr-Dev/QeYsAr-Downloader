param(
    [Parameter(Mandatory = $true)]
    [string]$BotToken
)

$ErrorActionPreference = "Stop"

$ApiUrl = "https://api.telegram.org/bot$BotToken/deleteWebhook"

$Body = @{
    drop_pending_updates = $true
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri $ApiUrl `
    -Method Post `
    -ContentType "application/json" `
    -Body $Body

if (-not $response.ok) {
    throw "Telegram rejected webhook deletion."
}

Write-Host "Telegram webhook deleted successfully." -ForegroundColor Green
