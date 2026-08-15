import re
import sys

def increase_fonts(filename):
    with open(filename, 'r') as f:
        content = f.read()

    # 1. Update font families
    content = content.replace('Inter:wght', 'Roboto+Condensed:wght')
    content = content.replace('font-family: Inter', "font-family: 'Roboto Condensed'")
    content = content.replace('10px Inter', "12px 'Roboto Condensed'")

    # 2. Increase px sizes in font-size and font
    def replace_px(match):
        prefix = match.group(1)
        size = int(match.group(2))
        unit = match.group(3)
        # Increase by 25% + 2px
        new_size = int(size * 1.25) + 2
        return f"{prefix}{new_size}{unit}"

    content = re.sub(r'(font-size:\s*|font:\s*\d+\s+)(\d+)(px)', replace_px, content)

    # 3. Increase px in clamp
    def replace_clamp(match):
        prefix = match.group(1)
        min_size = int(match.group(2))
        vw = match.group(3)
        max_size = int(match.group(4))
        
        new_min = int(min_size * 1.25) + 2
        new_max = int(max_size * 1.25) + 2
        
        return f"clamp({new_min}px, {vw}, {new_max}px)"
    
    content = re.sub(r'(clamp\()(\d+)px,\s*([^,]+),\s*(\d+)px\)', replace_clamp, content)

    with open(filename, 'w') as f:
        f.write(content)

increase_fonts(sys.argv[1])
