"""
Provenance Validation for Resume Tailor.

Validates that generated content correctly attributes achievements to jobs.
Catches misattribution where achievements appear under the wrong company/role.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

from provenance import (
    ProvenanceTrace, DocumentProvenance, SectionProvenance,
    BulletProvenance, SourceReference, SourceType
)


class ProvenanceValidator:
    """Validates provenance claims in generated content."""

    def __init__(self, career_data=None):
        """
        Initialize validator with career data.

        Args:
            career_data: CareerData instance. If None, loads from career_data_manager.
        """
        if career_data is None:
            try:
                from career_data_manager import load_career_data
                self.career_data = load_career_data()
            except Exception as e:
                print(f"Warning: Could not load career data: {e}")
                self.career_data = None
        else:
            self.career_data = career_data

        self._build_source_index()

    def _build_source_index(self):
        """Build index of all source data for quick lookup."""
        self.achievement_index: Dict[str, Dict[str, Any]] = {}  # ach_id -> {company, job_title, text, result}
        self.company_achievements: Dict[str, List[str]] = {}  # company.lower() -> [ach_ids]
        self.metrics_index: Dict[str, str] = {}  # metric (e.g., "32%") -> ach_id
        self.job_index: Dict[str, Dict[str, Any]] = {}  # job_id -> {company, title, dates}

        if not self.career_data:
            return

        # Build a lookup from company -> job info for matching achievements to jobs
        company_to_job: Dict[str, Dict[str, Any]] = {}

        # Index jobs and their achievements
        for job in self.career_data.jobs:
            job_id = getattr(job, 'id', None)
            company_lower = job.company.lower()

            # Index the job itself
            if job_id:
                self.job_index[job_id] = {
                    'company': job.company,
                    'title': job.title,
                    'dates': f"{job.start_date} to {job.end_date or 'Present'}"
                }

            # Store for achievement matching
            company_to_job[company_lower] = {
                'company': job.company,
                'title': job.title,
                'job_id': job_id
            }

            # Initialize company achievements list
            if company_lower not in self.company_achievements:
                self.company_achievements[company_lower] = []

            # Index achievements under each job (if stored directly)
            if hasattr(job, 'achievements') and job.achievements:
                for ach in job.achievements:
                    self._index_achievement(ach, job.company, job.title, job_id)

        # Also index achievements from skill examples
        # (achievements can be stored as skill.examples with company field)
        if hasattr(self.career_data, 'skills') and self.career_data.skills:
            for skill in self.career_data.skills:
                if hasattr(skill, 'examples') and skill.examples:
                    for example in skill.examples:
                        company = getattr(example, 'company', None)
                        if company:
                            company_lower = company.lower()
                            job_info = company_to_job.get(company_lower, {})
                            job_title = job_info.get('title', 'Unknown')
                            job_id = job_info.get('job_id')
                            self._index_achievement(example, company, job_title, job_id)

    def _index_achievement(self, ach, company: str, job_title: str, job_id: Optional[str]):
        """Index a single achievement for validation lookup."""
        ach_id = getattr(ach, 'id', None)
        if not ach_id:
            return

        company_lower = company.lower()

        # Initialize company list if needed
        if company_lower not in self.company_achievements:
            self.company_achievements[company_lower] = []

        # Don't re-index if already present
        if ach_id in self.achievement_index:
            return

        self.achievement_index[ach_id] = {
            'company': company,
            'job_title': job_title,
            'job_id': job_id,
            'text': getattr(ach, 'description', ''),
            'result': getattr(ach, 'result', ''),
            'metrics': getattr(ach, 'metrics', []) or []
        }
        self.company_achievements[company_lower].append(ach_id)

        # Index metrics for fuzzy matching
        for metric in (getattr(ach, 'metrics', []) or []):
            # Extract percentage patterns
            percentages = re.findall(r'\d+%', metric)
            for pct in percentages:
                if pct not in self.metrics_index:
                    self.metrics_index[pct] = ach_id

        # Also extract metrics from result text
        result_text = getattr(ach, 'result', '') or ''
        result_pcts = re.findall(r'\d+%', result_text)
        for pct in result_pcts:
            if pct not in self.metrics_index:
                self.metrics_index[pct] = ach_id

        # Also extract metrics from description text
        description_text = getattr(ach, 'description', '') or ''
        desc_pcts = re.findall(r'\d+%', description_text)
        for pct in desc_pcts:
            if pct not in self.metrics_index:
                self.metrics_index[pct] = ach_id

    def validate_bullet(
        self,
        bullet_text: str,
        claimed_company: str,
        claimed_source_id: Optional[str] = None
    ) -> Tuple[str, List[str]]:
        """
        Validate a bullet point's attribution.

        Args:
            bullet_text: The generated bullet point text
            claimed_company: Company this bullet is claimed to be from
            claimed_source_id: Optional ACH:id if extracted from the text

        Returns:
            Tuple of (status, notes) where status is one of:
            - "valid": Achievement correctly attributed
            - "warning": Possible misattribution
            - "error": Definite misattribution
            - "unverified": Cannot verify (no source ID or match)
        """
        notes = []

        # Try to extract ACH:id from the bullet text itself
        if not claimed_source_id:
            ach_match = re.search(r'ACH:(\w+)', bullet_text)
            if ach_match:
                claimed_source_id = ach_match.group(1)

        # If we have a source ID, verify it matches the claimed company
        if claimed_source_id and claimed_source_id in self.achievement_index:
            source = self.achievement_index[claimed_source_id]
            if source['company'].lower() == claimed_company.lower():
                notes.append(f"Verified: ACH:{claimed_source_id} belongs to {claimed_company}")
                return 'valid', notes
            else:
                notes.append(
                    f"MISATTRIBUTION: ACH:{claimed_source_id} is from "
                    f"'{source['company']}' ({source['job_title']}), "
                    f"not '{claimed_company}'"
                )
                return 'error', notes

        # No source ID - try fuzzy matching by metrics
        return self._fuzzy_validate(bullet_text, claimed_company)

    def _fuzzy_validate(
        self,
        bullet_text: str,
        claimed_company: str
    ) -> Tuple[str, List[str]]:
        """
        Validate by matching metrics/keywords when no explicit ID.

        Args:
            bullet_text: The bullet point text
            claimed_company: Company this is attributed to

        Returns:
            Tuple of (status, notes)
        """
        notes = []
        bullet_lower = bullet_text.lower()
        claimed_company_lower = claimed_company.lower()

        # Extract metrics from bullet text (e.g., "32%", "50%", "$50M")
        metrics_in_text = re.findall(r'\d+%|\$\d+[MKB]?', bullet_text)

        matches_at_claimed = []
        matches_at_other = []

        for metric in metrics_in_text:
            if metric in self.metrics_index:
                ach_id = self.metrics_index[metric]
                source = self.achievement_index.get(ach_id, {})
                source_company = source.get('company', '').lower()

                if source_company == claimed_company_lower:
                    matches_at_claimed.append({
                        'metric': metric,
                        'ach_id': ach_id,
                        'company': source.get('company'),
                        'job_title': source.get('job_title')
                    })
                else:
                    matches_at_other.append({
                        'metric': metric,
                        'ach_id': ach_id,
                        'company': source.get('company'),
                        'job_title': source.get('job_title')
                    })

        # Analyze matches
        if matches_at_claimed and not matches_at_other:
            for match in matches_at_claimed:
                notes.append(
                    f"Metric {match['metric']} verified at {match['company']} "
                    f"({match['job_title']})"
                )
            return 'valid', notes

        if matches_at_other and not matches_at_claimed:
            for match in matches_at_other:
                notes.append(
                    f"WARNING: Metric {match['metric']} belongs to {match['company']} "
                    f"({match['job_title']}), but attributed to {claimed_company}"
                )
            return 'warning', notes

        if matches_at_claimed and matches_at_other:
            notes.append(
                f"Mixed attribution: some metrics match {claimed_company}, "
                f"some match other companies"
            )
            return 'warning', notes

        # No metrics found - try text similarity
        return self._text_similarity_validate(bullet_text, claimed_company)

    def _text_similarity_validate(
        self,
        bullet_text: str,
        claimed_company: str
    ) -> Tuple[str, List[str]]:
        """
        Last resort validation using text similarity.

        Args:
            bullet_text: The bullet point text
            claimed_company: Company this is attributed to

        Returns:
            Tuple of (status, notes)
        """
        notes = []
        bullet_lower = bullet_text.lower()
        claimed_company_lower = claimed_company.lower()

        # Check for company name mentions
        company_mentioned = claimed_company_lower in bullet_lower

        # Check for key achievement phrases
        for ach_id, source in self.achievement_index.items():
            source_text_lower = source['text'].lower()
            source_company_lower = source['company'].lower()

            # Check if significant words from source appear in bullet
            source_words = set(source_text_lower.split())
            bullet_words = set(bullet_lower.split())
            common_words = source_words & bullet_words
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            significant_common = common_words - stop_words

            if len(significant_common) >= 5:  # Threshold for similarity
                if source_company_lower == claimed_company_lower:
                    notes.append(f"Text similarity match at {source['company']}")
                    return 'valid', notes
                else:
                    notes.append(
                        f"Text similarity suggests this achievement is from "
                        f"{source['company']}, not {claimed_company}"
                    )
                    return 'warning', notes

        notes.append("Could not trace to source data - no metrics or text match")
        return 'unverified', notes

    def validate_document(
        self,
        content: str,
        provenance: DocumentProvenance
    ) -> DocumentProvenance:
        """
        Validate all claims in a generated document.

        Args:
            content: The generated document content
            provenance: DocumentProvenance object to update

        Returns:
            Updated DocumentProvenance with validation results
        """
        for section in provenance.sections:
            section_company = section.job_company

            for bullet in section.bullets:
                # Use section company if available, otherwise try to extract
                claimed_company = section_company
                if not claimed_company:
                    claimed_company = self._extract_company_from_bullet(bullet.bullet_text)

                if claimed_company:
                    # Get source IDs if any
                    source_ids = [s.source_id for s in bullet.sources] if bullet.sources else []
                    source_id = source_ids[0] if source_ids else None

                    # Validate
                    status, notes = self.validate_bullet(
                        bullet.bullet_text,
                        claimed_company,
                        source_id
                    )

                    bullet.validation_status = status
                    bullet.validation_notes = notes
                else:
                    bullet.validation_status = 'unverified'
                    bullet.validation_notes = ['Could not determine claimed company']

                # Update counters
                if bullet.validation_status == 'valid':
                    provenance.verified_claims += 1
                elif bullet.validation_status == 'warning':
                    provenance.warning_claims += 1
                elif bullet.validation_status == 'error':
                    provenance.error_claims += 1
                else:
                    provenance.unverified_claims += 1

                provenance.total_claims += 1

        # Check for company references outside Experience sections
        self.validate_company_references(content, provenance)

        return provenance

    def validate_company_references(
        self,
        content: str,
        provenance: DocumentProvenance
    ) -> None:
        """
        Check if any company is referenced in the document but has no Experience section entry.

        Appends a 'Company Reference Check' section to provenance if issues found.

        Args:
            content: The full document content
            provenance: DocumentProvenance to append warnings to
        """
        if not self.career_data:
            return

        # Collect company names that have Experience sections in the provenance
        experience_companies = set()
        for section in provenance.sections:
            if section.job_company:
                experience_companies.add(section.job_company.lower())

        # Check all known companies from career data
        content_lower = content.lower()
        warnings = []

        for job in self.career_data.jobs:
            company_lower = job.company.lower()
            if company_lower not in experience_companies and company_lower in content_lower:
                warnings.append(BulletProvenance(
                    bullet_text=f"'{job.company}' is referenced in the document but has no Experience section entry",
                    validation_status='warning',
                    validation_notes=[
                        f"Company '{job.company}' appears in document content but is not listed under Experience. "
                        f"This may indicate a stale reference from hardcoded data or a missing job section."
                    ]
                ))

        if warnings:
            ref_section = SectionProvenance(
                section_name="Company Reference Check",
                bullets=warnings
            )
            provenance.sections.append(ref_section)
            provenance.warning_claims += len(warnings)
            provenance.total_claims += len(warnings)

    def _extract_company_from_bullet(self, bullet_text: str) -> Optional[str]:
        """
        Extract company name from bullet text.

        Args:
            bullet_text: The bullet point text

        Returns:
            Company name if found, None otherwise
        """
        # Look for "at Company" pattern
        match = re.search(r'at\s+([A-Z][A-Za-z\s\.]+?)(?:\s*[,\(\-]|$)', bullet_text)
        if match:
            return match.group(1).strip()

        # Check if any known company name is in the text
        if self.career_data:
            for job in self.career_data.jobs:
                if job.company.lower() in bullet_text.lower():
                    return job.company

        return None

    def parse_resume_for_validation(self, resume_content: str) -> DocumentProvenance:
        """
        Parse a generated resume and create a DocumentProvenance for validation.

        Args:
            resume_content: The generated resume markdown

        Returns:
            DocumentProvenance ready for validation
        """
        provenance = DocumentProvenance(document_type="resume")
        lines = resume_content.split('\n')

        current_section = None
        current_company = None
        current_title = None

        in_experience_section = False

        for line in lines:
            line = line.strip()

            # Detect section headers (## Section)
            if line.startswith('## '):
                section_name = line[3:].strip()
                in_experience_section = (section_name.lower() == 'experience')
                current_section = SectionProvenance(section_name=section_name)
                provenance.sections.append(current_section)
                current_company = None
                current_title = None
                continue

            # Detect job headers (### Company) - create NEW section for each job
            if line.startswith('### '):
                header = line[4:].strip()
                # Extract company from header like "### Company Name" or "### Company Name (dates)"
                match = re.match(r'([^(]+)', header)
                if match:
                    current_company = match.group(1).strip()

                # Create a NEW section for this specific job (Experience - Company)
                section_name = f"Experience - {current_company}" if current_company else "Experience"
                current_section = SectionProvenance(section_name=section_name)
                current_section.job_company = current_company
                provenance.sections.append(current_section)
                continue

            elif '|' in line and not line.startswith('-'):
                # Format: **Title** | Dates  OR  **Title** | Company | Dates
                parts = [p.strip().strip('*') for p in line.split('|')]
                if len(parts) >= 2:
                    current_title = parts[0]
                    # Only set company from this line if we have 3+ parts (Title | Company | Dates)
                    # If only 2 parts, it's Title | Dates (company was set from ### header)
                    if len(parts) >= 3:
                        current_company = parts[1]
                    if current_section:
                        if current_company:  # Don't overwrite with None
                            current_section.job_company = current_company
                        current_section.job_title = current_title

            # Detect bullet points
            elif line.startswith('- ') and current_section:
                bullet_text = line[2:].strip()
                bullet = BulletProvenance(bullet_text=bullet_text)

                # Try to extract ACH:id if present
                ach_match = re.search(r'ACH:(\w+)', bullet_text)
                if ach_match:
                    ach_id = ach_match.group(1)
                    if ach_id in self.achievement_index:
                        source_data = self.achievement_index[ach_id]
                        bullet.sources.append(SourceReference(
                            source_type=SourceType.ACHIEVEMENT,
                            source_id=f"ACH:{ach_id}",
                            company=source_data['company'],
                            job_title=source_data['job_title'],
                            original_text=source_data['text']
                        ))

                current_section.bullets.append(bullet)

        return provenance

    def validate_resume(self, resume_content: str) -> DocumentProvenance:
        """
        Convenience method to parse and validate a resume in one call.

        Args:
            resume_content: The generated resume markdown

        Returns:
            Validated DocumentProvenance
        """
        provenance = self.parse_resume_for_validation(resume_content)
        return self.validate_document(resume_content, provenance)


def validate_and_report(resume_content: str, output_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Validate a resume and optionally generate a trace report.

    Args:
        resume_content: The generated resume markdown
        output_path: Optional path to write trace document

    Returns:
        Dict with validation summary
    """
    validator = ProvenanceValidator()
    provenance = validator.validate_resume(resume_content)

    summary = {
        'total_claims': provenance.total_claims,
        'verified': provenance.verified_claims,
        'warnings': provenance.warning_claims,
        'errors': provenance.error_claims,
        'unverified': provenance.unverified_claims,
        'issues': []
    }

    # Collect issues
    for section in provenance.sections:
        for bullet in section.bullets:
            if bullet.validation_status in ['warning', 'error']:
                summary['issues'].append({
                    'status': bullet.validation_status,
                    'section': section.section_name,
                    'company': section.job_company,
                    'bullet': bullet.bullet_text,
                    'notes': bullet.validation_notes
                })

    # Generate trace document if path provided
    if output_path:
        from provenance import generate_trace_document, ProvenanceTrace
        import hashlib

        trace = ProvenanceTrace(
            session_id=hashlib.md5(resume_content.encode()).hexdigest()[:8],
            target_company="Unknown",
            target_title="Unknown",
            resume_provenance=provenance
        )
        generate_trace_document(trace, output_path)
        summary['trace_file'] = str(output_path)

    return summary


if __name__ == '__main__':
    # Quick test
    validator = ProvenanceValidator()

    print("ProvenanceValidator initialized")
    print(f"  Achievements indexed: {len(validator.achievement_index)}")
    print(f"  Companies indexed: {len(validator.company_achievements)}")
    print(f"  Metrics indexed: {len(validator.metrics_index)}")

    # Test validation
    test_bullet = "Drove 32% YoY user engagement increase through data-driven UX improvements"
    status, notes = validator.validate_bullet(test_bullet, "Discovery Education")
    print(f"\nTest validation:")
    print(f"  Bullet: {test_bullet}")
    print(f"  Claimed company: Discovery Education")
    print(f"  Status: {status}")
    print(f"  Notes: {notes}")
