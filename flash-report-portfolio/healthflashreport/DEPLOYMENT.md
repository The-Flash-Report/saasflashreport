# Health Flash Report - Deployment Guide 🧬

## Overview
This guide covers deploying the Health Flash Report site to GitHub and setting up automated content updates.

**Site Details:**
- **Theme**: Emerald (#10B981)
- **Focus**: Longevity research, biohacking studies, health tech
- **Domain**: healthflashreport.com
- **Repository**: https://github.com/The-Flash-Report/healthflashreport

## Quick Deployment

### Option 1: Automated Script (Recommended)
```bash
# Make sure you're in the healthflashreport directory
cd healthflashreport

# Make the script executable and run it
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual Deployment
```bash
# Initialize git repository
git init
git remote add origin https://github.com/The-Flash-Report/healthflashreport.git

# Add all files
git add .

# Commit changes
git commit -m "Initial deployment: Health Flash Report

- Emerald theme (#10B981)
- Longevity and biohacking focus  
- 8 topic pages with AI template structure
- Flash summary integration
- SEO optimization"

# Push to GitHub
git branch -M main
git push -u origin main
```

## Repository Setup

### 1. GitHub Repository
- **Organization**: The-Flash-Report
- **Repository Name**: healthflashreport
- **URL**: https://github.com/The-Flash-Report/healthflashreport
- **Visibility**: Public

### 2. Environment Variables
Set these secrets in the GitHub repository settings:

**Required:**
- `PERPLEXITY_API_KEY` - For AI flash summaries
- `NEWS_API_KEY` - For news content aggregation

**Optional:**
- `REDDIT_CLIENT_ID` - For Reddit content sources
- `REDDIT_CLIENT_SECRET` - For Reddit authentication

### 3. Branch Protection
- **Main branch**: Protected
- **Require pull request reviews**: Disabled (for automation)
- **Dismiss stale reviews**: Enabled
- **Require status checks**: Enabled

## Automated Daily Updates

### GitHub Actions Workflow
The site includes a GitHub Actions workflow (`.github/workflows/daily-update.yml`) that:

- **Runs daily at 6 AM UTC** (1 AM EST, 10 PM PST)
- **Can be triggered manually** via GitHub Actions tab
- **Pulls latest content** from health news sources
- **Generates AI flash summaries** using Perplexity
- **Commits and pushes updates** automatically

### Workflow Features
- ✅ **Health-specific content aggregation**
- ✅ **Longevity research updates**  
- ✅ **Biohacking studies integration**
- ✅ **Flash summary generation**
- ✅ **SEO optimization**
- ✅ **Error handling and retry logic**
- ✅ **Deployment notifications**

## Netlify Deployment

### 1. Connect Repository
1. Go to [Netlify](https://netlify.com)
2. Click "Add new site" → "Import from Git"
3. Select GitHub and choose `The-Flash-Report/healthflashreport`
4. Configure build settings (see below)

### 2. Build Settings
```yaml
# Netlify build configuration
Build command: (leave empty - static site)
Publish directory: /
Branch to deploy: main
```

### 3. Domain Configuration
- **Custom domain**: healthflashreport.com
- **SSL/HTTPS**: Enabled (automatic)
- **Deploy previews**: Enabled for pull requests

### 4. Environment Variables (Netlify)
Add the same environment variables as GitHub:
- `PERPLEXITY_API_KEY`
- `NEWS_API_KEY`
- `REDDIT_CLIENT_ID` (optional)
- `REDDIT_CLIENT_SECRET` (optional)

## Site Structure

### Pages
```
healthflashreport/
├── index.html                 # Main page with flash summary
├── about.html                 # About Health Flash Report
├── contact.html               # Contact form
├── longevity-research.html    # Topic page
├── biohacking-studies.html    # Topic page  
├── health-tech.html           # Topic page
├── medical-breakthroughs.html # Topic page
├── nutrition-science.html     # Topic page
├── performance-optimization.html # Topic page
├── health-news-today.html     # Topic page
└── health-breakthrough-news.html # Topic page
```

### Configuration Files
- `config.json` - Site configuration (theme, branding)
- `keyword_config.json` - Content source keywords
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules

## Content Sources

### Health News APIs
- **PubMed/NIH** - Medical research
- **Health Tech News** - Industry developments
- **Longevity Research** - Anti-aging studies
- **Biohacking Blogs** - Performance optimization

### RSS Feeds
- Harvard Health Blog
- Mayo Clinic News
- Dave Asprey Blog
- Rhonda Patrick FoundMyFitness
- Life Extension Foundation

### Keywords
- longevity, biohacking, health tech
- medical breakthrough, precision medicine
- wearable health, nutrition research
- anti-aging, wellness technology

## Monitoring & Maintenance

### 1. Content Quality
- **Daily review** of flash summaries
- **Source validation** for health claims
- **Fact-checking** medical information

### 2. Performance Monitoring
- **Site speed** via Netlify analytics
- **Uptime monitoring** via external service
- **SEO performance** via Google Search Console

### 3. Regular Updates
- **Monthly dependency updates**
- **Quarterly content source review**
- **Annual design refresh**

## Troubleshooting

### Common Issues

**1. Deployment Failed**
```bash
# Check repository access
git remote -v

# Verify credentials
git config --list

# Re-run deployment
./deploy.sh
```

**2. GitHub Actions Not Running**
- Check environment variables are set
- Verify workflow file syntax
- Check repository permissions

**3. Content Not Updating**
- Verify API keys are valid
- Check content source availability
- Review workflow logs

### Getting Help
- **Repository Issues**: https://github.com/The-Flash-Report/healthflashreport/issues
- **Documentation**: This file
- **Contact**: health@flashreport.network

## Next Steps After Deployment

1. ✅ **Verify deployment**: Check https://healthflashreport.com loads correctly
2. ✅ **Test automation**: Trigger manual workflow run
3. ✅ **Configure analytics**: Set up Plausible or Google Analytics  
4. ✅ **SEO setup**: Submit sitemap to Google Search Console
5. ✅ **Content review**: Verify all 8 topic pages load properly
6. ✅ **Flash summary test**: Confirm AI summaries are generating

---

**🎉 Health Flash Report Deployment Complete!**

Your longevity and biohacking news site is now live and updating automatically with the latest health intelligence. 