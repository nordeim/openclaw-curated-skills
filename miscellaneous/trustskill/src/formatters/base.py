"""
Base Output Formatter Class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from ..types import ScanResult


class BaseFormatter(ABC):
    """Abstract base class for all output formatters."""
    
    @abstractmethod
    def format(self, result: ScanResult) -> str:
        """
        Format the scan results.
        
        Args:
            result: The scan results object.
            
        Returns:
            The formatted string representation of the scan results.
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the formatter."""
        pass
