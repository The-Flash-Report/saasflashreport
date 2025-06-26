"""
Configuration for Flash Summary Component

Handles all styling, colors, and formatting options.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FlashSummaryConfig:
    """Configuration options for the Flash Summary component."""
    
    # Colors
    background_color: str = "#f8f8f8"
    text_color: str = "#333"
    link_color: str = "#dc3545"
    
    # Layout
    padding: str = "25px"
    margin: str = "30px 0"
    border_radius: str = "0 8px 8px 0"
    border_left: str = "4px solid #cc0000"
    box_shadow: str = "0 3px 8px rgba(0,0,0,0.08)"
    
    # Typography
    font_family: str = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    line_height: str = "1.6"
    
    # Component behavior
    remove_prompt_leakage: bool = True
    add_sources_header: bool = True
    target_blank_links: bool = True
    
    @classmethod
    def for_crypto_site(cls) -> "FlashSummaryConfig":
        """Configuration preset for crypto news sites."""
        return cls(
            link_color="#f7931a",  # Bitcoin orange
            border_left="4px solid #f7931a"
        )
    
    @classmethod
    def for_ai_site(cls) -> "FlashSummaryConfig":
        """Configuration preset for AI news sites (default)."""
        return cls()  # Uses default values
    
    @classmethod
    def minimal(cls) -> "FlashSummaryConfig":
        """Minimal styling configuration."""
        return cls(
            background_color="transparent",
            padding="10px",
            margin="10px 0",
            border_left="none",
            border_radius="0"
        ) 
