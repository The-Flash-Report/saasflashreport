"""
Flash Summary Component

A reusable component for generating AI news flash summaries with clickable citations.
Can be used across multiple projects (AI news, crypto news, etc.).
"""

from .core import FlashSummaryGenerator
from .config import FlashSummaryConfig

__version__ = "1.0.0"
__all__ = ["FlashSummaryGenerator", "FlashSummaryConfig"] 