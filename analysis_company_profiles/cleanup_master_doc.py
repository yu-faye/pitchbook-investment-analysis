#!/usr/bin/env python3
"""
Clean up MASTER_DOCUMENT:
1. Remove all "Data extracted" dates
2. Fix page breaks to avoid empty pages
"""

import re
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
master_doc = os.path.join(script_dir, 'reports', 'MASTER_DOCUMENT.md')

print("Cleaning up MASTER_DOCUMENT.md...")

# Read the file
with open(master_doc, 'r', encoding='utf-8') as f:
    content = f.read()

# Count dates before removal
dates_before = len(re.findall(r'\*Data extracted:.*?\*', content))
print(f"Found {dates_before} 'Data extracted' lines")

# Remove all "Data extracted" lines
content = re.sub(r'\n\*Data extracted:.*?\*\n', '\n', content)

# Remove lines with just "---" followed by page break
# This creates empty pages
content = re.sub(r'\n---\n+<div style="page-break-after: always;"></div>\n+', '\n\n<div style="page-break-after: always;"></div>\n\n', content)

# Remove multiple consecutive blank lines (max 2)
content = re.sub(r'\n{4,}', '\n\n\n', content)

# Remove page breaks that come right after another page break
content = re.sub(r'(<div style="page-break-after: always;"></div>\s*){2,}', r'<div style="page-break-after: always;"></div>\n\n', content)

# Remove trailing whitespace on each line
lines = content.split('\n')
lines = [line.rstrip() for line in lines]
content = '\n'.join(lines)

# Count changes
dates_after = len(re.findall(r'\*Data extracted:.*?\*', content))
print(f"Removed {dates_before - dates_after} date lines")
print(f"✓ Cleaned up spacing and page breaks")

# Write back
with open(master_doc, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✓ Updated {master_doc}")
print("\nChanges made:")
print("  - Removed all 'Data extracted' dates")
print("  - Fixed page breaks to avoid empty pages")
print("  - Cleaned up excessive blank lines")
print("  - Removed trailing whitespace")
print("\nRegenerate PDF to see cleaner output!")



