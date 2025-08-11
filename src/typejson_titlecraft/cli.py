"""Command-line interface for TypeJSON TitleCraft."""

import argparse
import sys

from . import DEFAULT_MODEL, SUPPORTED_MODELS, Client, TitleCraftError


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="typejson-titlecraft",
        description="Generate human-readable titles from text using ChatGPT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  typejson-titlecraft "Your text here"
  typejson-titlecraft --model gpt-4o-mini "Your text here"
  echo "Your text" | typejson-titlecraft --stdin
  
Supported models: {', '.join(SUPPORTED_MODELS)}
Default model: {DEFAULT_MODEL}
        """.strip()
    )
    
    # Text input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "text",
        nargs="?",
        help="Text to generate title from"
    )
    input_group.add_argument(
        "--stdin",
        action="store_true",
        help="Read text from standard input"
    )
    
    # Model selection
    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default=DEFAULT_MODEL,
        help=f"OpenAI model to use (default: {DEFAULT_MODEL})"
    )
    
    # API key (optional, can use environment variable)
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (uses OPENAI_API_KEY env var if not provided)"
    )
    
    # Verbose output
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information"
    )
    
    return parser


def read_stdin() -> str:
    """Read text from standard input."""
    try:
        return sys.stdin.read().strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Get input text
    if args.stdin:
        text = read_stdin()
        if not text:
            print("Error: No input provided via stdin.", file=sys.stderr)
            sys.exit(1)
    else:
        text = args.text
        if not text:
            print("Error: No text provided.", file=sys.stderr)
            parser.print_help()
            sys.exit(1)
    
    try:
        # Initialize client
        if args.verbose:
            print(f"Using model: {args.model}", file=sys.stderr)
        
        client = Client(
            openai_api_key=args.api_key,
            model=args.model
        )
        
        # Generate title
        if args.verbose:
            print(f"Generating title for {len(text)} characters of text...", file=sys.stderr)
        
        title = client.generate_title(text)
        
        # Output result
        print(title)
        
    except TitleCraftError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()