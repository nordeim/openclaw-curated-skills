"""
Main Scanner Engine - Orchestrates all analyzers.
"""

import time
from pathlib import Path
from typing import List, Optional, Type

from .types import ScanResult, SecurityIssue, AnalysisMode
from .analyzers.base import BaseAnalyzer
from .analyzers.regex_analyzer import RegexAnalyzer
from .analyzers.ast_analyzer import ASTAnalyzer
from .analyzers.secret_analyzer import SecretAnalyzer
from .analyzers.dependency_analyzer import DependencyAnalyzer
from .analyzers.taint_analyzer import TaintAnalyzer
from .rules import SCAN_EXTENSIONS, IGNORE_PATTERNS, LOCK_FILES
import re


class SkillScanner:
    """Skill Security Scanner - Main Entry Point"""

    def __init__(self, mode: AnalysisMode = AnalysisMode.STANDARD, config=None):
        """
        Initialize the scanner.

        Args:
            mode: Analysis mode (FAST, STANDARD, DEEP)
            config: Optional configuration object (v3.0+)
        """
        self.mode = mode
        self.config = config
        self.analyzers = self._init_analyzers()

    def _init_analyzers(self) -> List[BaseAnalyzer]:
        """Initialize the list of active analyzers."""
        analyzers = []

        # Regex analysis is included in all modes
        analyzers.append(RegexAnalyzer(self.mode, self.config))

        # AST analysis is included in STANDARD and DEEP modes
        if self.mode in [AnalysisMode.STANDARD, AnalysisMode.DEEP]:
            analyzers.append(ASTAnalyzer(self.mode, self.config))

        # v3.0: Add secret detection analyzer
        try:
            analyzers.append(SecretAnalyzer(self.mode, self.config))
        except Exception:
            pass  # Secret analyzer is optional

        # v3.0: Add dependency vulnerability analyzer
        try:
            analyzers.append(DependencyAnalyzer(self.mode, self.config))
        except Exception:
            pass  # Dependency analyzer is optional

        # v3.0: Add taint analysis for DEEP mode
        if self.mode == AnalysisMode.DEEP:
            try:
                analyzers.append(TaintAnalyzer(self.mode, self.config))
            except Exception:
                pass  # Taint analyzer is optional

        return analyzers

    def _should_ignore(self, path: Path) -> bool:
        """Check if the given path should be ignored based on ignore patterns."""
        path_str = str(path)
        for pattern in IGNORE_PATTERNS:
            if re.search(pattern, path_str):
                return True
        return False

    def _is_lock_file(self, path: Path) -> bool:
        """Check if file is a lock file that should have minimal scanning."""
        return path.name in LOCK_FILES

    def _get_files_to_scan(self, skill_path: Path) -> List[Path]:
        """Retrieve the list of files to be scanned."""
        files = []

        # Recursively traverse the directory
        for item in skill_path.rglob("*"):
            if item.is_file():
                # Check if file is in ignore list
                if self._should_ignore(item):
                    continue

                # Check file extension
                if item.suffix in SCAN_EXTENSIONS:
                    files.append(item)

        # Ensure SKILL.md is included
        skill_md = skill_path / "SKILL.md"
        if skill_md.exists() and skill_md not in files:
            files.append(skill_md)

        return sorted(set(files))  # Deduplicate and sort

    def scan(
        self, skill_path: str, progress_callback: Optional[callable] = None
    ) -> ScanResult:
        """
        Scan a specific skill directory.

        Args:
            skill_path: Path to the skill directory
            progress_callback: Callback function for progress updates (name, current, total, findings)

        Returns:
            ScanResult object containing all findings
        """
        start_time = time.time()
        skill_path = Path(skill_path)

        if not skill_path.exists():
            return ScanResult(
                skill_path=str(skill_path),
                files_scanned=0,
                findings=[],
                scan_time=0,
                timestamp="",
            )

        # Retrieve list of files to scan
        files = self._get_files_to_scan(skill_path)
        total_files = len(files)

        all_findings: List[SecurityIssue] = []
        files_scanned = 0

        # Scan each file
        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            file_findings = []

            # Execute each active analyzer
            for analyzer in self.analyzers:
                try:
                    findings = analyzer.analyze(file_path, content)
                    file_findings.extend(findings)
                except Exception:
                    # Continue if an analyzer fails
                    continue

            all_findings.extend(file_findings)
            files_scanned += 1

            # Update progress
            if progress_callback:
                progress_callback(
                    file_path.name, files_scanned, total_files, len(all_findings)
                )

        scan_time = time.time() - start_time

        return ScanResult(
            skill_path=str(skill_path),
            files_scanned=files_scanned,
            findings=all_findings,
            scan_time=scan_time,
        )
