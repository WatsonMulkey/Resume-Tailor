"""
Interactive LinkedIn Import - Review and Edit Mode

Shows each piece of LinkedIn data one by one for review and editing
before adding to career data.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from models import CareerData, Job, Skill, Education, Certification
from career_data_manager import load_career_data, save_career_data
from import_linkedin import parse_linkedin_export, compare_with_career_data


def review_job(job_data: Dict[str, Any], index: int, total: int) -> Optional[Dict[str, Any]]:
    """
    Review a single job entry.

    Returns:
        Updated job data if user approves, None if skipped
    """
    print("\n" + "="*80)
    print(f"JOB #{index}/{total}: {job_data['title']} at {job_data['company']}")
    print("="*80)

    print(f"\nCompany:     {job_data['company']}")
    print(f"Title:       {job_data['title']}")
    print(f"Dates:       {job_data['start_date']} to {job_data['end_date']}")
    print(f"Location:    {job_data['location']}")
    print(f"\nDescription:")
    print("-" * 80)
    if job_data['description']:
        # Word wrap the description
        desc = job_data['description']
        print(desc)
    else:
        print("(No description)")
    print("-" * 80)

    while True:
        print("\nOptions:")
        print("  [a] Add as-is")
        print("  [e] Edit before adding")
        print("  [s] Skip this job")
        print("  [q] Quit import process")

        choice = input("\nYour choice: ").strip().lower()

        if choice == 'a':
            return job_data
        elif choice == 'e':
            return edit_job(job_data)
        elif choice == 's':
            print("  >> Skipped")
            return None
        elif choice == 'q':
            print("\nExiting import process...")
            exit(0)
        else:
            print("Invalid choice. Please enter a, e, s, or q.")


def edit_job(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interactive job editor.
    """
    print("\n" + "-"*80)
    print("EDIT JOB")
    print("-"*80)

    # Edit company
    new_company = input(f"\nCompany [{job_data['company']}]: ").strip()
    if new_company:
        job_data['company'] = new_company

    # Edit title
    new_title = input(f"Title [{job_data['title']}]: ").strip()
    if new_title:
        job_data['title'] = new_title

    # Edit start date
    new_start = input(f"Start date (YYYY-MM) [{job_data['start_date']}]: ").strip()
    if new_start:
        job_data['start_date'] = new_start

    # Edit end date
    new_end = input(f"End date (YYYY-MM or 'Present') [{job_data['end_date']}]: ").strip()
    if new_end:
        job_data['end_date'] = new_end

    # Edit location
    new_location = input(f"Location [{job_data['location']}]: ").strip()
    if new_location:
        job_data['location'] = new_location

    # Edit description
    print(f"\nCurrent description ({len(job_data['description'])} chars):")
    print(job_data['description'][:200] + "..." if len(job_data['description']) > 200 else job_data['description'])

    edit_desc = input("\nEdit description? (y/n): ").strip().lower()
    if edit_desc == 'y':
        print("\nEnter new description (press Ctrl+Z then Enter when done on Windows, Ctrl+D on Unix):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass

        new_desc = '\n'.join(lines).strip()
        if new_desc:
            job_data['description'] = new_desc

    print("\n  >> Job updated")
    return job_data


def review_job_update(update_data: Dict[str, Any], index: int, total: int) -> bool:
    """
    Review a job description update.

    Returns:
        True to apply update, False to skip
    """
    print("\n" + "="*80)
    print(f"UPDATE #{index}/{total}: {update_data['title']} at {update_data['company']}")
    print("="*80)

    print("\nCURRENT DESCRIPTION:")
    print("-" * 80)
    if update_data['old_description']:
        print(update_data['old_description'])
    else:
        print("(Empty)")
    print("-" * 80)

    print(f"\nLINKEDIN DESCRIPTION ({len(update_data['new_description'])} chars):")
    print("-" * 80)
    print(update_data['new_description'])
    print("-" * 80)

    while True:
        print("\nOptions:")
        print("  [r] Replace current with LinkedIn description")
        print("  [k] Keep current description (skip)")
        print("  [q] Quit import process")

        choice = input("\nYour choice: ").strip().lower()

        if choice == 'r':
            print("  >> Will update description")
            return True
        elif choice == 'k':
            print("  >> Keeping current description")
            return False
        elif choice == 'q':
            print("\nExiting import process...")
            exit(0)
        else:
            print("Invalid choice. Please enter r, k, or q.")


def review_certification(cert_data: Dict[str, Any], index: int, total: int) -> Optional[Dict[str, Any]]:
    """
    Review a single certification.

    Returns:
        Certification data if approved, None if skipped
    """
    print("\n" + "="*80)
    print(f"CERTIFICATION #{index}/{total}")
    print("="*80)

    print(f"\nTitle:        {cert_data['title']}")
    print(f"Organization: {cert_data['organization']}")
    print(f"Date:         {cert_data['date_obtained']}")

    while True:
        print("\nOptions:")
        print("  [a] Add")
        print("  [s] Skip")
        print("  [q] Quit import process")

        choice = input("\nYour choice: ").strip().lower()

        if choice == 'a':
            return cert_data
        elif choice == 's':
            print("  >> Skipped")
            return None
        elif choice == 'q':
            print("\nExiting import process...")
            exit(0)
        else:
            print("Invalid choice. Please enter a, s, or q.")


def review_education(edu_data: Dict[str, Any], index: int, total: int) -> Optional[Dict[str, Any]]:
    """
    Review a single education entry.

    Returns:
        Updated education data if approved, None if skipped
    """
    print("\n" + "="*80)
    print(f"EDUCATION #{index}/{total}")
    print("="*80)

    print(f"\nSchool:     {edu_data['school']}")
    print(f"Degree:     {edu_data['degree']}")
    print(f"Dates:      {edu_data['dates']}")
    if edu_data['activities']:
        print(f"Activities: {edu_data['activities']}")

    while True:
        print("\nOptions:")
        print("  [a] Add as-is")
        print("  [e] Edit before adding")
        print("  [s] Skip")
        print("  [q] Quit import process")

        choice = input("\nYour choice: ").strip().lower()

        if choice == 'a':
            return edu_data
        elif choice == 'e':
            return edit_education(edu_data)
        elif choice == 's':
            print("  >> Skipped")
            return None
        elif choice == 'q':
            print("\nExiting import process...")
            exit(0)
        else:
            print("Invalid choice. Please enter a, e, s, or q.")


def edit_education(edu_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interactive education editor.
    """
    print("\n" + "-"*80)
    print("EDIT EDUCATION")
    print("-"*80)

    # Edit school (CRITICAL - LinkedIn export had it as "Unknown")
    new_school = input(f"\nSchool name [{edu_data['school']}]: ").strip()
    if new_school:
        edu_data['school'] = new_school

    # Edit degree
    new_degree = input(f"Degree [{edu_data['degree']}]: ").strip()
    if new_degree:
        edu_data['degree'] = new_degree

    # Edit dates
    new_dates = input(f"Dates [{edu_data['dates']}]: ").strip()
    if new_dates:
        edu_data['dates'] = new_dates

    # Edit activities
    new_activities = input(f"Activities [{edu_data['activities']}]: ").strip()
    if new_activities:
        edu_data['activities'] = new_activities

    print("\n  >> Education updated")
    return edu_data


def main():
    """Main interactive import function."""
    print("=" * 80)
    print("  LinkedIn Import - Interactive Review Mode")
    print("=" * 80)
    print("\nThis will show you each piece of LinkedIn data for review before adding.")
    print("You can edit, skip, or add each item individually.")

    # Paths
    export_dir = Path(r"C:\Users\watso\Downloads\linkedin_export")

    if not export_dir.exists():
        print(f"\n[ERROR] LinkedIn export not found at {export_dir}")
        print("Please extract your LinkedIn export first.")
        return

    # Load existing career data
    print("\nLoading existing career data...")
    career_data = load_career_data()
    print(f"[OK] Loaded {len(career_data.jobs)} jobs, {len(career_data.skills)} skills")

    # Parse LinkedIn export
    print("\nParsing LinkedIn export...")
    linkedin_data = parse_linkedin_export(export_dir)
    print(f"[OK] Found {len(linkedin_data['positions'])} positions, {len(linkedin_data['skills'])} skills")

    # Compare
    print("\nComparing data...")
    differences = compare_with_career_data(linkedin_data, career_data)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY OF NET NEW INFORMATION")
    print("="*80)
    print(f"  New jobs:          {len(differences['new_jobs'])}")
    print(f"  Job updates:       {len(differences['job_updates'])}")
    print(f"  New skills:        {len(differences['new_skills'])} (will skip - add via Discovery Mode)")
    print(f"  New education:     {len(differences['new_education'])}")
    print(f"  New certifications: {len(differences['new_certifications'])}")

    input("\nPress Enter to begin interactive review...")

    # Track what we're adding
    jobs_to_add = []
    jobs_to_update = []
    certs_to_add = []
    edu_to_add = []

    # Review new jobs
    if differences['new_jobs']:
        print("\n\n" + "="*80)
        print("REVIEWING NEW JOBS")
        print("="*80)

        for i, job_data in enumerate(differences['new_jobs'], 1):
            result = review_job(job_data, i, len(differences['new_jobs']))
            if result:
                jobs_to_add.append(result)

    # Review job updates
    if differences['job_updates']:
        print("\n\n" + "="*80)
        print("REVIEWING JOB DESCRIPTION UPDATES")
        print("="*80)

        for i, update_data in enumerate(differences['job_updates'], 1):
            if review_job_update(update_data, i, len(differences['job_updates'])):
                jobs_to_update.append(update_data)

    # Review certifications
    if differences['new_certifications']:
        print("\n\n" + "="*80)
        print("REVIEWING CERTIFICATIONS")
        print("="*80)

        for i, cert_data in enumerate(differences['new_certifications'], 1):
            result = review_certification(cert_data, i, len(differences['new_certifications']))
            if result:
                certs_to_add.append(result)

    # Review education
    if differences['new_education']:
        print("\n\n" + "="*80)
        print("REVIEWING EDUCATION")
        print("="*80)

        for i, edu_data in enumerate(differences['new_education'], 1):
            result = review_education(edu_data, i, len(differences['new_education']))
            if result:
                edu_to_add.append(result)

    # Summary of changes
    print("\n\n" + "="*80)
    print("REVIEW COMPLETE - SUMMARY OF CHANGES")
    print("="*80)
    print(f"  Jobs to add:            {len(jobs_to_add)}")
    print(f"  Jobs to update:         {len(jobs_to_update)}")
    print(f"  Certifications to add:  {len(certs_to_add)}")
    print(f"  Education to add:       {len(edu_to_add)}")

    if not any([jobs_to_add, jobs_to_update, certs_to_add, edu_to_add]):
        print("\nNo changes to apply.")
        return

    # Confirm
    confirm = input("\nApply these changes to your career data? (yes/no): ").strip().lower()

    if confirm != 'yes':
        print("\nNo changes made.")
        return

    # Apply changes
    print("\nApplying changes...")

    # Add new jobs
    for job_data in jobs_to_add:
        print(f"  + Adding: {job_data['title']} at {job_data['company']}")
        new_job = Job(
            company=job_data['company'],
            title=job_data['title'],
            start_date=job_data['start_date'],
            end_date=job_data['end_date'],
            location=job_data['location'],
            description=job_data['description']
        )
        career_data.jobs.append(new_job)

    # Update job descriptions
    for update in jobs_to_update:
        print(f"  * Updating: {update['title']} at {update['company']}")
        for job in career_data.jobs:
            if (job.company.lower() == update['company'].lower() and
                job.title.lower() == update['title'].lower()):
                job.description = update['new_description']
                break

    # Add certifications
    for cert_data in certs_to_add:
        print(f"  + Adding certification: {cert_data['title']}")
        new_cert = Certification(
            title=cert_data['title'],
            organization=cert_data['organization'],
            date_obtained=cert_data['date_obtained']
        )
        career_data.certifications.append(new_cert)

    # Add education
    for edu_data in edu_to_add:
        print(f"  + Adding education: {edu_data['degree']} from {edu_data['school']}")
        new_edu = Education(
            school=edu_data['school'],
            degree=edu_data['degree'],
            dates=edu_data['dates'],
            details=[edu_data['activities']] if edu_data['activities'] else []
        )
        career_data.education.append(new_edu)

    # Save
    print("\nSaving career data...")
    save_career_data(career_data)
    print("[OK] Career data updated successfully!")

    print("\n" + "="*80)
    print("IMPORT COMPLETE")
    print("="*80)

    if differences['new_skills']:
        print(f"\n[NOTE] {len(differences['new_skills'])} skills from LinkedIn were not added.")
        print("Use Discovery Mode when generating resumes to add skills with specific examples.")


if __name__ == '__main__':
    main()
