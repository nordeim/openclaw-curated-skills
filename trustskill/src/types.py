"""
Core Data Types for Orange TrustSkill
Defines Severity, AnalysisMode, SecurityIssue, and ScanResult.
"""

from enum import Enum, auto
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime


class Severity(Enum):
    """Security Risk Severity Levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM" 
    LOW = "LOW"
    INFO = "INFO"


class AnalysisMode(Enum):
    """Scanner Analysis Intensity Modes."""
    FAST = "fast"           # Regex only
    STANDARD = "standard"   # Regex + AST
    DEEP = "deep"           # Regex + AST + Enhanced inspection


@dataclass
class SecurityIssue:
    """Represents a single detected security vulnerability."""
    level: Severity
    category: str
    description: str
    file: str
    line: int
    snippet: str
    confidence: float = 1.0  # Detection confidence (0.0 to 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the issue to a serializable dictionary."""
        return {
            "level": self.level.value,
            "category": self.category,
            "description": self.description,
            "file": self.file,
            "line": self.line,
            "snippet": self.snippet,
            "confidence": self.confidence
        }


@dataclass
class ScanResult:
    """Container for the complete scan operation results."""
    skill_path: str
    files_scanned: int
    findings: List[SecurityIssue]
    scan_time: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def risk_summary(self) -> Dict[str, int]:
        """Generate a summary count of issues by severity."""
        summary = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for finding in self.findings:
            summary[finding.level.value] += 1
        return summary
    
    @property
    def security_assessment(self) -> str:
        """Provide a human-readable assessment of the overall risk."""
        summary = self.risk_summary
        if summary["HIGH"] > 0:
            return "🔴 CRITICAL: High-risk issues detected. Manual review required."
        elif summary["MEDIUM"] > 5:
            return "🟡 WARNING: Multiple medium-risk issues found. Review recommended."
        elif summary["MEDIUM"] > 0:
            return "🟢 CAUTION: Some medium-risk issues found. Review suggested."
        else:
            return "✅ SAFE: No significant security issues found."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the full scan result to a serializable dictionary."""
        return {
            "skill_path": self.skill_path,
            "files_scanned": self.files_scanned,
            "findings": [f.to_dict() for f in self.findings],
            "risk_summary": self.risk_summary,
            "security_assessment": self.security_assessment,
            "scan_time": self.scan_time,
            "timestamp": self.timestamp
        }
