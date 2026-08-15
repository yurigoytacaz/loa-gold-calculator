import re

def update_css_spacing(filename):
    with open(filename, 'r') as f:
        content = f.read()

    # app.css changes
    content = content.replace('height: 76px;', 'height: 96px;')
    content = content.replace('padding: 28px clamp(27px, 3vw, 62px) 0;', 'padding: 48px clamp(27px, 3vw, 62px) 0;')
    content = content.replace('min-height: 108px;', 'min-height: 140px;')
    content = content.replace('padding: 15px clamp(18px, 3vw, 48px);', 'padding: 24px clamp(24px, 4vw, 56px);')
    content = content.replace('gap: 12px;', 'gap: 20px;')
    content = content.replace('margin-bottom: 28px;', 'margin-bottom: 48px;')
    content = content.replace('margin: 30px 0 13px;', 'margin: 50px 0 24px;')

    # columns.css changes
    content = content.replace('min-height: 104px;', 'min-height: 140px;')
    content = content.replace('padding: 12px;', 'padding: 20px;')
    content = content.replace('gap: 10px;', 'gap: 16px;')
    content = content.replace('margin: 7px 0 0;', 'margin: 12px 0 0;')
    
    content = content.replace('padding: 10px 9px;', 'padding: 18px 16px;')
    content = content.replace('padding: 0 8px 8px;', 'padding: 0 16px 16px;')
    
    content = content.replace('height: 31px;', 'height: 45px;')
    content = content.replace('padding: 0 2px 5px;', 'padding: 0 4px 10px;')
    
    content = content.replace('gap: 5px; padding-top: 5px;', 'gap: 10px; padding-top: 10px;')
    content = content.replace('min-height: 90px;', 'min-height: 110px;')
    content = content.replace('padding: 12px 6px;', 'padding: 16px 8px;')
    
    content = content.replace('min-height: 58px;', 'min-height: 85px;')
    content = content.replace('padding: 9px 11px;', 'padding: 16px 20px;')

    with open(filename, 'w') as f:
        f.write(content)

update_css_spacing('src/app.css')
update_css_spacing('src/columns.css')
