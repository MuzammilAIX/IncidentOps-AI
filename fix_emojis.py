"""Replace all emojis with ASCII equivalents across all frontend files."""
import glob
import re

# Emoji → ASCII replacement map
replacements = {
    '🚨': '[!]',
    '📊': '[#]',
    '📖': '[R]',
    '✅': '[OK]',
    '💬': '[?]',
    '🔗': '[>]',
    '🔍': '[S]',
    '🧪': '[T]',
    '🔄': '[R]',
    '👍': '+1',
    '👎': '-1',
    '🤔': '?',
    '❌': '[X]',
    '⚠️': '[!]',
    '▸': '>',
    '←': '<',
    '→': '->',
    '▸': '>',
    '▶': '>>',
    '·': '-',
    '’': "'",
    '“': '"',
    '”': '"',
    '…': '...',
    '—': '-',
    '–': '-',
}

files = glob.glob('/app/frontend/**/*.html', recursive=True) + glob.glob('/app/frontend/**/*.js', recursive=True)
for path in files:
    try:
        content = open(path, encoding='utf-8').read()
    except Exception:
        continue
    original = content
    for emoji, ascii_rep in replacements.items():
        content = content.replace(emoji, ascii_rep)
    if content != original:
        open(path, 'w', encoding='utf-8').write(content)
        print('Fixed:', path)

print('\\nAll emojis replaced with ASCII')
