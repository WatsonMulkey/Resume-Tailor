"""
Centralized configuration for Resume Tailor.

Single source of truth for contact info, API settings, and output preferences.
"""

from pathlib import Path
import os

# ==========================================
# Contact Information
# ==========================================

# Default contact info - used if import_career_data is unavailable
DEFAULT_CONTACT = {
    "name": "M. Watson Mulkey",
    "email": "watsonmulkey@gmail.com",
    "phone": "434-808-2493",
    "linkedin": "linkedin.com/in/watsonmulkey",
    "location": "Denver, Colorado"
}

def get_contact_info() -> dict:
    """
    Get contact info, preferring CAREER_DATA if available.

    Returns:
        dict: Contact information with keys: name, email, phone, linkedin, location
    """
    try:
        from import_career_data import CAREER_DATA
        return CAREER_DATA.get("contact_info", DEFAULT_CONTACT)
    except ImportError:
        return DEFAULT_CONTACT

# ==========================================
# API Settings
# ==========================================

# Claude model to use for generation
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Token limits for generation
MAX_RESUME_TOKENS = 2500
MAX_COVER_LETTER_TOKENS = 1500

# Retry settings
MAX_API_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0  # seconds

# ==========================================
# Output Settings
# ==========================================

# Default output directory for generated files
DEFAULT_OUTPUT_DIR = Path(os.environ.get(
    "RESUME_OUTPUT_DIR",
    str(Path.home() / "OneDrive" / "Desktop" / "Jobs")
))

# Output format preferences
OUTPUT_CONFIG = {
    "resume": {
        "formats": ["pdf"],  # Only PDF for resumes
        "cleanup_intermediate": True,  # Remove .md and .html files
    },
    "cover_letter": {
        "formats": ["docx", "pdf"],  # DOCX and PDF for cover letters
        "cleanup_intermediate": True,  # Remove .md files
    },
}

def get_output_formats(content_type: str) -> list:
    """Get configured output formats for a content type."""
    return OUTPUT_CONFIG.get(content_type, {}).get("formats", [])

def should_cleanup_intermediate(content_type: str) -> bool:
    """Check if intermediate files should be cleaned up."""
    return OUTPUT_CONFIG.get(content_type, {}).get("cleanup_intermediate", True)

# ==========================================
# Optional Dependencies
# ==========================================

def check_optional_dependency(module_name: str) -> bool:
    """
    Check if an optional dependency is available.

    Args:
        module_name: Name of the module to check (e.g., 'reportlab', 'docx')

    Returns:
        bool: True if module is available, False otherwise
    """
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

# Check availability of optional format generators
PDF_AVAILABLE = check_optional_dependency('reportlab')
DOCX_AVAILABLE = check_optional_dependency('docx')
HTML_AVAILABLE = check_optional_dependency('markdown')
