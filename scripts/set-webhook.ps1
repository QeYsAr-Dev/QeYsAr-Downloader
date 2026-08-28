param(
    [Parameter(Mandatory = $true)]
    [string]$BotToken,

    [Parameter(Mandatory = $true)]
    [string]$WebhookUrl,

    [Parameter(Mandatory = $true)]
    [string]$WebhookSecret
)

$ErrorActionPreference = "Stop"

if (-not $WebhookUrl.StartsWith("https://")) {
    throw "WebhookUrl must use HTTPS."
}

$ApiUrl = "https://api.telegram.org/bot$BotToken/setWebhook"

$Body = @{
    url = "$($WebhookUrl.TrimEnd('/'))/telegram/webhook"
    secret_token = $WebhookSecret
    drop_pending_updates = $true
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri $ApiUrl `
    -Method Post `
    -ContentType "application/json" `
    -Body $Body

if (-not $response.ok) {
    throw "Telegram rejected the webhook configuration."
}

Write-Host "Telegram webhook configured successfully." -ForegroundColor Green
Write-Host "URL: $($WebhookUrl.TrimEnd('/'))/telegram/webhook"
