#!/usr/bin/env python3
"""
Orange TrustSkill v3.0 - Main Entry Script
Advanced Security Scanner for OpenClaw Skills
"""

import sys
import argparse
from pathlib import Path

# Add src and its parent to the Python path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(script_dir.parent))

try:
    from src.types import AnalysisMode
    from src.scanner import SkillScanner
    from src.formatters.text_formatter import TextFormatter, ProgressTracker
    from src.formatters.json_formatter import JsonFormatter
    from src.formatters.markdown_formatter import MarkdownFormatter
except ImportError:
    # Attempt direct import if src-prefixed import fails
    from types import AnalysisMode
    from scanner import SkillScanner
    from formatters.text_formatter import TextFormatter, ProgressTracker
    from formatters.json_formatter import JsonFormatter
    from formatters.markdown_formatter import MarkdownFormatter


def main():
    parser = argparse.ArgumentParser(
        description='🍊 Orange TrustSkill v3.0 - Security Scanner for OpenClaw Skills',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/skill
  %(prog)s /path/to/skill --mode deep
  %(prog)s /path/to/skill --format json
  %(prog)s /path/to/skill --export-for-llm
  %(prog)s /path/to/skill --config trustskill.yaml
        """
    )
    
    parser.add_argument(
        'skill_path',
        help='Path to skill directory to scan'
    )
    
    parser.add_argument(
        '-m', '--mode',
        choices=['fast', 'standard', 'deep'],
        default='standard',
        help='Analysis mode (default: standard)'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['text', 'json', 'markdown'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Disable progress bar'
    )
    
    parser.add_argument(
        '--export-for-llm',
        action='store_true',
        help='Export as Markdown for LLM review (equivalent to --format markdown)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode, display summary only'
    )
    
    parser.add_argument(
        '-c', '--config',
        help='Path to configuration file (YAML or JSON)'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 3.0.0'
    )
    
    args = parser.parse_args()
    
    # Load configuration if provided
    config = None
    if args.config:
        try:
            from src.config.loader import ConfigLoader
            config = ConfigLoader.load(args.config)
        except Exception as e:
            print(f"Warning: Failed to load config file: {e}", file=sys.stderr)
    
    # Handle export-for-llm flag
    if args.export_for_llm:
        args.format = 'markdown'
    
    # Map mode string to AnalysisMode enum
    mode_map = {
        'fast': AnalysisMode.FAST,
        'standard': AnalysisMode.STANDARD,
        'deep': AnalysisMode.DEEP
    }
    mode = mode_map[args.mode]
    
    # Initialize scanner
    scanner = SkillScanner(mode=mode, config=config)
    
    # Initialize progress tracker if requested
    progress = None
    if not args.no_progress and args.format == 'text' and not args.quiet:
        from src.rules import SCAN_EXTENSIONS, IGNORE_PATTERNS
        import re
        
        skill_path = Path(args.skill_path)
        total_files = 0
        if skill_path.exists():
            for item in skill_path.rglob('*'):
                if item.is_file():
                    path_str = str(item)
                    should_ignore = any(re.search(p, path_str) for p in IGNORE_PATTERNS)
                    if not should_ignore and item.suffix in SCAN_EXTENSIONS:
                        total_files += 1
        
        if total_files > 0:
            progress = ProgressTracker(total_files, use_color=not args.no_color)
    
    # Progress callback function
    def progress_callback(filename: str, current: int, total: int, findings: int):
        if progress:
            progress.update(filename, 0)
    
    # Execute scan
    result = scanner.scan(args.skill_path, progress_callback if progress else None)
    
    if progress:
        progress.finish()
    
    # Initialize appropriate formatter
    if args.format == 'json':
        formatter = JsonFormatter()
    elif args.format == 'markdown':
        formatter = MarkdownFormatter()
    else:
        formatter = TextFormatter(use_color=not args.no_color)
    
    # Format and print the results
    output = formatter.format(result)
    print(output)
    
    # Exit with appropriate code
    if result.risk_summary['HIGH'] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
