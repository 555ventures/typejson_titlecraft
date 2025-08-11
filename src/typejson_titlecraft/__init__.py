"""TypeJSON TitleCraft - Generate human-readable titles from text using ChatGPT."""

from .core import (
    DEFAULT_MODEL,
    GPT5_MODELS,
    SUPPORTED_MODELS,
    APIError,
    Client,
    SupportedModel,
    TitleCraftError,
    ValidationError,
)

__version__ = "0.1.0"

__all__ = [
    "Client",
    "SUPPORTED_MODELS", 
    "DEFAULT_MODEL",
    "GPT5_MODELS",
    "SupportedModel",
    "TitleCraftError",
    "APIError",
    "ValidationError",
    "__version__",
]