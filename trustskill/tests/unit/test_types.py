"""
Unit Tests for src/types.py

TDD Approach:
1. Test dataclass creation and defaults
2. Test enum values
3. Test method behavior
4. Test edge cases
"""

import pytest
from datetime import datetime
from src.types import Severity, AnalysisMode, SecurityIssue, ScanResult


# =============================================================================
# Severity Enum Tests
# =============================================================================

class TestSeverity:
    """Tests for Severity enum."""
    
    @pytest.mark.unit
    def test_severity_values(self):
        """Test that Severity enum has expected values."""
        assert Severity.HIGH.value == "HIGH"
        assert Severity.MEDIUM.value == "MEDIUM"
        assert Severity.LOW.value == "LOW"
        assert Severity.INFO.value == "INFO"
    
    @pytest.mark.unit
    def test_severity_comparison(self, severity_high, severity_medium, severity_low):
        """Test severity ordering if applicable."""
        # Severity levels should be comparable (enum members are singletons)
        assert severity_high != severity_medium
        assert severity_medium != severity_low
        assert severity_high != severity_low
    
    @pytest.mark.unit
    def test_severity_membership(self):
        """Test that all expected severities exist."""
        expected = {"HIGH", "MEDIUM", "LOW", "INFO"}
        actual = {s.value for s in Severity}
        assert actual == expected


# =============================================================================
# AnalysisMode Enum Tests
# =============================================================================

class TestAnalysisMode:
    """Tests for AnalysisMode enum."""
    
    @pytest.mark.unit
    def test_analysis_mode_values(self, mode_fast, mode_standard, mode_deep):
        """Test that AnalysisMode enum has expected values."""
        assert mode_fast.value == "fast"
        assert mode_standard.value == "standard"
        assert mode_deep.value == "deep"
    
    @pytest.mark.unit
    def test_analysis_mode_uniqueness(self):
        """Test that all mode values are unique."""
        values = [m.value for m in AnalysisMode]
        assert len(values) == len(set(values))


# =============================================================================
# SecurityIssue Dataclass Tests
# =============================================================================

class TestSecurityIssue:
    """Tests for SecurityIssue dataclass."""
    
    @pytest.mark.unit
    def test_security_issue_creation(self, get_mock_security_issue):
        """Test creating a SecurityIssue with default values."""
        issue = get_mock_security_issue()
        
        assert issue.level == Severity.HIGH
        assert issue.category == "command_injection"
        assert issue.description == "eval() execution with variable"
        assert issue.file == "test.py"
        assert issue.line == 10
        assert issue.snippet == "eval(user_input)"
        assert issue.confidence == 0.9
    
    @pytest.mark.unit
    def test_security_issue_with_overrides(self, get_mock_security_issue):
        """Test creating a SecurityIssue with custom values."""
        issue = get_mock_security_issue(
            level=Severity.MEDIUM,
            category="network_request",
            description="HTTP request detected",
            file="network.py",
            line=25,
            snippet="requests.get(url)",
            confidence=0.75
        )
        
        assert issue.level == Severity.MEDIUM
        assert issue.category == "network_request"
        assert issue.description == "HTTP request detected"
        assert issue.file == "network.py"
        assert issue.line == 25
        assert issue.snippet == "requests.get(url)"
        assert issue.confidence == 0.75
    
    @pytest.mark.unit
    def test_security_issue_default_confidence(self):
        """Test that confidence defaults to 1.0."""
        issue = SecurityIssue(
            level=Severity.HIGH,
            category="test",
            description="test issue",
            file="test.py",
            line=1,
            snippet="test"
        )
        assert issue.confidence == 1.0
    
    @pytest.mark.unit
    def test_security_issue_to_dict(self, get_mock_security_issue):
        """Test to_dict method returns correct structure."""
        issue = get_mock_security_issue()
        result = issue.to_dict()
        
        assert isinstance(result, dict)
        assert result["level"] == "HIGH"
        assert result["category"] == "command_injection"
        assert result["description"] == "eval() execution with variable"
        assert result["file"] == "test.py"
        assert result["line"] == 10
        assert result["snippet"] == "eval(user_input)"
        assert result["confidence"] == 0.9
    
    @pytest.mark.unit
    def test_security_issue_to_dict_all_severities(self, get_mock_security_issue):
        """Test to_dict with all severity levels."""
        for severity in Severity:
            issue = get_mock_security_issue(level=severity)
            result = issue.to_dict()
            assert result["level"] == severity.value
    
    @pytest.mark.unit
    def test_security_issue_immutability(self, get_mock_security_issue):
        """Test that frozen dataclass behavior works (if frozen=True)."""
        # Note: The dataclass is not frozen, so this tests current behavior
        issue = get_mock_security_issue()
        issue.confidence = 0.5  # Should work since not frozen
        assert issue.confidence == 0.5


# =============================================================================
# ScanResult Dataclass Tests
# =============================================================================

class TestScanResult:
    """Tests for ScanResult dataclass."""
    
    @pytest.mark.unit
    def test_scan_result_creation(self, get_mock_scan_result):
        """Test creating a ScanResult with default values."""
        result = get_mock_scan_result()
        
        assert result.skill_path == "/tmp/test-skill"
        assert result.files_scanned == 5
        assert result.findings == []
        assert result.scan_time == 1.23
        assert result.timestamp is not None
    
    @pytest.mark.unit
    def test_scan_result_with_findings(self, get_mock_scan_result, get_mock_security_issue):
        """Test ScanResult with security findings."""
        findings = [
            get_mock_security_issue(level=Severity.HIGH),
            get_mock_security_issue(level=Severity.MEDIUM),
            get_mock_security_issue(level=Severity.HIGH),
        ]
        result = get_mock_scan_result(findings=findings)
        
        assert len(result.findings) == 3
        assert result.findings[0].level == Severity.HIGH
    
    @pytest.mark.unit
    def test_risk_summary_empty(self, get_mock_scan_result):
        """Test risk_summary with no findings."""
        result = get_mock_scan_result(findings=[])
        summary = result.risk_summary
        
        assert summary == {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    
    @pytest.mark.unit
    def test_risk_summary_with_findings(self, get_mock_scan_result, get_mock_security_issue):
        """Test risk_summary correctly counts findings by severity."""
        findings = [
            get_mock_security_issue(level=Severity.HIGH),
            get_mock_security_issue(level=Severity.HIGH),
            get_mock_security_issue(level=Severity.MEDIUM),
            get_mock_security_issue(level=Severity.LOW),
            get_mock_security_issue(level=Severity.LOW),
            get_mock_security_issue(level=Severity.LOW),
        ]
        result = get_mock_scan_result(findings=findings)
        summary = result.risk_summary
        
        assert summary["HIGH"] == 2
        assert summary["MEDIUM"] == 1
        assert summary["LOW"] == 3
        assert summary["INFO"] == 0
    
    @pytest.mark.unit
    def test_risk_summary_all_levels(self, get_mock_scan_result, get_mock_security_issue):
        """Test risk_summary with all severity levels."""
        findings = [
            get_mock_security_issue(level=Severity.HIGH),
            get_mock_security_issue(level=Severity.MEDIUM),
            get_mock_security_issue(level=Severity.LOW),
            get_mock_security_issue(level=Severity.INFO),
        ]
        result = get_mock_scan_result(findings=findings)
        summary = result.risk_summary
        
        assert summary["HIGH"] == 1
        assert summary["MEDIUM"] == 1
        assert summary["LOW"] == 1
        assert summary["INFO"] == 1
    
    @pytest.mark.unit
    def test_security_assessment_critical(self, get_mock_scan_result, get_mock_security_issue):
        """Test security_assessment with HIGH severity findings."""
        findings = [get_mock_security_issue(level=Severity.HIGH)]
        result = get_mock_scan_result(findings=findings)
        
        assert "CRITICAL" in result.security_assessment
        assert "🔴" in result.security_assessment
    
    @pytest.mark.unit
    def test_security_assessment_warning_many_medium(self, get_mock_scan_result, get_mock_security_issue):
        """Test security_assessment with >5 medium findings."""
        findings = [get_mock_security_issue(level=Severity.MEDIUM) for _ in range(6)]
        result = get_mock_scan_result(findings=findings)
        
        assert "WARNING" in result.security_assessment
        assert "🟡" in result.security_assessment
    
    @pytest.mark.unit
    def test_security_assessment_caution_few_medium(self, get_mock_scan_result, get_mock_security_issue):
        """Test security_assessment with 1-5 medium findings."""
        findings = [get_mock_security_issue(level=Severity.MEDIUM) for _ in range(3)]
        result = get_mock_scan_result(findings=findings)
        
        assert "CAUTION" in result.security_assessment
        assert "🟢" in result.security_assessment
    
    @pytest.mark.unit
    def test_security_assessment_safe(self, get_mock_scan_result):
        """Test security_assessment with no significant findings."""
        result = get_mock_scan_result(findings=[])
        
        assert "SAFE" in result.security_assessment
        assert "✅" in result.security_assessment
    
    @pytest.mark.unit
    def test_to_dict(self, get_mock_scan_result, get_mock_security_issue):
        """Test to_dict method returns correct structure."""
        findings = [get_mock_security_issue()]
        result = get_mock_scan_result(findings=findings)
        output = result.to_dict()
        
        assert "skill_path" in output
        assert "files_scanned" in output
        assert "findings" in output
        assert "risk_summary" in output
        assert "security_assessment" in output
        assert "scan_time" in output
        assert "timestamp" in output
        
        assert isinstance(output["findings"], list)
        assert isinstance(output["risk_summary"], dict)
        assert output["files_scanned"] == 5
    
    @pytest.mark.unit
    def test_to_dict_empty_findings(self, get_mock_scan_result):
        """Test to_dict with empty findings."""
        result = get_mock_scan_result(findings=[])
        output = result.to_dict()
        
        assert output["findings"] == []
        assert output["risk_summary"] == {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        assert "SAFE" in output["security_assessment"]
    
    @pytest.mark.unit
    def test_timestamp_auto_generation(self):
        """Test that timestamp is auto-generated if not provided."""
        result = ScanResult(
            skill_path="/test",
            files_scanned=1,
            findings=[],
            scan_time=0.1
        )
        
        # Should be a valid ISO format timestamp
        assert result.timestamp is not None
        # Try to parse it
        try:
            datetime.fromisoformat(result.timestamp)
        except ValueError:
            pytest.fail("timestamp is not a valid ISO format")


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestEdgeCases:
    """Edge case tests for types module."""
    
    @pytest.mark.unit
    def test_security_issue_negative_line_number(self):
        """Test SecurityIssue with negative line number."""
        # Should work even with negative line (edge case)
        issue = SecurityIssue(
            level=Severity.HIGH,
            category="test",
            description="test",
            file="test.py",
            line=-1,
            snippet="test"
        )
        assert issue.line == -1
    
    @pytest.mark.unit
    def test_security_issue_zero_confidence(self):
        """Test SecurityIssue with zero confidence."""
        issue = SecurityIssue(
            level=Severity.LOW,
            category="test",
            description="test",
            file="test.py",
            line=1,
            snippet="test",
            confidence=0.0
        )
        assert issue.confidence == 0.0
    
    @pytest.mark.unit
    def test_security_issue_high_confidence(self):
        """Test SecurityIssue with high confidence."""
        issue = SecurityIssue(
            level=Severity.HIGH,
            category="test",
            description="test",
            file="test.py",
            line=1,
            snippet="test",
            confidence=1.0
        )
        assert issue.confidence == 1.0
    
    @pytest.mark.unit
    def test_scan_result_zero_scan_time(self, get_mock_scan_result):
        """Test ScanResult with zero scan time."""
        result = get_mock_scan_result(scan_time=0.0)
        assert result.scan_time == 0.0
    
    @pytest.mark.unit
    def test_scan_result_large_scan_time(self, get_mock_scan_result):
        """Test ScanResult with very large scan time."""
        result = get_mock_scan_result(scan_time=999999.999)
        assert result.scan_time == 999999.999
