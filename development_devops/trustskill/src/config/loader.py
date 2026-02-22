"""
Configuration Loader for Orange TrustSkill v3.0

Supports YAML and JSON configuration files with default values.
"""

import yaml
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union


@dataclass
class ScanningConfig:
    """Scanning configuration."""
    mode: str = "standard"
    max_file_size: str = "10MB"
    follow_symlinks: bool = False


@dataclass
class CustomPattern:
    """Custom security pattern definition."""
    name: str = ""
    pattern: str = ""
    severity: str = "MEDIUM"
    description: str = ""


@dataclass
class WhitelistConfig:
    """Whitelist configuration."""
    files: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)


@dataclass
class RulesConfig:
    """Rules configuration."""
    custom_patterns: List[CustomPattern] = field(default_factory=list)
    severity_overrides: Dict[str, str] = field(default_factory=dict)
    whitelist: WhitelistConfig = field(default_factory=WhitelistConfig)


@dataclass
class SecretDetectionConfig:
    """Secret detection configuration."""
    enabled: bool = True
    min_entropy: float = 4.5
    min_length: int = 20
    check_common_passwords: bool = True


@dataclass
class DependencyCheckConfig:
    """Dependency vulnerability check configuration."""
    enabled: bool = True
    cache_duration: int = 3600


@dataclass
class OutputConfig:
    """Output configuration."""
    format: str = "text"
    color: bool = True
    show_confidence: bool = True


@dataclass
class Config:
    """Main configuration class."""
    version: str = "3.0"
    scanning: ScanningConfig = field(default_factory=ScanningConfig)
    rules: RulesConfig = field(default_factory=RulesConfig)
    secret_detection: SecretDetectionConfig = field(default_factory=SecretDetectionConfig)
    dependency_check: DependencyCheckConfig = field(default_factory=DependencyCheckConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create Config from dictionary."""
        config = cls(version=data.get('version', '3.0'))
        
        # Parse scanning config
        if 'scanning' in data:
            scanning_data = data['scanning']
            config.scanning = ScanningConfig(
                mode=scanning_data.get('mode', 'standard'),
                max_file_size=scanning_data.get('max_file_size', '10MB'),
                follow_symlinks=scanning_data.get('follow_symlinks', False)
            )
        
        # Parse rules config
        if 'rules' in data:
            rules_data = data['rules']
            
            # Parse custom patterns
            custom_patterns = []
            for pattern_data in rules_data.get('custom_patterns', []):
                custom_patterns.append(CustomPattern(
                    name=pattern_data.get('name', ''),
                    pattern=pattern_data.get('pattern', ''),
                    severity=pattern_data.get('severity', 'MEDIUM'),
                    description=pattern_data.get('description', '')
                ))
            
            # Parse whitelist
            whitelist_data = rules_data.get('whitelist', {})
            whitelist = WhitelistConfig(
                files=whitelist_data.get('files', []),
                patterns=whitelist_data.get('patterns', [])
            )
            
            config.rules = RulesConfig(
                custom_patterns=custom_patterns,
                severity_overrides=rules_data.get('severity_overrides', {}),
                whitelist=whitelist
            )
        
        # Parse secret detection config
        if 'secret_detection' in data:
            sd_data = data['secret_detection']
            config.secret_detection = SecretDetectionConfig(
                enabled=sd_data.get('enabled', True),
                min_entropy=sd_data.get('min_entropy', 4.5),
                min_length=sd_data.get('min_length', 20),
                check_common_passwords=sd_data.get('check_common_passwords', True)
            )
        
        # Parse dependency check config
        if 'dependency_check' in data:
            dc_data = data['dependency_check']
            config.dependency_check = DependencyCheckConfig(
                enabled=dc_data.get('enabled', True),
                cache_duration=dc_data.get('cache_duration', 3600)
            )
        
        # Parse output config
        if 'output' in data:
            output_data = data['output']
            config.output = OutputConfig(
                format=output_data.get('format', 'text'),
                color=output_data.get('color', True),
                show_confidence=output_data.get('show_confidence', True)
            )
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Config to dictionary."""
        return {
            'version': self.version,
            'scanning': {
                'mode': self.scanning.mode,
                'max_file_size': self.scanning.max_file_size,
                'follow_symlinks': self.scanning.follow_symlinks
            },
            'rules': {
                'custom_patterns': [
                    {
                        'name': p.name,
                        'pattern': p.pattern,
                        'severity': p.severity,
                        'description': p.description
                    }
                    for p in self.rules.custom_patterns
                ],
                'severity_overrides': self.rules.severity_overrides,
                'whitelist': {
                    'files': self.rules.whitelist.files,
                    'patterns': self.rules.whitelist.patterns
                }
            },
            'secret_detection': {
                'enabled': self.secret_detection.enabled,
                'min_entropy': self.secret_detection.min_entropy,
                'min_length': self.secret_detection.min_length,
                'check_common_passwords': self.secret_detection.check_common_passwords
            },
            'dependency_check': {
                'enabled': self.dependency_check.enabled,
                'cache_duration': self.dependency_check.cache_duration
            },
            'output': {
                'format': self.output.format,
                'color': self.output.color,
                'show_confidence': self.output.show_confidence
            }
        }


class ConfigLoader:
    """Configuration file loader."""
    
    DEFAULT_CONFIG_PATHS = [
        'trustskill.yaml',
        'trustskill.yml',
        'trustskill.json',
        '.trustskill.yaml',
        '.trustskill.yml',
        '.trustskill.json',
    ]
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> Config:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to config file. If None, searches default paths.
            
        Returns:
            Config object
        """
        if config_path is None:
            config_path = cls._find_config_file()
        
        if config_path is None or not Path(config_path).exists():
            # Return default configuration
            return Config()
        
        config_path = Path(config_path)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f) or {}
                elif config_path.suffix == '.json':
                    data = json.load(f)
                else:
                    # Try YAML first, then JSON
                    try:
                        data = yaml.safe_load(f) or {}
                    except yaml.YAMLError:
                        f.seek(0)
                        data = json.load(f)
        except Exception as e:
            from .validator import ConfigValidationError
            raise ConfigValidationError(f"Failed to load config file: {e}")
        
        # Validate configuration
        from .validator import ConfigValidator
        ConfigValidator.validate(data)
        
        return Config.from_dict(data)
    
    @classmethod
    def _find_config_file(cls) -> Optional[str]:
        """Find configuration file in default locations."""
        for path in cls.DEFAULT_CONFIG_PATHS:
            if Path(path).exists():
                return path
        return None
    
    @classmethod
    def save(cls, config: Config, config_path: str) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Config object to save
            config_path: Path to save to
        """
        config_path = Path(config_path)
        data = config.to_dict()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if config_path.suffix in ['.yaml', '.yml']:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            elif config_path.suffix == '.json':
                json.dump(data, f, indent=2)
            else:
                # Default to YAML
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
