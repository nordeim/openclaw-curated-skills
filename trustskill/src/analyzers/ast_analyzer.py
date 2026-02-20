"""
AST Analyzer - Python Abstract Syntax Tree analysis.
"""

import ast
import re
from typing import List, Optional, Dict, Any
from pathlib import Path

from .base import BaseAnalyzer
from ..types import SecurityIssue, Severity, AnalysisMode
from ..rules import TESTING_UTILITY_FILES, DOCUMENTATION_FILES


class ASTAnalyzer(BaseAnalyzer):
    """AST Analyzer - Performs deep code structure analysis for Python files."""

    def get_name(self) -> str:
        return "ASTAnalyzer"

    def analyze(self, file_path: Path, content: str) -> List[SecurityIssue]:
        """Analyze Python code using its Abstract Syntax Tree."""
        issues = []

        # Only analyze Python files
        if file_path.suffix != ".py":
            return issues

        try:
            tree = ast.parse(content)
            analyzer = PythonASTVisitor(content, str(file_path.name), file_path)
            analyzer.visit(tree)
            issues.extend(analyzer.issues)
        except SyntaxError:
            # Skip AST analysis if there's a syntax error
            pass
        except Exception:
            # Skip on any other processing error
            pass

        return issues

        try:
            tree = ast.parse(content)
            analyzer = PythonASTVisitor(content, str(file_path.name))
            analyzer.visit(tree)
            issues.extend(analyzer.issues)
        except SyntaxError:
            # Skip AST analysis if there's a syntax error
            pass
        except Exception:
            # Skip on any other processing error
            pass

        return issues


class PythonASTVisitor(ast.NodeVisitor):
    """Custom AST visitor for identifying security patterns in Python code."""

    def __init__(self, content: str, filename: str, filepath: Optional[Path] = None):
        self.content = content
        self.filename = filename
        self.filepath = filepath or Path(filename)
        self.issues: List[SecurityIssue] = []
        self.lines = content.split("\n")

    def _get_line(self, node: ast.AST) -> int:
        """Extract the line number from an AST node."""
        return getattr(node, "lineno", 1)

    def _get_snippet(self, node: ast.AST, context: int = 50) -> str:
        """Retrieve a code snippet for the given AST node."""
        line_num = self._get_line(node)
        if 1 <= line_num <= len(self.lines):
            line = self.lines[line_num - 1].strip()
            return line[:100] + "..." if len(line) > 100 else line
        return ""

    def _is_dangerous_call(self, func_name: str) -> tuple:
        """Check if a function name matches a known dangerous function."""
        dangerous_funcs = {
            "eval": ("command_injection", "eval() execution"),
            "exec": ("command_injection", "exec() execution"),
            "__import__": ("dynamic_import", "Dynamic import"),
            "compile": ("command_injection", "compile() execution"),
        }
        return dangerous_funcs.get(func_name, None)

    def visit_Call(self, node: ast.Call):
        """Analyze function calls for security risks."""
        func_name = self._get_func_name(node.func)

        if func_name:
            # Check for generic dangerous functions
            danger = self._is_dangerous_call(func_name)
            if danger:
                category, description = danger
                # Check for variable arguments (suggests dynamic execution)
                has_variable = any(
                    not isinstance(arg, (ast.Constant, ast.Str)) for arg in node.args
                )

                if has_variable:
                    self.issues.append(
                        SecurityIssue(
                            level=Severity.HIGH,
                            category=category,
                            description=f"{description} with variable",
                            file=self.filename,
                            line=self._get_line(node),
                            snippet=self._get_snippet(node),
                            confidence=0.9,
                        )
                    )

            # Check for os.system and os.popen calls
            if func_name in ["system", "popen"] and self._is_os_call(node.func):
                self.issues.append(
                    SecurityIssue(
                        level=Severity.HIGH,
                        category="command_injection",
                        description=f"os.{func_name}() call",
                        file=self.filename,
                        line=self._get_line(node),
                        snippet=self._get_snippet(node),
                        confidence=0.85,
                    )
                )

            # Check for subprocess calls with shell=True
            if func_name in ["call", "run", "Popen"] and self._is_subprocess_call(
                node.func
            ):
                if self._has_shell_true(node):
                    # Skip if file is whitelisted (testing utilities)
                    if self.filepath.name not in TESTING_UTILITY_FILES:
                        self.issues.append(
                            SecurityIssue(
                                level=Severity.HIGH,
                                category="command_injection",
                                description="subprocess with shell=True",
                                file=self.filename,
                                line=self._get_line(node),
                                snippet=self._get_snippet(node),
                                confidence=0.95,
                            )
                        )

            # Check for open() calls on sensitive files
            if func_name == "open":
                self._check_open_call(node)

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        """Identify imports of modules known for unsafe deserialization."""
        for alias in node.names:
            if alias.name in ["pickle", "marshal", "shelve"]:
                self.issues.append(
                    SecurityIssue(
                        level=Severity.MEDIUM,
                        category="deserialization",
                        description=f"{alias.name} import (unsafe deserialization)",
                        file=self.filename,
                        line=self._get_line(node),
                        snippet=self._get_snippet(node),
                        confidence=0.7,
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Identify 'from ... import' statements for unsafe modules."""
        if node.module == "subprocess" and node.names:
            for alias in node.names:
                if alias.name in ["call", "run", "Popen", "check_output"]:
                    # Note: We track these but only flag on actual usage
                    pass

        if node.module in ["pickle", "marshal"]:
            self.issues.append(
                SecurityIssue(
                    level=Severity.MEDIUM,
                    category="deserialization",
                    description=f"{node.module} import (unsafe deserialization)",
                    file=self.filename,
                    line=self._get_line(node),
                    snippet=self._get_snippet(node),
                    confidence=0.7,
                )
            )

        self.generic_visit(node)

    def _get_func_name(self, node: ast.expr) -> Optional[str]:
        """Extract the function name from a Call node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _is_os_call(self, node: ast.expr) -> bool:
        """Verify if a call attribute belongs to the 'os' module."""
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                return node.value.id == "os"
        return False

    def _is_subprocess_call(self, node: ast.expr) -> bool:
        """Verify if a call attribute belongs to the 'subprocess' module."""
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                return node.value.id == "subprocess"
        return False

    def _has_shell_true(self, node: ast.Call) -> bool:
        """Check if a Call node contains the 'shell=True' keyword argument."""
        for keyword in node.keywords:
            if keyword.arg == "shell":
                if isinstance(keyword.value, ast.Constant):
                    return keyword.value.value is True
                elif isinstance(keyword.value, ast.NameConstant):
                    return keyword.value.value is True
        return False

    def _check_open_call(self, node: ast.Call):
        """Analyze open() calls for access to sensitive system or config files."""
        if not node.args:
            return

        first_arg = node.args[0]

        # Check for hardcoded paths to sensitive files
        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
            filepath = first_arg.value
            sensitive_patterns = [
                (r"\.ssh[/\\]", "SSH key access"),
                (r"password", "Password file access"),
                (r"token", "Token file access"),
                (r"secret", "Secret file access"),
                (r"\.openclaw[/\\]config", "OpenClaw config access"),
                (r"MEMORY\.md|SOUL\.md|USER\.md", "Memory file access"),
            ]

            for pattern, description in sensitive_patterns:
                if re.search(pattern, filepath, re.IGNORECASE):
                    self.issues.append(
                        SecurityIssue(
                            level=Severity.HIGH,
                            category="sensitive_file_access",
                            description=description,
                            file=self.filename,
                            line=self._get_line(node),
                            snippet=self._get_snippet(node),
                            confidence=0.85,
                        )
                    )
                    break
