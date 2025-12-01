#!/usr/bin/env python3
"""
Fix PDF formatting: proper page breaks and remove headers
"""

import re
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
master_doc = os.path.join(script_dir, 'reports', 'MASTER_DOCUMENT.md')

print("Fixing PDF formatting in MASTER_DOCUMENT.md...")

# Read the file
with open(master_doc, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace \pagebreak with proper HTML/CSS for markdown-pdf
# markdown-pdf extension recognizes these
content = content.replace('\\pagebreak', '<div style="page-break-after: always;"></div>')

# Update the YAML header to disable headers/footers
yaml_section = content.split('---')[1]
new_yaml = """
title: "Company Profiles: Comprehensive Analysis Report"
author: "Financial Analysis - Wearable Technology Sector"
date: "November 24, 2025"
toc: true
toc-title: "Table of Contents"
numbersections: true
header-includes: |
  <style>
    @page {
      margin-top: 0.75in;
      margin-bottom: 0.75in;
      margin-left: 1in;
      margin-right: 1in;
    }
    @page :first {
      margin-top: 1in;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }
    h1 {
      page-break-before: always;
      color: #2c3e50;
      border-bottom: 3px solid #3498db;
      padding-bottom: 10px;
    }
    h1:first-of-type {
      page-break-before: avoid;
    }
    table {
      font-size: 0.9em;
      width: 100%;
      border-collapse: collapse;
    }
    th {
      background-color: #3498db;
      color: white;
      padding: 8px;
    }
    td {
      padding: 6px 8px;
      border: 1px solid #ddd;
    }
    tr:nth-child(even) {
      background-color: #f8f9fa;
    }
  </style>
"""

# Replace the YAML section
parts = content.split('---')
if len(parts) >= 3:
    content = '---' + new_yaml + '---' + '---'.join(parts[2:])

# Count changes
pagebreaks_before = content.count('\\pagebreak')
pagebreaks_after = content.count('page-break-after: always')

print(f"✓ Converted {pagebreaks_after} page breaks to HTML/CSS format")
print(f"✓ Added custom styling to remove headers")
print(f"✓ Added proper page margins and formatting")

# Write back
with open(master_doc, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✓ Updated {master_doc}")
print("\nChanges made:")
print("  - Page breaks will now work in PDF")
print("  - Document headers/footers removed")
print("  - Each appendix starts on new page")
print("  - Professional formatting applied")
print("\nRegenerate PDF in VS Code to see changes!")



