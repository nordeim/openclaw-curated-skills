"""
Regex-based Security Analyzer
"""

import re
from typing import List
from pathlib import Path

from .base import BaseAnalyzer
from ..types import SecurityIssue, Severity, AnalysisMode
from ..rules import (
    HIGH_RISK_PATTERNS,
    MEDIUM_RISK_PATTERNS,
    LOW_RISK_PATTERNS,
    SUSPICIOUS_PATTERNS,
    SAFE_SERVICES,
    DEFAULT_WHITELIST_PATTERNS,
    DOCUMENTATION_FILES,
    TESTING_UTILITY_FILES,
    LOCK_FILES,
    PLACEHOLDER_PATTERNS,
)


class RegexAnalyzer(BaseAnalyzer):
    """Regex Analyzer - Performs rapid pattern matching for known security risks."""

    def get_name(self) -> str:
        return "RegexAnalyzer"

    def _is_lock_file(self, file_path: Path) -> bool:
        """Check if file is a lock file that should have special handling."""
        return file_path.name in LOCK_FILES

    def _is_in_string_literal(self, content: str, position: int) -> bool:
        """Determine if a given position is inside a string literal."""
        lines_before = content[:position].split("\n")
        current_line = lines_before[-1] if lines_before else ""

        single_quotes = current_line.count("'") - current_line.count("'")
        double_quotes = current_line.count('"') - current_line.count('"')

        return single_quotes % 2 == 1 or double_quotes % 2 == 1

    def _is_pattern_definition(self, content: str, position: int) -> bool:
        """Check if the context suggests the match is part of a pattern definition."""
        context = content[max(0, position - 100) : position + 100]
        indicators = [
            "PATTERNS",
            "patterns",
            "regex",
            "PATTERN",
            "r'",
            'r"',
            "re.compile",
            ".compile(",
        ]
        return any(ind in context for ind in indicators)

    def _is_example_code(self, content: str, position: int) -> bool:
        """Identify if the match is likely inside example or documentation code."""
        start = max(0, position - 200)
        end = min(len(content), position + 200)
        context = content[start:end].lower()

        indicators = [
            "example",
            "danger:",
            "caution:",
            "warning:",
            "bad:",
            "wrong:",
            "unsafe:",
            "risk:",
            "pattern",
            "todo:",
            "note:",
            "security notice",
            # i18n patterns (Chinese, Japanese, Korean)
            "示例",
            "配置",
            "设置",
            "例",
            "例如",
            "注意",
            "警告",
            "请将",
            "填入",
            "你的",
            "密钥",
            "替换",
        ]

        if any(ind in context for ind in indicators):
            return True

        # Check for placeholder patterns
        for pattern in PLACEHOLDER_PATTERNS:
            if __import__("re").search(pattern, context, __import__("re").IGNORECASE):
                return True

        return False

    def _is_safe_service(self, url: str) -> bool:
        """Verify if a URL belongs to a whitelisted safe service."""
        return any(service in url for service in SAFE_SERVICES)

    def _is_whitelisted_pattern(
        self, content: str, position: int, file_path: Path
    ) -> bool:
        """Check if the match is whitelisted based on context and file type."""
        context_start = max(0, position - 150)
        context_end = min(len(content), position + 150)
        context = content[context_start:context_end]

        # Check default whitelist patterns
        for whitelist_pattern in DEFAULT_WHITELIST_PATTERNS:
            if __import__("re").search(
                whitelist_pattern,
                context,
                __import__("re").IGNORECASE | __import__("re").DOTALL,
            ):
                return True

        # Lock files: Skip most security checks for package-lock.json, yarn.lock, etc.
        # These files contain integrity hashes which are safe by design
        if self._is_lock_file(file_path):
            return True

        # Documentation files: Allow references to memory files
        if file_path.name in DOCUMENTATION_FILES:
            # Check if this is just a documentation reference (not code)
            if self._is_documentation_reference(content, position):
                return True

        # Testing utility files: Allow shell=True for subprocess
        # These are legitimate server orchestration tools
        if file_path.name in TESTING_UTILITY_FILES:
            return True

        return False

    def _is_documentation_reference(self, content: str, position: int) -> bool:
        """Determine if the match is a documentation reference vs actual code."""
        lines_before = content[:position].split("\n")

        # Check if we're inside a code block
        code_block_count = 0
        for line in lines_before:
            if line.strip().startswith("```"):
                code_block_count += 1

        # If even number of code blocks before position, we're outside code block
        # This means it's just documentation text
        if code_block_count % 2 == 0:
            return True

        # Check if the line contains just a reference (not an actual file operation)
        current_line = lines_before[-1] if lines_before else ""

        # It's a reference if it's in backticks or quotes (documentation style)
        if "`" in current_line or '"' in current_line or "'" in current_line:
            # But not if it's an open() call
            if "open(" not in current_line and "with open" not in current_line:
                return True

        # Check for placeholder patterns that indicate documentation examples
        for pattern in PLACEHOLDER_PATTERNS:
            if __import__("re").search(
                pattern, current_line, __import__("re").IGNORECASE
            ):
                return True

        # Check for i18n documentation patterns
        i18n_indicators = ["配置", "设置", "示例", "请将", "填入", "你的", "密钥"]
        if any(ind in current_line for ind in i18n_indicators):
            return True

        return False

    def _get_snippet(self, content: str, position: int, context: int = 50) -> str:
        """Extract a short code snippet around the identified position."""
        start = max(0, position - context)
        end = min(len(content), position + context)
        snippet = content[start:end].replace("\n", " ").strip()
        return snippet[:100] + "..." if len(snippet) > 100 else snippet

    def _check_patterns(
        self, content: str, patterns: dict, severity: Severity, file_path: Path
    ) -> List[SecurityIssue]:
        """Iterate through patterns and identify security issues."""
        issues = []
        relative_path = file_path.name

        for category, pattern_list in patterns.items():
            for pattern, description in pattern_list:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    pos = match.start()

                    # Skip lock files for most patterns
                    if self._is_lock_file(file_path):
                        continue

                    # Skip matches in string literals (likely false positives)
                    if self._is_in_string_literal(content, pos):
                        continue

                    # Skip matches in pattern definitions
                    if self._is_pattern_definition(content, pos):
                        continue

                    # Skip matches in example or documentation code
                    if self._is_example_code(content, pos):
                        continue

                    # Skip whitelisted patterns (v3.0+)
                    if self._is_whitelisted_pattern(content, pos, file_path):
                        continue

                    line_num = content[:pos].count("\n") + 1

                    issues.append(
                        SecurityIssue(
                            level=severity,
                            category=category,
                            description=description,
                            file=str(relative_path),
                            line=line_num,
                            snippet=self._get_snippet(content, pos),
                            confidence=0.8,
                        )
                    )

        return issues

    def analyze(self, file_path: Path, content: str) -> List[SecurityIssue]:
        """Analyze file content using regular expressions."""
        issues = []

        # High Risk Patterns
        issues.extend(
            self._check_patterns(content, HIGH_RISK_PATTERNS, Severity.HIGH, file_path)
        )

        # Medium Risk Patterns (Standard/Deep mode)
        if self.mode in [AnalysisMode.STANDARD, AnalysisMode.DEEP]:
            issues.extend(
                self._check_patterns(
                    content, MEDIUM_RISK_PATTERNS, Severity.MEDIUM, file_path
                )
            )

        # Low Risk Patterns (Deep mode only)
        if self.mode == AnalysisMode.DEEP:
            issues.extend(
                self._check_patterns(
                    content, LOW_RISK_PATTERNS, Severity.LOW, file_path
                )
            )

        # Suspicious URL Detection
        if self.mode in [AnalysisMode.STANDARD, AnalysisMode.DEEP]:
            for pattern, description in SUSPICIOUS_PATTERNS:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    url = match.group(0)
                    if self._is_safe_service(url):
                        continue

                    pos = match.start()
                    line_num = content[:pos].count("\n") + 1

                    issues.append(
                        SecurityIssue(
                            level=Severity.MEDIUM,
                            category="suspicious_url",
                            description=description,
                            file=str(file_path.name),
                            line=line_num,
                            snippet=self._get_snippet(content, pos),
                            confidence=0.7,
                        )
                    )

        return issues
