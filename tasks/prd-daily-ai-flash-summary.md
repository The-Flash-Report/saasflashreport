# Product Requirements Document: Daily AI Flash Summary

## Introduction/Overview

The Daily AI Flash Summary feature will provide users with a concise, compelling daily digest of the most significant AI news stories at the top of the main page. This feature addresses two key needs: giving users a quick overview before they explore full articles, and providing additional SEO-rich content to improve search rankings. The summary will be generated automatically using Perplexity AI and integrated seamlessly into the existing news aggregation workflow.

## Goals

1. **User Experience**: Provide users with a quick daily digest of the most important AI news stories
2. **SEO Enhancement**: Add fresh, keyword-rich content to the main page for improved search rankings
3. **Content Freshness**: Ensure the main page always has up-to-date, compelling content at the top
4. **Workflow Integration**: Seamlessly integrate with existing automated daily news aggregation
5. **Reliability**: Provide consistent daily summaries with appropriate fallback mechanisms

## User Stories

1. **As a busy professional**, I want to see the day's most important AI news in a quick summary so that I can stay informed without reading multiple articles.

2. **As a regular visitor**, I want the homepage to always show fresh, current content so that I know the site is actively maintained and up-to-date.

3. **As a casual browser**, I want to understand the significance of today's AI developments through expert analysis so that I can better comprehend industry trends.

4. **As a returning user**, I want to see how today's news compares to previous days when I visit archived pages so that I can track AI industry evolution over time.

## Functional Requirements

1. **Daily Generation**: The system must automatically generate a new AI flash summary every day as part of the existing GitHub Actions workflow.

2. **Perplexity Integration**: The system must use the Perplexity API with the specified prompt to generate the summary content.

3. **Content Format**: The summary must follow the exact format:
   - **AI FLASH - [DATE]**
   - One compelling headline about the most significant AI story
   - **Today's Top Stories**: 3 bullet points with one-sentence summaries and sources
   - **Flash Insight**: 1-2 sentence analysis of industry implications

4. **Homepage Placement**: The summary must appear at the top of the main `index.html` page, above existing content.

5. **Archive Integration**: The summary must be automatically included in daily archive pages as they are generated.

6. **Link Preservation**: The system must preserve and display any links provided in the Perplexity response.

7. **Date Formatting**: The system must use consistent date formatting matching the site's existing conventions.

8. **Fallback Generation**: When Perplexity API is unavailable, the system must generate a fallback summary using the same format from existing aggregated articles.

9. **Error Handling**: The system must gracefully handle API failures without breaking the main workflow.

10. **Styling Integration**: The summary must use CSS styling that integrates with the existing site design.

## Non-Goals (Out of Scope)

1. **Manual Editing**: The summary will not support manual editing or override capabilities
2. **Multiple Daily Updates**: Only one summary per day will be generated, not real-time updates
3. **User Customization**: Users will not be able to customize summary content or format
4. **Historical Updates**: Existing archive pages will not be retroactively updated with summaries
5. **Interactive Elements**: No commenting, sharing, or interactive features for the summary
6. **Alternative AI Providers**: Only Perplexity AI will be used, no multi-provider fallback
7. **Separate Pages**: No dedicated summary-only pages will be created

## Design Considerations

1. **Visual Hierarchy**: The flash summary should be visually prominent but not overwhelm the existing content
2. **Typography**: Use consistent heading styles and typography that match the current site design
3. **Layout**: Implement as a contained section that clearly separates from the main article content
4. **Responsive Design**: Ensure the summary displays properly on mobile, tablet, and desktop
5. **CSS Classes**: Use semantic CSS class names (e.g., `flash-daily-summary`, `flash-insight`) for styling consistency
6. **Spacing**: Maintain appropriate white space and margins consistent with existing page elements

## Technical Considerations

1. **API Integration**: Leverage existing Perplexity API key stored as GitHub Secret (`PERPLEXITY_API_KEY`)
2. **Template Updates**: Modify `template.html` to include the flash summary section
3. **Aggregator Script**: Update `aggregator.py` to call Perplexity API and generate summary content
4. **Date Handling**: Use consistent date formatting with existing archive naming conventions
5. **Error Logging**: Implement proper error logging for API failures and fallback activation
6. **Rate Limiting**: Respect Perplexity API rate limits and implement appropriate delays if needed
7. **Content Sanitization**: Ensure proper HTML escaping and content sanitization for security
8. **Workflow Integration**: Add Perplexity API call to existing GitHub Actions workflow without breaking current functionality

## Success Metrics

1. **Content Quality**: Daily summaries are generated successfully with relevant, accurate AI news
2. **User Engagement**: Increased time on page and reduced bounce rate for homepage visitors
3. **SEO Performance**: Improved search rankings for AI-related keywords on the main page
4. **Reliability**: 95%+ success rate for daily summary generation (including fallback scenarios)
5. **Content Freshness**: Homepage always displays current date's summary
6. **Link Quality**: External links from Perplexity responses are valid and relevant

## Open Questions

1. **API Rate Limits**: What are the specific rate limits for the Perplexity API and do we need any throttling?
2. **Content Moderation**: Should there be any content filtering or moderation for the generated summaries?
3. **Backup Strategy**: How many days of fallback content should be maintained if both Perplexity and aggregation fail?
4. **Performance Impact**: Will the additional API call significantly impact the overall workflow execution time?
5. **Content Validation**: Should there be any automated validation of the generated content format before publishing? 