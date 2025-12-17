#!/usr/bin/env python3
"""
Resume Tailor - AI-powered resume and cover letter customization tool

This CLI tool uses supermemory for career data storage and Claude API for generation
to create tailored resumes and cover letters with zero hallucinations.
"""

import argparse
import json
import sys
import os
from pathlib import Path


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate tailored resumes and cover letters for job applications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from job description file
  resume-tailor --job job_description.txt

  # Generate from pasted text
  resume-tailor --paste

  # Specify output directory
  resume-tailor --job job_description.txt --output-dir ./applications/company-name

  # Generate only cover letter
  resume-tailor --job job_description.txt --cover-letter-only

  # Generate only resume
  resume-tailor --job job_description.txt --resume-only
        """
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--job',
        type=str,
        help='Path to job description file'
    )
    input_group.add_argument(
        '--paste',
        action='store_true',
        help='Paste job description interactively'
    )
    input_group.add_argument(
        '--url',
        type=str,
        help='URL to job posting (will attempt to fetch and parse)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for generated documents (default: C:\\Users\\watso\\OneDrive\\Desktop\\Jobs\\<company-name>)'
    )

    parser.add_argument(
        '--company-name',
        type=str,
        help='Company name (helps with file naming and personalization)'
    )

    parser.add_argument(
        '--resume-only',
        action='store_true',
        help='Generate only the resume'
    )

    parser.add_argument(
        '--cover-letter-only',
        action='store_true',
        help='Generate only the cover letter'
    )

    parser.add_argument(
        '--format',
        type=str,
        choices=['markdown', 'pdf', 'html', 'docx', 'all'],
        default='markdown',
        help='Output format: markdown (default), pdf (ReportLab), html (styled, print to PDF), docx (ATS-friendly Word), all (all formats)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed information during processing'
    )

    return parser.parse_args()


def get_job_description(args):
    """Get job description from various sources."""
    if args.job:
        # Read from file
        job_file = Path(args.job)
        if not job_file.exists():
            print(f"Error: File '{args.job}' not found")
            sys.exit(1)

        with open(job_file, 'r', encoding='utf-8') as f:
            return f.read()

    elif args.paste:
        # Interactive paste
        print("Paste the job description below (press Ctrl+D or Ctrl+Z then Enter when done):")
        print("-" * 60)
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass

        return '\n'.join(lines)

    elif args.url:
        # Fetch from URL
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            print("Error: URL fetching requires 'requests' and 'beautifulsoup4'")
            print("Install with: pip install requests beautifulsoup4")
            sys.exit(1)

        try:
            print(f"Fetching job description from {args.url}...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(args.url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            if not text.strip():
                print("Error: Could not extract text from URL")
                sys.exit(1)

            print(f"Successfully fetched {len(text)} characters")
            return text

        except requests.RequestException as e:
            print(f"Error fetching URL: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error processing URL content: {e}")
            sys.exit(1)


def main():
    """Main entry point for the CLI tool."""
    args = parse_arguments()

    # Get job description
    if args.verbose:
        print("Reading job description...")

    job_description = get_job_description(args)

    if not job_description.strip():
        print("Error: Job description is empty")
        sys.exit(1)

    if args.verbose:
        print(f"Job description loaded ({len(job_description)} characters)")
        print()

    # Import the generator
    from generator import ResumeGenerator

    generator = ResumeGenerator(verbose=args.verbose)

    # Determine company name (need to parse job description if not provided)
    company_name = args.company_name
    if not company_name and not args.output_dir:
        # Quick parse to get company name for folder
        if args.verbose:
            print("Parsing job description to determine company name...")
        temp_job_info = generator.parser.parse(job_description)
        company_name = temp_job_info.get('company', 'Unknown_Company')

    # Create output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        # Default: C:\Users\watso\OneDrive\Desktop\Jobs\<company-name>
        base_jobs_dir = Path(r"C:\Users\watso\OneDrive\Desktop\Jobs")
        safe_company_name = company_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        output_dir = base_jobs_dir / safe_company_name

    output_dir.mkdir(parents=True, exist_ok=True)

    if args.verbose:
        print(f"Output directory: {output_dir.absolute()}")
        print()

    # Generate documents
    print("Analyzing job description...")
    results = generator.generate(
        job_description=job_description,
        company_name=company_name,
        output_dir=output_dir,
        resume_only=args.resume_only,
        cover_letter_only=args.cover_letter_only,
        output_format=args.format
    )

    # Print results
    print()
    print("Generation complete!")
    print()
    print("Generated files:")
    for file_path in results['files']:
        print(f"  - {file_path}")

    print()
    print("Next steps:")
    print("  1. Review the generated documents")
    print("  2. Customize any sections that need personal touches")
    print("  3. Verify all facts against your actual experience")
    print("  4. Submit your application!")


if __name__ == '__main__':
    main()
