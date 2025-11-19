"""
Core Flash Summary Component

Handles conversion of Perplexity API output to properly formatted HTML
with clickable citations and sources.
"""

import re
from typing import Dict, Optional, List, Tuple
from .config import FlashSummaryConfig


class FlashSummaryGenerator:
    """
    Converts Perplexity API markdown content to HTML with clickable citations.
    
    Handles multiple citation formats:
    - [1], [2] regular citations  
    - [^1], [^6] footnote citations
    - Sources sections with URLs
    """
    
    def __init__(self, config: Optional[FlashSummaryConfig] = None):
        self.config = config or FlashSummaryConfig()
        
    def convert_to_html(self, content: str) -> str:
        """
        Main conversion method. Takes Perplexity markdown and returns styled HTML.
        
        Args:
            content: Raw markdown content from Perplexity API
            
        Returns:
            Styled HTML with clickable citations and sources
        """
        if not content:
            return ""
            
        # Clean up any prompt leakage first
        html_content = self._remove_prompt_leakage(content)
        
        # Format headline as h2
        html_content = self._format_headline(html_content)
        
        # Extract citations and URLs
        citation_mapping = self._extract_citations(html_content)
        
        # Convert citations to clickable links
        html_content = self._convert_citations_to_links(html_content, citation_mapping)
        
        # Convert source URL definitions to clickable links
        html_content = self._convert_sources_to_links(html_content, citation_mapping)
        
        # Add sources header if we have citations
        # if citation_mapping:
        #     html_content = self._add_sources_header(html_content)
        
        # Simple markdown to HTML conversion
        html_content = self._simple_markdown_to_html(html_content)
        
        # Wrap in styled container
        return self._wrap_in_container(html_content)
    
    def _format_headline(self, content: str) -> str:
        """Format the AI-generated headline as an h2 element."""
        lines = content.split('\n')
        if len(lines) < 2:
            return content
            
        # Find the headline after "AI NEWS FLASH" and before bullet points
        headline_index = -1
        found_flash_line = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                continue
                
            # Mark when we've found the AI NEWS FLASH line
            if re.match(r'^\*\*AI NEWS FLASH.*\*\*$', stripped, re.IGNORECASE):
                found_flash_line = True
                continue
                
            # If we found the flash line, look for the next significant line that's not a bullet
            if found_flash_line:
                # Skip lines that start with bullet points or dashes
                if stripped.startswith('-') or stripped.startswith('•'):
                    break
                    
                # This should be the actual headline - it might be bold wrapped
                headline_index = i
                break
            
        if headline_index >= 0:
            headline = lines[headline_index].strip()
            # Remove any bold markdown formatting
            headline = re.sub(r'^\*\*(.+)\*\*$', r'\1', headline)
            # Replace with h2 wrapped version
            h2_headline = f'<h2 style="color: {self.config.link_color}; font-size: 1.4em; margin: 15px 0; font-weight: bold; line-height: 1.3;">{headline}</h2>'
            lines[headline_index] = h2_headline
            return '\n'.join(lines)
            
        return content
    
    def _remove_prompt_leakage(self, content: str) -> str:
        """Remove any leaked prompt instructions from the content."""
        # Remove common prompt instruction patterns
        patterns_to_remove = [
            r'IMPORTANT:.*?provide the corresponding URLs at the bottom\.',
            r'Focus on:.*?and speculation\.',
            r'Use the following headlines.*?summary:',
        ]
        
        cleaned_content = content
        for pattern in patterns_to_remove:
            cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Replace "IMPORTANT:" with "Sources" when it appears before citations
        cleaned_content = re.sub(r'IMPORTANT:\s*', 'Sources<br>', cleaned_content, flags=re.IGNORECASE)
        
        return cleaned_content.strip()
    
    def _extract_citations(self, content: str) -> Dict[str, str]:
        """
        Extract citation mappings from content.
        
        Handles multiple formats:
        - [1] https://example.com
        - - [1] https://example.com  
        - [^1]: https://example.com
        """
        citation_mapping = {}
        
        # Pattern 1: Regular citations [1] URL or - [1] URL
        pattern1 = r'-?\s*\[(\d+)\]\s*(https?://[^\s<>"\']+)'
        matches1 = re.findall(pattern1, content)
        
        for citation_num, url in matches1:
            citation_mapping[citation_num] = url
            
        # Pattern 2: Footnote citations [^1]: URL
        pattern2 = r'\[(\^?\d+)\]:\s*(https?://[^\s<>"\']+)'
        matches2 = re.findall(pattern2, content)
        
        for citation_num, url in matches2:
            clean_num = citation_num.replace('^', '')
            citation_mapping[clean_num] = url
            
        return citation_mapping
    
    def _convert_citations_to_links(self, content: str, citation_mapping: Dict[str, str]) -> str:
        """Convert citation numbers in main text to clickable links."""
        html_content = content
        
        for citation_num, url in citation_mapping.items():
            # Handle both [1] and [^1] formats in main text
            for pattern in [f'\\[{citation_num}\\]', f'\\[\\^{citation_num}\\]']:
                replacement = f'<a href="{url}" target="_blank" rel="noopener" style="color: {self.config.link_color}; font-weight: bold; text-decoration: none;">[{citation_num}]</a>'
                html_content = re.sub(pattern, replacement, html_content)
                
        return html_content
    
    def _convert_sources_to_links(self, content: str, citation_mapping: Dict[str, str]) -> str:
        """Convert source URL definitions to clickable links."""
        html_content = content
        
        for citation_num, url in citation_mapping.items():
            # Handle multiple source definition formats
            patterns = [
                r'-\s*\[' + citation_num + r'\]\s*(https?://[^\s<>"\']+)',
                r'\[\^?' + citation_num + r'\]:\s*(https?://[^\s<>"\']+)'
            ]
            
            for pattern in patterns:
                replacement = f'[{citation_num}]: <a href="{url}" target="_blank" rel="noopener" style="color: {self.config.link_color};">{url}</a>'
                html_content = re.sub(pattern, replacement, html_content)
                
        return html_content
    
    def _add_sources_header(self, content: str) -> str:
        """Add Sources header before the sources section if citations exist."""
        # Look for source definitions (URLs starting with http)
        if 'http' in content and ('[1]' in content or '[2]' in content or '[3]' in content):
            # Find the first source URL and add header before it
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'http' in line and ('[1]' in line or '[2]' in line or '[3]' in line):
                    # Add Sources header with normal styling (not red)
                    lines.insert(i, '\n<strong>Sources:</strong>')
                    break
            content = '\n'.join(lines)
        return content
    
    def _simple_markdown_to_html(self, content: str) -> str:
        """Simple markdown conversion with AI branding styling."""
        html_content = content
        
        # Convert ## Headings to styled <h3>
        html_content = re.sub(r'^##\s*(.+)$', f'<h3 style="color:{self.config.link_color}; font-size: 1.3em; margin: 20px 0 10px 0; font-weight: bold; border-bottom: 2px solid {self.config.link_color}; padding-bottom: 5px;">\\1</h3>', html_content, flags=re.MULTILINE)
        
        # Convert ### Headings to styled <h4>
        html_content = re.sub(r'^###\s*(.+)$', f'<h4 style="color:{self.config.link_color}; font-size: 1.2em; margin: 15px 0 10px 0; font-weight: bold;">\\1</h4>', html_content, flags=re.MULTILINE)
        
        # Convert markdown links [text](url) to HTML links with AI branding
        html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', f'<a href="\\2" target="_blank" rel="noopener" style="color: {self.config.link_color};">\\1</a>', html_content)
        
        # Convert **bold** to <strong> with AI branding for section headers
        html_content = re.sub(r'\*\*([^*]+)\*\*', f'<strong style="color: {self.config.link_color};">\\1</strong>', html_content)
        
        # Convert bullet points with AI branding color
        html_content = re.sub(r'^- (.+)$', f'<span style="position: relative; padding-left: 20px;"><span style="position: absolute; left: 0; color: {self.config.link_color}; font-weight: bold;">•</span>\\1</span>', html_content, flags=re.MULTILINE)
        
        # Convert newlines to <br> tags
        html_content = re.sub(r'\n', '<br>', html_content)
        
        return html_content
    
    def _wrap_in_container(self, content: str) -> str:
        """Wrap content in styled container matching the site design."""
        return f"""
        <div class="ai-flash-summary" style="
            background: {self.config.background_color}; padding: {self.config.padding};
            margin: {self.config.margin};
            color: {self.config.text_color};
            font-family: {self.config.font_family};
            line-height: {self.config.line_height}; border-radius: {self.config.border_radius}; border-left: {self.config.border_left}; box-shadow: {self.config.box_shadow};
        ">
            {content}
        </div>
        """ 
