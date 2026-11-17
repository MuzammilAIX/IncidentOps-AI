"""Fix sendSimulatedAlert to include CSRF token."""
import re

path = '/app/frontend/js/dashboard.js'
content = open(path).read()

# Find the sendSimulatedAlert function
old = "headers: { 'Content-Type': 'application/json' },"
new = """headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') || '' },
          credentials: 'include',"""

# Check if credentials already exists
if "credentials: 'include'" in content and "X-CSRFToken" in content:
    print('Already has CSRF + credentials')
else:
    # Add CSRF header + credentials
    content = content.replace(old, new, 1)
    open(path, 'w').write(content)
    print('Fixed: added X-CSRFToken + credentials')
    print('Has CSRF:', 'X-CSRFToken' in content)
    print('Has credentials:', "credentials: 'include'" in content)
