
class OpenRouterKeyError(Exception):
    """Invalid or missing OpenRouter API key (HTTP 401)."""
    pass


class OpenRouterNoCreditsError(Exception):
    """Insufficient OpenRouter credits (HTTP 402)."""
    pass


class OpenRouterNonRetriableError(Exception):
    """Any other non-retriable client error (4xx not suitable for retry)."""
    pass
