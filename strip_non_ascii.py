"""Strip ALL non-ASCII characters from all frontend files."""
import glob

def clean_text(text):
    """Remove all non-ASCII characters."""
    # Keep only ASCII printable + newlines/tabs
    return ''.join(c for c in text if ord(c) < 128 or c in '\n\r\t')

files = (
    glob.glob('/app/frontend/**/*.html', recursive=True) +
    glob.glob('/app/frontend/**/*.js', recursive=True) +
    glob.glob('/app/frontend/**/*.css', recursive=True)
)

for path in files:
    try:
        with open(path, 'rb') as f:
            raw = f.read()
        # Try UTF-8 first
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            text = raw.decode('latin-1')
        
        original = text
        cleaned = clean_text(text)
        
        if cleaned != original:
            with open(path, 'w', encoding='ascii', errors='ignore') as f:
                f.write(cleaned)
            print('Cleaned:', path)
    except Exception as e:
        print('Error:', path, str(e))

print('\nAll files cleaned of non-ASCII characters')
