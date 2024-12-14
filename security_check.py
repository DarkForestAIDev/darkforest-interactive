import os
import re
import json
from pathlib import Path

class SecurityChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []

    def add_issue(self, message):
        self.issues.append(message)
        print(f"❌ ISSUE: {message}")

    def add_warning(self, message):
        self.warnings.append(message)
        print(f"⚠️ WARNING: {message}")

    def check_env_files(self):
        print("\n🔍 Checking environment files...")
        
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                content = f.read()
                if re.search(r'sk-[a-zA-Z0-9-]{30,}', content):
                    self.add_issue("API key found in .env file - ensure this file is in .gitignore")

        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as f:
                content = f.read()
                if re.search(r'sk-[a-zA-Z0-9-]{30,}', content):
                    self.add_issue("API key found in .env.example - remove it immediately")

    def check_git_ignore(self):
        print("\n🔍 Checking .gitignore...")
        
        required_entries = ['.env', '__pycache__/', '*.pyc', '.DS_Store', 'Thumbs.db']
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as f:
                content = f.read()
                for entry in required_entries:
                    if entry not in content:
                        self.add_warning(f"Missing {entry} in .gitignore")
        else:
            self.add_issue(".gitignore file not found")

    def check_debug_settings(self):
        print("\n🔍 Checking debug settings...")
        
        if os.path.exists('app.py'):
            with open('app.py', 'r') as f:
                content = f.read()
                if 'debug=True' in content:
                    self.add_issue("Debug mode is enabled in app.py")

    def check_sensitive_files(self):
        print("\n🔍 Checking for sensitive files...")
        
        sensitive_patterns = [
            r'\.log$',
            r'\.sqlite3$',
            r'\.db$',
            r'\.pem$',
            r'\.key$',
            r'\.crt$'
        ]
        
        for pattern in sensitive_patterns:
            for file in Path('.').rglob('*'):
                if re.search(pattern, str(file)):
                    self.add_warning(f"Potentially sensitive file found: {file}")

    def run_all_checks(self):
        print("🔒 Starting security checks...")
        
        self.check_env_files()
        self.check_git_ignore()
        self.check_debug_settings()
        self.check_sensitive_files()
        
        print("\n📊 Security Check Summary:")
        print(f"Found {len(self.issues)} issues and {len(self.warnings)} warnings")
        
        if self.issues:
            print("\n❌ Issues that need immediate attention:")
            for issue in self.issues:
                print(f"- {issue}")
        
        if self.warnings:
            print("\n⚠️ Warnings to review:")
            for warning in self.warnings:
                print(f"- {warning}")
        
        if not self.issues and not self.warnings:
            print("\n✅ All security checks passed!")

if __name__ == "__main__":
    checker = SecurityChecker()
    checker.run_all_checks() 