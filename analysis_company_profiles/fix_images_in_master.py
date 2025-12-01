#!/usr/bin/env python3
"""
Fix image references in MASTER_DOCUMENT to display images in PDF
Change from links to actual image embeds
"""

import re
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
master_doc = os.path.join(script_dir, 'reports', 'MASTER_DOCUMENT.md')

print("Fixing image references in MASTER_DOCUMENT.md...")
print("Changing links to embedded images for PDF display\n")

# Read the file
with open(master_doc, 'r', encoding='utf-8') as f:
    content = f.read()

# Count current links
current_links = len(re.findall(r'\[Timeline Chart\]\(\.\.\/visualizations\/', content))
print(f"Found {current_links} visualization links")

# Replace visualization links with image embeds
# From: [Timeline Chart](../visualizations/file.png)
# To: ![Timeline Chart](../visualizations/file.png)
content = re.sub(
    r'\*\*Visualization\*\*: \[Timeline Chart\]\((\.\.\/visualizations\/[^)]+)\)',
    r'**Visualization**:\n\n![Timeline Chart](\1)',
    content
)

# Also add width specification for better PDF formatting
content = re.sub(
    r'!\[Timeline Chart\]\((\.\.\/visualizations\/[^)]+)\)',
    r'![Timeline Chart](\1){ width=100% }',
    content
)

# Count new images
new_images = len(re.findall(r'!\[Timeline Chart\]', content))
print(f"Converted to {new_images} embedded images")

# Write back
with open(master_doc, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✓ Updated {master_doc}")
print("\nImages will now display in PDF when converted!")
print("\nTo regenerate PDF:")
print("1. Open MASTER_DOCUMENT.md in VS Code")
print("2. Right-click → Markdown PDF: Export (pdf)")
print("3. Charts will now be embedded in the PDF")



