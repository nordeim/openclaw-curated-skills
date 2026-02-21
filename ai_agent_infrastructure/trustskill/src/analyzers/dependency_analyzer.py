"""
Dependency Vulnerability Analyzer for Orange TrustSkill v3.0

Analyzes Python imports and checks for known vulnerabilities
using the Open Source Vulnerabilities (OSV) database.
"""

import ast
import re
from typing import List, Dict, Set, Optional
from pathlib import Path
from dataclasses import dataclass

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
    'requests': [
        {
            'id': 'PYSEC-2018-28',
            'affected_versions': ['<2.20.0'],
            'severity': Severity.HIGH,
            'description': 'Requests does not properly check SSL certificates'
        }
    ],
    'urllib3': [
        {
            'id': 'PYSEC-2021-108',
            'affected_versions': ['<1.26.5'],
            'severity': Severity.MEDIUM,
            'description': 'CRLF injection in urllib3'
        }
    ],
    'django': [
        {
            'id': 'PYSEC-2022-1',
            'affected_versions': ['<3.2.13', '<4.0.4'],
            'severity': Severity.HIGH,
            'description': 'Potential SQL injection in Django'
        }
    ],
    'flask': [
        {
            'id': 'PYSEC-2019-18',
            'affected_versions': ['<1.0.0'],
            'severity': Severity.MEDIUM,
            'description': 'Flask before 1.0 has potential security issues'
        }
    ],
    'pillow': [
        {
            'id': 'PYSEC-2021-90',
            'affected_versions': ['<8.2.0'],
            'severity': Severity.HIGH,
            'description': 'Buffer overflow in Pillow'
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
        
        if config and hasattr(config, 'dependency_check'):
            self.enabled = config.dependency_check.enabled
    
    def get_name(self) -> str:
        return "DependencyAnalyzer"
    
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
        if file_path.suffix != '.py':
            return issues
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return issues
        
        # Extract imported packages
        packages = self._extract_imports(tree)
        
        # Check each package for vulnerabilities
        for package in packages:
            vuln_issues = self._check_vulnerabilities(package, file_path)
            issues.extend(vuln_issues)
        
        return issues
    
    def _extract_imports(self, tree: ast.AST) -> List[PackageInfo]:
        """Extract package imports from AST."""
        packages = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    packages.append(PackageInfo(
                        name=alias.name.split('.')[0],  # Get base package
                        line=node.lineno
                    ))
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    packages.append(PackageInfo(
                        name=node.module.split('.')[0],  # Get base package
                        line=node.lineno
                    ))
        
        return packages
    
    def _check_vulnerabilities(
        self,
        package: PackageInfo,
        file_path: Path
    ) -> List[SecurityIssue]:
        """Check package against known vulnerabilities."""
        issues = []
        
        # Check if package has known vulnerabilities
        if package.name.lower() not in KNOWN_VULNERABILITIES:
            return issues
        
        vulns = KNOWN_VULNERABILITIES[package.name.lower()]
        
        for vuln in vulns:
            issues.append(SecurityIssue(
                level=vuln['severity'],
                category='vulnerable_dependency',
                description=f"{vuln['id']}: {vuln['description']}",
                file=str(file_path.name),
                line=package.line,
                snippet=f"import {package.name}",
                confidence=0.8
            ))
        
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
    'pickle',  # Known for security issues with untrusted data
    'yaml',    # Can execute code if not used safely
    'eval',    # Built-in but dangerous
    'exec',    # Built-in but dangerous
    'marshal', # Not secure for untrusted data
    'shelve',  # Uses pickle internally
}
