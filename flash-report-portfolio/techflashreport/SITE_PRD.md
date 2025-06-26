# Tech Flash Report - Site PRD

## Overview
Tech Flash Report is a specialized news aggregation site targeting the technology industry and startup ecosystem. Built on the proven Flash Report architecture, it delivers daily intelligence on startup funding, product launches, enterprise software, and big tech developments.

**Site URL**: techflashreport.com  
**Launch Status**: Foundation Complete, RSS Integration Pending  
**Part of**: Flash Report Network (7-site portfolio)

## Target Users & User Stories

### Primary Audience: Startup Founders & Entrepreneurs
- **As a startup founder**, I want funding news and industry moves so that I can track competition and opportunities
- **As a tech entrepreneur**, I want product launch intelligence so that I can identify market gaps and timing
- **As a startup employee**, I want acquisition news so that I can understand market dynamics and career opportunities

### Secondary Audience: Tech Professionals & Investors
- **As a tech professional**, I want enterprise software developments so that I can stay relevant in my field
- **As an investor**, I want IPO and acquisition news so that I can identify market trends and opportunities
- **As a VC**, I want deal flow intelligence so that I can spot emerging sectors and valuations

### Tertiary Audience: Enterprise Decision-Makers
- **As a CTO**, I want developer tools news so that I can evaluate new technologies for my team
- **As an enterprise buyer**, I want enterprise software updates so that I can make informed purchasing decisions

## Functional Requirements

### Content Requirements
**Tech Content Categories:**
1. **Startup Funding** - Seed, Series A-C, venture capital, valuations, unicorn companies
2. **Product Launches** - New products, features, beta releases, platform launches
3. **Enterprise Software** - B2B tools, SaaS platforms, business applications, integrations
4. **Developer Tools** - APIs, frameworks, programming tools, DevOps, infrastructure
5. **Big Tech Moves** - Strategic partnerships, acquisitions, new initiatives from major companies
6. **IPOs & Acquisitions** - Public offerings, mergers, exit events, market valuations

**Content Sources (25+ Active Feeds):**
- **Startup News**: TechCrunch, VentureBeat, Crunchbase News, PitchBook
- **Enterprise Tech**: ZDNet, InfoWorld, SiliconANGLE, CIO, Computerworld
- **Big Tech**: Google Blog, Microsoft News, Apple Newsroom, Meta Newsroom
- **Investment**: Reuters Technology, Bloomberg Technology, CB Insights

### Flash Summary Requirements
**Custom Tech Prompt Format:**
```
TECH FLASH - [Date]
[Compelling headline about biggest tech story or startup development]

TOP 3 STORIES:
1. [Tech story with market implications for tech professionals]
2. [Startup story with funding and competition insights]
3. [Enterprise story with technology adoption trends]

Flash Insight: [Commentary on tech trends, disruption, and industry impact]
```

**Focus Areas**: Startup funding, product launches, enterprise software, developer tools, big tech moves, IPOs, acquisitions

### Technical Requirements  
- **Independence**: Complete site portability for separate deployment
- **Template Compliance**: Exact AI Flash Report structure with violet branding
- **Flash Summary Component**: Independent component with tech-specific Perplexity prompt
- **Analytics**: Separate Plausible Analytics domain (techflashreport.com)
- **SEO**: Startup funding and tech industry keyword optimization

## Implementation Status

### ✅ Foundation Complete
- [x] Site structure and branding (violet theme, tech focus)
- [x] Template compliance with AI Flash Report structure  
- [x] About and contact pages with tech-specific content
- [x] Topic pages for all 6 tech categories
- [x] Cross-linking to Flash Report Network
- [x] Independent Flash Summary Component
- [x] Custom tech-focused Perplexity prompt
- [x] RSS source documentation (25+ feeds)

### 🚧 RSS Integration (Current Phase)
- [ ] Implement RSS feed integration with documented tech sources
- [ ] Configure NewsAPI with tech and startup keywords
- [ ] Set up Reddit integration with startup and technology subreddits
- [ ] Test content categorization with tech categories
- [ ] Validate Flash Summary generation with real tech content

## Success Criteria
- Daily Flash Summary generating with tech industry insights and citations
- 25+ RSS feeds actively providing relevant startup and tech content
- Proper categorization across 6 tech categories
- High-quality, actionable content for tech professionals and startup founders

---

**Next Steps**: Implement RSS feed integration using documented tech sources, configure NewsAPI for startup and tech keywords. 