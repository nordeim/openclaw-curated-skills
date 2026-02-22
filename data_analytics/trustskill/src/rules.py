"""
Scanning Rules and Configurations
"""

from typing import List, Tuple, Dict, Any

# High Risk Patterns - Malicious Code Detection
HIGH_RISK_PATTERNS = {
    "command_injection": [
        (r"eval\s*\(", "eval() execution"),
        (r"exec\s*\([^)]*[\+\%\$\{\}]", "exec() with variable"),
        (r"os\.system\s*\([^)]*[\+\%\$\{\}]", "os.system with variable"),
        (
            r"subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True",
            "subprocess with shell=True",
        ),
        (r"compile\s*\([^)]*[\+\%\$\{\}]", "compile() with variable"),
    ],
    "data_upload": [
        (r"requests\.(post|put)\s*\([^)]*http", "HTTP POST/PUT to external server"),
        (r"http\.client.*(?:POST|PUT)", "HTTP client upload"),
        (r"socket\.(socket|connect).*send", "Socket data transmission"),
    ],
    "data_exfiltration": [
        (
            r"requests\.(post|put)\s*\([^)]*(?:password|token|secret|key|credential)",
            "Sensitive data upload",
        ),
    ],
    "file_deletion": [
        (r"shutil\.rmtree\s*\([^)]*[\/\*]", "Recursive directory deletion"),
        (r"os\.remove\s*\([^)]*\*", "Wildcard file deletion"),
        (r"rm\s+-rf", "rm -rf command"),
        (r"os\.unlink\s*\([^)]*\*", "Wildcard file unlink"),
    ],
    "credential_access": [
        (r"open\s*\([^)]*\.ssh[/\\]", "SSH key access"),
        (r"open\s*\([^)]*password", "Password file access"),
        (r"open\s*\([^)]*token", "Token file access"),
        (r"open\s*\([^)]*secret", "Secret file access"),
        (r"open\s*\([^)]*api[_-]?key", "API key file access"),
    ],
    "sensitive_file_access": [
        (r"\.openclaw[/\\]config\.json", "OpenClaw config access"),
        (r"MEMORY\.md|SOUL\.md|USER\.md|AGENTS\.md|TOOLS\.md", "Memory file access"),
        (r"\.bashrc|\.zshrc|\.profile|\.bash_profile", "Shell config access"),
        (r"~/.ssh/", "SSH directory access"),
    ],
}

# Medium Risk Patterns - Manual Review Recommended
MEDIUM_RISK_PATTERNS = {
    "network_request": [
        (r"requests\.(get|post|put|delete)", "HTTP request"),
        (r"urllib", "urllib usage"),
        (r"httpx", "httpx usage"),
        (r"aiohttp", "aiohttp usage"),
    ],
    "data_download": [
        (r"urllib\.request\.urlretrieve", "File download via urllib"),
        (r"requests\.get\s*\([^)]*stream\s*=\s*True", "Streaming download"),
        (r"wget\s+", "wget download command"),
        (r"curl\s+-[Oo]", "curl download"),
    ],
    "file_access_outside_workspace": [
        (r'open\s*\([^)]*[\'"]\s*/etc/', "System file access (/etc)"),
        (r'open\s*\([^)]*[\'"]\s*/sys/', "System file access (/sys)"),
        (r'expanduser\s*\(\s*[\'"]~[\'"]', "Home directory access"),
        (r"Path\.home\(\)", "Home directory access"),
    ],
    "obfuscation": [
        (r"base64\.(b64decode|decode)", "Base64 decoding"),
        (r"codecs\.decode", "Codec decoding"),
        (r"\.decode\s*\([^)]*rot13", "ROT13 decoding"),
        (r"zlib\.(decompress|compress)", "zlib compression"),
        (r"gzip\.", "gzip compression"),
    ],
    "dynamic_import": [
        (r"__import__\s*\(", "Dynamic import"),
        (r"importlib\.(import_module|__import__)", "Dynamic import"),
        (r"exec\s*\(", "exec() call"),
        (r"compile\s*\(", "compile() call"),
    ],
    "api_key_usage": [
        (r"api[_-]?key\s*=", "API key assignment"),
        (r"gemini|openai|anthropic|claude", "AI service API"),
        (r"api[_-]?secret", "API secret usage"),
        (r"auth[_-]?token", "Auth token usage"),
    ],
    "environment_access": [
        (r"os\.environ", "Environment variable access"),
        (r"os\.getenv", "getenv call"),
        (r"dotenv", "dotenv usage"),
    ],
}

# Low Risk Patterns - Informational
LOW_RISK_PATTERNS = {
    "shell_command": [
        (r"os\.system\s*\(", "os.system call"),
        (r"subprocess\.", "Subprocess usage"),
        (r"os\.popen", "os.popen call"),
    ],
    "file_operation": [
        (r"open\s*\(", "File open"),
        (r"os\.path\.", "Path manipulation"),
        (r"pathlib", "Pathlib usage"),
        (r"shutil\.", "shutil usage"),
    ],
    "json_parsing": [
        (r"json\.loads", "JSON parsing"),
        (r"json\.load", "JSON file loading"),
    ],
    "yaml_parsing": [
        (r"yaml\.", "YAML parsing"),
        (r"pyyaml", "PyYAML usage"),
    ],
}

# Suspicious URL/IP Patterns
SUSPICIOUS_PATTERNS = [
    (r"http://[^/\s]*\d+\.\d+\.\d+\.\d+", "Direct IP access (HTTP)"),
    (r"https?://[^/\s]*pastebin", "Pastebin URL"),
    (r"https?://[^/\s]*githubusercontent", "Raw GitHub content"),
    (r"https?://[^/\s]*ngrok", "Ngrok tunnel"),
    (r"https?://[^/\s]*serveo", "Serveo tunnel"),
    (r"https?://[^/\s]*localhost\.run", "Localtunnel"),
]

# Safe Services Whitelist
SAFE_SERVICES = [
    "api.nvidia.com",
    "integrate.api.nvidia.com",
    "api.openai.com",
    "generativelanguage.googleapis.com",
    "api.anthropic.com",
    "api.xiaohongshu.com",
    "xiaohongshu.com",
    "api.github.com",
    "raw.githubusercontent.com",
    "pypi.org",
    "files.pythonhosted.org",
]

# File Extensions to Scan
SCAN_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".rb",
    ".pl",
    ".php",
    ".go",
    ".rs",
    ".java",
    ".c",
    ".cpp",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
}

# Ignored Files and Directories
IGNORE_PATTERNS = [
    r"\.git",
    r"\.svn",
    r"\.hg",
    r"node_modules",
    r"__pycache__",
    r"\.pytest_cache",
    r"\.venv",
    r"venv",
    r"\.env",
    r"dist",
    r"build",
    r"\.egg-info",
    r"\.tox",
    r"\.coverage",
]

# Default Whitelist Patterns for Known False Positives
# These patterns are safe by design and should not trigger security warnings
DEFAULT_WHITELIST_PATTERNS = [
    # Documentation references to memory/config files in SKILL.md files
    # These are just text mentions, not actual file access
    r'AGENTS\.md["\']?\s*[`\n]',  # AGENTS.md in markdown
    r'MEMORY\.md["\']?\s*[`\n]',  # MEMORY.md in markdown
    r'SOUL\.md["\']?\s*[`\n]',  # SOUL.md in markdown
    r'USER\.md["\']?\s*[`\n]',  # USER.md in markdown
    r'TOOLS\.md["\']?\s*[`\n]',  # TOOLS.md in markdown
    r"Configure in `AGENTS\.md`",  # Configuration documentation
    r"registered slash commands in AGENTS\.md",  # Documentation reference
    # Testing utilities with shell=True (legitimate use cases)
    r"# .*[Tt]esting.*\n.*subprocess.*shell\s*=\s*True",  # Testing context
    r"# .*[Ss]erver.*\n.*subprocess.*shell\s*=\s*True",  # Server management
    r"with_server\.py",  # Server orchestration utilities
    r"test_.*\.py",  # Test files
    r"_test\.py",  # Test files (alternative naming)
    # NPM/PNPM/Yarn integrity hashes - these are SRI hashes, not secrets
    r'"integrity"\s*:\s*"sha(256|384|512)-[A-Za-z0-9+/=]+',
    r"sha(256|384|512)-[A-Za-z0-9+/=]{40,}",
    # Placeholder patterns in documentation
    r"your[_-]?(api[_-]?key|secret|token|password)[_-]?here",
    r"REPLACE[_-]?ME",
    r"xxx+",
    r"sk-[a-zA-Z0-9_]*\.{3}",
    r"<[A-Z_]+>",  # <API_KEY>, <YOUR_TOKEN>, etc.
    r"\$\{[^}]+\}",  # ${VARIABLE} template patterns
    # i18n documentation patterns (Chinese, Japanese, Korean, etc.)
    r"[配置设置示例请将填入你的密钥]+",
]

# Lock files that contain integrity hashes (safe by design)
LOCK_FILES = [
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "composer.lock",
    "poetry.lock",
    "Cargo.lock",
    "Gemfile.lock",
]

# Placeholder patterns that indicate documentation examples, not real secrets
PLACEHOLDER_PATTERNS = [
    r"your[_-]?\w+[_-]?here",
    r"xxx+",
    r"0000+",
    r"12345+",
    r"test[_-]?\w+",
    r"dummy",
    r"sample",
    r"fake",
    r"example",
    r"placeholder",
    r"REPLACE[_-]?ME",
    r"TODO",
    r"<[A-Z_]+>",
    r"\$\{[^}]+\}",
    r"{{[^}]+}}",
    r"sk-\.\.\.",
    r"sk_?\.\.\.",
    r"your_api_key",
    r"your_secret",
    r"your_token",
    r"your_password",
    r"your[_-]?key",
    r"[配填入设置示例密钥你的]+",
]

# Files that are known to be documentation-only
DOCUMENTATION_FILES = [
    "SKILL.md",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "AGENTS.md",
]

# Testing utility files where shell=True is expected
TESTING_UTILITY_FILES = [
    "with_server.py",
    "test_server.py",
    "conftest.py",
    "test_helpers.py",
]
