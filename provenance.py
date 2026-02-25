"""
Provenance tracking for Resume Tailor.

This module provides data structures and utilities for tracking the source
of every claim in generated resumes and cover letters, enabling:
1. Traceability - Know where each bullet point came from
2. Validation - Verify achievements are attributed to correct jobs
3. Debugging - Understand why the AI made specific choices
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Types of source data that can be referenced."""
    JOB = "job"
    ACHIEVEMENT = "achievement"
    SKILL = "skill"
    EDUCATION = "education"
    CERTIFICATION = "certification"
    PERSONAL_VALUE = "personal_value"
    RESPONSIBILITY = "responsibility"


class SourceReference(BaseModel):
    """Reference to a specific piece of source data."""
    source_type: SourceType
    source_id: str  # e.g., "ACH:abc123" or "JOB:def456"
    company: str
    job_title: Optional[str] = None
    timeframe: Optional[str] = None
    original_text: str  # Exact text from source data


class BulletProvenance(BaseModel):
    """Provenance tracking for a single bullet point in generated output."""
    bullet_text: str  # The generated bullet point
    target_requirement: Optional[str] = None  # Job requirement this addresses
    sources: List[SourceReference] = Field(default_factory=list)
    validation_status: str = "pending"  # pending, valid, warning, error, unverified
    validation_notes: List[str] = Field(default_factory=list)


class SectionProvenance(BaseModel):
    """Provenance for a resume/cover letter section."""
    section_name: str  # e.g., "Experience", "Key Achievements", "Professional Summary"
    job_company: Optional[str] = None  # Which job this section is for (for Experience sections)
    job_title: Optional[str] = None
    bullets: List[BulletProvenance] = Field(default_factory=list)


class DocumentProvenance(BaseModel):
    """Complete provenance record for a generated document."""
    document_type: str  # "resume" or "cover_letter"
    generated_at: datetime = Field(default_factory=datetime.now)
    sections: List[SectionProvenance] = Field(default_factory=list)

    # Summary statistics
    total_claims: int = 0
    verified_claims: int = 0
    warning_claims: int = 0
    error_claims: int = 0
    unverified_claims: int = 0


class ProvenanceTrace(BaseModel):
    """Complete trace document for a generation session."""
    session_id: str
    generated_at: datetime = Field(default_factory=datetime.now)
    target_company: str
    target_title: str
    job_description_summary: Optional[str] = None
    jd_required_skills: List[str] = Field(default_factory=list)
    jd_responsibilities: List[str] = Field(default_factory=list)
    resume_provenance: Optional[DocumentProvenance] = None
    cover_letter_provenance: Optional[DocumentProvenance] = None
    validation_summary: Dict[str, Any] = Field(default_factory=dict)


def generate_trace_document(trace: ProvenanceTrace, output_path: Path) -> str:
    """
    Generate a human-readable markdown trace document.

    Args:
        trace: The complete provenance trace
        output_path: Path to write the markdown file

    Returns:
        Path to the generated file as string
    """
    # Calculate totals across both documents
    total_claims = 0
    verified = 0
    warnings = 0
    errors = 0
    unverified = 0

    for doc in [trace.resume_provenance, trace.cover_letter_provenance]:
        if doc:
            total_claims += doc.total_claims
            verified += doc.verified_claims
            warnings += doc.warning_claims
            errors += doc.error_claims
            unverified += doc.unverified_claims

    md = f"""# Provenance Trace
## {trace.target_title} at {trace.target_company}

**Generated:** {trace.generated_at.strftime('%Y-%m-%d %H:%M:%S')}
**Session ID:** {trace.session_id}

---

## Validation Summary

| Status | Count | Description |
|--------|-------|-------------|
| ✓ Verified | {verified} | Claims traced to correct source |
| ⚠ Warning | {warnings} | Possible misattribution |
| ✗ Error | {errors} | Definite misattribution |
| ? Unverified | {unverified} | Could not trace to source |
| **Total** | **{total_claims}** | |

"""

    # Add issues summary if any exist
    issues = []
    for doc in [trace.resume_provenance, trace.cover_letter_provenance]:
        if doc:
            for section in doc.sections:
                for bullet in section.bullets:
                    if bullet.validation_status in ["warning", "error"]:
                        issues.append({
                            "status": bullet.validation_status,
                            "document": doc.document_type,
                            "section": section.section_name,
                            "company": section.job_company,
                            "bullet": bullet.bullet_text,
                            "notes": bullet.validation_notes
                        })

    if issues:
        md += """## ⚠ Issues Found

"""
        for issue in issues:
            status_icon = "✗" if issue["status"] == "error" else "⚠"
            md += f"""### [{status_icon}] {issue['document'].title()} - {issue['section']}
"""
            if issue["company"]:
                md += f"**Claimed for:** {issue['company']}\n\n"
            md += f"> {issue['bullet']}\n\n"
            for note in issue["notes"]:
                md += f"- {note}\n"
            md += "\n"

    # JD Requirements Reference table
    if trace.jd_required_skills or trace.jd_responsibilities:
        # Build resume content for substring matching
        resume_content = ""
        if trace.resume_provenance:
            for section in trace.resume_provenance.sections:
                for bullet in section.bullets:
                    resume_content += " " + bullet.bullet_text
        resume_content_lower = resume_content.lower()

        md += """---

## JD Requirements Reference

"""
        if trace.jd_required_skills:
            md += "### Required Skills\n\n"
            md += "| Skill | Present in Resume |\n"
            md += "|-------|------------------|\n"
            for skill in trace.jd_required_skills:
                present = "✓" if skill.lower() in resume_content_lower else "✗"
                md += f"| {skill} | {present} |\n"
            md += "\n"

        if trace.jd_responsibilities:
            md += "### Key Responsibilities\n\n"
            md += "| Responsibility | Addressed in Resume |\n"
            md += "|---------------|--------------------|\n"
            for resp in trace.jd_responsibilities:
                # Truncate long responsibilities for table display
                display = resp[:80] + "..." if len(resp) > 80 else resp
                # Check if key words from responsibility appear in resume
                resp_words = set(resp.lower().split()) - {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
                resume_words = set(resume_content_lower.split())
                overlap = resp_words & resume_words
                present = "✓" if len(overlap) >= 3 else "✗"
                md += f"| {display} | {present} |\n"
            md += "\n"

        md += "_This is an informational reference table. Presence is checked via case-insensitive substring/keyword matching and may have false positives or negatives._\n\n"

    # Resume provenance details
    if trace.resume_provenance:
        md += """---

## Resume Bullet Traceability

"""
        for section in trace.resume_provenance.sections:
            md += f"### {section.section_name}"
            if section.job_company:
                md += f" - {section.job_company}"
                if section.job_title:
                    md += f" ({section.job_title})"
            md += "\n\n"

            if not section.bullets:
                md += "_No bullets tracked for this section._\n\n"
                continue

            for bullet in section.bullets:
                status_icons = {
                    'valid': '✓',
                    'warning': '⚠',
                    'error': '✗',
                    'unverified': '?',
                    'pending': '...'
                }
                icon = status_icons.get(bullet.validation_status, '?')

                md += f"**[{icon}]** {bullet.bullet_text}\n"

                if bullet.target_requirement:
                    md += f"  - *Addresses:* {bullet.target_requirement}\n"

                if bullet.sources:
                    md += "  - *Sources:*\n"
                    for src in bullet.sources:
                        md += f"    - `{src.source_id}` @ {src.company}"
                        if src.job_title:
                            md += f" ({src.job_title})"
                        md += "\n"
                        if src.original_text:
                            # Truncate long original text
                            orig = src.original_text[:150]
                            if len(src.original_text) > 150:
                                orig += "..."
                            md += f"      > \"{orig}\"\n"

                if bullet.validation_notes:
                    md += "  - *Validation:*\n"
                    for note in bullet.validation_notes:
                        md += f"    - {note}\n"

                md += "\n"

    # Cover letter provenance details
    if trace.cover_letter_provenance:
        md += """---

## Cover Letter Bullet Traceability

"""
        for section in trace.cover_letter_provenance.sections:
            md += f"### {section.section_name}\n\n"

            if not section.bullets:
                md += "_No bullets tracked for this section._\n\n"
                continue

            for bullet in section.bullets:
                status_icons = {
                    'valid': '✓',
                    'warning': '⚠',
                    'error': '✗',
                    'unverified': '?',
                    'pending': '...'
                }
                icon = status_icons.get(bullet.validation_status, '?')

                md += f"**[{icon}]** {bullet.bullet_text}\n"

                if bullet.sources:
                    for src in bullet.sources:
                        md += f"  - `{src.source_id}` @ {src.company}\n"

                if bullet.validation_notes:
                    for note in bullet.validation_notes:
                        md += f"  - {note}\n"

                md += "\n"

    # Source data reference
    md += """---

## Source Data Reference

The source IDs used in this trace follow this format:
- `ACH:xxxxxxxx` - Achievement ID (linked to a specific job)
- `JOB:xxxxxxxx` - Job ID
- `SKILL:name` - Skill reference
- `RESP:index` - Responsibility from a job

Each achievement is permanently linked to the job where it was accomplished.
If an achievement appears under a different job in the generated document,
it will be flagged as a misattribution error.

"""

    # Write to file
    output_path = Path(output_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md)

    return str(output_path)


if __name__ == '__main__':
    # Quick test
    trace = ProvenanceTrace(
        session_id="test123",
        target_company="TestCorp",
        target_title="Senior PM"
    )
    trace.resume_provenance = DocumentProvenance(
        document_type="resume",
        total_claims=5,
        verified_claims=3,
        warning_claims=1,
        error_claims=1
    )

    print("Provenance models loaded successfully")
    print(f"Test trace: {trace.session_id} for {trace.target_title} at {trace.target_company}")
