Tasks.md

# SaaS Flash Report - Current Tasks

## Phase 3: Immediate QA Fixes (IN PROGRESS)

### Critical Issues - Next Up
- [x] **PRIORITY 1**: Add Flash Summary Component to index.html (missing daily summary section)
- [x] **PRIORITY 2**: Fix archive page H1 sizing to match index.html consistency
- [x] **PRIORITY 3**: Update topic page taglines - remove "Artificial Intelligence News at Machine Speed" → "Software Intelligence, Business Speed"

### Template Consistency Issues
- [x] Verify H1 consistency across all pages (some pages may have different H1 styling e.g archive). Index.html has the correct h1.
- [x] Ensure topic pages have title case headlines (not ALL CAPS) - Aggregator configured correctly, old content will be replaced on next content update
- [x] Ensure topic pages have correct newsletter form configured for Netlify (use the one from index.html)
- [x] Update newsletter form text from "AI enthusiasts" to "SaaS professionals" - Template configured correctly, old static pages will be replaced on next content update
- [x] Fix any remaining color inconsistencies (should be blue #3B82F6, not red #cc0000) - Templates correctly configured with blue colors, old static pages will be replaced on next content update

### Other
- [x] Verify this plausible script is present: <script defer data-domain="saasflashreport.com" src="https://plausible.io/js/script.outbound-links.js"></script> - Template correctly configured, old static pages will be replaced on next content update
- [x] Clean up project of extraneous files and files related to the old AI site

### Content Issues
- [x] Verify all topic pages have SaaS-appropriate content (not AI content) - Removed 40+ AI-specific pages, updated remaining with SaaS branding
- [x] Check navigation dropdown has correct SaaS topic categories
- [x] Ensure all meta descriptions reference SaaS, not AI - Updated template with SaaS-focused descriptions

## Phase 4: Content Aggregation ✅ COMPLETED

All content aggregation systems are now properly configured and tested for SaaS-focused content.

## Completed ✅

### Content Aggregation ✅ 
- [x] **RSS Integration**: 30 SaaS-focused RSS feeds configured (SaaStr, ChartMogul, Salesforce, GitHub, Slack, etc.)
- [x] **API Integration**: NewsAPI with SaaS keywords, Reddit SaaS subreddits, Perplexity SaaS-focused prompts
- [x] **Content Pipeline**: End-to-end workflow tested, 8 SaaS categories with keyword matching 
- [x] **SaaS Categorization**: SaaS Funding, Enterprise Software, Product Launches, SaaS Analytics, B2B Technology, Software Industry, SaaS Acquisitions, SaaS Metrics

### Template & Branding ✅
- [x] Archive directory cleaned (removed non-existent archive links)
- [x] Footer consistency fixed across all pages (SaaS branding, consistent format)
- [x] Site converted from AI branding to SaaS branding (blue colors, cloud emoji, SaaS messaging)
- [x] Universal template implemented with SaaS-specific styling
- [x] Cross-portfolio linking implemented in About page
- [x] Analytics configured (saasflashreport domain)
- [x] **MAJOR**: templates/template.html completely updated - removed ALL AI references, added SaaS categories, updated meta tags, URLs, analytics

### Site Structure ✅
- [x] All required pages created (index, about, contact, topic pages)
- [x] Topic pages created with SaaS categories
- [x] Navigation structure implemented
- [x] Archive structure established

## Testing Checklist (Before Content Aggregation)

### Page Validation
- [x] Index page: Flash summary component present and working
- [x] Archive page: H1 sizing matches index page
- [x] Create relevant topic pages and add to site menu
- [x] Topic pages: All have SaaS taglines (not AI)
- [x] Topic pages: All have title case headlines
- [x] Topic pages: All have correct newsletter forms
- [x] All pages: Consistent H1 styling and SaaS branding

### Navigation Testing
- [x] Topics dropdown works on all pages **FIXED**: Added Topics dropdown to about.html and contact.html 
- [x] All navigation links work correctly
- [x] Cross-site portfolio links work (to other Flash Report sites)
- [x] Footer links work correctly

### Other
- [x] Add link to aiflashreport.com to panel on /about and remove the link to saasflashreport as that is THIS site
- [x] change site tag line to the latest Saas news at breaking speed
- [x] remove duplicate archive page link in the footer


## Local QA Task List

- [x] **Opengraph Lettermark**: Confirm that an on-brand lettermark/logo is created and set for OpenGraph/social media previews (check `meta` tags and preview on Twitter/X, LinkedIn, Facebook).
- [x] **SEO Keywords**: Add and verify the following keywords in the `<meta name="keywords">` tag on all pages: `saas news, saas updates, saas industry, saas funding news, saas news today`.
- [x] **Menu Cleanup**: Remove the RSS link from the navigation menu on `/about` (it should only appear in the footer). Double-check that the menu is consistent across all pages.
- [x] **Contact Form Simplification**: Update the contact form to remove the subject line dropdown and organization field. Use a standard subject line for all submissions. Test the form to ensure it works as expected.
- [x] **Sitemap & Robots.txt Validation**: Validate that `sitemap.xml` and `robots.txt` exist, are up-to-date, and follow SEO best practices (e.g., correct URLs, no disallowed important pages, sitemap is referenced in robots.txt).
- [x] **Footer Links Consistency**: Remove any duplicate `/index` links from the footer. Ensure there is only one link to the homepage and that the footer is identical on all pages.
- [x] **Topic Page Story Message Bug**: Investigate and fix the issue where topic pages display both stories and the message: "No stories found for this topic yet. Stories are automatically added daily when they match relevant keywords." (e.g., https://saasflashreport.com/topics/ipos-acquisitions-page-10). The message should only appear if there are truly no stories for the topic.

### Additional QA Steps (for completeness)
- [x] **Cross-Page Consistency**: Review all pages for consistent branding, navigation, and footer.
- [x] **Meta Tag Review**: Ensure all pages have correct and up-to-date meta tags (title, description, OpenGraph, Twitter Card).
- [x] **Mobile Responsiveness**: Check that all changes render correctly on mobile devices.
- [x] **Accessibility**: Confirm that navigation and forms are accessible (labels, alt text, keyboard navigation).

### Content Validation
- [x] Newsletter forms mention "SaaS professionals" 
- [x] Meta descriptions are SaaS-focused
- [x] Remove Subjects dropdown from Contact form and change to a standard subject line

## Notes
- **Current Focus**: Complete Phase 3 QA fixes before moving to content aggregation
- **Next Major Phase**: RSS and API integration for live content
- **Template Reference**: Use AI Flash Report structure but with SaaS branding
- **Color Scheme**: Blue (#3B82F6) throughout, cloud emoji ☁️, "Software Intelligence, Business Speed" tagline