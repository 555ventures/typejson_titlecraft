"""Core functionality for TypeJSON TitleCraft."""

import os
from typing import Literal

from openai import OpenAI

# Supported OpenAI models for text generation
SupportedModel = Literal[
    "gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"
]

SUPPORTED_MODELS: list[SupportedModel] = [
    "gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"
]

# GPT-5 models that require Responses API
GPT5_MODELS: set[SupportedModel] = {"gpt-5", "gpt-5-mini", "gpt-5-nano"}

# Default model for cost/performance balance
DEFAULT_MODEL: SupportedModel = "gpt-4o"


class TitleCraftError(Exception):
    """Base exception for TypeJSON TitleCraft errors."""
    pass


class APIError(TitleCraftError):
    """Raised when OpenAI API call fails."""
    pass


class ValidationError(TitleCraftError):
    """Raised when input validation fails."""
    pass


class Client:
    """TypeJSON TitleCraft client for generating human-readable titles."""
    
    def __init__(
        self, 
        openai_api_key: str | None = None, 
        model: SupportedModel = DEFAULT_MODEL
    ) -> None:
        """Initialize the TitleCraft client.
        
        Args:
            openai_api_key: OpenAI API key. If None, uses OPENAI_API_KEY env var.
            model: OpenAI model to use for title generation. Defaults to gpt-4o.
            
        Raises:
            ValidationError: If API key is not provided and OPENAI_API_KEY env var is not set.
            ValidationError: If model is not supported.
        """
        # Validate model
        if model not in SUPPORTED_MODELS:
            raise ValidationError(
                f"Unsupported model '{model}'. Supported models: {', '.join(SUPPORTED_MODELS)}"
            )
        
        # Get API key from parameter or environment
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValidationError(
                "OpenAI API key required. Provide it via openai_api_key parameter "
                "or set OPENAI_API_KEY environment variable."
            )
        
        self.model = model
        self._client = OpenAI(api_key=api_key)
    
    def generate_title(self, text: str) -> str:
        """Generate a concise, human-readable title from input text.
        
        Args:
            text: The input text to generate a title from.
            
        Returns:
            A concise title in the same language as the input text.
            
        Raises:
            ValidationError: If input text is empty or too long.
            APIError: If OpenAI API call fails.
        """
        # Validate input
        if not text or not text.strip():
            raise ValidationError("Input text cannot be empty.")
        
        text = text.strip()
        if len(text) > 8000:  # Reasonable limit for context window
            raise ValidationError("Input text too long (max 8000 characters).")
        
        try:
            if self.model in GPT5_MODELS:
                return self._generate_title_responses_api(text)
            else:
                return self._generate_title_chat_api(text)
            
        except Exception as e:
            if hasattr(e, 'status_code'):
                if e.status_code == 429:
                    raise APIError("Rate limit exceeded. Please try again later.") from e
                elif e.status_code == 401:
                    raise APIError("Invalid API key.") from e
                elif e.status_code >= 500:
                    raise APIError("OpenAI API server error. Please try again later.") from e
            
            raise APIError(f"Failed to generate title: {str(e)}") from e
    
    def _get_system_prompt(self) -> str:
        """Get model-optimized system prompt for title generation."""
        base_prompt = (
            "You convert plain text into a concise, descriptive, human-readable title for "
            "frontend display.\n"
            "Rules:\n"
            "• Output in the same language as the input.\n"
            "• Be concise: aim for 4–9 words or ≤60 characters. Prefer clarity over creativity.\n"
            "• Preserve key proper nouns and terms; do not invent information.\n"
            "• Remove filler words, boilerplate, IDs, and dates unless essential.\n"
            "• Casing: Title Case for Latin scripts; keep natural casing for non-Latin scripts "
            "(e.g., Japanese).\n"
            "• Punctuation: no quotes/brackets/emojis/hashtags; no trailing period. Use colon "
            "or dash only if it clearly improves clarity.\n"
            "• If the input is already a good title, normalize casing/spacing and return it.\n"
            "• If input is empty or meaningless, return: Untitled\n"
            "Return only the title text—no explanations."
        )
        
        # Model-specific optimizations
        if self.model in ["gpt-3.5-turbo"]:
            # Simpler, more direct instruction for older models
            return (
                "Convert text to a concise title (4-9 words, ≤60 chars). "
                "Same language as input. Title Case for Latin scripts. "
                "No quotes/brackets/emojis. Return only the title."
            )
        
        return base_prompt
    
    def _generate_title_responses_api(self, text: str) -> str:
        """Generate title using GPT-5 models with Responses API."""
        # Build optimized prompt for title generation
        prompt = f"{self._get_system_prompt()}\n\nText to convert to title: {text}"
        
        response = self._client.responses.create(
            model=self.model,
            input=prompt,
            reasoning={"effort": "minimal"},  # Fast generation for title tasks
            text={"verbosity": "low"},  # Concise output for titles
            timeout=30.0
        )
        
        # Extract title from response
        title = response.output_text if response.output_text else None
        
        if not title:
            raise APIError(f"Model '{self.model}' returned empty response.")
        
        return str(title.strip().strip('"').strip("'"))
    
    def _generate_title_chat_api(self, text: str) -> str:
        """Generate title using non-GPT-5 models with Chat Completions API."""
        system_prompt = self._get_system_prompt()
        
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            max_completion_tokens=50,
            temperature=0.3,
            timeout=30.0
        )
        
        title = response.choices[0].message.content
        if not title:
            raise APIError("OpenAI API returned empty response.")
        
        return str(title.strip().strip('"').strip("'"))