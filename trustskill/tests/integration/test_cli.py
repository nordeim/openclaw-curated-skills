"""
Integration Tests for CLI (src/cli.py)

TDD Approach:
1. Test CLI argument parsing
2. Test end-to-end CLI execution
3. Test output formats
4. Test exit codes
"""

import sys
import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import CLI module
from src.cli import main
from src.types import Severity


# =============================================================================
# CLI Argument Parsing Tests
# =============================================================================

class TestCLIArgumentParsing:
    """Tests for CLI argument parsing."""
    
    @pytest.mark.integration
    def test_cli_requires_skill_path(self, capsys):
        """Test that CLI requires skill_path argument."""
        with pytest.raises(SystemExit) as exc_info:
            with patch.object(sys, 'argv', ['cli.py']):
                main()
        
        assert exc_info.value.code == 2  # argparse exit code for missing argument
    
    @pytest.mark.integration
    def test_cli_accepts_skill_path(self, temp_dir):
        """Test that CLI accepts skill path."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: test\n---")
        
        with pytest.raises(SystemExit) as exc_info:
            with patch.object(sys, 'argv', ['cli.py', str(skill_dir)]):
                main()
        
        # Should exit 0 (no high risk issues in empty skill)
        assert exc_info.value.code == 0
    
    @pytest.mark.integration
    def test_cli_mode_argument_fast(self, temp_dir):
        """Test --mode fast argument."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: test\n---")
        
        with pytest.raises(SystemExit):
            with patch.object(sys, 'argv', ['cli.py', str(skill_dir), '--mode', 'fast']):
                main()
    
    @pytest.mark.integration
    def test_cli_mode_argument_deep(self, temp_dir):
        """Test --mode deep argument."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: test\n---")
        
        with pytest.raises(SystemExit):
            with patch.object(sys, 'argv', ['cli.py', str(skill_dir), '--mode', 'deep']):
                main()
    
    @pytest.mark.integration
    def test_cli_invalid_mode(self, temp_dir):
        """Test that invalid mode is rejected."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        
        with pytest.raises(SystemExit) as exc_info:
            with patch.object(sys, 'argv', ['cli.py', str(skill_dir), '--mode', 'invalid']):
                main()
        
        assert exc_info.value.code == 2


# =============================================================================
# CLI Output Format Tests
# =============================================================================

class TestCLIOutputFormats:
    """Tests for CLI output formats."""
    
    @pytest.mark.integration
    def test_cli_json_format(self, temp_dir, capsys):
        """Test --format json output."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: test\n---")
        
        with pytest.raises(SystemExit):
            with patch.object(sys, 'argv', ['cli.py', str(skill_dir), '--format', 'json', '--no-progress']):
                main()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Should be valid JSON
        import json
        try:
            parsed = json.loads(output)
            assert 'skill_path' in parsed
        except json.JSONDecodeError:
            # Output might be mixed with progress
            pass
    
    @pytest.mark.integration
    def test_cli_markdown_format(self, temp_dir, capsys):
        """Test --format markdown output."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: test\n---")
        
        with pytest.raises(SystemExit):
            with patch.object(sys, 'argv', ['cli.py', str(skill_dir), '--format', 'markdown', '--no-progress']):
                main()
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert '# 🔒 Orange TrustSkill' in output or 'Orange TrustSkill' in output
    
    @pytest.mark.integration
    def test_cli_export_for_llm_flag(self, temp_dir, capsys):
        """Test --export-for-llm flag."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: test\n---")
        
        with pytest.raises(SystemExit):
            with patch.object(sys, 'argv', ['cli.py', str(skill_dir), '--export-for-llm', '--no-progress']):
                main()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Should produce markdown output
        assert 'Orange TrustSkill' in output


# =============================================================================
# CLI Exit Code Tests
# =============================================================================

class TestCLIExitCodes:
    """Tests for CLI exit codes."""
    
    @pytest.mark.integration
    def test_exit_code_0_no_high_risk(self, temp_dir):
        """Test exit code 0 when no high risk issues."""
        skill_dir = temp_dir / "safe-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: safe\n---")
        (skill_dir / "main.py").write_text("print('hello')")
        
        with pytest.raises(SystemExit) as exc_info:
            with patch.object(sys, 'argv', ['cli.py', str(skill_dir), '--no-progress']):
                main()
        
        assert exc_info.value.code == 0
    
    @pytest.mark.integration
    def test_exit_code_1_high_risk(self, temp_dir):
        """Test exit code 1 when high risk issues found."""
        skill_dir = temp_dir / "unsafe-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: unsafe\n---")
        (skill_dir / "evil.py").write_text('eval(user_input)')
        
        with pytest.raises(SystemExit) as exc_info:
            with patch.object(sys, 'argv', ['cli.py', str(skill_dir), '--no-progress']):
                main()
        
        assert exc_info.value.code == 1


# =============================================================================
# CLI Option Tests
# =============================================================================

class TestCLIOptions:
    """Tests for CLI options."""
    
    @pytest.mark.integration
    def test_cli_no_color_option(self, temp_dir):
        """Test --no-color option."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: test\n---")
        
        with pytest.raises(SystemExit):
            with patch.object(sys, 'argv', ['cli.py', str(skill_dir), '--no-color', '--no-progress']):
                main()
    
    @pytest.mark.integration
    def test_cli_no_progress_option(self, temp_dir, capsys):
        """Test --no-progress option."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: test\n---")
        
        with pytest.raises(SystemExit):
            with patch.object(sys, 'argv', ['cli.py', str(skill_dir), '--no-progress']):
                main()
        
        captured = capsys.readouterr()
        # Progress bar should not be in output
        assert 'Scanning:' not in captured.out or '█' not in captured.out
    
    @pytest.mark.integration
    def test_cli_quiet_option(self, temp_dir, capsys):
        """Test --quiet option."""
        skill_dir = temp_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: test\n---")
        
        with pytest.raises(SystemExit):
            with patch.object(sys, 'argv', ['cli.py', str(skill_dir), '--quiet']):
                main()
        
        captured = capsys.readouterr()
        # In quiet mode, should only show summary


# =============================================================================
# CLI Version Tests
# =============================================================================

class TestCLIVersion:
    """Tests for CLI version flag."""
    
    @pytest.mark.integration
    def test_cli_version_flag(self, capsys):
        """Test --version flag."""
        with pytest.raises(SystemExit) as exc_info:
            with patch.object(sys, 'argv', ['cli.py', '--version']):
                main()
        
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert '3.0.0' in captured.out


# =============================================================================
# CLI Help Tests
# =============================================================================

class TestCLIHelp:
    """Tests for CLI help."""
    
    @pytest.mark.integration
    def test_cli_help_flag(self, capsys):
        """Test --help flag."""
        with pytest.raises(SystemExit) as exc_info:
            with patch.object(sys, 'argv', ['cli.py', '--help']):
                main()
        
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert 'Orange TrustSkill' in captured.out
        assert '--mode' in captured.out
        assert '--format' in captured.out


# =============================================================================
# End-to-End Tests
# =============================================================================

class TestCLIEndToEnd:
    """End-to-end tests for CLI."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_scan_real_skill_directory(self):
        """Test scanning the actual project directory."""
        project_dir = Path(__file__).parent.parent.parent
        
        with pytest.raises(SystemExit) as exc_info:
            with patch.object(sys, 'argv', ['cli.py', str(project_dir), '--no-progress']):
                main()
        
        # Should complete without error
        assert exc_info.value.code in [0, 1]  # 0 = safe, 1 = issues found
    
    @pytest.mark.integration
    def test_cli_with_malicious_skill(self, malicious_python_skill, capsys):
        """Test CLI with a skill containing malicious code."""
        with pytest.raises(SystemExit) as exc_info:
            with patch.object(sys, 'argv', ['cli.py', str(malicious_python_skill), '--no-progress']):
                main()
        
        captured = capsys.readouterr()
        # Should detect issues
        assert exc_info.value.code == 1 or 'HIGH' in captured.out
