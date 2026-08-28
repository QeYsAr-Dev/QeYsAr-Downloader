$ErrorActionPreference = "Stop"

$Port = if ($env:PORT) {
    [int]$env:PORT
}
else {
    8080
}

python -m uvicorn api:app `
    --host 0.0.0.0 `
    --port $Port `
    --proxy-headers `
    --forwarded-allow-ips "*"
