"""
Import LinkedIn Export Data

Parses LinkedIn CSV export and compares with existing career data
to identify and import net new information.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime

from models import CareerData, Job, Skill, Education, Certification
from career_data_manager import load_career_data, save_career_data


def parse_linkedin_export(export_dir: Path) -> Dict[str, Any]:
    """
    Parse LinkedIn export directory and extract structured data.

    Args:
        export_dir: Path to extracted LinkedIn export directory

    Returns:
        Dictionary with parsed data
    """
    data = {
        'profile': {},
        'positions': [],
        'skills': [],
        'education': [],
        'certifications': []
    }

    # Parse Profile
    profile_file = export_dir / 'Profile.csv'
    if profile_file.exists():
        with open(profile_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data['profile'] = {
                    'first_name': row.get('First Name', ''),
                    'last_name': row.get('Last Name', ''),
                    'headline': row.get('Headline', ''),
                    'summary': row.get('Summary', ''),
                    'location': row.get('Geo Location', ''),
                }
                break  # Only one row

    # Parse Positions
    positions_file = export_dir / 'Positions.csv'
    if positions_file.exists():
        with open(positions_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get('Company Name'):
                    continue

                # Parse dates
                start_date = parse_linkedin_date(row.get('Started On', ''))
                end_date = parse_linkedin_date(row.get('Finished On', ''))

                data['positions'].append({
                    'company': row.get('Company Name', ''),
                    'title': row.get('Title', ''),
                    'description': row.get('Description', ''),
                    'location': row.get('Location', ''),
                    'start_date': start_date,
                    'end_date': end_date if end_date else 'Present'
                })

    # Parse Skills
    skills_file = export_dir / 'Skills.csv'
    if skills_file.exists():
        with open(skills_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                skill_name = row.get('Name', '').strip()
                if skill_name:
                    data['skills'].append(skill_name)

    # Parse Education
    education_file = export_dir / 'Education.csv'
    if education_file.exists():
        with open(education_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                school = row.get('School Name', '').strip()
                degree = row.get('Degree Name', '').strip()

                if degree:  # Only add if there's a degree
                    start = row.get('Start Date', '')
                    end = row.get('End Date', '')
                    dates = f"{start}-{end}" if start and end else ''

                    data['education'].append({
                        'school': school if school else 'Unknown',
                        'degree': degree,
                        'dates': dates,
                        'activities': row.get('Activities', ''),
                        'notes': row.get('Notes', '')
                    })

    # Parse Certifications
    cert_file = export_dir / 'Certifications.csv'
    if cert_file.exists():
        with open(cert_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cert_name = row.get('Name', '').strip()
                if cert_name:
                    data['certifications'].append({
                        'title': cert_name,
                        'organization': row.get('Authority', ''),
                        'date_obtained': row.get('Started On', ''),
                        'url': row.get('Url', '')
                    })

    return data


def parse_linkedin_date(date_str: str) -> str:
    """
    Convert LinkedIn date format to YYYY-MM format.

    Examples:
        'Jan 2024' -> '2024-01'
        '2025' -> '2025-01'
        'Dec 2020' -> '2020-12'
    """
    if not date_str:
        return ''

    date_str = date_str.strip()

    # If it's just a year
    if date_str.isdigit() and len(date_str) == 4:
        return f"{date_str}-01"

    # If it's "Mon YYYY" format
    months = {
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
        'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
    }

    parts = date_str.lower().split()
    if len(parts) == 2:
        month_str = parts[0][:3]  # First 3 chars
        year = parts[1]
        if month_str in months:
            return f"{year}-{months[month_str]}"

    return date_str


def compare_with_career_data(linkedin_data: Dict[str, Any], career_data: CareerData) -> Dict[str, Any]:
    """
    Compare LinkedIn data with existing career data and identify differences.

    Returns:
        Dictionary with net new information
    """
    differences = {
        'new_jobs': [],
        'job_updates': [],
        'new_skills': [],
        'new_education': [],
        'new_certifications': [],
        'profile_updates': {}
    }

    # Compare jobs
    existing_jobs = {
        (job.company.lower(), job.title.lower()): job
        for job in career_data.jobs
    }

    for linkedin_job in linkedin_data['positions']:
        key = (linkedin_job['company'].lower(), linkedin_job['title'].lower())

        if key not in existing_jobs:
            differences['new_jobs'].append(linkedin_job)
        else:
            # Check if description is more detailed in LinkedIn
            existing = existing_jobs[key]
            if linkedin_job['description'] and len(linkedin_job['description']) > len(existing.description or ''):
                differences['job_updates'].append({
                    'company': linkedin_job['company'],
                    'title': linkedin_job['title'],
                    'old_description': existing.description,
                    'new_description': linkedin_job['description']
                })

    # Compare skills
    existing_skills = {skill.name.lower() for skill in career_data.skills}

    for linkedin_skill in linkedin_data['skills']:
        if linkedin_skill.lower() not in existing_skills:
            differences['new_skills'].append(linkedin_skill)

    # Compare education
    existing_education = {
        (edu.school.lower(), edu.degree.lower()): edu
        for edu in career_data.education
    }

    for linkedin_edu in linkedin_data['education']:
        key = (linkedin_edu['school'].lower(), linkedin_edu['degree'].lower())
        if key not in existing_education:
            differences['new_education'].append(linkedin_edu)

    # Compare certifications
    existing_certs = {cert.title.lower() for cert in career_data.certifications}

    for linkedin_cert in linkedin_data['certifications']:
        if linkedin_cert['title'].lower() not in existing_certs:
            differences['new_certifications'].append(linkedin_cert)

    # Profile updates (headline, summary)
    if linkedin_data['profile'].get('headline'):
        differences['profile_updates']['headline'] = linkedin_data['profile']['headline']
    if linkedin_data['profile'].get('summary'):
        differences['profile_updates']['summary'] = linkedin_data['profile']['summary']

    return differences


def print_differences(differences: Dict[str, Any]):
    """Print differences in a readable format."""
    print("\n" + "="*80)
    print("NET NEW INFORMATION FROM LINKEDIN")
    print("="*80)

    # New Jobs
    if differences['new_jobs']:
        print(f"\n[NEW JOBS] {len(differences['new_jobs'])} position(s) not in career data:")
        for i, job in enumerate(differences['new_jobs'], 1):
            print(f"\n  {i}. {job['title']} at {job['company']}")
            print(f"     Dates: {job['start_date']} to {job['end_date']}")
            print(f"     Location: {job['location']}")
            if job['description']:
                desc = job['description'][:200]
                print(f"     Description: {desc}...")
    else:
        print("\n[NEW JOBS] None - all jobs already in career data")

    # Job Updates
    if differences['job_updates']:
        print(f"\n[JOB UPDATES] {len(differences['job_updates'])} job(s) have more detailed descriptions on LinkedIn:")
        for i, update in enumerate(differences['job_updates'], 1):
            print(f"\n  {i}. {update['title']} at {update['company']}")
            print(f"     Current length: {len(update['old_description'] or '')} chars")
            print(f"     LinkedIn length: {len(update['new_description'])} chars")
    else:
        print("\n[JOB UPDATES] None")

    # New Skills
    if differences['new_skills']:
        print(f"\n[NEW SKILLS] {len(differences['new_skills'])} skill(s) not in career data:")
        for skill in differences['new_skills']:
            print(f"  - {skill}")
    else:
        print("\n[NEW SKILLS] None - all skills already in career data")

    # New Education
    if differences['new_education']:
        print(f"\n[NEW EDUCATION] {len(differences['new_education'])} education entry(ies) not in career data:")
        for i, edu in enumerate(differences['new_education'], 1):
            print(f"\n  {i}. {edu['degree']} from {edu['school']}")
            print(f"     Dates: {edu['dates']}")
            if edu['activities']:
                print(f"     Activities: {edu['activities']}")
    else:
        print("\n[NEW EDUCATION] None - all education already in career data")

    # New Certifications
    if differences['new_certifications']:
        print(f"\n[NEW CERTIFICATIONS] {len(differences['new_certifications'])} certification(s) not in career data:")
        for i, cert in enumerate(differences['new_certifications'], 1):
            print(f"\n  {i}. {cert['title']}")
            print(f"     Organization: {cert['organization']}")
            print(f"     Date: {cert['date_obtained']}")
    else:
        print("\n[NEW CERTIFICATIONS] None - all certifications already in career data")

    # Profile Updates
    if differences['profile_updates']:
        print(f"\n[PROFILE INFORMATION] Available from LinkedIn:")
        if differences['profile_updates'].get('headline'):
            print(f"  Headline: {differences['profile_updates']['headline']}")
        if differences['profile_updates'].get('summary'):
            summary = differences['profile_updates']['summary'][:200]
            print(f"  Summary: {summary}...")

    print("\n" + "="*80)


def main():
    """Main import function."""
    print("=" * 60)
    print("  LinkedIn Import - Data Comparison")
    print("=" * 60)

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

    # Print differences
    print_differences(differences)

    # Offer to add new data
    print("\n" + "="*80)
    choice = input("\nWould you like to add this new information to your career data? (yes/no): ").strip().lower()

    if choice == 'yes':
        add_linkedin_data_to_career(linkedin_data, differences, career_data)
    else:
        print("\nNo changes made. You can run this script again anytime.")


def add_linkedin_data_to_career(linkedin_data: Dict[str, Any], differences: Dict[str, Any], career_data: CareerData):
    """Add new LinkedIn data to career data."""
    print("\nAdding new information to career data...")

    # Add new jobs
    for job_data in differences['new_jobs']:
        print(f"  + Adding job: {job_data['title']} at {job_data['company']}")
        # Note: We'll add jobs without achievements/responsibilities initially
        # User can add those through discovery mode later
        new_job = Job(
            company=job_data['company'],
            title=job_data['title'],
            start_date=job_data['start_date'],
            end_date=job_data['end_date'],
            location=job_data['location'],
            description=job_data['description']
        )
        career_data.jobs.append(new_job)

    # Note: Skills from LinkedIn don't have examples, so we'll skip adding them automatically
    # The user should add skills through discovery mode to ensure they have proper examples
    if differences['new_skills']:
        print(f"\n  ℹ Skipping {len(differences['new_skills'])} skills - add them through Discovery Mode to include examples")

    # Add new education
    for edu_data in differences['new_education']:
        print(f"  + Adding education: {edu_data['degree']} from {edu_data['school']}")
        new_edu = Education(
            school=edu_data['school'],
            degree=edu_data['degree'],
            dates=edu_data['dates'],
            details=[edu_data['activities']] if edu_data['activities'] else []
        )
        career_data.education.append(new_edu)

    # Add new certifications
    for cert_data in differences['new_certifications']:
        print(f"  + Adding certification: {cert_data['title']}")
        new_cert = Certification(
            title=cert_data['title'],
            organization=cert_data['organization'],
            date_obtained=cert_data['date_obtained']
        )
        career_data.certifications.append(new_cert)

    # Save
    print("\nSaving career data...")
    save_career_data(career_data)
    print("[OK] Career data updated successfully!")

    if differences['new_skills']:
        print(f"\n[TIP] Use Discovery Mode when generating your next resume to add the {len(differences['new_skills'])} new skills with examples.")


if __name__ == '__main__':
    main()
