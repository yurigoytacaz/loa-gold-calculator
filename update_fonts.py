import re

def update_css_fonts(filename):
    with open(filename, 'r') as f:
        content = f.read()

    def replace_size(match):
        size = int(match.group(2))
        unit = match.group(3)
        if size <= 11:
            size += 2
        elif size == 12:
            size += 1
        elif size == 13:
            size += 1
        return f"{match.group(1)}{size}{unit}"

    # Match `font-size: XXpx` or `font: 400 XXpx`
    # group 1: everything before the number, including a space or colon
    # group 2: the number itself
    # group 3: the unit (px, em, etc - mostly px)
    content = re.sub(r'(font-size:\s*|font:\s*\d+\s+)(\d+)(px)', replace_size, content)
    
    with open(filename, 'w') as f:
        f.write(content)

update_css_fonts('/mnt/c/Users/Yuri/Documents/loa-gold-calculator/src/app.css')
update_css_fonts('/mnt/c/Users/Yuri/Documents/loa-gold-calculator/src/columns.css')
