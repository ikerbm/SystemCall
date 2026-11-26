"""
Rafael Service wrapper for API.
Provides a singleton instance of Rafael initialized without TTS for fast web API text responses.
"""
import logging
from typing import Optional
from Core.Rafael import Rafael

logger = logging.getLogger(__name__)

_rafael_instance: Optional[Rafael] = None


def get_rafael() -> Rafael:
    """
    Returns the singleton instance of Rafael (lazy-loaded).
    Initializes Rafael with use_tts=False so no local audio is played on the server.
    """
    global _rafael_instance
    if _rafael_instance is None:
        logger.info("[Rafael Service] Initializing Rafael AI core...")
        _rafael_instance = Rafael(use_tts=False)
        logger.info("[Rafael Service] Rafael AI core ready.")
    return _rafael_instance
