"""
Orange TrustSkill v2.0 - Test Suite
====================================

Test-Driven Development (TDD) Test Suite for the Security Scanner.

Test Organization:
- unit/: Unit tests for individual modules
- integration/: Integration tests for end-to-end workflows
- fixtures/: Test data and sample files

Running Tests:
    $ source /opt/venv/bin/activate
    $ pytest tests/ -v
    $ pytest tests/ --cov=src --cov-report=html
"""

import sys
from pathlib import Path

# Add src to path for all tests
TEST_DIR = Path(__file__).parent
PROJECT_DIR = TEST_DIR.parent
SRC_DIR = PROJECT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(PROJECT_DIR))
