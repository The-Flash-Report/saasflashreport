# Product Requirements Document: Flash Summary Reusable Component

## Introduction/Overview

This project will extract the existing Daily AI Flash Summary functionality into a standalone, reusable component that can be easily integrated across multiple niche news aggregation projects. The component will maintain the same Perplexity API integration, exact prompt format, and styling while allowing customization for different domains (AI news, crypto, health tech, etc.). This addresses the need for code reusability, consistent quality assurance, and easy maintenance across multiple projects.

## Goals

1. **Code Reusability**: Create a standalone component that can be dropped into any news aggregation project
2. **Consistency**: Maintain identical functionality, styling, and prompt format across all implementations
3. **Easy Maintenance**: Enable updates to be pushed to all projects from a single codebase
4. **Niche Customization**: Allow easy configuration for different domains without code changes
5. **Quality Assurance**: Standardize the flash summary feature across all projects for consistent user experience

## User Stories

1. **As a developer**, I want to add a flash summary to my crypto news site by importing a component so that I don't have to rewrite the entire feature.

2. **As a project maintainer**, I want to fix a bug in the flash summary once and have it automatically apply to all my niche sites so that maintenance is efficient.

3. **As a site visitor**, I want to see the same high-quality flash summary format on different niche sites so that I have a consistent experience.

4. **As a content creator**, I want the flash summary to automatically adapt to my niche (crypto, health tech, etc.) without manual prompt engineering so that the content stays relevant.

## Functional Requirements

1. **Standalone Package**: The component must be a separate, importable Python package that can be installed in any project.

2. **Configuration-Based**: The component must accept configuration parameters for:
   - Domain/niche (e.g., "AI", "crypto", "health tech")
   - Site-specific keywords and focus areas
   - Date formatting preferences
   - API rate limiting settings

3. **Perplexity API Integration**: Must maintain the exact same Perplexity API integration:
   - Same model (`llama-3.1-sonar-small-128k-online`)
   - Same retry logic and error handling
   - Same API key management approach

4. **Prompt Template Preservation**: Must use the exact same prompt structure:
   - `**[DOMAIN] FLASH - {date}**` format
   - Same 3-story bullet point structure
   - Same "Flash Insight" section
   - Same citation and URL requirements

5. **HTML/CSS Output**: Must generate identical HTML output with:
   - Same CSS class names (`.flash-daily-summary`, `.flash-insight`, etc.)
   - Same styling and responsive design
   - Same link formatting and styling

6. **Fallback Mechanism**: Must include the same fallback content generation when Perplexity API fails.

7. **Easy Integration**: Must integrate into existing aggregator scripts with minimal code changes (2-3 lines maximum).

8. **Environment Variable Support**: Must work with existing environment variable patterns for API keys.

9. **Logging Compatibility**: Must use compatible logging that integrates with existing project logs.

10. **Archive Support**: Must generate content that works with existing archive page generation.

## Non-Goals (Out of Scope)

1. **Different API Providers**: Will not support OpenAI, Claude, or other AI services - only Perplexity
2. **Custom Prompt Formats**: Will not allow custom prompt structures - maintains exact current format
3. **Advanced Configuration UI**: No web interface for configuration - uses config files only
4. **Real-time Updates**: Still limited to once-daily generation per original design
5. **Multi-language Support**: English only, same as current implementation
6. **Database Integration**: Continues to use file-based approach of original implementation

## Design Considerations

1. **Package Structure**: Organize as a standard Python package with clear module separation:
   ```
   flash_summary_component/
   ├── __init__.py
   ├── core.py          # Main component logic
   ├── config.py        # Configuration handling
   ├── templates.py     # HTML/CSS templates
   └── utils.py         # Helper functions
   ```

2. **Configuration Format**: Use JSON configuration files for easy customization:
   ```json
   {
     "domain": "crypto",
     "focus_areas": ["Bitcoin", "Ethereum", "DeFi", "regulation"],
     "exclude_topics": ["basic tutorials", "old news"],
     "brand_color": "#f7931a"
   }
   ```

3. **CSS Inheritance**: Maintain existing CSS structure but allow brand color customization

4. **Import Simplicity**: Enable simple integration:
   ```python
   from flash_summary_component import FlashSummary
   
   flash = FlashSummary(config_path="crypto_config.json")
   summary_html = flash.generate(headlines, date)
   ```

## Technical Considerations

1. **Dependency Management**: Package with minimal dependencies, reusing existing libraries where possible

2. **Version Control**: Separate Git repository for the component with semantic versioning

3. **Installation Method**: Publishable as pip package or Git submodule for easy inclusion

4. **Backward Compatibility**: Ensure existing projects continue working without modification

5. **Testing Framework**: Include comprehensive tests for different niche configurations

6. **Documentation**: Provide clear setup instructions and configuration examples

7. **Performance**: Maintain same performance characteristics as current implementation

8. **Security**: Preserve existing API key security patterns and best practices

## Success Metrics

1. **Adoption**: Successfully deployed across 3+ different niche projects
2. **Maintenance Efficiency**: 90% reduction in duplicate code maintenance across projects
3. **Setup Time**: New project integration completed in under 15 minutes
4. **Consistency**: Identical functionality and styling across all implementations
5. **Update Propagation**: Bug fixes and improvements deployed to all projects within 24 hours
6. **Configuration Success**: Different niches generate relevant, domain-specific content

## Open Questions

1. **Distribution Method**: Should this be a separate GitHub repository, pip package, or Git submodule?
2. **Configuration Validation**: How comprehensive should the configuration validation be?
3. **Brand Customization**: How much visual customization should be allowed while maintaining consistency?
4. **Update Mechanism**: Should there be an automated way to update the component across projects?
5. **Testing Strategy**: Should there be integration tests that verify functionality across different niche configurations? 