"""
Configuration Validator for Orange TrustSkill v3.0

Validates configuration files against schema requirements.
"""

import re
from typing import Dict, Any, List, Optional


class ConfigValidationError(Exception):
    """Configuration validation error."""
    pass


class ConfigValidator:
    """Configuration validator."""
    
    VALID_MODES = ['fast', 'standard', 'deep']
    VALID_SEVERITIES = ['HIGH', 'MEDIUM', 'LOW', 'INFO']
    VALID_FORMATS = ['text', 'json', 'markdown']
    
    @classmethod
    def validate(cls, data: Dict[str, Any]) -> None:
        """
        Validate configuration data.
        
        Args:
            data: Configuration dictionary
            
        Raises:
            ConfigValidationError: If validation fails
        """
        if not isinstance(data, dict):
            raise ConfigValidationError("Configuration must be a dictionary")
        
        # Check version (optional - defaults handled in loader)
        if 'version' in data:
            version = data['version']
            if not isinstance(version, str):
                raise ConfigValidationError("'version' must be a string")
        
        # Validate scanning config
        if 'scanning' in data:
            cls._validate_scanning(data['scanning'])
        
        # Validate rules config
        if 'rules' in data:
            cls._validate_rules(data['rules'])
        
        # Validate secret detection config
        if 'secret_detection' in data:
            cls._validate_secret_detection(data['secret_detection'])
        
        # Validate dependency check config
        if 'dependency_check' in data:
            cls._validate_dependency_check(data['dependency_check'])
        
        # Validate output config
        if 'output' in data:
            cls._validate_output(data['output'])
    
    @classmethod
    def _validate_scanning(cls, scanning: Dict[str, Any]) -> None:
        """Validate scanning configuration."""
        if not isinstance(scanning, dict):
            raise ConfigValidationError("'scanning' must be a dictionary")
        
        if 'mode' in scanning:
            mode = scanning['mode']
            if mode not in cls.VALID_MODES:
                raise ConfigValidationError(
                    f"Invalid scanning mode: '{mode}'. "
                    f"Must be one of: {', '.join(cls.VALID_MODES)}"
                )
        
        if 'max_file_size' in scanning:
            size = scanning['max_file_size']
            if not cls._is_valid_file_size(size):
                raise ConfigValidationError(
                    f"Invalid max_file_size: '{size}'. "
                    f"Must be a valid size string (e.g., '10MB', '1GB')"
                )
    
    @classmethod
    def _validate_rules(cls, rules: Dict[str, Any]) -> None:
        """Validate rules configuration."""
        if not isinstance(rules, dict):
            raise ConfigValidationError("'rules' must be a dictionary")
        
        # Validate custom patterns
        if 'custom_patterns' in rules:
            patterns = rules['custom_patterns']
            if not isinstance(patterns, list):
                raise ConfigValidationError("'custom_patterns' must be a list")
            
            for i, pattern in enumerate(patterns):
                cls._validate_custom_pattern(pattern, i)
        
        # Validate severity overrides
        if 'severity_overrides' in rules:
            overrides = rules['severity_overrides']
            if not isinstance(overrides, dict):
                raise ConfigValidationError("'severity_overrides' must be a dictionary")
            
            for category, severity in overrides.items():
                if severity not in cls.VALID_SEVERITIES:
                    raise ConfigValidationError(
                        f"Invalid severity override for '{category}': '{severity}'. "
                        f"Must be one of: {', '.join(cls.VALID_SEVERITIES)}"
                    )
        
        # Validate whitelist
        if 'whitelist' in rules:
            whitelist = rules['whitelist']
            if not isinstance(whitelist, dict):
                raise ConfigValidationError("'whitelist' must be a dictionary")
            
            if 'files' in whitelist and not isinstance(whitelist['files'], list):
                raise ConfigValidationError("'whitelist.files' must be a list")
            
            if 'patterns' in whitelist and not isinstance(whitelist['patterns'], list):
                raise ConfigValidationError("'whitelist.patterns' must be a list")
    
    @classmethod
    def _validate_custom_pattern(cls, pattern: Dict[str, Any], index: int) -> None:
        """Validate a single custom pattern."""
        if not isinstance(pattern, dict):
            raise ConfigValidationError(f"Custom pattern at index {index} must be a dictionary")
        
        if 'name' not in pattern:
            raise ConfigValidationError(f"Custom pattern at index {index} missing 'name'")
        
        if 'pattern' not in pattern:
            raise ConfigValidationError(f"Custom pattern at index {index} missing 'pattern'")
        
        # Validate severity if provided
        if 'severity' in pattern:
            severity = pattern['severity']
            if severity not in cls.VALID_SEVERITIES:
                raise ConfigValidationError(
                    f"Invalid severity in custom pattern '{pattern.get('name', index)}': "
                    f"'{severity}'. Must be one of: {', '.join(cls.VALID_SEVERITIES)}"
                )
        
        # Validate regex pattern
        try:
            re.compile(pattern['pattern'])
        except re.error as e:
            raise ConfigValidationError(
                f"Invalid regex pattern in '{pattern.get('name', index)}': {e}"
            )
    
    @classmethod
    def _validate_secret_detection(cls, config: Dict[str, Any]) -> None:
        """Validate secret detection configuration."""
        if not isinstance(config, dict):
            raise ConfigValidationError("'secret_detection' must be a dictionary")
        
        if 'min_entropy' in config:
            entropy = config['min_entropy']
            if not isinstance(entropy, (int, float)):
                raise ConfigValidationError("'min_entropy' must be a number")
            if not 0 <= entropy <= 8:
                raise ConfigValidationError(
                    f"'min_entropy' must be between 0 and 8, got {entropy}"
                )
        
        if 'min_length' in config:
            length = config['min_length']
            if not isinstance(length, int):
                raise ConfigValidationError("'min_length' must be an integer")
            if length < 1:
                raise ConfigValidationError("'min_length' must be at least 1")
        
        if 'enabled' in config and not isinstance(config['enabled'], bool):
            raise ConfigValidationError("'secret_detection.enabled' must be a boolean")
        
        if 'check_common_passwords' in config:
            if not isinstance(config['check_common_passwords'], bool):
                raise ConfigValidationError("'check_common_passwords' must be a boolean")
    
    @classmethod
    def _validate_dependency_check(cls, config: Dict[str, Any]) -> None:
        """Validate dependency check configuration."""
        if not isinstance(config, dict):
            raise ConfigValidationError("'dependency_check' must be a dictionary")
        
        if 'enabled' in config and not isinstance(config['enabled'], bool):
            raise ConfigValidationError("'dependency_check.enabled' must be a boolean")
        
        if 'cache_duration' in config:
            duration = config['cache_duration']
            if not isinstance(duration, int):
                raise ConfigValidationError("'cache_duration' must be an integer")
            if duration < 0:
                raise ConfigValidationError("'cache_duration' must be non-negative")
    
    @classmethod
    def _validate_output(cls, output: Dict[str, Any]) -> None:
        """Validate output configuration."""
        if not isinstance(output, dict):
            raise ConfigValidationError("'output' must be a dictionary")
        
        if 'format' in output:
            fmt = output['format']
            if fmt not in cls.VALID_FORMATS:
                raise ConfigValidationError(
                    f"Invalid output format: '{fmt}'. "
                    f"Must be one of: {', '.join(cls.VALID_FORMATS)}"
                )
        
        if 'color' in output and not isinstance(output['color'], bool):
            raise ConfigValidationError("'output.color' must be a boolean")
        
        if 'show_confidence' in output:
            if not isinstance(output['show_confidence'], bool):
                raise ConfigValidationError("'output.show_confidence' must be a boolean")
    
    @classmethod
    def _is_valid_file_size(cls, size: str) -> bool:
        """Check if file size string is valid."""
        if not isinstance(size, str):
            return False
        
        # Pattern: number followed by optional unit (B, KB, MB, GB)
        pattern = r'^\d+\s*(B|KB|MB|GB|K|M|G)?$'
        return bool(re.match(pattern, size, re.IGNORECASE))
