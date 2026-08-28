class DownloaderError(Exception):
    """Base exception for QeYsAr Downloader."""


class InvalidURLError(DownloaderError):
    """Raised when a URL is invalid."""


class UnsupportedPlatformError(DownloaderError):
    """Raised when a platform is unsupported."""


class FileTooLargeError(DownloaderError):
    """Raised when a downloaded file exceeds the size limit."""


class DownloadInProgressError(DownloaderError):
    """Raised when the user already has an active download."""


class DailyLimitExceededError(DownloaderError):
    """Raised when the daily download limit is exceeded."""


class DownloadFailedError(DownloaderError):
    """Raised when a download fails."""


class TelegramUploadError(DownloaderError):
    """Raised when Telegram file upload fails."""
