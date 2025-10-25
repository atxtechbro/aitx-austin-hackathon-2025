"""
Gaming Highlights Autonomous Agent

An autonomous AI agent built with Claude Agent SDK and NVIDIA Nemotron Nano.
"""

__version__ = "1.0.0"
__author__ = "AITX Austin Hackathon Team"

from .gaming_agent import GamingHighlightsAgent
from .nemotron_analyzer import NemotronAnalyzer
from .video_tools import VideoTools

__all__ = ["GamingHighlightsAgent", "NemotronAnalyzer", "VideoTools"]
