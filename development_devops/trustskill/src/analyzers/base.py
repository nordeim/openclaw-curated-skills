"""
Base Analyzer Module
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path

from ..types import SecurityIssue, AnalysisMode


class BaseAnalyzer(ABC):
    """Abstract base class for all security analyzers."""
    
    def __init__(self, mode: AnalysisMode = AnalysisMode.STANDARD, config=None):
        self.mode = mode
        self.config = config
    
    @abstractmethod
    def analyze(self, file_path: Path, content: str) -> List[SecurityIssue]:
        """
        Analyze the content of a file.
        
        Args:
            file_path: The path to the file being analyzed.
            content: The text content of the file.
            
        Returns:
            A list of detected SecurityIssue objects.
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the identifier name of the analyzer."""
        pass
