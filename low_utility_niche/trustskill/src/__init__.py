"""
Orange TrustSkill v3.0
Advanced Security Scanner for OpenClaw Skills
"""

__version__ = "3.0.0"
__author__ = "Orange"
__description__ = "Advanced security scanner with AST analysis, secret detection, and dependency scanning"

from .types import (
    Severity,
    AnalysisMode,
    SecurityIssue,
    ScanResult
)
from .scanner import SkillScanner
from .analyzers.regex_analyzer import RegexAnalyzer
from .analyzers.ast_analyzer import ASTAnalyzer
from .analyzers.secret_analyzer import SecretAnalyzer
from .analyzers.dependency_analyzer import DependencyAnalyzer
from .analyzers.taint_analyzer import TaintAnalyzer
from .formatters.text_formatter import TextFormatter, ProgressTracker
from .formatters.json_formatter import JsonFormatter
from .formatters.markdown_formatter import MarkdownFormatter

# v3.0: Config system
from .config import ConfigLoader, Config, ConfigValidator

__all__ = [
    '__version__',
    'Severity',
    'AnalysisMode',
    'SecurityIssue',
    'ScanResult',
    'SkillScanner',
    'RegexAnalyzer',
    'ASTAnalyzer',
    'SecretAnalyzer',
    'DependencyAnalyzer',
    'TaintAnalyzer',
    'TextFormatter',
    'ProgressTracker',
    'JsonFormatter',
    'MarkdownFormatter',
    'ConfigLoader',
    'Config',
    'ConfigValidator',
]
