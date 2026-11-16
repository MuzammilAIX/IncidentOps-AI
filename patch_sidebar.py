"""Add Runbooks sidebar link to all HTML files."""
import glob
import re

files = glob.glob('/app/frontend/*.html')
for path in files:
    if path.endswith('login.html') or path.endswith('runbooks.html'):
        print(f'SKIP: {path}')
        continue
    
    content = open(path).read()
    if 'href="/runbooks/"' in content:
        print(f'OK: {path}')
        continue
    
    # Find the incidents nav item, insert runbooks after it
    # Pattern: <a href="/incidents/" class="nav-item...>...</a>
    pattern = r'(<a href="/incidents/"[^>]*>.*?</a>)'
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        incidents_link = match.group(1)
        runbooks_link = '''
        <a href="/runbooks/" class="nav-item">
          <span class="nav-item-icon">📖</span>
          <span>Runbooks</span>
        </a>'''
        new_content = content.replace(incidents_link, incidents_link + runbooks_link, 1)
        open(path, 'w').write(new_content)
        print(f'FIXED: {path}')
    else:
        print(f'NO MATCH: {path}')
