#!/usr/bin/env python3
"""
Test Runner for Orange TrustSkill v2.0

Usage:
    $ source /opt/venv/bin/activate
    $ python tests/run_tests.py              # Run all tests
    $ python tests/run_tests.py unit         # Run unit tests only
    $ python tests/run_tests.py integration  # Run integration tests only
    $ python tests/run_tests.py coverage     # Run with coverage report
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode


def main():
    """Main test runner."""
    args = sys.argv[1:]
    
    if not args or args[0] == 'all':
        # Run all tests
        return run_command(
            ['python', '-m', 'pytest', 'tests/', '-v'],
            "All Tests"
        )
    
    elif args[0] == 'unit':
        # Run unit tests only
        return run_command(
            ['python', '-m', 'pytest', 'tests/unit/', '-v', '-m', 'unit'],
            "Unit Tests"
        )
    
    elif args[0] == 'integration':
        # Run integration tests only
        return run_command(
            ['python', '-m', 'pytest', 'tests/integration/', '-v', '-m', 'integration'],
            "Integration Tests"
        )
    
    elif args[0] == 'coverage':
        # Run with coverage
        return run_command(
            [
                'python', '-m', 'pytest', 'tests/',
                '-v', '--cov=src', '--cov-report=term-missing',
                '--cov-report=html:htmlcov'
            ],
            "All Tests with Coverage"
        )
    
    elif args[0] == 'fast':
        # Run fast tests only (no slow tests)
        return run_command(
            ['python', '-m', 'pytest', 'tests/', '-v', '-m', 'not slow'],
            "Fast Tests (excluding slow)"
        )
    
    elif args[0] == 'help':
        print(__doc__)
        return 0
    
    else:
        print(f"Unknown command: {args[0]}")
        print(__doc__)
        return 1


if __name__ == '__main__':
    sys.exit(main())
