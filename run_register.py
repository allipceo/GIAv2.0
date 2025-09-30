#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Set environment variables and run the Notion registration script.
"""
import os
import subprocess
import sys

# Set environment variables
os.environ['NOTION_TOKEN'] = ''
os.environ['TARGET_DATABASE_ID'] = '5d15b3aa0f174b04bceeb22107e06a03'
os.environ['PYTHONPATH'] = '.'

# Run the registration script
try:
    result = subprocess.run([
        sys.executable, 'scripts/a2g2n_register_from_temp.py', 
        '--folder', 'temp_drive'
    ], capture_output=True, text=True, encoding='cp949', errors='ignore')
    
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
    
except Exception as e:
    print(f"Error: {e}")
