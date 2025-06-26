# Cleanup Commands

# 1. Remove backup files (safe to delete)
find . -name '*.backup' -delete
find . -name '.DS_Store' -delete

# 2. Organize QA files (optional)
mkdir -p QA
mv qa-site-navigator.html QA/ 2>/dev/null || true

# 3. Kill any running servers
pkill -f 'python3 -m http.server' || true

# 4. Git cleanup (commit independent setup)
git add .
git commit -m 'Phase 11: Independent site setup complete'

echo '✅ Cleanup complete - all sites ready for independent development'

