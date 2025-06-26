#!/bin/bash

# Tech Flash Report - GitHub Deployment Script
# This script deploys the Tech Flash Report site to GitHub

set -e

echo "🚀 Tech Flash Report - GitHub Deployment"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "config.json" ]; then
    echo "❌ Error: config.json not found. Make sure you're in the techflashreport directory."
    exit 1
fi

# Check if this is the Tech Flash Report
if ! grep -q "Tech Flash Report" config.json 2>/dev/null; then
    echo "❌ Error: This doesn't appear to be the Tech Flash Report directory."
    exit 1
fi

echo "✅ Directory validated - Tech Flash Report"

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    git remote add origin https://github.com/The-Flash-Report/techflashreport.git
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Add .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs and temp files
*.log
*.tmp
processed_urls.json
processed_urls_backup.json
temp/
tmp/

# Archive files (optional - uncomment if you don't want to commit archives)
# archive/
# topic_archives/
EOF
    echo "✅ .gitignore created"
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    # Get current timestamp
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    
    # Commit changes
    echo "📝 Committing changes..."
    git commit -m "Deploy Tech Flash Report - $TIMESTAMP

- Violet theme (#8B5CF6)
- Startup ecosystem and tech industry focus
- 8 topic pages with AI template structure
- Flash summary integration
- SEO optimization"

    echo "✅ Changes committed"
fi

# Set main branch and push
echo "🚀 Pushing to GitHub..."
git branch -M main

# Push to GitHub
if git push -u origin main; then
    echo ""
    echo "🎉 Tech Flash Report deployed successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Go to https://github.com/The-Flash-Report/techflashreport"
    echo "2. Set up Netlify deployment:"
    echo "   - Build command: (leave empty for static site)"
    echo "   - Publish directory: /"
    echo "   - Domain: techflashreport.com"
    echo "3. Configure environment variables in GitHub:"
    echo "   - PERPLEXITY_API_KEY"
    echo "   - NEWS_API_KEY"
    echo "4. Test the deployed site"
    echo ""
    echo "🔗 Repository: https://github.com/The-Flash-Report/techflashreport"
    echo "🌐 Target domain: https://techflashreport.com"
else
    echo "❌ Deployment failed. Please check your GitHub credentials and repository access."
    exit 1
fi 