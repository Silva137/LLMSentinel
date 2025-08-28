class OpenRouterHTTPError(Exception):
    code = "OPENROUTER_ERROR"
    status = 500
    message = "OpenRouter error"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.message)


class OpenRouterAPIKeyError(OpenRouterHTTPError):
    code, status, message = "INVALID_API_KEY", 401, "Invalid OpenRouter API key."


class OpenRouterNoCreditsError(OpenRouterHTTPError):
    code, status, message = "NO_CREDITS", 402, "Insufficient OpenRouter credits."


class OpenRouterRateLimitError(OpenRouterHTTPError):
    code, status, message = "RATE_LIMITED", 429, "You are being rate limited."


class OpenRouterProviderUnavailableError(OpenRouterHTTPError):
    code, status, message = "PROVIDER_UNAVAILABLE", 503, "No available model provider."


class OpenRouterTimeoutError(OpenRouterHTTPError):
    code, status, message = "TIMEOUT", 408, "Request to the model timed out."


class OpenRouterNonRetriableError(OpenRouterHTTPError):
    code, status, message = "OPENROUTER_4XX", 400, "Non-retriable client error."
