"""
Dependency Vulnerability Analyzer for Orange TrustSkill v3.0

Analyzes Python imports and checks for known vulnerabilities
using the Open Source Vulnerabilities (OSV) database.
"""

import ast
import re
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from packaging.specifiers import SpecifierSet
from packaging.version import Version, InvalidVersion

from .base import BaseAnalyzer
from ..types import SecurityIssue, Severity, AnalysisMode


@dataclass
class PackageInfo:
    """Package information."""

    name: str
    version: Optional[str] = None
    line: int = 1


# Known vulnerable packages (simplified for offline operation)
# In production, this would query the OSV API
KNOWN_VULNERABILITIES: Dict[str, List[Dict]] = {
    "requests": [
        {
            "id": "PYSEC-2018-28",
            "affected_versions": ["<2.20.0"],
            "severity": Severity.HIGH,
            "description": "Requests does not properly check SSL certificates",
        }
    ],
    "urllib3": [
        {
            "id": "PYSEC-2021-108",
            "affected_versions": ["<1.26.5"],
            "severity": Severity.MEDIUM,
            "description": "CRLF injection in urllib3",
        }
    ],
    "django": [
        {
            "id": "PYSEC-2022-1",
            "affected_versions": ["<3.2.13", "<4.0.4"],
            "severity": Severity.HIGH,
            "description": "Potential SQL injection in Django",
        }
    ],
    "flask": [
        {
            "id": "PYSEC-2019-18",
            "affected_versions": ["<1.0.0"],
            "severity": Severity.MEDIUM,
            "description": "Flask before 1.0 has potential security issues",
        }
    ],
    "pillow": [
        {
            "id": "PYSEC-2021-90",
            "affected_versions": ["<8.2.0"],
            "severity": Severity.HIGH,
            "description": "Buffer overflow in Pillow",
        }
    ],
}


class DependencyAnalyzer(BaseAnalyzer):
    """
    Dependency vulnerability analyzer.

    Scans Python imports and checks against known vulnerability databases.
    """

    def __init__(self, mode: AnalysisMode = AnalysisMode.STANDARD, config=None):
        super().__init__(mode)
        self.config = config
        self.enabled = True
        self._requirements_cache: Dict[str, Dict[str, SpecifierSet]] = {}

        if config and hasattr(config, "dependency_check"):
            self.enabled = config.dependency_check.enabled

    def get_name(self) -> str:
        return "DependencyAnalyzer"

    def _find_requirements_file(self, file_path: Path) -> Optional[Path]:
        """Find requirements.txt in the skill directory."""
        current = file_path.parent
        for _ in range(5):
            req_file = current / "requirements.txt"
            if req_file.exists():
                return req_file
            if current.parent == current:
                break
            current = current.parent
        return None

    def _parse_requirements(self, req_path: Path) -> Dict[str, SpecifierSet]:
        """Parse requirements.txt and return package -> version specifier mapping."""
        specs = {}
        try:
            content = req_path.read_text()
            for line in content.strip().split("\n"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                match = re.match(
                    r"^([a-zA-Z0-9_-]+)\s*([<>=!~]+\s*[\d\.\*]+.*)?$", line
                )
                if match:
                    pkg_name = match.group(1).lower()
                    version_spec = match.group(2)
                    if version_spec:
                        try:
                            specs[pkg_name] = SpecifierSet(version_spec.strip())
                        except Exception:
                            pass
        except Exception:
            pass
        return specs

    def _is_version_safe(self, vuln: Dict, specifiers: Optional[SpecifierSet]) -> bool:
        """Check if the version specifier satisfies safe version requirement."""
        if not specifiers:
            return False

        for affected in vuln.get("affected_versions", []):
            match = re.match(r"^([<>=!]+)\s*(\d+\.\d+(?:\.\d+)?)", affected)
            if match:
                op, vuln_version = match.groups()
                try:
                    safe_version = Version(vuln_version)
                    if op == "<":
                        for spec in specifiers:
                            if hasattr(spec, "version"):
                                try:
                                    spec_ver = Version(str(spec.version))
                                    if spec_ver >= safe_version:
                                        return True
                                except InvalidVersion:
                                    pass
                except InvalidVersion:
                    pass
        return False

    def analyze(self, file_path: Path, content: str) -> List[SecurityIssue]:
        """
        Analyze Python file for vulnerable dependencies.

        Args:
            file_path: Path to file being analyzed
            content: File content

        Returns:
            List of security issues
        """
        issues = []

        if not self.enabled:
            return issues

        # Only analyze Python files
        if file_path.suffix != ".py":
            return issues

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return issues

        # Extract imported packages
        packages = self._extract_imports(tree)

        # Find and parse requirements.txt
        req_path = self._find_requirements_file(file_path)
        req_specs = {}
        if req_path:
            cache_key = str(req_path)
            if cache_key not in self._requirements_cache:
                self._requirements_cache[cache_key] = self._parse_requirements(req_path)
            req_specs = self._requirements_cache[cache_key]

        # Check each package for vulnerabilities
        for package in packages:
            pkg_spec = req_specs.get(package.name.lower())
            vuln_issues = self._check_vulnerabilities(package, file_path, pkg_spec)
            issues.extend(vuln_issues)

        return issues

    def _extract_imports(self, tree: ast.AST) -> List[PackageInfo]:
        """Extract package imports from AST."""
        packages = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    packages.append(
                        PackageInfo(
                            name=alias.name.split(".")[0],  # Get base package
                            line=node.lineno,
                        )
                    )

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    packages.append(
                        PackageInfo(
                            name=node.module.split(".")[0],  # Get base package
                            line=node.lineno,
                        )
                    )

        return packages

    def _check_vulnerabilities(
        self,
        package: PackageInfo,
        file_path: Path,
        specifiers: Optional[SpecifierSet] = None,
    ) -> List[SecurityIssue]:
        """Check package against known vulnerabilities."""
        issues = []

        # Check if package has known vulnerabilities
        if package.name.lower() not in KNOWN_VULNERABILITIES:
            return issues

        vulns = KNOWN_VULNERABILITIES[package.name.lower()]

        for vuln in vulns:
            # Check if version constraint satisfies safe version
            if self._is_version_safe(vuln, specifiers):
                continue

            issues.append(
                SecurityIssue(
                    level=vuln["severity"],
                    category="vulnerable_dependency",
                    description=f"{vuln['id']}: {vuln['description']}",
                    file=str(file_path.name),
                    line=package.line,
                    snippet=f"import {package.name}",
                    confidence=0.8,
                )
            )

        return issues

    def _get_package_version(self, package_name: str) -> Optional[str]:
        """
        Try to get installed version of a package.

        In production, this would use importlib.metadata or pkg_resources.
        """
        try:
            import importlib.metadata

            return importlib.metadata.version(package_name)
        except Exception:
            return None


# Legacy package names that are known to be risky
RISKY_PACKAGES: Set[str] = {
    "pickle",  # Known for security issues with untrusted data
    "yaml",  # Can execute code if not used safely
    "eval",  # Built-in but dangerous
    "exec",  # Built-in but dangerous
    "marshal",  # Not secure for untrusted data
    "shelve",  # Uses pickle internally
}
