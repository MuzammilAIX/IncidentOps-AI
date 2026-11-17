"""Register assistant app in settings + urls."""
# 1. Add to INSTALLED_APPS
path = '/app/config/settings/base.py'
content = open(path).read()
if 'apps.assistant' not in content:
    # Find any apps.X entry and add after it
    import re
    m = re.search(r'("apps\.\w+",)', content)
    if m:
        content = content.replace(m.group(1), m.group(1) + '\n    "apps.assistant",', 1)
        open(path, 'w').write(content)
        print('Added apps.assistant to INSTALLED_APPS')
    else:
        print('ERROR: Could not find apps to insert after')
else:
    print('Already registered')

# 2. Add URL route
path = '/app/config/urls.py'
content = open(path).read()
if 'api/assistant/' not in content:
    old = 'path("api/auth/", include("apps.accounts.urls")),'
    new = 'path("api/auth/", include("apps.accounts.urls")),\n    path("api/assistant/", include("apps.assistant.urls")),'
    content = content.replace(old, new, 1)
    open(path, 'w').write(content)
    print('Added /api/assistant/ route')
else:
    print('Already has route')
