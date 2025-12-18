"""
Unified markdown-to-structured-data parser for all format generators.

Single source of truth for parsing resume markdown into structured data.
Eliminates duplicate parsing logic across PDF, DOCX, and HTML generators.
"""

from dataclasses import dataclass, field
from typing import List, Dict
import re

from config import get_contact_info

# Get contact info once
CONTACT_INFO = get_contact_info()


@dataclass
class Job:
    """Represents a single job experience."""
    title: str = ""
    company: str = ""
    dates: str = ""
    location: str = ""
    bullets: List[str] = field(default_factory=list)


@dataclass
class ResumeData:
    """Structured resume data for all format generators."""
    name: str = ""
    title: str = "Senior Product Manager"
    contact_info: str = ""
    summary: str = ""
    experience: List[Job] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    skills: Dict[str, str] = field(default_factory=dict)  # {category: skills_text}
    education: Dict[str, str] = field(default_factory=dict)
    certifications: List[str] = field(default_factory=list)


def parse_markdown_resume(markdown_text: str) -> ResumeData:
    """
    Parse markdown resume into structured data.

    Single source of truth for all format generators (PDF, DOCX, HTML).

    Args:
        markdown_text: Markdown formatted resume

    Returns:
        ResumeData: Structured resume data
    """
    data = ResumeData()
    lines = markdown_text.split('\n')

    current_section = None
    current_job = None
    summary_lines = []
    achievement_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Parse name (first # heading)
        if line.startswith('# ') and not data.name:
            data.name = line.replace('#', '').strip()
            continue

        # Parse contact info (line with | separators and @ symbol)
        if '|' in stripped and '@' in stripped and not data.contact_info:
            # Use correct contact info from config, not from markdown
            data.contact_info = f"{CONTACT_INFO['phone']} | {CONTACT_INFO['email']} | {CONTACT_INFO['linkedin']} | {CONTACT_INFO['location']}"
            continue

        # Parse section headers (## Header)
        if line.startswith('## '):
            section_name = line.replace('##', '').strip().lower()

            # Save any current job before switching sections
            if current_job and current_job.company:
                data.experience.append(current_job)
                current_job = None

            # Detect section type
            if 'summary' in section_name or 'professional summary' in section_name:
                current_section = 'summary'
            elif 'experience' in section_name:
                current_section = 'experience'
            elif 'achievement' in section_name or 'key achievement' in section_name:
                current_section = 'achievements'
            elif 'skill' in section_name:
                current_section = 'skills'
            elif 'education' in section_name:
                current_section = 'education'
            elif 'certification' in section_name:
                current_section = 'certifications'
            else:
                current_section = None

            continue

        # Parse content based on current section
        if current_section == 'summary':
            if not stripped.startswith('**'):  # Skip bold headers
                summary_lines.append(stripped)

        elif current_section == 'experience':
            # Job header: **Title** | Company | Dates
            if stripped.startswith('**') and '|' in stripped:
                # Save previous job
                if current_job and current_job.company:
                    data.experience.append(current_job)

                # Parse new job header
                current_job = Job()
                parts = stripped.split('|')

                if len(parts) >= 2:
                    # Extract title (remove ** markers)
                    title_part = parts[0].replace('**', '').strip()
                    current_job.title = title_part

                    # Extract company
                    current_job.company = parts[1].strip()

                    # Extract dates if present
                    if len(parts) >= 3:
                        current_job.dates = parts[2].strip()

            # Job bullet points
            elif stripped.startswith('-') and current_job:
                bullet = stripped[1:].strip()  # Remove leading '-'
                current_job.bullets.append(bullet)

        elif current_section == 'achievements':
            if stripped.startswith('-') or stripped.startswith('*'):
                # Remove leading bullet and ** markers
                achievement = stripped.lstrip('-*').strip().replace('**', '')
                achievement_lines.append(achievement)

        elif current_section == 'skills':
            # Skills section: **Category:** description
            if stripped.startswith('**') and ':' in stripped:
                parts = stripped.split(':', 1)
                category = parts[0].replace('**', '').strip()
                skills_text = parts[1].strip() if len(parts) > 1 else ""
                data.skills[category] = skills_text

        elif current_section == 'education':
            # Education format: **Degree** | School | Dates
            if stripped.startswith('**') and '|' in stripped:
                parts = stripped.split('|')
                if len(parts) >= 2:
                    data.education['degree'] = parts[0].replace('**', '').strip()
                    data.education['school'] = parts[1].strip()
                    if len(parts) >= 3:
                        data.education['dates'] = parts[2].strip()

        elif current_section == 'certifications':
            # Certification list
            if stripped and not stripped.startswith('**'):
                # Remove leading bullets or markers
                cert = stripped.lstrip('-*').strip()
                if cert:
                    data.certifications.append(cert)

    # Save final job if exists
    if current_job and current_job.company:
        data.experience.append(current_job)

    # Combine summary lines
    data.summary = ' '.join(summary_lines).strip()

    # Store achievements
    data.achievements = achievement_lines

    # Set name from contact info if not found in markdown
    if not data.name:
        data.name = CONTACT_INFO['name']

    return data
