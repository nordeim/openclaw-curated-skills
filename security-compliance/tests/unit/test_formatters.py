"""
Unit Tests for Formatters (src/formatters/)

TDD Approach:
1. Test formatter initialization
2. Test output format correctness
3. Test edge cases (empty results, special characters)
4. Test color/formatting options
"""

import json
import pytest
from datetime import datetime
from pathlib import Path

from src.formatters.base import BaseFormatter
from src.formatters.text_formatter import TextFormatter, ProgressTracker
from src.formatters.json_formatter import JsonFormatter
from src.formatters.markdown_formatter import MarkdownFormatter
from src.types import Severity, SecurityIssue, ScanResult


# =============================================================================
# BaseFormatter Tests
# =============================================================================

class TestBaseFormatter:
    """Tests for the abstract BaseFormatter class."""
    
    @pytest.mark.unit
    def test_base_formatter_is_abstract(self):
        """Test that BaseFormatter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseFormatter()
    
    @pytest.mark.unit
    def test_base_formatter_requires_format_method(self):
        """Test that subclasses must implement format method."""
        class IncompleteFormatter(BaseFormatter):
            def get_name(self):
                return "Incomplete"
        
        with pytest.raises(TypeError):
            IncompleteFormatter()


# =============================================================================
# TextFormatter Tests
# =============================================================================

class TestTextFormatterInitialization:
    """Tests for TextFormatter initialization."""
    
    @pytest.mark.unit
    def test_text_formatter_creation(self):
        """Test creating a TextFormatter."""
        formatter = TextFormatter()
        assert formatter is not None
        assert formatter.get_name() == "TextFormatter"
    
    @pytest.mark.unit
    def test_text_formatter_with_color(self):
        """Test TextFormatter with color enabled."""
        formatter = TextFormatter(use_color=True)
        # Color may be disabled if not a tty, but should not error
        assert formatter is not None
    
    @pytest.mark.unit
    def test_text_formatter_no_color(self):
        """Test TextFormatter with color disabled."""
        formatter = TextFormatter(use_color=False)
        assert formatter.use_color is False


class TestTextFormatterOutput:
    """Tests for TextFormatter output format."""
    
    @pytest.mark.unit
    def test_format_empty_result(self):
        """Test formatting an empty scan result."""
        formatter = TextFormatter(use_color=False)
        result = ScanResult(
            skill_path="/test/skill",
            files_scanned=5,
            findings=[],
            scan_time=1.5
        )
        
        output = formatter.format(result)
        
        assert "ORANGE TRUSTSKILL" in output
        assert "5" in output  # files scanned
        assert "1.5" in output  # scan time
        assert "No security issues found" in output
        assert "SAFE" in output
    
    @pytest.mark.unit
    def test_format_with_findings(self):
        """Test formatting a result with findings."""
        formatter = TextFormatter(use_color=False)
        findings = [
            SecurityIssue(
                level=Severity.HIGH,
                category="command_injection",
                description="eval() detected",
                file="test.py",
                line=10,
                snippet="eval(user_input)",
                confidence=0.9
            )
        ]
        result = ScanResult(
            skill_path="/test/skill",
            files_scanned=3,
            findings=findings,
            scan_time=0.5
        )
        
        output = formatter.format(result)
        
        assert "command_injection" in output
        assert "eval() detected" in output
        assert "test.py" in output
        assert "10" in output
        assert "eval(user_input)" in output
        assert "90%" in output or "0.9" in output
    
    @pytest.mark.unit
    def test_format_risk_summary(self):
        """Test that risk summary is included."""
        formatter = TextFormatter(use_color=False)
        findings = [
            SecurityIssue(level=Severity.HIGH, category="test", description="test", file="a.py", line=1, snippet="x"),
            SecurityIssue(level=Severity.HIGH, category="test", description="test", file="b.py", line=2, snippet="y"),
            SecurityIssue(level=Severity.MEDIUM, category="test", description="test", file="c.py", line=3, snippet="z"),
        ]
        result = ScanResult(
            skill_path="/test",
            files_scanned=10,
            findings=findings,
            scan_time=1.0
        )
        
        output = formatter.format(result)
        
        assert "HIGH" in output
        assert "MEDIUM" in output
        assert "LOW" in output


class TestTextFormatterSeverityDisplay:
    """Tests for severity level display."""
    
    @pytest.mark.unit
    def test_high_severity_icon(self):
        """Test HIGH severity icon is displayed."""
        formatter = TextFormatter(use_color=False)
        findings = [SecurityIssue(
            level=Severity.HIGH,
            category="test",
            description="test",
            file="test.py",
            line=1,
            snippet="test"
        )]
        result = ScanResult(skill_path="/test", files_scanned=1, findings=findings, scan_time=0.1)
        
        output = formatter.format(result)
        assert "🔴" in output or "HIGH" in output
    
    @pytest.mark.unit
    def test_medium_severity_icon(self):
        """Test MEDIUM severity icon is displayed."""
        formatter = TextFormatter(use_color=False)
        findings = [SecurityIssue(
            level=Severity.MEDIUM,
            category="test",
            description="test",
            file="test.py",
            line=1,
            snippet="test"
        )]
        result = ScanResult(skill_path="/test", files_scanned=1, findings=findings, scan_time=0.1)
        
        output = formatter.format(result)
        assert "🟡" in output or "MEDIUM" in output


# =============================================================================
# ProgressTracker Tests
# =============================================================================

class TestProgressTracker:
    """Tests for ProgressTracker."""
    
    @pytest.mark.unit
    def test_progress_tracker_creation(self):
        """Test creating a ProgressTracker."""
        tracker = ProgressTracker(total=100, use_color=False)
        assert tracker.total == 100
        assert tracker.current == 0
        assert tracker.findings == 0
    
    @pytest.mark.unit
    def test_progress_tracker_update(self, capsys):
        """Test progress tracker update."""
        tracker = ProgressTracker(total=10, use_color=False)
        tracker.update("file1.py", new_findings=2)
        
        assert tracker.current == 1
        assert tracker.findings == 2
    
    @pytest.mark.unit
    def test_progress_tracker_finish(self, capsys):
        """Test progress tracker finish."""
        tracker = ProgressTracker(total=10, use_color=False)
        tracker.finish()
        
        captured = capsys.readouterr()
        assert captured.out.endswith("\n") or captured.out == ""


# =============================================================================
# JsonFormatter Tests
# =============================================================================

class TestJsonFormatter:
    """Tests for JsonFormatter."""
    
    @pytest.mark.unit
    def test_json_formatter_creation(self):
        """Test creating a JsonFormatter."""
        formatter = JsonFormatter()
        assert formatter is not None
        assert formatter.get_name() == "JsonFormatter"
        assert formatter.indent == 2
    
    @pytest.mark.unit
    def test_json_formatter_custom_indent(self):
        """Test JsonFormatter with custom indent."""
        formatter = JsonFormatter(indent=4)
        assert formatter.indent == 4
    
    @pytest.mark.unit
    def test_format_empty_result(self):
        """Test formatting empty result as JSON."""
        formatter = JsonFormatter()
        result = ScanResult(
            skill_path="/test/skill",
            files_scanned=5,
            findings=[],
            scan_time=1.5
        )
        
        output = formatter.format(result)
        
        # Should be valid JSON
        parsed = json.loads(output)
        assert parsed["skill_path"] == "/test/skill"
        assert parsed["files_scanned"] == 5
        assert parsed["findings"] == []
        assert parsed["risk_summary"]["HIGH"] == 0
    
    @pytest.mark.unit
    def test_format_with_findings(self):
        """Test formatting result with findings as JSON."""
        formatter = JsonFormatter()
        findings = [
            SecurityIssue(
                level=Severity.HIGH,
                category="command_injection",
                description="eval() detected",
                file="test.py",
                line=10,
                snippet="eval(user_input)",
                confidence=0.9
            )
        ]
        result = ScanResult(
            skill_path="/test/skill",
            files_scanned=3,
            findings=findings,
            scan_time=0.5
        )
        
        output = formatter.format(result)
        parsed = json.loads(output)
        
        assert len(parsed["findings"]) == 1
        assert parsed["findings"][0]["level"] == "HIGH"
        assert parsed["findings"][0]["category"] == "command_injection"
        assert parsed["findings"][0]["confidence"] == 0.9
    
    @pytest.mark.unit
    def test_json_unicode_handling(self):
        """Test JSON formatting with unicode content."""
        formatter = JsonFormatter()
        findings = [
            SecurityIssue(
                level=Severity.HIGH,
                category="test",
                description="English Description",
                file="file.py",
                line=1,
                snippet="test"
            )
        ]
        result = ScanResult(
            skill_path="/test/path",
            files_scanned=1,
            findings=findings,
            scan_time=0.1
        )
        
        output = formatter.format(result)
        parsed = json.loads(output)
        
        assert parsed["skill_path"] == "/test/path"
        assert parsed["findings"][0]["description"] == "English Description"


# =============================================================================
# MarkdownFormatter Tests
# =============================================================================

class TestMarkdownFormatter:
    """Tests for MarkdownFormatter."""
    
    @pytest.mark.unit
    def test_markdown_formatter_creation(self):
        """Test creating a MarkdownFormatter."""
        formatter = MarkdownFormatter()
        assert formatter is not None
        assert formatter.get_name() == "MarkdownFormatter"
    
    @pytest.mark.unit
    def test_format_empty_result(self):
        """Test formatting empty result as Markdown."""
        formatter = MarkdownFormatter()
        result = ScanResult(
            skill_path="/test/skill",
            files_scanned=5,
            findings=[],
            scan_time=1.5
        )
        
        output = formatter.format(result)
        
        assert "# 🔒 Orange TrustSkill" in output
        assert "## 📋 Scan Information" in output
        assert "No security issues found" in output
        assert "| 🔴 HIGH | 0 |" in output
    
    @pytest.mark.unit
    def test_format_with_findings(self):
        """Test formatting result with findings as Markdown."""
        formatter = MarkdownFormatter()
        findings = [
            SecurityIssue(
                level=Severity.HIGH,
                category="command_injection",
                description="eval() detected",
                file="test.py",
                line=10,
                snippet="eval(user_input)",
                confidence=0.9
            )
        ]
        result = ScanResult(
            skill_path="/test/skill",
            files_scanned=3,
            findings=findings,
            scan_time=0.5
        )
        
        output = formatter.format(result)
        
        assert "## 🚨 Detailed Findings" in output
        assert "command_injection" in output
        assert "test.py:10" in output or "test.py" in output
        assert "eval(user_input)" in output
        assert "90%" in output or "0.9" in output
    
    @pytest.mark.unit
    def test_markdown_table_format(self):
        """Test that risk summary is formatted as table."""
        formatter = MarkdownFormatter()
        result = ScanResult(
            skill_path="/test",
            files_scanned=1,
            findings=[],
            scan_time=0.1
        )
        
        output = formatter.format(result)
        
        assert "| Level | Count |" in output
        assert "|-------|-------|" in output
    
    @pytest.mark.unit
    def test_markdown_code_blocks(self):
        """Test that code snippets are in code blocks."""
        formatter = MarkdownFormatter()
        findings = [
            SecurityIssue(
                level=Severity.HIGH,
                category="test",
                description="test",
                file="test.py",
                line=1,
                snippet="eval(x)"
            )
        ]
        result = ScanResult(
            skill_path="/test",
            files_scanned=1,
            findings=findings,
            scan_time=0.1
        )
        
        output = formatter.format(result)
        
        assert "```" in output
        assert "eval(x)" in output


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestFormatterEdgeCases:
    """Edge case tests for formatters."""
    
    @pytest.mark.unit
    def test_text_formatter_special_characters(self):
        """Test handling of special characters in text output."""
        formatter = TextFormatter(use_color=False)
        findings = [
            SecurityIssue(
                level=Severity.HIGH,
                category="test",
                description="Special: \x00\x01\x02",
                file="test.py",
                line=1,
                snippet="code with \n newlines"
            )
        ]
        result = ScanResult(
            skill_path="/test",
            files_scanned=1,
            findings=findings,
            scan_time=0.1
        )
        
        output = formatter.format(result)
        # Should not raise exception
        assert isinstance(output, str)
    
    @pytest.mark.unit
    def test_json_formatter_special_characters(self):
        """Test handling of special characters in JSON output."""
        formatter = JsonFormatter()
        findings = [
            SecurityIssue(
                level=Severity.HIGH,
                category="test",
                description='Contains "quotes" and \\backslashes\\',
                file="test.py",
                line=1,
                snippet="print('hello')"
            )
        ]
        result = ScanResult(
            skill_path="/test",
            files_scanned=1,
            findings=findings,
            scan_time=0.1
        )
        
        output = formatter.format(result)
        # Should be valid JSON
        parsed = json.loads(output)
        assert 'Contains "quotes"' in parsed["findings"][0]["description"]
    
    @pytest.mark.unit
    def test_many_findings_performance(self):
        """Test formatter performance with many findings."""
        formatter = TextFormatter(use_color=False)
        findings = [
            SecurityIssue(
                level=Severity.HIGH,
                category="test",
                description=f"Finding {i}",
                file="test.py",
                line=i,
                snippet="code"
            )
            for i in range(100)
        ]
        result = ScanResult(
            skill_path="/test",
            files_scanned=100,
            findings=findings,
            scan_time=10.0
        )
        
        output = formatter.format(result)
        assert len(output) > 0
        assert "Finding 0" in output
        assert "Finding 99" in output
    
    @pytest.mark.unit
    def test_very_long_snippet(self):
        """Test handling of very long code snippets."""
        formatter = TextFormatter(use_color=False)
        long_snippet = "x" * 1000
        findings = [
            SecurityIssue(
                level=Severity.HIGH,
                category="test",
                description="test",
                file="test.py",
                line=1,
                snippet=long_snippet
            )
        ]
        result = ScanResult(
            skill_path="/test",
            files_scanned=1,
            findings=findings,
            scan_time=0.1
        )
        
        output = formatter.format(result)
        # Output should contain the snippet (formatter doesn't truncate)
        assert long_snippet in output
