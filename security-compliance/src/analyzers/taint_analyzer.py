"""
Taint Analyzer for Orange TrustSkill v3.0

Basic taint analysis to track data flow from sources (user input)
to sinks (dangerous operations).
"""

import ast
from typing import List, Set, Dict, Optional
from pathlib import Path

from .base import BaseAnalyzer
from ..types import SecurityIssue, Severity, AnalysisMode


# Sources of tainted data (user input)
TAINT_SOURCES = {
    'input': 'user_input',
    'sys.argv': 'command_line_args',
    'os.environ.get': 'environment_variable',
    'os.getenv': 'environment_variable',
    'request.args.get': 'http_parameter',
    'request.form.get': 'form_data',
    'request.json': 'json_data',
    'open': 'file_content',
}

# Sinks where tainted data is dangerous
TAINT_SINKS = {
    'eval': 'code_execution',
    'exec': 'code_execution',
    'os.system': 'command_execution',
    'os.popen': 'command_execution',
    'subprocess.call': 'command_execution',
    'subprocess.run': 'command_execution',
    'subprocess.Popen': 'command_execution',
    'compile': 'code_execution',
    '__import__': 'dynamic_import',
}


class TaintAnalyzer(BaseAnalyzer):
    """
    Basic taint analyzer.
    
    Tracks simple data flow from sources to sinks.
    Note: This is a simplified implementation. Full taint analysis
    requires more sophisticated control flow analysis.
    """
    
    def __init__(self, mode: AnalysisMode = AnalysisMode.STANDARD, config=None):
        super().__init__(mode)
        self.config = config
    
    def get_name(self) -> str:
        return "TaintAnalyzer"
    
    def analyze(self, file_path: Path, content: str) -> List[SecurityIssue]:
        """
        Analyze Python file for taint flow issues.
        
        Args:
            file_path: Path to file being analyzed
            content: File content
            
        Returns:
            List of security issues
        """
        issues = []
        
        # Only analyze Python files in standard or deep mode
        if file_path.suffix != '.py':
            return issues
        
        if self.mode == AnalysisMode.FAST:
            return issues
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return issues
        
        # Track tainted variables
        tainted_vars: Dict[str, int] = {}  # var_name -> line_number
        
        # Walk the AST
        for node in ast.walk(tree):
            # Track assignments from taint sources
            if isinstance(node, ast.Assign):
                self._track_assignment(node, tainted_vars)
            
            # Check for tainted data reaching sinks
            elif isinstance(node, ast.Call):
                sink_issues = self._check_sink(node, tainted_vars, file_path, content)
                issues.extend(sink_issues)
        
        return issues
    
    def _track_assignment(
        self,
        node: ast.Assign,
        tainted_vars: Dict[str, int]
    ) -> None:
        """Track variable assignments that may be tainted."""
        # Check if RHS is a taint source
        is_tainted = self._is_taint_source(node.value)
        
        if is_tainted:
            # Mark all assigned variables as tainted
            for target in node.targets:
                if isinstance(target, ast.Name):
                    tainted_vars[target.id] = node.lineno
    
    def _check_sink(
        self,
        node: ast.Call,
        tainted_vars: Dict[str, int],
        file_path: Path,
        content: str
    ) -> List[SecurityIssue]:
        """Check if a function call is a sink with tainted data."""
        issues = []
        
        # Get function name
        func_name = self._get_func_name(node.func)
        if not func_name:
            return issues
        
        # Check if it's a sink
        sink_category = self._get_sink_category(func_name)
        if not sink_category:
            return issues
        
        # Check if any argument is tainted
        for arg in node.args:
            if self._is_tainted(arg, tainted_vars):
                # Get the line content
                lines = content.split('\n')
                line_content = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
                
                issues.append(SecurityIssue(
                    level=Severity.HIGH,
                    category=f'tainted_{sink_category}',
                    description=f'{func_name}() called with tainted user input',
                    file=str(file_path.name),
                    line=node.lineno,
                    snippet=line_content.strip()[:100],
                    confidence=0.85
                ))
                break
        
        return issues
    
    def _is_taint_source(self, node: ast.AST) -> bool:
        """Check if a node is a taint source."""
        if isinstance(node, ast.Call):
            func_name = self._get_func_name(node.func)
            if func_name:
                # Check if it's a known source
                for source_pattern in TAINT_SOURCES:
                    if source_pattern in func_name:
                        return True
        
        elif isinstance(node, ast.Name):
            if node.id in ['input']:
                return True
        
        elif isinstance(node, ast.Attribute):
            # Check for sys.argv
            if isinstance(node.value, ast.Name) and node.value.id == 'sys':
                if node.attr == 'argv':
                    return True
        
        return False
    
    def _is_tainted(
        self,
        node: ast.AST,
        tainted_vars: Dict[str, int]
    ) -> bool:
        """Check if a node represents tainted data."""
        # Direct variable reference
        if isinstance(node, ast.Name):
            return node.id in tainted_vars
        
        # Direct taint source
        if self._is_taint_source(node):
            return True
        
        # Binary operations with tainted data
        if isinstance(node, ast.BinOp):
            return self._is_tainted(node.left, tainted_vars) or \
                   self._is_tainted(node.right, tainted_vars)
        
        # Formatted values
        if isinstance(node, ast.JoinedStr):
            for value in node.values:
                if isinstance(value, ast.FormattedValue):
                    if self._is_tainted(value.value, tainted_vars):
                        return True
        
        # Calls that return tainted data
        if isinstance(node, ast.Call):
            return self._is_taint_source(node)
        
        return False
    
    def _get_func_name(self, node: ast.expr) -> Optional[str]:
        """Get function name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                return f"{node.value.id}.{node.attr}"
            return node.attr
        return None
    
    def _get_sink_category(self, func_name: str) -> Optional[str]:
        """Get sink category if function is a known sink."""
        for sink_pattern, category in TAINT_SINKS.items():
            if sink_pattern in func_name:
                return category
        return None
