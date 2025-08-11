# TypeJSON TitleCraft

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://mypy.readthedocs.io/)

A powerful Python package that generates concise, human-readable titles from text using OpenAI's ChatGPT models. Perfect for creating displayable titles from raw content, documentation, or user-generated text.

## ✨ Features

- 🤖 **Multiple AI Models**: Support for GPT-5, GPT-4o, GPT-4, and GPT-3.5-turbo models
- 🌍 **Multi-language Support**: Preserves input language and handles proper casing
- ⚡ **Fast & Efficient**: Optimized prompts for quick title generation
- 🛡️ **Error Handling**: Comprehensive error handling with meaningful messages
- 📝 **Smart Processing**: Removes boilerplate, IDs, and filler words automatically
- 🎯 **Configurable**: Flexible model selection and API key management
- 📦 **Easy Integration**: Simple Python API and CLI tool

## 🚀 Quick Start

### Installation

#### From PyPI (Recommended)
```bash
pip install typejson-titlecraft
```

#### From Source
```bash
# Clone the repository
git clone https://github.com/555ventures/typejson_titlecraft.git
cd typejson_titlecraft

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### Basic Usage

#### Command Line Interface

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Generate title from text
typejson-titlecraft "This is a long article about machine learning and artificial intelligence in modern software development"

# Use a specific model
typejson-titlecraft --model gpt-4o-mini "Your text here"

# Read from stdin
echo "Your content here" | typejson-titlecraft --stdin

# Verbose output
typejson-titlecraft --verbose "Your text here"
```

#### Python API

```python
from typejson_titlecraft import Client

# Initialize client (uses OPENAI_API_KEY environment variable)
client = Client()

# Generate a title
title = client.generate_title(
    "This is a comprehensive guide about implementing REST APIs in Python using FastAPI framework"
)
print(title)  # Output: "Implementing REST APIs with FastAPI Guide"

# Use a specific model
client = Client(model="gpt-4o-mini")
title = client.generate_title("Your text here")

# Custom API key
client = Client(openai_api_key="your-api-key-here", model="gpt-4o")
```

## 📚 Documentation

### Supported Models

| Model | Type | Speed | Cost | Best For |
|-------|------|-------|------|----------|
| `gpt-5` | Latest | Medium | High | Highest quality titles |
| `gpt-5-mini` | Latest | Fast | Medium | Balanced performance |
| `gpt-5-nano` | Latest | Fastest | Low | Quick processing |
| `gpt-4o` | Standard | Medium | Medium | **Default - Best balance** |
| `gpt-4o-mini` | Standard | Fast | Low | Cost-effective |
| `gpt-4` | Standard | Slower | High | High quality |
| `gpt-3.5-turbo` | Legacy | Fast | Lowest | Budget option |

### API Reference

#### Client Class

```python
class Client:
    def __init__(
        self,
        openai_api_key: str | None = None,
        model: SupportedModel = "gpt-4o"
    ) -> None:
        """Initialize the TitleCraft client.
        
        Args:
            openai_api_key: OpenAI API key. If None, uses OPENAI_API_KEY env var.
            model: OpenAI model to use for title generation.
            
        Raises:
            ValidationError: If API key is missing or model is unsupported.
        """
    
    def generate_title(self, text: str) -> str:
        """Generate a concise, human-readable title from input text.
        
        Args:
            text: The input text to generate a title from (max 8000 characters).
            
        Returns:
            A concise title in the same language as the input text.
            
        Raises:
            ValidationError: If input text is empty or too long.
            APIError: If OpenAI API call fails.
        """
```

#### Exception Classes

```python
class TitleCraftError(Exception):
    """Base exception for TypeJSON TitleCraft errors."""

class APIError(TitleCraftError):
    """Raised when OpenAI API call fails."""

class ValidationError(TitleCraftError):
    """Raised when input validation fails."""
```

### CLI Reference

```bash
typejson-titlecraft [OPTIONS] [TEXT]

Options:
  TEXT                    Text to generate title from
  --stdin                Read text from standard input
  --model MODEL          OpenAI model to use (default: gpt-4o)
  --api-key KEY          OpenAI API key (uses OPENAI_API_KEY env var if not provided)
  --verbose              Show detailed information
  -h, --help             Show help message
```

## 🛠️ Development

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- OpenAI API key

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/555ventures/typejson_titlecraft.git
cd typejson_titlecraft

# Install with development dependencies
uv sync --group dev

# Or with pip
pip install -e ".[dev]"

# Set up pre-commit hooks (optional)
pre-commit install
```

### Running Tests

```bash
# Run tests with coverage
uv run pytest

# Run with coverage report
uv run pytest --cov=typejson_titlecraft --cov-report=html

# Run specific test file
uv run pytest tests/test_core.py -v
```

### Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Type checking
uv run mypy src/typejson_titlecraft

# Run all checks
uv run ruff check && uv run mypy src/typejson_titlecraft && uv run pytest
```

### Project Structure

```
typejson_titlecraft/
├── src/typejson_titlecraft/
│   ├── __init__.py          # Package exports and version
│   ├── core.py              # Main Client class and exceptions
│   └── cli.py               # Command-line interface
├── tests/
│   └── test_core.py         # Test suite
├── pyproject.toml           # Project configuration
├── README.md                # This file
└── uv.lock                  # Dependency lock file
```

## 📖 Examples

### Basic Title Generation

```python
from typejson_titlecraft import Client

client = Client()

# Blog post content
blog_content = """
In this comprehensive tutorial, we'll explore the fundamentals of building 
scalable web applications using modern Python frameworks. We'll cover everything 
from setting up your development environment to deploying your application in production.
"""

title = client.generate_title(blog_content)
print(title)  # "Building Scalable Web Applications with Python"
```

### Error Handling

```python
from typejson_titlecraft import Client, ValidationError, APIError

try:
    client = Client(model="gpt-4o")
    title = client.generate_title("")  # Empty text
except ValidationError as e:
    print(f"Validation error: {e}")
except APIError as e:
    print(f"API error: {e}")
```

### Batch Processing

```python
from typejson_titlecraft import Client

client = Client()
texts = [
    "First article about Python programming...",
    "Second article about web development...",
    "Third article about machine learning..."
]

titles = []
for text in texts:
    try:
        title = client.generate_title(text)
        titles.append(title)
    except Exception as e:
        print(f"Error processing text: {e}")
        titles.append("Untitled")

print(titles)
```

### Different Models Comparison

```python
from typejson_titlecraft import Client, SUPPORTED_MODELS

text = "A detailed analysis of performance optimization techniques in modern web applications"

for model in ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]:
    client = Client(model=model)
    title = client.generate_title(text)
    print(f"{model}: {title}")
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes* |

\* Required unless provided directly to the `Client` constructor.

### API Key Setup

1. **Get an OpenAI API Key**: Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Set Environment Variable**:
   ```bash
   # Unix/Linux/macOS
   export OPENAI_API_KEY="your-api-key-here"
   
   # Windows
   set OPENAI_API_KEY=your-api-key-here
   ```
3. **Or provide directly**:
   ```python
   client = Client(openai_api_key="your-api-key-here")
   ```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and ensure tests pass
4. **Run code quality checks**: `uv run ruff check && uv run mypy src/`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Add type hints for all functions and methods
- Write tests for new functionality
- Update documentation for API changes
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under a Proprietary License. See the license terms for details.

## 🙋 Support

- **Issues**: [GitHub Issues](https://github.com/555ventures/typejson_titlecraft/issues)
- **Email**: info@555.ventures
- **Documentation**: See this README and inline code documentation

## 🏗️ Built With

- [OpenAI Python SDK](https://github.com/openai/openai-python) - OpenAI API client
- [Hatchling](https://hatch.pypa.io/latest/) - Build system
- [Ruff](https://github.com/astral-sh/ruff) - Code formatting and linting
- [MyPy](https://mypy.readthedocs.io/) - Static type checking
- [pytest](https://pytest.org/) - Testing framework

## 📈 Version History

- **v0.1.0** - Initial release with core functionality

---

Made with ❤️ by [555 Ventures LLC](https://555.ventures)