#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix Unicode encoding issues in Python files for Windows cp949 compatibility"""

import os
import re

def fix_file(filepath):
    """Replace unicode emojis with ASCII equivalents"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Replace common unicode characters
        replacements = {
            '✓': '[OK]',
            '⚠️': '[WARN]',
            '❌': '[ERROR]',
            '✅': '[OK]',
            '🔴': '[!]',
            '🟢': '[OK]',
            '🟡': '[?]',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    services_dir = 'ml-service/services'
    fixed_count = 0
    
    for filename in os.listdir(services_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(services_dir, filename)
            if fix_file(filepath):
                fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
