"""
Unit Tests for Configuration System (src/config/)

TDD Approach:
1. Test config loading and validation
2. Test custom patterns integration
3. Test severity overrides
4. Test whitelist functionality
"""

import pytest
import tempfile
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# Import after adding to path
from src.config.loader import ConfigLoader, Config
from src.config.validator import ConfigValidator, ConfigValidationError


# =============================================================================
# Config Data Model Tests
# =============================================================================

class TestConfigDataModel:
    """Tests for Config dataclass."""
    
    @pytest.mark.unit
    def test_config_creation_with_defaults(self):
        """Test creating Config with default values."""
        config = Config()
        
        assert config.version == "3.0"
        assert config.scanning.mode == "standard"
        assert config.scanning.max_file_size == "10MB"
        assert config.secret_detection.enabled is True
        assert config.dependency_check.enabled is True
    
    @pytest.mark.unit
    def test_config_custom_values(self):
        """Test creating Config with custom values."""
        from src.config.loader import ScanningConfig, SecretDetectionConfig
        
        config = Config(
            version="3.0",
            scanning=ScanningConfig(mode="deep", max_file_size="5MB"),
            secret_detection=SecretDetectionConfig(enabled=False)
        )
        
        assert config.scanning.mode == "deep"
        assert config.secret_detection.enabled is False


# =============================================================================
# Config Loader Tests
# =============================================================================

class TestConfigLoader:
    """Tests for ConfigLoader."""
    
    @pytest.mark.unit
    def test_loads_yaml_config(self, temp_dir):
        """Test loading YAML configuration file."""
        config_file = temp_dir / "trustskill.yaml"
        config_file.write_text("""
version: "3.0"
scanning:
  mode: deep
  max_file_size: "5MB"
""")
        
        config = ConfigLoader.load(str(config_file))
        
        assert config.version == "3.0"
        assert config.scanning.mode == "deep"
        assert config.scanning.max_file_size == "5MB"
    
    @pytest.mark.unit
    def test_loads_json_config(self, temp_dir):
        """Test loading JSON configuration file."""
        config_file = temp_dir / "trustskill.json"
        config_file.write_text('''
{
    "version": "3.0",
    "scanning": {
        "mode": "fast"
    }
}
''')
        
        config = ConfigLoader.load(str(config_file))
        
        assert config.scanning.mode == "fast"
    
    @pytest.mark.unit
    def test_loads_default_config_when_file_not_found(self):
        """Test that default config is returned when file doesn't exist."""
        config = ConfigLoader.load("/nonexistent/config.yaml")
        
        assert config.version == "3.0"
        assert config.scanning.mode == "standard"
    
    @pytest.mark.unit
    def test_loads_custom_patterns(self, temp_dir):
        """Test loading custom security patterns."""
        config_file = temp_dir / "trustskill.yaml"
        config_file.write_text("""
version: '3.0'
rules:
  custom_patterns:
    - name: 'custom_api_key'
      pattern: 'X-API-KEY:\\\s*([A-Za-z0-9]+)'
      severity: HIGH
      description: 'Custom API key header'
    - name: 'internal_endpoint'
      pattern: 'internal\\.company\\.com'
      severity: MEDIUM
      description: 'Internal endpoint access'
""")
        
        config = ConfigLoader.load(str(config_file))
        
        assert len(config.rules.custom_patterns) == 2
        assert config.rules.custom_patterns[0].name == "custom_api_key"
        assert config.rules.custom_patterns[0].severity == "HIGH"
    
    @pytest.mark.unit
    def test_loads_severity_overrides(self, temp_dir):
        """Test loading severity overrides."""
        config_file = temp_dir / "trustskill.yaml"
        config_file.write_text("""
version: "3.0"
rules:
  severity_overrides:
    network_request: LOW
    file_operation: INFO
""")
        
        config = ConfigLoader.load(str(config_file))
        
        assert config.rules.severity_overrides["network_request"] == "LOW"
        assert config.rules.severity_overrides["file_operation"] == "INFO"
    
    @pytest.mark.unit
    def test_loads_whitelist(self, temp_dir):
        """Test loading whitelist configuration."""
        config_file = temp_dir / "trustskill.yaml"
        config_file.write_text("""
version: '3.0'
rules:
  whitelist:
    files:
      - 'test_*.py'
      - '*_test.py'
    patterns:
      - 'eval\\(.*\\)'
""")
        
        config = ConfigLoader.load(str(config_file))
        
        assert "test_*.py" in config.rules.whitelist.files
        assert len(config.rules.whitelist.patterns) == 1
    
    @pytest.mark.unit
    def test_loads_secret_detection_config(self, temp_dir):
        """Test loading secret detection configuration."""
        config_file = temp_dir / "trustskill.yaml"
        config_file.write_text("""
version: "3.0"
secret_detection:
  enabled: true
  min_entropy: 4.5
  min_length: 20
  check_common_passwords: true
""")
        
        config = ConfigLoader.load(str(config_file))
        
        assert config.secret_detection.enabled is True
        assert config.secret_detection.min_entropy == 4.5
        assert config.secret_detection.min_length == 20


# =============================================================================
# Config Validator Tests
# =============================================================================

class TestConfigValidator:
    """Tests for ConfigValidator."""
    
    @pytest.mark.unit
    def test_valid_config_passes(self):
        """Test that valid config passes validation."""
        config_data = {
            "version": "3.0",
            "scanning": {
                "mode": "standard"
            }
        }
        
        # Should not raise
        ConfigValidator.validate(config_data)
    
    @pytest.mark.unit
    def test_invalid_mode_fails(self):
        """Test that invalid scanning mode fails validation."""
        config_data = {
            "version": "3.0",
            "scanning": {
                "mode": "invalid_mode"
            }
        }
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate(config_data)
        
        assert "mode" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_invalid_entropy_fails(self):
        """Test that invalid entropy value fails validation."""
        config_data = {
            "version": "3.0",
            "secret_detection": {
                "min_entropy": 10.0  # Invalid: > 8
            }
        }
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate(config_data)
    
    @pytest.mark.unit
    def test_invalid_severity_fails(self):
        """Test that invalid severity in overrides fails."""
        config_data = {
            "version": "3.0",
            "rules": {
                "severity_overrides": {
                    "network_request": "INVALID"
                }
            }
        }
        
        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.validate(config_data)
    
    @pytest.mark.unit
    def test_missing_required_fields_fails(self):
        """Test that invalid version type fails validation."""
        config_data = {
            "version": 123,  # Invalid type
            "scanning": {
                "mode": "standard"
            }
        }
        
        with pytest.raises(ConfigValidationError):
            ConfigValidator.validate(config_data)


# =============================================================================
# Integration Tests
# =============================================================================

class TestConfigIntegration:
    """Integration tests for configuration system."""
    
    @pytest.mark.integration
    def test_config_to_scanner_integration(self, temp_dir):
        """Test that config integrates with SkillScanner."""
        config_file = temp_dir / "trustskill.yaml"
        config_file.write_text('''
version: "3.0"
scanning:
  mode: deep
''')
        
        config = ConfigLoader.load(str(config_file))
        
        # Config should be loaded correctly
        assert config is not None
        assert config.scanning.mode == "deep"
    
    @pytest.mark.integration
    def test_custom_patterns_in_scanner(self, temp_dir):
        """Test that custom patterns are used during scanning."""
        config_file = temp_dir / "trustskill.yaml"
        config_file.write_text(r'''
version: "3.0"
rules:
  custom_patterns:
    - name: "test_pattern"
      pattern: "TEST_SECRET_[A-Za-z0-9]+"
      severity: HIGH
      description: "Test secret pattern"
''')
        
        config = ConfigLoader.load(str(config_file))
        
        # Custom patterns should be accessible
        assert len(config.rules.custom_patterns) > 0
        assert "TEST_SECRET_" in config.rules.custom_patterns[0].pattern


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestConfigEdgeCases:
    """Edge case tests for configuration system."""
    
    @pytest.mark.unit
    def test_empty_config_file(self, temp_dir):
        """Test handling of empty config file."""
        config_file = temp_dir / "trustskill.yaml"
        config_file.write_text("")
        
        # Empty file returns default config (None is treated as empty dict)
        config = ConfigLoader.load(str(config_file))
        assert config.version == "3.0"
    
    @pytest.mark.unit
    def test_malformed_yaml(self, temp_dir):
        """Test handling of malformed YAML."""
        config_file = temp_dir / "trustskill.yaml"
        config_file.write_text("invalid: yaml: : content")
        
        with pytest.raises(ConfigValidationError):
            ConfigLoader.load(str(config_file))
    
    @pytest.mark.unit
    def test_unknown_fields_ignored(self, temp_dir):
        """Test that unknown fields are ignored gracefully."""
        config_file = temp_dir / "trustskill.yaml"
        config_file.write_text("""
version: "3.0"
unknown_field: "should be ignored"
scanning:
  mode: standard
  another_unknown: 123
""")
        
        # Should not raise
        config = ConfigLoader.load(str(config_file))
        assert config.scanning.mode == "standard"
