# Flash Report Portfolio - Master Deployment Guide 🚀

## Overview
This guide covers deploying all 6 Flash Report sites to GitHub and setting up automated content updates. Each site is an independent project with its own repository, domain, and deployment process.

## Portfolio Sites

| Site | Theme | Domain | Repository | Focus |
|------|-------|--------|------------|-------|
| 🧬 Health Flash Report | Emerald (#10B981) | healthflashreport.com | [healthflashreport](https://github.com/The-Flash-Report/healthflashreport) | Longevity, biohacking |
| 🚀 Tech Flash Report | Violet (#8B5CF6) | techflashreport.com | [techflashreport](https://github.com/The-Flash-Report/techflashreport) | Startups, tech industry |
| 💪 Fitness Flash Report | Red (#EF4444) | fitnessflashreport.com | [fitnessflashreport](https://github.com/The-Flash-Report/fitnessflashreport) | Athletic performance |
| ✈️ Travel Flash Report | Sky Blue (#0EA5E9) | travelflashreport.com | [travelflashreport](https://github.com/The-Flash-Report/travelflashreport) | Travel industry |
| 🦄 Startup Flash Report | Pink (#EC4899) | startupflashreport.com | [startupflashreport](https://github.com/The-Flash-Report/startupflashreport) | Entrepreneurship |
| ☁️ SaaS Flash Report | Indigo (#6366F1) | saasflashreport.com | [saasflashreport](https://github.com/The-Flash-Report/saasflashreport) | Cloud software |

## Quick Deploy All Sites

### Option 1: Deploy Individual Sites (Recommended)
```bash
# Health Flash Report
cd healthflashreport && ./deploy.sh && cd ..

# Tech Flash Report
cd techflashreport && ./deploy.sh && cd ..

# Fitness Flash Report
cd fitnessflashreport && ./deploy.sh && cd ..

# Travel Flash Report
cd travelflashreport && ./deploy.sh && cd ..

# Startup Flash Report
cd startupflashreport && ./deploy.sh && cd ..

# SaaS Flash Report
cd saasflashreport && ./deploy.sh && cd ..
```

### Option 2: Deploy Single Site
```bash
# Navigate to specific site directory
cd [site-directory]

# Run deployment script
./deploy.sh
```

## Deployment Files Structure

Each site directory contains:
```
[site-directory]/
├── deploy.sh                          # 🚀 Deployment script
├── .github/workflows/daily-update.yml # ⚙️ GitHub Actions workflow
├── DEPLOYMENT.md                       # 📚 Site-specific guide
├── .gitignore                         # 🚫 Git ignore rules (auto-generated)
├── index.html                         # 🏠 Main page
├── about.html                         # ℹ️ About page
├── contact.html                       # 📞 Contact page
├── [topic-pages].html                 # 📄 Topic pages (8 per site)
├── config.json                        # ⚙️ Site configuration
└── keyword_config.json                # 🔑 Content keywords
```

## GitHub Organization Setup

### Organization Details
- **Name**: The-Flash-Report
- **Repositories**: 6 individual repositories (one per site)
- **Visibility**: Public repositories
- **Environment Variables**: Set at organization level

### Required Environment Variables
These should be set at the **GitHub organization level** (inherited by all repos):

**Required:**
- `PERPLEXITY_API_KEY` - For AI flash summaries
- `NEWS_API_KEY` - For news content aggregation

**Optional:**
- `REDDIT_CLIENT_ID` - For Reddit content sources
- `REDDIT_CLIENT_SECRET` - For Reddit authentication

## Automated Daily Updates

### GitHub Actions Features
Each site includes a GitHub Actions workflow that:

- ✅ **Runs daily at 6 AM UTC**
- ✅ **Manual trigger capability**
- ✅ **Site-specific content aggregation**
- ✅ **AI flash summary generation**
- ✅ **Error handling and retry logic**
- ✅ **Automatic commits and deployment**

### Workflow Schedule
```yaml
# Daily at 6 AM UTC (1 AM EST, 10 PM PST)
schedule:
  - cron: '0 6 * * *'
```

## Netlify Deployment

### Bulk Netlify Setup
For each site:

1. **Connect Repository**
   - Go to [Netlify](https://netlify.com)
   - "Add new site" → "Import from Git"
   - Select GitHub organization: `The-Flash-Report`
   - Choose repository: `[site-repository]`

2. **Build Settings**
   ```yaml
   Build command: (leave empty - static sites)
   Publish directory: /
   Branch to deploy: main
   ```

3. **Domain Configuration**
   - Set custom domain per site (see table above)
   - Enable SSL/HTTPS (automatic)
   - Enable deploy previews

4. **Environment Variables**
   - Copy same variables from GitHub organization
   - `PERPLEXITY_API_KEY`
   - `NEWS_API_KEY`
   - Optional: Reddit credentials

## Site-Specific Content

### Health Flash Report 🧬
- **Topic Pages**: Longevity Research, Biohacking Studies, Health Tech, Medical Breakthroughs, Nutrition Science, Performance Optimization, Health News Today, Health Breakthrough News
- **Content Sources**: PubMed, Harvard Health, Mayo Clinic, Dave Asprey, Rhonda Patrick
- **Keywords**: longevity, biohacking, health tech, medical breakthrough

### Tech Flash Report 🚀
- **Topic Pages**: Startup Funding, Product Launches, Enterprise Software, Developer Tools, Big Tech Moves, IPOs & Acquisitions, Tech News Today, Tech Breakthrough News
- **Content Sources**: TechCrunch, The Information, VentureBeat, Y Combinator
- **Keywords**: startup funding, IPO, acquisition, product launch

### Fitness Flash Report 💪
- **Topic Pages**: Training Science, Gear Releases, Athletic Performance, Nutrition Studies, Recovery Technology, Sports Medicine, Fitness News Today, Fitness Breakthrough News
- **Content Sources**: Precision Nutrition, Stronger by Science, ACSM, TrainingPeaks
- **Keywords**: sports science, exercise research, fitness technology

### Travel Flash Report ✈️
- **Topic Pages**: Airline Updates, Aviation Industry, Destination Trends, Hospitality Innovations, Tourism Insights, Travel Technology, Travel News Today, Travel Breakthrough News
- **Content Sources**: Skift, Travel Weekly, PhocusWire, Airlines for America
- **Keywords**: airline policy, travel restrictions, tourism, travel technology

### Startup Flash Report 🦄
- **Topic Pages**: Funding Rounds, Startup Acquisitions, Innovation Showcase, Market Analysis, Product Launches, Founder Insights, Startup News Today, Startup Breakthrough News
- **Content Sources**: TechCrunch Startups, AngelList, Crunchbase, PitchBook
- **Keywords**: seed funding, Series A, venture capital, founder, unicorn

### SaaS Flash Report ☁️
- **Topic Pages**: Product Launches, Pricing Changes, Acquisitions, Enterprise Deals, Platform Updates, Cloud Infrastructure, Enterprise Software, API Integrations
- **Content Sources**: SaaStr, OpenView, ChartMogul, ProfitWell
- **Keywords**: SaaS funding, software acquisition, enterprise software

## Repository Management

### Branch Protection Rules
For each repository:
- **Main branch**: Protected
- **Require pull request reviews**: Disabled (for automation)
- **Dismiss stale reviews**: Enabled
- **Require status checks**: Enabled
- **Allow force pushes**: Disabled

### Automation Settings
- **Actions permissions**: Allow all actions
- **Workflow permissions**: Read and write permissions
- **Fork pull request workflows**: Disabled

## Monitoring & Maintenance

### Daily Monitoring
- ✅ **Content Updates**: Check GitHub Actions logs
- ✅ **Site Health**: Monitor Netlify deployments
- ✅ **Flash Summaries**: Verify AI content generation
- ✅ **Error Tracking**: Review workflow failures

### Weekly Tasks
- 📊 **Analytics Review**: Check site traffic and engagement
- 🔍 **Content Quality**: Review flash summaries and headlines
- 🔗 **Link Validation**: Test external content links
- 🚀 **Performance Check**: Monitor site speed

### Monthly Tasks
- 📦 **Dependency Updates**: Update Python packages
- 🔐 **Security Review**: Check for vulnerabilities
- 📝 **Content Source Review**: Validate RSS feeds and APIs
- 🎨 **Design Updates**: Minor template improvements

## Troubleshooting

### Common Deployment Issues

**1. Git Authentication Failed**
```bash
# Check Git credentials
git config --list | grep user

# Re-authenticate if needed
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**2. Repository Already Exists**
```bash
# Remove existing remote and re-add
git remote remove origin
git remote add origin https://github.com/The-Flash-Report/[repository].git
```

**3. GitHub Actions Not Running**
- Check environment variables are set at org level
- Verify workflow file syntax (YAML formatting)
- Check repository permissions for Actions

**4. Content Not Updating**
- Verify API keys are valid and not expired
- Check content source availability (RSS feeds, APIs)
- Review GitHub Actions workflow logs for errors

### Getting Help

**Documentation:**
- Individual site guides: `[site-directory]/DEPLOYMENT.md`
- Master guide: This file
- GitHub workflow files: `.github/workflows/daily-update.yml`

**Support Channels:**
- **Repository Issues**: Create issues in specific site repositories
- **General Questions**: Use main organization discussions
- **Technical Support**: Contact development team

## Post-Deployment Checklist

### For Each Site:
- [ ] ✅ **Deployment successful**: Site deploys without errors
- [ ] 🌐 **Domain configured**: Custom domain pointing correctly
- [ ] 🔐 **SSL enabled**: HTTPS working properly
- [ ] ⚙️ **GitHub Actions**: Workflow running successfully
- [ ] 📊 **Analytics setup**: Plausible or Google Analytics configured
- [ ] 🔍 **SEO setup**: Sitemap submitted to Google Search Console
- [ ] 📄 **Content verification**: All 8 topic pages loading correctly
- [ ] 🤖 **Flash summaries**: AI content generating properly
- [ ] 📧 **Contact forms**: Newsletter signup and contact working
- [ ] 🔗 **Navigation**: All internal links functional

### Portfolio-Wide:
- [ ] 🌐 **All 6 sites deployed**: Complete portfolio live
- [ ] 🔄 **Cross-linking**: About pages link to other sites
- [ ] 📊 **Unified analytics**: Tracking across all properties
- [ ] 🤖 **Automation working**: Daily updates on all sites
- [ ] 🎨 **Brand consistency**: All sites match AI template structure
- [ ] 📱 **Mobile responsive**: All sites work on mobile devices

---

## 🎉 Deployment Complete!

Your Flash Report Portfolio is now live with 6 independent news sites covering:
- 🧬 **Health & Longevity**
- 🚀 **Tech & Startups** 
- 💪 **Fitness & Performance**
- ✈️ **Travel & Tourism**
- 🦄 **Entrepreneurship**
- ☁️ **SaaS & Cloud Software**

Each site automatically updates daily with fresh content and AI-generated flash summaries, providing comprehensive intelligence across these high-value verticals.

**Total Sites**: 6 deployed + 2 existing live (AI + Crypto) = **8 Flash Report Sites** 