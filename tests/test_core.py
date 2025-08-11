"""Tests for core functionality."""

import os
from unittest.mock import Mock, patch

import pytest

from typejson_titlecraft import (
    DEFAULT_MODEL,
    SUPPORTED_MODELS,
    APIError,
    Client,
    SupportedModel,
    ValidationError,
)


class TestClient:
    """Test Client class initialization and configuration."""
    
    def test_init_with_api_key(self) -> None:
        """Test Client initialization with explicit API key."""
        client = Client(openai_api_key="test-key")
        assert client.model == DEFAULT_MODEL
    
    def test_init_with_custom_model(self) -> None:
        """Test Client initialization with custom model."""
        client = Client(openai_api_key="test-key", model="gpt-4o-mini")
        assert client.model == "gpt-4o-mini"
    
    def test_init_with_env_var(self) -> None:
        """Test Client initialization using environment variable."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
            client = Client()
            assert client.model == DEFAULT_MODEL
    
    def test_init_no_api_key(self) -> None:
        """Test Client initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError, match="OpenAI API key required"):
                Client()
    
    def test_init_invalid_model(self) -> None:
        """Test Client initialization fails with invalid model."""
        with pytest.raises(ValidationError, match="Unsupported model"):
            Client(openai_api_key="test-key", model="invalid-model")  # type: ignore[arg-type]
    
    def test_supported_models_coverage(self) -> None:
        """Test all supported models can be initialized."""
        for model in SUPPORTED_MODELS:
            client = Client(openai_api_key="test-key", model=model)
            assert client.model == model


class TestGenerateTitle:
    """Test title generation functionality."""
    
    @pytest.fixture
    def client(self) -> Client:
        """Create test client."""
        return Client(openai_api_key="test-key")
    
    @pytest.fixture
    def mock_response(self) -> Mock:
        """Create mock OpenAI response."""
        mock_choice = Mock()
        mock_choice.message.content = "Test Title"
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        return mock_response
    
    def test_generate_title_success(self, client: Client, mock_response: Mock) -> None:
        """Test successful title generation."""
        with patch.object(client._client.chat.completions, 'create', return_value=mock_response):
            title = client.generate_title("This is some test text for title generation.")
            assert title == "Test Title"
    
    def test_generate_title_with_quotes(self, client: Client) -> None:
        """Test title generation strips quotes."""
        mock_choice = Mock()
        mock_choice.message.content = '"Quoted Title"'
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        with patch.object(client._client.chat.completions, 'create', return_value=mock_response):
            title = client.generate_title("Test text")
            assert title == "Quoted Title"
    
    def test_generate_title_empty_input(self, client: Client) -> None:
        """Test title generation with empty input."""
        with pytest.raises(ValidationError, match="Input text cannot be empty"):
            client.generate_title("")
        
        with pytest.raises(ValidationError, match="Input text cannot be empty"):
            client.generate_title("   ")
    
    def test_generate_title_too_long_input(self, client: Client) -> None:
        """Test title generation with too long input."""
        long_text = "x" * 8001
        with pytest.raises(ValidationError, match="Input text too long"):
            client.generate_title(long_text)
    
    def test_generate_title_empty_response(self, client: Client) -> None:
        """Test handling of empty API response."""
        mock_choice = Mock()
        mock_choice.message.content = None
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        with patch.object(client._client.chat.completions, 'create', return_value=mock_response):
            with pytest.raises(APIError, match="OpenAI API returned empty response"):
                client.generate_title("Test text")
    
    def test_generate_title_api_error_handling(self, client: Client) -> None:
        """Test API error handling."""
        # Test rate limit error
        rate_limit_error = Exception()
        rate_limit_error.status_code = 429  # type: ignore[attr-defined]
        
        with patch.object(client._client.chat.completions, 'create', side_effect=rate_limit_error):
            with pytest.raises(APIError, match="Rate limit exceeded"):
                client.generate_title("Test text")
        
        # Test authentication error
        auth_error = Exception()
        auth_error.status_code = 401  # type: ignore[attr-defined]
        
        with patch.object(client._client.chat.completions, 'create', side_effect=auth_error):
            with pytest.raises(APIError, match="Invalid API key"):
                client.generate_title("Test text")
        
        # Test server error
        server_error = Exception()
        server_error.status_code = 500  # type: ignore[attr-defined]
        
        with patch.object(client._client.chat.completions, 'create', side_effect=server_error):
            with pytest.raises(APIError, match="OpenAI API server error"):
                client.generate_title("Test text")
        
        # Test generic error
        generic_error = Exception("Network error")
        
        with patch.object(client._client.chat.completions, 'create', side_effect=generic_error):
            with pytest.raises(APIError, match="Failed to generate title"):
                client.generate_title("Test text")
    
    def test_generate_title_api_call_parameters(self, client: Client, mock_response: Mock) -> None:
        """Test API call uses correct parameters."""
        with patch.object(
            client._client.chat.completions, 'create', return_value=mock_response
        ) as mock_create:
            client.generate_title("Test text")
            
            # Verify API call parameters
            mock_create.assert_called_once()
            call_args = mock_create.call_args
            
            assert call_args[1]['model'] == DEFAULT_MODEL
            assert call_args[1]['max_tokens'] == 50
            assert call_args[1]['temperature'] == 0.3
            assert call_args[1]['timeout'] == 30.0
            
            # Check messages structure
            messages = call_args[1]['messages']
            assert len(messages) == 2
            assert messages[0]['role'] == 'system'
            assert messages[1]['role'] == 'user'
            assert messages[1]['content'] == 'Test text'


class TestModelSpecificPrompts:
    """Test model-specific prompt optimization."""
    
    def test_gpt35_turbo_prompt(self) -> None:
        """Test gpt-3.5-turbo uses simplified prompt."""
        client = Client(openai_api_key="test-key", model="gpt-3.5-turbo")
        prompt = client._get_system_prompt()
        
        # Should be the simplified prompt
        assert "Convert text to a concise title" in prompt
        assert len(prompt) < 200  # Shorter than the full prompt
    
    def test_gpt4_and_gpt5_prompt(self) -> None:
        """Test gpt-4 and gpt-5 models use full prompt."""
        models: list[SupportedModel] = [
            "gpt-5-nano", "gpt-5-mini", "gpt-4o", "gpt-4o-mini", "gpt-4"
        ]
        for model in models:
            client = Client(openai_api_key="test-key", model=model)
            prompt = client._get_system_prompt()
            
            # Should be the full prompt
            assert "You convert plain text into a concise" in prompt
            assert "aim for 4–9 words or ≤60 characters" in prompt


class TestInputValidation:
    """Test input validation and sanitization."""
    
    @pytest.fixture
    def client(self) -> Client:
        """Create test client."""
        return Client(openai_api_key="test-key")
    
    def test_text_stripping(self, client: Client) -> None:
        """Test input text is properly stripped."""
        mock_choice = Mock()
        mock_choice.message.content = "Test Title"
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        with patch.object(
            client._client.chat.completions, 'create', return_value=mock_response
        ) as mock_create:
            client.generate_title("  \n  Test text with whitespace  \n  ")
            
            # Verify stripped text was sent to API
            call_args = mock_create.call_args
            messages = call_args[1]['messages']
            assert messages[1]['content'] == "Test text with whitespace"
    
    def test_length_validation(self, client: Client) -> None:
        """Test text length validation."""
        # Test at boundary
        boundary_text = "x" * 8000
        # Should not raise an exception
        with patch.object(client._client.chat.completions, 'create'):
            try:
                client.generate_title(boundary_text)
            except ValidationError:
                pytest.fail("Should not raise ValidationError for 8000 characters")
        
        # Test over boundary
        over_boundary_text = "x" * 8001
        with pytest.raises(ValidationError, match="Input text too long"):
            client.generate_title(over_boundary_text)