#!/usr/bin/env python3
"""
Remove all hardcoded API keys from ATLAS code
"""

import os
import re

# Files to fix
files_to_fix = [
    'agents/scout.py',
    'agents/forge.py',
    'agents/mercury.py',
    'agents/vault.py',
    'atlas_backend.py'
]

def fix_file(filepath):
    """Remove hardcoded keys from a Python file"""
    print(f"Fixing {filepath}...")

    with open(filepath, 'r') as f:
        content = f.read()

    # Pattern to find Supabase URL with hardcoded default
    pattern1 = r"os\.getenv\(\s*'SUPABASE_URL',\s*'https://yozmayslzckaczdfohll\.supabase\.co'\s*\)"
    replacement1 = "os.getenv('SUPABASE_URL')"

    # Pattern to find Supabase key with hardcoded default
    pattern2 = r"os\.getenv\(\s*'SUPABASE_ANON_KEY',\s*'eyJ[^']+'\s*\)"
    replacement2 = "os.getenv('SUPABASE_ANON_KEY')"

    # Replace patterns
    content = re.sub(pattern1, replacement1, content)
    content = re.sub(pattern2, replacement2, content)

    # Add validation after the getenv calls if not already present
    if "if not self.supabase_url or not self.supabase_key:" not in content:
        # Find where to insert validation
        create_client_match = re.search(r"(self\.supabase: Client = create_client\(self\.supabase_url, self\.supabase_key\))", content)
        if create_client_match:
            insert_pos = create_client_match.start()
            validation = """
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")

        """
            content = content[:insert_pos] + validation + content[insert_pos:]

    # Write back
    with open(filepath, 'w') as f:
        f.write(content)

    print(f"  ✅ Fixed {filepath}")

def main():
    """Fix all files"""
    os.chdir('/Users/ashishtaneja/Desktop/Business Opp/ATLAS')

    for filepath in files_to_fix:
        if os.path.exists(filepath):
            fix_file(filepath)
        else:
            print(f"  ⚠️  File not found: {filepath}")

    # Also remove the N8N-CREDENTIAL-SETUP.md file with exposed keys
    if os.path.exists('N8N-CREDENTIAL-SETUP.md'):
        os.remove('N8N-CREDENTIAL-SETUP.md')
        print("  ✅ Removed N8N-CREDENTIAL-SETUP.md with exposed keys")

    print("\n✅ All hardcoded keys removed!")
    print("⚠️  Remember to:")
    print("  1. Set environment variables in config/.env")
    print("  2. Rotate your API keys if they were exposed")
    print("  3. Never commit API keys to git")

if __name__ == "__main__":
    main()