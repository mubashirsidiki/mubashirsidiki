#!/usr/bin/env python3
"""
Script to update year progress bar in README.md
"""
from datetime import datetime, timezone
import os
import math

def calculate_year_progress():
    """Calculate the percentage of year completed"""
    now = datetime.now(timezone.utc)
    year_start = datetime(now.year, 1, 1, tzinfo=timezone.utc)
    year_end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
    
    year_duration = (year_end - year_start).total_seconds()
    elapsed = (now - year_start).total_seconds()
    
    percentage = (elapsed / year_duration) * 100
    return percentage, now

def generate_progress_bar(percentage, total_blocks=30):
    """Generate a visual progress bar"""
    filled_blocks = math.floor((percentage / 100) * total_blocks)
    empty_blocks = total_blocks - filled_blocks
    
    # Using block characters
    filled = '█' * filled_blocks
    empty = '▁' * empty_blocks
    
    return f"{{ {filled}{empty} }}"

def update_readme(percentage, progress_bar, timestamp):
    """Update the README.md file with new progress"""
    readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Format the date
    date_str = timestamp.strftime('%d-%b-%Y')
    
    # Create the new progress section with beautiful formatting
    new_section = f"""<div align="center">
  
### ⏳ Year Progress

```text
{progress_bar}
```

**{percentage:.2f}%** completed • 🗓️ {date_str}

</div>"""
    
    # Find and replace the year progress section using regex
    import re
    pattern = r'<div align="center">\s*\n\s*\n### ⏳ Year Progress\s*\n\s*\n```text\s*\n.*?\n```\s*\n\s*\n\*\*.*?\*\* completed • 🗓️ .*?\s*\n\s*\n</div>'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, new_section, content, flags=re.DOTALL)
    else:
        # Fallback: try old format
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '**Year Progress:**' in line or '### ⏳ Year Progress' in line:
                # Find the section boundaries
                start_idx = i
                # Go back to find the opening div or line before
                while start_idx > 0 and lines[start_idx-1].strip() not in ['---', '']:
                    start_idx -= 1
                
                # Find end of section
                end_idx = i
                while end_idx < len(lines) - 1 and lines[end_idx+1].strip() not in ['---', '']:
                    end_idx += 1
                
                # Replace the section
                lines[start_idx:end_idx+1] = [new_section]
                content = '\n'.join(lines)
                break
    
    # Write back to file
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated README with {percentage:.2f}% year progress")
    print(f"📊 Progress bar: {progress_bar}")
    print(f"📅 Date: {date_str}")

if __name__ == "__main__":
    percentage, timestamp = calculate_year_progress()
    progress_bar = generate_progress_bar(percentage)
    update_readme(percentage, progress_bar, timestamp)
