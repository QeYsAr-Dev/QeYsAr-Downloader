# Deployment

## Required secrets

Do not place production secrets inside `cloud-run.yaml`.

Configure these environment variables in the deployment platform:

- BOT_TOKEN
- ADMIN_ID
- WEBHOOK_SECRET

## Runtime configuration

The application also supports:

- DATABASE_PATH
- MAX_FILE_SIZE_MB
- DAILY_DOWNLOAD_LIMIT
- MAX_ACTIVE_DOWNLOADS_PER_USER
- DOWNLOAD_TIMEOUT
- DOWNLOAD_RETRIES
- TEMP_DOWNLOAD_DIR
- LOG_DIR
- RATE_LIMIT_REQUESTS
- RATE_LIMIT_WINDOW_SECONDS
- RATE_LIMIT_BLOCK_SECONDS
- SPAM_THRESHOLD
- SPAM_WINDOW_SECONDS
- ENVIRONMENT
- PORT

## Container

The container listens on port 8080 by default.

Health endpoints:

- `/`
- `/health`
- `/ready`

Telegram webhook:

- `/telegram/webhook`
