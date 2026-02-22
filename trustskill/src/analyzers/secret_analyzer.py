"""
Secret Analyzer for Orange TrustSkill v3.0

Detects hardcoded secrets, API keys, passwords, and tokens using:
1. High-entropy string detection
2. Pattern-based detection for known secret formats
3. Context analysis to reduce false positives
"""

import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path

from .base import BaseAnalyzer
from ..types import SecurityIssue, Severity, AnalysisMode
from ..utils.entropy import EntropyCalculator


# Secret detection patterns
SECRET_PATTERNS: Dict[str, List[Tuple[str, str, Severity]]] = {
    "aws": [
        (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID", Severity.HIGH),
        (r"ASIA[0-9A-Z]{16}", "AWS Temporary Access Key", Severity.HIGH),
        (
            r'aws[_-]?secret[_-]?access[_-]?key\s*=\s*["\']?[A-Za-z0-9/+=]{40}["\']?',
            "AWS Secret Access Key",
            Severity.HIGH,
        ),
    ],
    "github": [
        (r"gh[pousr]_[A-Za-z0-9_]{36,}", "GitHub Token", Severity.HIGH),
        (r'github[_-]?token\s*=\s*["\']?\w+["\']?', "GitHub Token", Severity.HIGH),
    ],
    "openai": [
        (r"sk-[a-zA-Z0-9]{48}", "OpenAI API Key", Severity.HIGH),
        (
            r'openai[_-]?api[_-]?key\s*=\s*["\']?\w+["\']?',
            "OpenAI API Key",
            Severity.HIGH,
        ),
    ],
    "google": [
        (r"AIza[0-9A-Za-z_-]{35}", "Google API Key", Severity.HIGH),
    ],
    "slack": [
        (r"xox[baprs]-[0-9a-zA-Z]{10,48}", "Slack Token", Severity.HIGH),
    ],
    "generic": [
        (
            r'api[_-]?key\s*=\s*["\']?[^"\'\s]{16,}["\']?',
            "Generic API Key",
            Severity.MEDIUM,
        ),
        (
            r'api[_-]?secret\s*=\s*["\']?[^"\'\s]{16,}["\']?',
            "API Secret",
            Severity.HIGH,
        ),
        (r'password\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded Password", Severity.HIGH),
        (
            r'secret[_-]?key\s*=\s*["\']?[^"\'\s]{16,}["\']?',
            "Secret Key",
            Severity.HIGH,
        ),
        (r'token\s*=\s*["\']?[^"\'\s]{16,}["\']?', "Token", Severity.MEDIUM),
        (r'private[_-]?key\s*=\s*["\']?[-]+BEGIN', "Private Key", Severity.HIGH),
        (
            r'auth[_-]?token\s*=\s*["\']?[^"\'\s]{16,}["\']?',
            "Auth Token",
            Severity.MEDIUM,
        ),
    ],
}

# Common false positive patterns to ignore
FALSE_POSITIVE_PATTERNS = [
    r"example",
    r"placeholder",
    r"your_\w+_here",
    r"xxxx+",
    r"0000+",
    r"12345+",
    r"test_\w+",
    r"dummy",
    r"sample",
    r"fake",
    r"REPLACE[_-]?ME",
    r"<[A-Z_]+>",
    r"\$\{[^}]+\}",
    r"{{[^}]+}}",
]

# NPM/PNPM/Yarn integrity hash patterns (SRI hashes - safe by design)
INTEGRITY_HASH_PATTERN = r"sha(256|384|512)-[A-Za-z0-9+/=]+"

# Lock files that contain integrity hashes
LOCK_FILES = [
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "composer.lock",
    "poetry.lock",
    "Cargo.lock",
    "Gemfile.lock",
]

# Placeholder patterns in documentation
PLACEHOLDER_PATTERNS = [
    r"your[_-]?\w+[_-]?here",
    r"sk-\.\.\.",
    r"sk_\.\.\.",
    r"your_api_key",
    r"your_secret",
    r"your_token",
    r"your_password",
    r"your[_-]?key",
]


class SecretAnalyzer(BaseAnalyzer):
    """
    Secret detection analyzer.

    Combines entropy analysis with pattern matching to detect
    hardcoded secrets in code.
    """

    def __init__(self, mode: AnalysisMode = AnalysisMode.STANDARD, config=None):
        super().__init__(mode)

        # Use config if provided, otherwise defaults
        if config and hasattr(config, "secret_detection"):
            self.config = config.secret_detection
        else:
            # Default configuration
            from ..config.loader import SecretDetectionConfig

            self.config = SecretDetectionConfig()

    def get_name(self) -> str:
        return "SecretAnalyzer"

    def analyze(self, file_path: Path, content: str) -> List[SecurityIssue]:
        """
        Analyze file for hardcoded secrets.

        Args:
            file_path: Path to file being analyzed
            content: File content

        Returns:
            List of security issues
        """
        issues = []

        if not self.config.enabled:
            return issues

        # Skip lock files entirely - they contain integrity hashes, not secrets
        if file_path.name in LOCK_FILES:
            return issues

        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            line_issues = self._analyze_line(line, line_num, file_path)
            issues.extend(line_issues)

        return issues

        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            line_issues = self._analyze_line(line, line_num, file_path)
            issues.extend(line_issues)

        return issues

    def _analyze_line(
        self, line: str, line_num: int, file_path: Path
    ) -> List[SecurityIssue]:
        """Analyze a single line for secrets."""
        issues = []

        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            return issues

        # Check for false positives
        if self._is_false_positive(stripped):
            return issues

        # Pattern-based detection
        pattern_issues = self._check_patterns(line, line_num, file_path)
        issues.extend(pattern_issues)

        # Entropy-based detection
        entropy_issues = self._check_entropy(line, line_num, file_path)
        issues.extend(entropy_issues)

        return issues

    def _check_patterns(
        self, line: str, line_num: int, file_path: Path
    ) -> List[SecurityIssue]:
        """Check line against known secret patterns."""
        issues = []

        for category, patterns in SECRET_PATTERNS.items():
            for pattern, description, severity in patterns:
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    # Verify the match isn't a false positive
                    matched_text = match.group(0)
                    if self._is_false_positive(matched_text):
                        continue

                    # Extract the actual secret value
                    secret_value = self._extract_secret_value(line, match)

                    # Calculate confidence based on context
                    confidence = self._calculate_confidence(line, secret_value)

                    issues.append(
                        SecurityIssue(
                            level=severity,
                            category="hardcoded_secret",
                            description=description,
                            file=str(file_path.name),
                            line=line_num,
                            snippet=line.strip()[:100],
                            confidence=confidence,
                        )
                    )

        return issues

    def _check_entropy(
        self, line: str, line_num: int, file_path: Path
    ) -> List[SecurityIssue]:
        """Check for high-entropy strings that may be secrets."""
        issues = []

        # Skip lines that contain integrity hashes (npm/yarn lock files)
        if '"integrity"' in line and "sha" in line:
            return issues

        # Skip lines with SRI hash patterns
        if re.search(INTEGRITY_HASH_PATTERN, line):
            return issues

        # Look for string literals that might contain secrets
        # Match quoted strings with high-entropy characters
        string_pattern = r'["\']([A-Za-z0-9_/@#$%^&*+=\-]{20,})["\']'

        for match in re.finditer(string_pattern, line):
            candidate = match.group(1)

            # Skip if too short
            if len(candidate) < self.config.min_length:
                continue

            # Skip if it's an integrity hash
            if re.match(r"^sha(256|384|512)-", candidate):
                continue

            # Check entropy
            entropy = EntropyCalculator.calculate(candidate)

            if entropy >= self.config.min_entropy:
                # Check for assignment context
                if self._is_likely_secret_assignment(line):
                    # Avoid duplicates from pattern matching
                    if not any(i.line == line_num for i in issues):
                        issues.append(
                            SecurityIssue(
                                level=Severity.HIGH,
                                category="hardcoded_secret",
                                description=f"High-entropy string (entropy: {entropy:.2f})",
                                file=str(file_path.name),
                                line=line_num,
                                snippet=line.strip()[:100],
                                confidence=min(0.95, entropy / 8.0),
                            )
                        )

        return issues

    def _is_false_positive(self, text: str) -> bool:
        """Check if text is a known false positive."""
        text_lower = text.lower()

        for pattern in FALSE_POSITIVE_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True

        # Check for placeholder patterns
        for pattern in PLACEHOLDER_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True

        # Check for integrity hash pattern (SRI hashes)
        if re.search(INTEGRITY_HASH_PATTERN, text):
            return True

        # Check for "integrity": context (npm lock files)
        if '"integrity"' in text_lower and "sha" in text_lower:
            return True

        return False

    def _is_likely_secret_assignment(self, line: str) -> bool:
        """Check if line looks like a secret assignment."""
        # Look for assignment patterns
        assignment_patterns = [
            r'[=:]\s*["\']',  # key = "value" or key: "value"
            r"export\s+\w+",  # export VARIABLE
            r'\w+:\s+["\']',  # YAML-style key: "value"
        ]

        for pattern in assignment_patterns:
            if re.search(pattern, line):
                return True

        return False

    def _extract_secret_value(self, line: str, match) -> str:
        """Extract the secret value from a match."""
        matched_text = match.group(0)

        # Try to extract just the value part after = or :
        value_match = re.search(r'[=:]\s*["\']?([^"\']+)["\']?', line)
        if value_match:
            return value_match.group(1)

        return matched_text

    def _calculate_confidence(self, line: str, secret_value: str) -> float:
        """Calculate confidence score for a secret detection."""
        confidence = 0.7  # Base confidence

        # Increase confidence for clear assignment patterns
        if re.search(r"(api[_-]?key|password|secret|token)\s*=", line, re.IGNORECASE):
            confidence += 0.15

        # Increase confidence for long, random-looking values
        if len(secret_value) >= 32:
            confidence += 0.1

        # Decrease confidence for test/placeholder values
        if self._is_false_positive(secret_value):
            confidence -= 0.3

        return min(1.0, max(0.1, confidence))
