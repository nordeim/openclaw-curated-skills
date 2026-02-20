# UV Priority for Claude Code

A Claude Code skill that prioritizes [uv](https://github.com/astral-sh/uv) over `pip` for all Python package management and execution commands.

## What is UV?

`uv` is an extremely fast Python package installer and resolver, written in Rust. It's a drop-in replacement for `pip`, `pip-tools`, `virtualenv`, and more, providing:

- 10-100x faster than `pip`
- Better dependency resolution
- Consistent behavior across platforms
- Modern Python project management

## What This Skill Does

When activated, this skill instructs Claude Code to always prefer `uv` commands over traditional `pip`:

| Traditional | UV Priority |
|-------------|-------------|
| `pip install package` | `uv add package` |
| `python -m venv .venv` | `uv venv` |
| `python script.py` | `uv run script.py` |
| `pytest` | `uv run pytest` |
| `pip list` | `uv pip list` |

## Installation in Claude Code

1. Clone this repository:
   ```bash
   git clone https://github.com/marcoracer/uv-priority.git
   ```

2. Copy the skill files to your Claude Code skills directory.

## Requirements

- [uv](https://astral.sh/uv) installed on your system

## Install UV

### Linux/macOS:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows (PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## License

MIT

## Credits

Created by [marcoracer](https://github.com/marcoracer)
