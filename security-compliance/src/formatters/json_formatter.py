"""
JSON Output Formatter
"""

import json
from typing import Dict, Any

from .base import BaseFormatter
from ..types import ScanResult


class JsonFormatter(BaseFormatter):
    """Structured JSON output formatter."""
    
    def __init__(self, indent: int = 2):
        self.indent = indent
    
    def get_name(self) -> str:
        return "JsonFormatter"
    
    def format(self, result: ScanResult) -> str:
        """Format the scan result as a JSON string."""
        return json.dumps(result.to_dict(), indent=self.indent, ensure_ascii=False)
