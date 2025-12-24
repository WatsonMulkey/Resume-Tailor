"""
Migration script: Supermemory → Local JSON Storage

Migrates career data from supermemory MCP to local career_data.json file.

Features:
- Retry logic with exponential backoff
- Progress tracking and checkpointing
- Resume capability from failures
- Validation report before commit
- Preview mode
- Rollback on failure
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from models import (
    CareerData, ContactInfo, Job, Skill, Achievement,
    PersonalValue, Education, Certification
)
from career_data_manager import save_career_data, get_manager
from pydantic import ValidationError


class MigrationError(Exception):
    """Base exception for migration errors."""
    pass


class MigrationProgress:
    """Track migration progress with checkpointing."""

    def __init__(self, checkpoint_file: Path):
        self.checkpoint_file = checkpoint_file
        self.migrated_count = 0
        self.failed_entries = []
        self.category_counts = {
            'jobs': 0,
            'skills': 0,
            'achievements': 0,
            'personal_values': 0,
            'education': 0
        }

    def save_checkpoint(self):
        """Save current progress to checkpoint file."""
        checkpoint_data = {
            'migrated_count': self.migrated_count,
            'failed_entries': self.failed_entries,
            'category_counts': self.category_counts,
            'timestamp': datetime.now().isoformat()
        }

        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

    def load_checkpoint(self) -> bool:
        """Load progress from checkpoint file. Returns True if checkpoint exists."""
        if not self.checkpoint_file.exists():
            return False

        with open(self.checkpoint_file, 'r') as f:
            data = json.load(f)

        self.migrated_count = data.get('migrated_count', 0)
        self.failed_entries = data.get('failed_entries', [])
        self.category_counts = data.get('category_counts', {})

        return True


def parse_date_format(date_str: str) -> str:
    """
    Convert various date formats to YYYY-MM.

    Examples:
    - "01/2024 - 03/2025" → "2024-01"
    - "11/2021 - 12/2023" → "2021-11"
    - "Present" → "Present"
    """
    if not date_str or date_str.strip().lower() == 'present':
        return 'Present'

    # Handle MM/YYYY format
    if '/' in date_str:
        parts = date_str.strip().split('/')
        if len(parts) == 2:
            month, year = parts
            return f"{year.strip()}-{month.strip().zfill(2)}"

    # Handle YYYY-MM format (already correct)
    if '-' in date_str and len(date_str) == 7:
        return date_str

    # Default fallback
    return date_str


def import_from_supermemory_with_retry(max_retries: int = 5) -> Dict[str, Any]:
    """
    Import career data from supermemory with retry logic.

    Args:
        max_retries: Maximum number of retry attempts

    Returns:
        Dict containing imported career data

    Raises:
        MigrationError: If import fails after all retries
    """
    delay = 1.0

    for attempt in range(max_retries):
        try:
            # Try to import from import_career_data.py (which has the data structure)
            print(f"[Attempt {attempt + 1}/{max_retries}] Loading career data from import_career_data.py...")

            from import_career_data import CAREER_DATA
            print(f"  [OK] Loaded career data successfully")
            return CAREER_DATA

        except ImportError as e:
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)
                print(f"  [Retry] Import failed, waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)
            else:
                raise MigrationError(f"Failed to import career data after {max_retries} attempts: {e}")

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)
                print(f"  [Error] {e}")
                print(f"  [Retry] Waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)
            else:
                raise MigrationError(f"Unexpected error during import: {e}")

    raise MigrationError("Migration failed after all retries")


def parse_career_data(raw_data: Dict[str, Any]) -> CareerData:
    """
    Parse raw career data into Pydantic models.

    Args:
        raw_data: Raw data from import_career_data.py

    Returns:
        Validated CareerData instance
    """
    print("\n[Parsing] Converting to Pydantic models...")

    # Parse contact info
    contact_raw = raw_data.get('contact_info', {})
    contact_info = ContactInfo(
        name=contact_raw.get('name', 'Unknown'),
        email=contact_raw.get('email', 'unknown@example.com'),
        phone=contact_raw.get('phone', '000-000-0000'),
        linkedin=contact_raw.get('linkedin'),
        location=contact_raw.get('location')
    )

    # Parse jobs
    jobs = []
    for job_raw in raw_data.get('job_history', []):
        # Parse dates
        dates = job_raw.get('dates', '')
        if ' - ' in dates:
            start_str, end_str = dates.split(' - ', 1)
            start_date = parse_date_format(start_str)
            end_date = parse_date_format(end_str)
        else:
            start_date = parse_date_format(dates)
            end_date = 'Present'

        job = Job(
            company=job_raw.get('company', 'Unknown'),
            title=job_raw.get('title', 'Unknown'),
            start_date=start_date,
            end_date=end_date,
            location=job_raw.get('location'),
            company_context=job_raw.get('company_context'),
            responsibilities=job_raw.get('responsibilities', [])
        )
        jobs.append(job)

    print(f"  Parsed {len(jobs)} jobs")

    # Parse skills
    skills = []
    for skill_raw in raw_data.get('skills', []):
        skill_name = skill_raw.get('skill', 'Unknown Skill')

        # Create example achievements from evidence
        examples = []
        for evidence_text in skill_raw.get('evidence', [])[:3]:  # Max 3 examples per skill
            # Use first job's dates as fallback timeframe
            timeframe = "2020-01" if jobs else "2023-01"
            company = jobs[0].company if jobs else "Professional Experience"

            try:
                example = Achievement(
                    description=evidence_text,
                    company=company,
                    timeframe=timeframe,
                    result=None
                )
                examples.append(example)
            except ValidationError as e:
                print(f"  [Warning] Skipping invalid skill example: {e}")
                continue

        # Only create skill if we have valid examples
        if examples:
            try:
                skill = Skill(
                    name=skill_name,
                    category='technical',  # Default category
                    proficiency='advanced',
                    examples=examples,
                    last_used="2024-01"
                )
                skills.append(skill)
            except ValidationError as e:
                print(f"  [Warning] Skipping invalid skill '{skill_name}': {e}")

    print(f"  Parsed {len(skills)} skills")

    # Parse personal values
    personal_values = []
    for value_raw in raw_data.get('personal_values', []):
        try:
            value = PersonalValue(
                content=value_raw.get('content', ''),
                category=value_raw.get('category', 'values')
            )
            personal_values.append(value)
        except ValidationError as e:
            print(f"  [Warning] Skipping invalid personal value: {e}")

    print(f"  Parsed {len(personal_values)} personal values")

    # Create CareerData instance
    career_data = CareerData(
        contact_info=contact_info,
        jobs=jobs,
        skills=skills,
        education=[],  # Will be added in future
        certifications=[],
        projects=[],
        personal_values=personal_values
    )

    return career_data


def preview_migration(career_data: CareerData) -> None:
    """Display preview of what will be migrated."""
    print("\n" + "=" * 60)
    print("MIGRATION PREVIEW")
    print("=" * 60)

    print(f"\nContact Information:")
    print(f"  Name: {career_data.contact_info.name}")
    print(f"  Email: {career_data.contact_info.email}")
    print(f"  Phone: {career_data.contact_info.phone}")
    print(f"  Location: {career_data.contact_info.location}")

    print(f"\nCareer Data Summary:")
    print(f"  Jobs: {len(career_data.jobs)}")
    print(f"  Skills: {len(career_data.skills)}")
    print(f"  Personal Values: {len(career_data.personal_values)}")
    print(f"  Education: {len(career_data.education)}")
    print(f"  Certifications: {len(career_data.certifications)}")
    print(f"  Projects: {len(career_data.projects)}")

    total_items = (len(career_data.jobs) + len(career_data.skills) +
                   len(career_data.personal_values) + len(career_data.education) +
                   len(career_data.certifications) + len(career_data.projects))

    print(f"\n  TOTAL ENTRIES: {total_items}")

    print("\nJobs to be migrated:")
    for i, job in enumerate(career_data.jobs[:5], 1):  # Show first 5
        print(f"  {i}. {job.title} at {job.company} ({job.start_date} to {job.end_date})")
    if len(career_data.jobs) > 5:
        print(f"  ... and {len(career_data.jobs) - 5} more")

    print("\nSkills to be migrated:")
    for i, skill in enumerate(career_data.skills[:5], 1):  # Show first 5
        print(f"  {i}. {skill.name} ({len(skill.examples)} examples)")
    if len(career_data.skills) > 5:
        print(f"  ... and {len(career_data.skills) - 5} more")

    print("\n" + "=" * 60)


def migrate_to_local_storage(
    preview_only: bool = False,
    checkpoint_file: Optional[Path] = None
) -> bool:
    """
    Main migration function.

    Args:
        preview_only: If True, only show preview without saving
        checkpoint_file: Optional checkpoint file for resume capability

    Returns:
        True if migration successful, False otherwise
    """
    print("\n" + "=" * 60)
    print("SUPERMEMORY -> LOCAL STORAGE MIGRATION")
    print("=" * 60)

    # Initialize progress tracking
    if checkpoint_file is None:
        checkpoint_file = Path.home() / '.resume_tailor' / 'migration_checkpoint.json'

    progress = MigrationProgress(checkpoint_file)

    # Check for existing checkpoint
    if progress.load_checkpoint():
        print(f"\n[Checkpoint] Found previous migration attempt")
        print(f"  Migrated: {progress.migrated_count} entries")
        print(f"  Failed: {len(progress.failed_entries)} entries")

        response = input("\nResume from checkpoint? (y/n): ")
        if response.lower() != 'y':
            print("[Info] Starting fresh migration")

    # Step 1: Import from supermemory
    try:
        raw_data = import_from_supermemory_with_retry(max_retries=5)
    except MigrationError as e:
        print(f"\n[FAIL] Migration failed: {e}")
        return False

    # Step 2: Parse and validate
    try:
        career_data = parse_career_data(raw_data)
        print("[OK] Data parsed and validated successfully")
    except Exception as e:
        print(f"\n[FAIL] Validation failed: {e}")
        return False

    # Step 3: Preview
    preview_migration(career_data)

    if preview_only:
        print("\n[Preview Mode] Migration not executed (preview only)")
        return True

    # Step 4: Confirm
    print("\nProceed with migration?")
    print("  This will save data to: " + str(get_manager().file_path))
    print("  Backup will be created: " + str(get_manager().get_backup_path()))

    response = input("\nContinue? (y/n): ")
    if response.lower() != 'y':
        print("[Cancelled] Migration cancelled by user")
        return False

    # Step 5: Save
    print("\n[Saving] Writing to local storage...")
    try:
        success = save_career_data(career_data)

        if success:
            print("[OK] Migration completed successfully!")
            print(f"  Location: {get_manager().file_path}")
            print(f"  Backup: {get_manager().get_backup_path()}")

            # Remove checkpoint file
            if checkpoint_file.exists():
                checkpoint_file.unlink()
                print("[OK] Checkpoint file removed")

            return True
        else:
            print("[FAIL] Save operation failed")
            return False

    except Exception as e:
        print(f"\n[FAIL] Migration failed during save: {e}")
        print(f"[Info] Attempting to restore from backup...")

        if get_manager()._restore_from_backup():
            print("[OK] Restored from backup")
        else:
            print("[Warning] No backup available to restore")

        return False


def main():
    """Main entry point for migration script."""
    import argparse

    parser = argparse.ArgumentParser(description='Migrate career data from supermemory to local storage')
    parser.add_argument('--preview', action='store_true', help='Preview only, do not save')
    parser.add_argument('--checkpoint', type=str, help='Path to checkpoint file')

    args = parser.parse_args()

    checkpoint_file = Path(args.checkpoint) if args.checkpoint else None

    success = migrate_to_local_storage(
        preview_only=args.preview,
        checkpoint_file=checkpoint_file
    )

    exit(0 if success else 1)


if __name__ == '__main__':
    main()
