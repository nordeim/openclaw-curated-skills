#!/usr/bin/env python3
"""
Orange TrustSkill v2.0 - Backward Compatibility Wrapper
Provides a v1.x compatible interface for the Python entry point.
"""

import sys
import os

# Get the script and source directories
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(script_dir), 'src')

# Add source directory to sys.path
sys.path.insert(0, src_dir)
sys.path.insert(0, os.path.dirname(src_dir))

# Import the v2 CLI entry point
from src.cli import main

if __name__ == '__main__':
    main()
