<div align="center">QeYsAr Downloader

Professional Telegram Media Downloader Bot

A streamlined Telegram bot for downloading supported social media content — directly through a link.

<p>
  <a href="https://github.com/QeYsAr-Dev/QeYsAr-Downloader">
    <img src="https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github" alt="GitHub Repository">
  </a>
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.13">
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Bot">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
</p><p>
  <strong>Built with Python · Powered by Telegram · Developed by QeYsAr-Dev</strong>
</p>---

</div>Overview

QeYsAr Downloader is a Telegram-based media downloading project designed to provide a simple and organized way to process supported social media links.

Instead of navigating through complicated interfaces, users simply send a supported content link to the bot. The application processes the request, manages download restrictions, and delivers the resulting file through Telegram.

The project combines an asynchronous Telegram bot with a FastAPI backend, a flexible database layer, and a modular downloader architecture.

Supported Platforms

Platform| Availability
TikTok| Supported
Pinterest| Supported

«Platform availability can depend on the source platform, content accessibility, and downloader compatibility. TikTok and Pinterest are the currently verified platforms. Other platforms are not advertised as active features.»

Key Features

Link-Based Downloading

- Submit a supported URL directly to the bot.
- Automatic platform detection and download processing.
- File delivery through Telegram.

Download Management

- Per-user download limits.
- Controlled active-download concurrency.
- Download history.
- Download statistics.
- Temporary file management.
- Duplicate-request protection.

User Experience

- Telegram-based interface.
- "/start" welcome screen.
- "/help" usage instructions.
- "/history" recent download records.
- "/stats" personal usage statistics.
- "/settings" service limits and configuration.

Security and Request Management

- Request rate limiting.
- Spam protection.
- User security middleware.
- Optional channel membership verification.
- Protected webhook endpoint using a secret token.
- Administrative management components.

Usage

Using QeYsAr Downloader is straightforward:

1. Open the Telegram bot.
2. Start the bot with "/start".
3. Copy a supported TikTok or Pinterest link.
4. Send the link directly to the bot.
5. Wait for processing and receive the available file.

No platform-selection menu is required.

Download Limits

The default configuration includes the following restrictions:

Setting| Default
Daily downloads per user| 10
Maximum file size| 50 MB
Active downloads per user| 1
Download timeout| 300 seconds
Download retries| 2

These values can be adjusted through environment configuration.

Available Commands

Command| Description
"/start"| Start the bot and open the main interface
"/help"| Display usage instructions
"/history"| View recent download records
"/stats"| View personal download statistics
"/settings"| View current service limits

Technology Stack

<div align="center">Core Technologies

<img src="https://skillicons.dev/icons?i=python,fastapi,postgres,sqlite,docker,github,linux" alt="Technology Stack"></div>Technology| Purpose
Python 3.13| Main programming language
aiogram 3| Asynchronous Telegram Bot framework
FastAPI| Backend API and webhook server
yt-dlp| Media extraction and downloading engine
PostgreSQL| Production database backend
SQLite| Lightweight database fallback
aiosqlite| Asynchronous SQLite access
asyncpg| Asynchronous PostgreSQL driver
Pydantic Settings| Environment-based configuration
Uvicorn| ASGI application server
Docker| Containerized deployment
GitHub Actions| Automation and deployment workflow

Architecture

The project follows a modular structure to keep bot interactions, download processing, database operations, and infrastructure concerns separated.

QeYsAr-Downloader/
│
├── .github/
│   └── workflows/       # Automation workflows
│
├── bot/                 # Telegram bot initialization
├── database/            # Database layer and repositories
├── deploy/              # Deployment resources
├── downloaders/         # Platform downloader modules
├── downloads/           # Runtime download directory
├── handlers/            # Telegram command and message handlers
├── keyboards/           # Telegram interface keyboards
├── logs/                # Runtime logs
├── middlewares/         # Security and request middleware
├── scripts/             # Utility and maintenance scripts
├── services/            # Application services
├── tests/               # Automated tests
├── utils/               # Shared utilities
│
├── api.py               # FastAPI application and webhook
├── main.py              # Application entry point
├── config.py            # Application configuration
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
├── Dockerfile
├── docker-compose.yml
├── cloud-run.yaml
└── .env.example

Installation

1. Clone the Repository

git clone https://github.com/QeYsAr-Dev/QeYsAr-Downloader.git

cd QeYsAr-Downloader

2. Create a Virtual Environment

Windows:

py -3.13 -m venv .venv

.\.venv\Scripts\Activate.ps1

Linux / macOS:

python3.13 -m venv .venv

source .venv/bin/activate

3. Install Dependencies

python -m pip install --upgrade pip

pip install -r requirements.txt

4. Configure Environment Variables

Create your local environment file from the example:

Windows:

Copy-Item .env.example .env

Linux / macOS:

cp .env.example .env

Open ".env" and configure the required values.

5. Start the Application

python -m uvicorn api:app --host 0.0.0.0 --port 8080

The API will be available at:

http://localhost:8080

Environment Configuration

The project uses environment variables for runtime configuration.

Variable| Description
"BOT_TOKEN"| Telegram bot token
"ADMIN_ID"| Administrator Telegram ID
"DATABASE_URL"| Optional PostgreSQL connection URL
"DATABASE_PATH"| SQLite database location
"MAX_FILE_SIZE_MB"| Maximum allowed download size
"DAILY_DOWNLOAD_LIMIT"| Daily user download limit
"MAX_ACTIVE_DOWNLOADS_PER_USER"| Maximum active downloads per user
"DOWNLOAD_TIMEOUT"| Download timeout in seconds
"DOWNLOAD_RETRIES"| Number of download retries
"TEMP_DOWNLOAD_DIR"| Temporary download directory
"LOG_DIR"| Application log directory
"RATE_LIMIT_REQUESTS"| Maximum requests in the configured window
"RATE_LIMIT_WINDOW_SECONDS"| Rate-limit time window
"RATE_LIMIT_BLOCK_SECONDS"| Temporary rate-limit block duration
"SPAM_THRESHOLD"| Spam detection threshold
"SPAM_WINDOW_SECONDS"| Spam detection time window
"WEBHOOK_SECRET"| Secret used to protect the Telegram webhook
"ENVIRONMENT"| Runtime environment
"PORT"| API server port

Important: Keep ".env" private. Never commit your Telegram bot token, database credentials, webhook secret, or other private configuration values to GitHub.

Database Support

QeYsAr Downloader includes a database abstraction layer with two supported backends:

PostgreSQL

- Designed for production deployments.
- Uses asynchronous database access through "asyncpg".
- Selected when "DATABASE_URL" is configured.

SQLite

- Lightweight local database option.
- Uses "aiosqlite" for asynchronous operations.
- Used when no PostgreSQL connection URL is configured.

The database layer manages user records, download records, administrative records, settings, and application logs.

API Endpoints

The FastAPI backend exposes the following endpoints:

Method| Endpoint| Purpose
"GET"| "/"| Basic service status
"GET"| "/health"| Health check
"GET"| "/ready"| Readiness check
"POST"| "/telegram/webhook"| Receive Telegram webhook updates

The webhook endpoint validates the configured secret before processing incoming Telegram updates.

Docker Deployment

A Dockerfile and Docker Compose configuration are included.

Build and start the application:

docker compose up --build -d

View application logs:

docker compose logs -f downloader

Stop the application:

docker compose down

The included Docker configuration uses Python 3.13, installs the project dependencies, and prepares runtime directories.

Testing

The repository includes a dedicated "tests/" directory and development dependencies.

Install development dependencies:

pip install -r requirements-dev.txt

Run the test suite:

python -m pytest

Deployment Notes

The application is designed around a FastAPI webhook backend rather than requiring Telegram long polling.

The backend provides health and readiness endpoints, while Telegram updates are received through the protected "/telegram/webhook" route.

For production deployment:

- Configure all required environment variables.
- Use a persistent PostgreSQL database when appropriate.
- Configure the Telegram webhook with the correct public HTTPS endpoint and matching secret token.
- Ensure temporary files and logs are handled according to the hosting environment.
- Monitor application health and deployment logs.

A running API process alone does not guarantee public availability. The hosting provider must keep the service reachable and correctly configure the webhook.

Project Goals

QeYsAr Downloader is built around a few practical engineering goals:

- Simple user interaction.
- Modular and maintainable code.
- Asynchronous request handling.
- Controlled resource usage.
- Database flexibility.
- Secure webhook processing.
- Deployment-friendly architecture.

Author

<div align="center">QeYsAr-Dev

Independent Developer & Project Creator

<a href="https://github.com/QeYsAr-Dev">
  <img src="https://img.shields.io/badge/GitHub-QeYsAr--Dev-black?style=for-the-badge&logo=github" alt="GitHub Profile">
</a><a href="https://t.me/QeYsar_Dev">
  <img src="https://img.shields.io/badge/Telegram-Contact-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Contact">
</a></div>License

No license information is currently specified in this README. Check the repository for a license file before reusing, modifying, or distributing this project.

---

<div align="center">QeYsAr-Dev

From Concept to Creation.

</div>
