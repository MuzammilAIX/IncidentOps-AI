"""Fix feedback method indentation in views.py."""
path = '/app/apps/investigations/views.py'
content = open(path).read()

old = '@action(detail=True, methods=["post", "get"], url_path="feedback", permission_classes=[permissions.IsAuthenticated])\n    def feedback'
new = '    @action(detail=True, methods=["post", "get"], url_path="feedback", permission_classes=[permissions.IsAuthenticated])\n    def feedback'

if old in content:
    content = content.replace(old, new, 1)
    open(path, 'w').write(content)
    print('Fixed indentation')
else:
    print('Pattern not found')
    idx = content.find('url_path="feedback"')
    if idx >= 0:
        print(repr(content[idx-30:idx+100]))

import py_compile
try:
    py_compile.compile(path, doraise=True)
    print('Syntax: OK')
except py_compile.PyCompileError as e:
    print('Syntax ERROR:', e)
