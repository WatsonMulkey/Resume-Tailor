"""
Core generation logic for resume and cover letter tailoring.

This module handles:
- Job description parsing and keyword extraction
- Local career data retrieval (from career_data.json)
- Claude API calls with anti-hallucination prompts
- Document formatting and output
"""

import os
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, that's okay
import anthropic

import config

try:
    from pdf_generator import markdown_to_pdf, generate_pdf_from_data, generate_cover_letter_pdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


def sanitize_filename(name: str) -> str:
    """Sanitize a string for use in filenames. Removes all characters except alphanumeric, underscore, and hyphen."""
    return re.sub(r'[^a-zA-Z0-9_-]', '', name.replace(' ', '_'))

try:
    from html_template import generate_html_resume
    HTML_AVAILABLE = True
except ImportError:
    HTML_AVAILABLE = False

try:
    from docx_generator import generate_docx_resume, parse_markdown_to_docx_data, generate_docx_cover_letter
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Import provenance tracking
try:
    from provenance import (
        ProvenanceTrace, DocumentProvenance, generate_trace_document
    )
    from trace_validator import ProvenanceValidator, validate_and_report
    PROVENANCE_AVAILABLE = True
except ImportError:
    PROVENANCE_AVAILABLE = False

# Import contact info to prevent hallucination
try:
    from import_career_data import CAREER_DATA
    CONTACT_INFO = CAREER_DATA["contact_info"]
except ImportError:
    # Fallback hardcoded contact info
    CONTACT_INFO = {
        "name": "M. Watson Mulkey",
        "email": "watsonmulkey@gmail.com",
        "phone": "434-808-2493",
        "linkedin": "linkedin.com/in/watsonmulkey",
        "location": "Denver, Colorado"
    }


class JobDescriptionParser:
    """Parse job descriptions to extract key requirements and context."""

    def parse(self, job_description: str) -> Dict[str, Any]:
        """
        Extract structured information from job description.

        Returns:
            Dict with keys: company, title, requirements, skills, responsibilities, etc.
        """
        # Check if API key is available
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("Warning: ANTHROPIC_API_KEY not set. Using basic parsing.")
            return self._basic_parse(job_description)

        # Use Claude to parse the job description
        client = anthropic.Anthropic(api_key=api_key)

        message = call_claude_with_retry(
            client,
            model=config.CLAUDE_MODEL,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Parse this job description and extract structured information.

Job Description:
{job_description}

Return a JSON object with these fields:
- company: company name (or "Unknown" if not found)
- title: job title
- required_skills: list of required skills/technologies
- preferred_skills: list of preferred/nice-to-have skills
- responsibilities: list of key responsibilities
- qualifications: list of qualifications/requirements
- keywords: list of important keywords for ATS optimization
- company_mission: any info about company mission/values (if mentioned)
- team_size: team size if mentioned
- remote_policy: remote/hybrid/onsite if mentioned

Only include information actually present in the job description. Don't invent anything."""
            }]
        )

        # Extract JSON from response
        response_text = message.content[0].text

        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

        # Fallback: return basic structure
        return {
            "company": "Unknown",
            "title": "Unknown",
            "required_skills": [],
            "preferred_skills": [],
            "responsibilities": [],
            "qualifications": [],
            "keywords": [],
            "company_mission": None,
            "team_size": None,
            "remote_policy": None
        }

    def _basic_parse(self, job_description: str) -> Dict[str, Any]:
        """Basic parsing without Claude API - uses simple heuristics."""
        lines = job_description.split('\n')

        result = {
            "company": "Unknown",
            "title": "Unknown",
            "required_skills": [],
            "preferred_skills": [],
            "responsibilities": [],
            "qualifications": [],
            "keywords": [],
            "company_mission": None,
            "team_size": None,
            "remote_policy": None
        }

        # Try to extract title (first non-empty line often contains it)
        for line in lines[:5]:
            line = line.strip()
            if line and not line.startswith('About'):
                result["title"] = line
                break

        # Extract key terms as skills/keywords
        skill_keywords = ['SQL', 'Python', 'Java', 'React', 'Vue', 'AWS', 'Azure',
                         'Looker', 'Analytics', 'A/B testing', 'Agile', 'Product Management',
                         'Data Analysis', 'Leadership', 'Stakeholder']

        for keyword in skill_keywords:
            if keyword.lower() in job_description.lower():
                result["required_skills"].append(keyword)
                result["keywords"].append(keyword)

        # Check for remote policy
        if 'remote' in job_description.lower():
            result["remote_policy"] = "Remote or Hybrid"

        return result


class LocalCareerDataRetriever:
    """Retrieve relevant career information from local JSON storage."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def _log(self, message: str):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"  [Local Data] {message}")

    def retrieve_relevant_context(self, job_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Load career data from local storage and format for AI generation.

        Returns:
            Dict with categories of relevant information as combined strings
        """
        context = {
            "career_history": "",  # NEW: unified format with achievements inline
            "achievements": "",    # Legacy: kept for backward compatibility
            "skills": "",
            "jobs": "",            # Legacy: kept for backward compatibility
            "writing_style": "",
            "personal_values": "",
            "education": "",
            "certifications": ""
        }

        try:
            # Import career_data_manager (local import to avoid circular dependency)
            from career_data_manager import load_career_data

            self._log("Loading career data from local storage...")
            career_data = load_career_data()

            # NEW: Format career history with achievements inline (prevents misattribution)
            context["career_history"] = self._format_career_history_with_provenance(career_data)

            # Legacy formats (kept for backward compatibility)
            context["achievements"] = self._format_achievements(career_data)
            context["skills"] = self._format_skills(career_data)
            context["jobs"] = self._format_jobs(career_data)

            # Format writing style (from personal values if available)
            context["writing_style"] = self._get_writing_style(career_data)

            # Format personal values
            context["personal_values"] = self._format_personal_values(career_data)

            # Format education and certifications
            context["education"] = self._format_education(career_data)
            context["certifications"] = self._format_certifications(career_data)

            self._log(f"Loaded: {len(career_data.jobs)} jobs, {len(career_data.skills)} skills")

        except Exception as e:
            # Fall back to import_career_data.py (hardcoded data)
            self._log(f"Local storage unavailable ({e}), using fallback data")
            context = self._get_fallback_context()

        return context

    def get_jobs_list(self) -> list:
        """
        Get list of jobs for per-job generation.

        Returns:
            List of job objects from career data
        """
        try:
            from career_data_manager import load_career_data
            career_data = load_career_data()
            return career_data.jobs
        except Exception:
            return []

    def get_single_job_context(self, job) -> Dict[str, str]:
        """
        Get context for a SINGLE job only - prevents cross-job contamination.

        This is the key fix for misattribution: the LLM only sees data
        for the specific job being written about.

        Args:
            job: A single Job object

        Returns:
            Dict with only this job's achievements and responsibilities
        """
        try:
            from career_data_manager import load_career_data
            career_data = load_career_data()
        except Exception:
            career_data = None

        job_id = getattr(job, 'id', 'unknown')
        company = job.company
        dates = f"{job.start_date} to {job.end_date or 'Present'}"
        context_text = getattr(job, 'company_context', '') or ''

        # Format achievements for THIS JOB ONLY
        achievements_text = ""
        job_achievements = []

        # Check for achievements directly on job
        if hasattr(job, 'achievements') and job.achievements:
            job_achievements.extend(job.achievements)

        # Also gather achievements from skills that reference this company
        if career_data:
            for skill in career_data.skills:
                if hasattr(skill, 'examples') and skill.examples:
                    for example in skill.examples:
                        if example.company.lower() == company.lower():
                            job_achievements.append(example)

        if job_achievements:
            ach_lines = []
            for ach in job_achievements:
                ach_id = getattr(ach, 'id', 'unknown')
                result = getattr(ach, 'result', '') or ''
                desc = getattr(ach, 'description', str(ach))
                ach_lines.append(f"  - [ACH:{ach_id}] {desc}")
                if result:
                    ach_lines.append(f"    Result: {result}")
            achievements_text = "\n".join(ach_lines)
        else:
            achievements_text = "  (No specific achievements recorded)"

        # Format responsibilities for THIS JOB ONLY
        responsibilities_text = ""
        if hasattr(job, 'responsibilities') and job.responsibilities:
            resp_lines = [f"  - {resp}" for resp in job.responsibilities[:5]]
            responsibilities_text = "\n".join(resp_lines)

        return {
            'company': company,
            'title': job.title,
            'dates': dates,
            'context': context_text,
            'job_id': job_id,
            'achievements': achievements_text,
            'responsibilities': responsibilities_text
        }

    def _format_achievements(self, career_data) -> str:
        """Format achievements for AI prompt."""
        achievements = []

        # Gather achievements from jobs
        for job in career_data.jobs:
            if hasattr(job, 'achievements') and job.achievements:
                for achievement in job.achievements:
                    achievements.append(f"{achievement.description} at {achievement.company}")

        # Gather achievements from skills
        for skill in career_data.skills:
            if hasattr(skill, 'examples') and skill.examples:
                for example in skill.examples:
                    if example.result:
                        achievements.append(f"{example.result} - {example.description} at {example.company}")

        if achievements:
            return "\n".join(achievements[:10])  # Top 10 achievements
        else:
            return self._get_fallback_achievements()

    def _format_skills(self, career_data) -> str:
        """Format skills for AI prompt."""
        skill_lines = []

        for skill in career_data.skills:
            # Format: Skill Name: Evidence/Examples
            examples = []
            if hasattr(skill, 'examples') and skill.examples:
                for example in skill.examples[:2]:  # Top 2 examples per skill
                    examples.append(f"{example.description} at {example.company}")

            evidence = "; ".join(examples) if examples else "Professional experience"
            skill_lines.append(f"{skill.name}: {evidence}")

        if skill_lines:
            return "\n".join(skill_lines)
        else:
            return self._get_fallback_skills()

    def _format_jobs(self, career_data) -> str:
        """Format job history for AI prompt."""
        job_lines = []

        for job in career_data.jobs:
            # Format: Company (Dates): Title - Key responsibilities/achievements
            dates = f"{job.start_date} to {job.end_date or 'Present'}"
            context = job.company_context if hasattr(job, 'company_context') and job.company_context else ""

            responsibilities = ""
            if hasattr(job, 'responsibilities') and job.responsibilities:
                responsibilities = ", ".join(job.responsibilities[:3])  # Top 3 responsibilities

            job_lines.append(f"{job.company} ({dates}): {job.title} - {context or responsibilities}")

        if job_lines:
            return "\n".join(job_lines)
        else:
            return self._get_fallback_jobs()

    def _format_career_history_with_provenance(self, career_data) -> str:
        """
        Format jobs with achievements INLINE - prevents misattribution.

        This is the key fix for the achievement misattribution problem:
        achievements are grouped with their source job, not in a separate section.
        Each achievement includes its ID for traceability.
        """
        history_blocks = []

        for job in career_data.jobs:
            job_id = getattr(job, 'id', 'unknown')
            dates = f"{job.start_date} to {job.end_date or 'Present'}"
            context = getattr(job, 'company_context', '') or ''

            block = f"""
=== {job.company} ({dates}) ===
[JOB_ID: {job_id}]
Title: {job.title}
Context: {context or 'N/A'}

ACHIEVEMENTS FOR THIS ROLE ONLY (do not use for other jobs):"""

            # Add achievements with IDs
            if hasattr(job, 'achievements') and job.achievements:
                for ach in job.achievements:
                    ach_id = getattr(ach, 'id', 'unknown')
                    result = getattr(ach, 'result', '') or ''
                    metrics = getattr(ach, 'metrics', []) or []
                    metrics_str = ', '.join(metrics) if metrics else 'N/A'

                    block += f"""
  - [ACH:{ach_id}] {ach.description}
    Result: {result or 'N/A'}
    Metrics: {metrics_str}"""
            else:
                block += "\n  (No recorded achievements for this role)"

            # Add responsibilities
            if hasattr(job, 'responsibilities') and job.responsibilities:
                block += f"\n\nKEY RESPONSIBILITIES:"
                for i, resp in enumerate(job.responsibilities[:4]):  # Top 4 responsibilities
                    block += f"\n  - [RESP:{job_id}:{i}] {resp}"

            history_blocks.append(block)

        if history_blocks:
            return "\n\n".join(history_blocks)
        else:
            return self._get_fallback_career_history()

    def _get_fallback_career_history(self) -> str:
        """Fallback career history with inline achievements when local data unavailable."""
        return """
=== Registria (01/2024 to 03/2025) ===
[JOB_ID: registria-2024]
Title: Senior Product Manager - ID/Onboarding/Platform
Context: Post-purchase consumer care for major brands (Sony, Whirlpool, Fujifilm)

ACHIEVEMENTS FOR THIS ROLE ONLY (do not use for other jobs):
  - [ACH:reg001] Delivered comprehensive reporting suite for flagship product
    Result: Actionable insights for major consumer brands
    Metrics: N/A

KEY RESPONSIBILITIES:
  - [RESP:registria-2024:0] Develop and maintain multi-vertical dependency roadmap
  - [RESP:registria-2024:1] Create consensus between sales, customer success, engineering, and clients


=== Discovery Education (11/2021 to 12/2023) ===
[JOB_ID: discovery-2021]
Title: Product Manager - Teacher Tools
Context: Industry leading edtech platform with 50M global user base, 1M+ MAU

ACHIEVEMENTS FOR THIS ROLE ONLY (do not use for other jobs):
  - [ACH:disc001] Improved user engagement on flagship product by 32% YoY
    Result: 32% Year-over-Year engagement increase
    Metrics: 32% YoY, 1M+ MAU
  - [ACH:disc002] Identified user flow responsible for losing 33% of traffic and recovered 10%
    Result: 33% traffic loss identified, 10% recovered in first month
    Metrics: 33% identified, 10% recovered
  - [ACH:disc003] 15% increase in delivery rate YoY through cross-functional leadership
    Result: 15% Year-over-Year delivery rate increase
    Metrics: 15% YoY, 20+ people, 5 teams

KEY RESPONSIBILITIES:
  - [RESP:discovery-2021:0] Lead team of 4-7 (design, dev, QA) and manage projects of 20+ people
  - [RESP:discovery-2021:1] Analyze and report on data trends, A/B test results to C-Suite


=== Bookshop.org (12/2020 to Present) ===
[JOB_ID: bookshop-2020]
Title: Product Consultant
Context: Independent online bookseller with over $50M in annual revenue

ACHIEVEMENTS FOR THIS ROLE ONLY (do not use for other jobs):
  (No recorded achievements for this role)

KEY RESPONSIBILITIES:
  - [RESP:bookshop-2020:0] Helping refine and validate short and long term product strategy
  - [RESP:bookshop-2020:1] Training an internally selected employee to be a product manager


=== Simplifya (01/2019 to 03/2021) ===
[JOB_ID: simplifya-2019]
Title: Product Manager
Context: Cannabis compliance software serving businesses, insurance agencies, banks

ACHIEVEMENTS FOR THIS ROLE ONLY (do not use for other jobs):
  - [ACH:simp001] Refactored flagship auditing product - 50% reduction in time-to-complete, 40% increase in usage YoY
    Result: 50% reduction in completion time, 40% usage increase YoY
    Metrics: 50% reduction, 40% increase
  - [ACH:simp002] Built 0-1 product for new industry needs
    Result: Launched new feature from scratch
    Metrics: 0-1 product launch

KEY RESPONSIBILITIES:
  - [RESP:simplifya-2019:0] Conducted user interviews and acceptance testing across various segments
  - [RESP:simplifya-2019:1] Investigated market trends and conducted competitive analysis


=== The Iron Yard (04/2017 to 09/2017) ===
[JOB_ID: ironyard-2017]
Title: Product Support Lead
Context: 12-week intensive coding school, first product person on Newline

ACHIEVEMENTS FOR THIS ROLE ONLY (do not use for other jobs):
  - [ACH:iron001] Created issue tracking system reducing open ticket time by 40%
    Result: 40% reduction in open ticket time
    Metrics: 40% reduction

KEY RESPONSIBILITIES:
  - [RESP:ironyard-2017:0] Total ownership of Customer Support functions
  - [RESP:ironyard-2017:1] Manage technical challenges for hundreds of students and staff
"""

    def _get_writing_style(self, career_data) -> str:
        """Extract writing style from personal values or use default."""
        # Look for writing style in personal values
        for value in career_data.personal_values:
            if 'writing' in value.content.lower() or 'style' in value.content.lower():
                return value.content

        # Default writing style
        return self._get_fallback_writing_style()

    def _format_personal_values(self, career_data) -> str:
        """Format personal values for AI prompt."""
        values = []

        for value in career_data.personal_values:
            # Filter out personal stories unless specifically about values/motivation
            if value.category in ['values', 'motivation']:
                values.append(value.content)

        if values:
            return "\n".join(values)
        else:
            return self._get_fallback_personal_values()

    def _get_fallback_achievements(self) -> str:
        """Fallback achievement data when supermemory unavailable."""
        return """32% YoY user engagement increase at Discovery Education - Overhauled teacher-side app based on user research
50% reduction in completion time and 40% usage increase at Simplifya - Refactored flagship auditing product
15% delivery rate increase at Discovery Education - Led cross-functional teams of 20+ people
33% traffic loss identified and 10% recovered in first month at Discovery Education
40% open ticket time reduction at The Iron Yard - Created issue tracking system
0-1 product launch at Simplifya - Built new compliance feature for regulatory needs"""

    def _get_fallback_skills(self) -> str:
        """Fallback skills data when supermemory unavailable."""
        return """Cross-functional Team Leadership: Led teams of 4-7 at Discovery (15% delivery increase), managed 20+ people across 5 teams
Data Analysis & A/B Testing: Partnered with data team, monthly C-Suite presentations, developed reporting pipelines. Tools: Looker, Fullstory, Google Analytics
User Research & Voice of Customer: Worked with teachers, booksellers internationally, conducted interviews across diverse segments
Product Strategy & Roadmapping: Multi-vertical dependency roadmaps, multi-year roadmaps, market trend investigation
Working with Less Technical Users: Explaining agile/PM concepts, training product managers, working with constrained users
Stakeholder Management: Monthly C-Suite presentations, sales/customer success alignment, client demos
Process Creation: Created agile ceremonies for distributed teams, issue tracking systems, documentation"""

    def _get_fallback_jobs(self) -> str:
        """Fallback job history when supermemory unavailable."""
        return """Registria (2024-2025): Senior PM for ID/Onboarding/Platform - Reporting suite for major brands (Sony, Whirlpool), multi-vertical roadmaps
Discovery Education (2021-2023): PM Teacher Tools - 50M user edtech platform, 32% engagement increase, A/B testing, C-Suite reporting
Bookshop.org (2020-Present): Product Consultant - $50M revenue e-commerce, global distributed teams, training PMs
Simplifya (2019-2021): PM - Cannabis compliance software, 50% efficiency gain, 40% usage increase, 0-1 product
Helix Education (2017-2018): PM - Higher education enrollment, multi-year roadmaps, vendor negotiations"""

    def _get_fallback_writing_style(self) -> str:
        """Fallback writing style when supermemory unavailable."""
        return """Opening style: Personal connection when mission-aligned, or enthusiastic professional greeting
Structure: Bullet-point mapping of job requirements to specific achievements with metrics
Tone: Warm, professional, quantified, collaborative
Common phrases: "I'd love an opportunity to...", "Here's why I'm a great fit...", "look forward to speaking soon"
Requirement mapping: Takes job requirement in quotes, provides company context, quantified outcome with underlined metrics"""

    def _get_fallback_personal_values(self) -> str:
        """Fallback personal values when supermemory unavailable."""
        # DO NOT include domain-specific personal stories by default
        return """Mission alignment: Most rewarding experiences from education (Discovery) and B-corps (Bookshop.org)
Career motivation: Seeks meaningful work creating economic mobility, supporting education, mission-driven organizations
Started career at coding school (The Iron Yard) supporting career changers"""

    def _format_education(self, career_data) -> str:
        """Format education for AI prompt."""
        if career_data.education:
            lines = []
            for edu in career_data.education:
                line = f"{edu.degree}, {edu.school}, {edu.dates}"
                if edu.details:
                    line += " - " + "; ".join(edu.details)
                lines.append(line)
            return "\n".join(lines)
        return "Bachelor of Arts - English, Hampden-Sydney College, 2004-2008"

    def _format_certifications(self, career_data) -> str:
        """Format certifications for AI prompt."""
        if career_data.certifications:
            lines = []
            for cert in career_data.certifications:
                line = f"{cert.title} ({cert.organization})"
                if cert.details:
                    line += f" - {cert.details}"
                lines.append(line)
            return "\n".join(lines)
        return "Pragmatic Marketing - Focus, Foundations, Build"

    def _get_fallback_context(self) -> Dict[str, str]:
        """Complete fallback context when supermemory unavailable."""
        return {
            "career_history": self._get_fallback_career_history(),  # NEW: unified format
            "achievements": self._get_fallback_achievements(),      # Legacy
            "skills": self._get_fallback_skills(),
            "jobs": self._get_fallback_jobs(),                      # Legacy
            "writing_style": self._get_fallback_writing_style(),
            "personal_values": self._get_fallback_personal_values(),
            "education": "Bachelor of Arts - English, Hampden-Sydney College, 2004-2008",
            "certifications": "Pragmatic Marketing - Focus, Foundations, Build"
        }

def call_claude_with_retry(
    client: anthropic.Anthropic,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    **api_kwargs
) -> anthropic.types.Message:
    """
    Call Claude API with exponential backoff retry logic.

    Args:
        client: Anthropic client instance
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds (doubles each retry)
        **api_kwargs: Arguments to pass to client.messages.create()

    Returns:
        API response message

    Raises:
        anthropic.AuthenticationError: If API key is invalid (no retry)
        anthropic.APIError: If all retries exhausted
    """
    delay = initial_delay
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            return client.messages.create(**api_kwargs)

        except anthropic.AuthenticationError as e:
            # Don't retry auth errors - API key is wrong
            raise Exception(f"Authentication failed. Check your ANTHROPIC_API_KEY: {e}")

        except anthropic.RateLimitError as e:
            # Rate limit - wait and retry
            if attempt < max_retries:
                wait_time = delay * (2 ** attempt)
                print(f"⏳ Rate limit hit. Waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                last_error = e
                continue
            else:
                raise Exception(f"Rate limit exceeded after {max_retries} retries: {e}")

        except anthropic.APIConnectionError as e:
            # Network issue - retry
            if attempt < max_retries:
                wait_time = delay * (2 ** attempt)
                print(f"🔌 Connection error. Retrying in {wait_time:.1f}s ({attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
                last_error = e
                continue
            else:
                raise Exception(f"Connection failed after {max_retries} retries: {e}")

        except anthropic.APIStatusError as e:
            # Server error (5xx) - retry
            if e.status_code >= 500 and attempt < max_retries:
                wait_time = delay * (2 ** attempt)
                print(f"⚠️  Server error ({e.status_code}). Retrying in {wait_time:.1f}s ({attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
                last_error = e
                continue
            else:
                raise Exception(f"API error ({e.status_code}): {e}")

        except anthropic.APIError as e:
            # Generic API error
            raise Exception(f"API error: {e}")

    # Should never reach here, but just in case
    raise Exception(f"Failed after {max_retries} retries: {last_error}")


def validate_generated_content(content: str, job_info: Dict[str, Any]) -> List[str]:
    """
    Post-generation validation to catch hallucinations.

    Returns list of warning messages if issues are detected.
    """
    warnings = []

    # Check for common hallucination patterns
    hallucination_patterns = {
        '555-555': 'Fake phone number pattern detected',
        '@email.com': 'Generic email address detected',
        'Lorem ipsum': 'Placeholder text detected',
        '[Your ': 'Template placeholder detected',
        '(XXX)': 'Phone placeholder detected',
    }

    for pattern, message in hallucination_patterns.items():
        if pattern.lower() in content.lower():
            warnings.append(f"HALLUCINATION WARNING: {message}")

    # Check for bracket placeholders (template text like [relevant area], [Key Requirement], etc.)
    bracket_placeholders = re.findall(r'\[[A-Z][^\]]{3,50}\]', content)
    if bracket_placeholders:
        warnings.append(f"CRITICAL: Template placeholder brackets detected: {', '.join(bracket_placeholders[:5])}")

    # Also check for common lowercase bracket patterns
    if '[relevant' in content or '[specific' in content or '[metric]' in content:
        warnings.append("CRITICAL: Template placeholder text detected - AI generation likely failed")

    # Verify correct contact info is present
    if CONTACT_INFO['email'] not in content:
        warnings.append(f"WARNING: Correct email ({CONTACT_INFO['email']}) not found in output")

    if CONTACT_INFO['phone'] not in content:
        warnings.append(f"WARNING: Correct phone ({CONTACT_INFO['phone']}) not found in output")

    # Check for therapist story in non-mental-health contexts
    therapist_keywords = ['therapist', 'therapy', 'mental health treatment']
    company = job_info.get('company', '').lower()
    job_desc = job_info.get('description', '').lower()

    is_mental_health = any(keyword in company or keyword in job_desc
                           for keyword in ['mental health', 'therapy', 'counseling', 'headway'])

    if not is_mental_health and any(keyword in content.lower() for keyword in therapist_keywords):
        warnings.append("WARNING: Therapist/mental health story used for non-mental-health company")

    return warnings


def inject_correct_contact_info(content: str, job_title: str = "Senior Product Manager") -> str:
    """
    Post-processing injection of contact information to prevent AI hallucination.

    Removes any AI-generated contact block and injects the correct one.
    This runs AFTER AI generation to guarantee factual contact info.
    """
    lines = content.split('\n')
    cleaned_lines = []
    header_found = False
    contact_line_found = False

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        # Skip the name header (first # line)
        if not header_found and stripped_line.startswith('# '):
            header_found = True
            continue

        # Skip contact info line (appears after name, has | and @)
        if header_found and not contact_line_found and '|' in stripped_line and '@' in stripped_line and i < 10:
            contact_line_found = True
            continue

        # Skip hallucinated contact patterns
        if ('555-555' in stripped_line or
            '@email.com' in stripped_line or
            (('Email:' in stripped_line or 'Phone:' in stripped_line) and '@' in stripped_line and i < 10)):
            continue

        # Keep all other lines
        cleaned_lines.append(line)

    # Build correct header
    correct_header = f"""# {CONTACT_INFO['name']}
{CONTACT_INFO['email']} | {CONTACT_INFO['phone']} | {CONTACT_INFO['linkedin']} | {CONTACT_INFO['location']}

"""

    # Join cleaned content
    content_without_header = '\n'.join(cleaned_lines)

    return correct_header + content_without_header


class ResumeGenerator:
    """Main generator class that orchestrates the entire process."""

    def __init__(self, verbose: bool = False, log_callback=None):
        self.verbose = verbose
        self.log_callback = log_callback
        self.parser = JobDescriptionParser()
        self.retriever = LocalCareerDataRetriever(verbose=verbose)  # Use local storage instead of supermemory
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None

    def _log(self, message: str, force: bool = False):
        """Print message if verbose mode is enabled or force is True. Always call callback if provided."""
        if self.verbose or force:
            print(message)
        if self.log_callback:
            self.log_callback(message)

    def _generate_job_bullets(
        self,
        job_context: Dict[str, str],
        job_info: Dict[str, Any],
        num_bullets: int = 4
    ) -> List[str]:
        """
        Generate bullet points for a SINGLE job using ONLY that job's data.

        This is the key fix for misattribution: the LLM receives ONLY the data
        for the specific job being written about. It literally cannot see
        achievements from other jobs.

        Args:
            job_context: Context for one job from get_single_job_context()
            job_info: Target job description info
            num_bullets: Number of bullets to generate (default 4)

        Returns:
            List of bullet point strings
        """
        if not self.client:
            return [f"• Contributed to {job_context['company']} success"]

        company = job_context['company']
        title = job_context['title']
        dates = job_context['dates']

        # Target job requirements for relevance matching
        required_skills = ', '.join(job_info.get('required_skills', [])[:5])
        responsibilities = ', '.join(job_info.get('responsibilities', [])[:3])

        prompt = f"""Generate {num_bullets} achievement-focused bullet points for this SPECIFIC job.

JOB TO WRITE ABOUT:
Company: {company}
Title: {title}
Dates: {dates}
Company Context: {job_context['context'] or 'N/A'}

AVAILABLE ACHIEVEMENTS FOR THIS JOB (use ONLY these - do not invent):
{job_context['achievements']}

AVAILABLE RESPONSIBILITIES FOR THIS JOB:
{job_context['responsibilities'] or '(None recorded)'}

TARGET POSITION REQUIREMENTS (for relevance - emphasize matching skills):
- Required Skills: {required_skills}
- Key Responsibilities: {responsibilities}

STRICT RULES:
1. ONLY use information from the "AVAILABLE ACHIEVEMENTS" and "AVAILABLE RESPONSIBILITIES" above
2. Do NOT invent metrics, percentages, or numbers not present in the data
3. Do NOT reference achievements from other companies
4. Preserve exact metrics from source data (32% stays 32%, not "over 30%")
5. Each bullet should start with a strong action verb
6. Focus on achievements that align with TARGET POSITION REQUIREMENTS

OUTPUT FORMAT:
Return ONLY the bullet points, one per line, starting with "- ":
- First bullet point here
- Second bullet point here
- etc.

Generate exactly {num_bullets} bullets for {company}:"""

        try:
            response = call_claude_with_retry(
                self.client,
                model=config.CLAUDE_MODEL,
                max_tokens=800,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse bullets from response
            content = response.content[0].text
            bullets = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    bullets.append(line)
                elif line.startswith('• '):
                    bullets.append('- ' + line[2:])

            # Ensure we have the right number
            if len(bullets) < num_bullets:
                # Pad with generic bullets if needed
                while len(bullets) < num_bullets:
                    bullets.append(f"- Contributed to {company}'s strategic initiatives")

            return bullets[:num_bullets]

        except Exception as e:
            self._log(f"Error generating bullets for {company}: {e}")
            return [f"- Contributed to {company}'s strategic initiatives"]

    def _generate_cover_letter_talking_points(
        self,
        job_context: Dict[str, str],
        job_info: Dict[str, Any]
    ) -> str:
        """
        Generate cover letter talking points for a SINGLE job using ONLY that job's data.

        Like _generate_job_bullets, this prevents cross-job contamination by only showing
        the LLM one job's data at a time.

        Args:
            job_context: Context for one job from get_single_job_context()
            job_info: Target job description info

        Returns:
            String with 1-2 sentence talking point for this job
        """
        if not self.client:
            return f"{job_context['company']}: Contributed to key initiatives as {job_context['title']}."

        company = job_context['company']
        title = job_context['title']

        required_skills = ', '.join(job_info.get('required_skills', [])[:5])
        responsibilities = ', '.join(job_info.get('responsibilities', [])[:3])

        prompt = f"""Generate a 1-2 sentence cover letter talking point for this SPECIFIC job experience.

JOB TO WRITE ABOUT:
Company: {company}
Title: {title}
Dates: {job_context['dates']}
Company Context: {job_context['context'] or 'N/A'}

AVAILABLE ACHIEVEMENTS FOR THIS JOB (use ONLY these - do not invent):
{job_context['achievements']}

AVAILABLE RESPONSIBILITIES FOR THIS JOB:
{job_context['responsibilities'] or '(None recorded)'}

TARGET POSITION REQUIREMENTS (for relevance - emphasize matching skills):
- Required Skills: {required_skills}
- Key Responsibilities: {responsibilities}

STRICT RULES:
1. ONLY use information from the "AVAILABLE ACHIEVEMENTS" and "AVAILABLE RESPONSIBILITIES" above
2. Do NOT invent metrics, percentages, or numbers not present in the data
3. Do NOT reference achievements from other companies
4. Preserve exact metrics from source data (32% stays 32%, not "over 30%")
5. Write in first person, conversational tone
6. Focus on the achievement most relevant to the TARGET POSITION

OUTPUT FORMAT:
Return ONLY a 1-2 sentence talking point. Example:
"At Discovery Education, I drove a 32% year-over-year increase in user engagement by overhauling the teacher-side app based on user research."

Generate talking point for {company}:"""

        try:
            response = call_claude_with_retry(
                self.client,
                model=config.CLAUDE_MODEL,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip().strip('"')
        except Exception as e:
            self._log(f"Error generating talking point for {company}: {e}")
            return f"At {company}, contributed to key initiatives as {title}."

    def generate(
        self,
        job_description: str,
        company_name: Optional[str] = None,
        output_dir: Path = Path("./output"),
        resume_only: bool = False,
        cover_letter_only: bool = False,
        output_format: str = "markdown",
        discovery_callback: Optional[callable] = None,
        thought_pattern: bool = False,
        trace_enabled: bool = False,
        interview_prep: bool = False,
        personal_connection: str = ""
    ) -> Dict[str, Any]:
        """
        Generate tailored resume and/or cover letter.

        Args:
            job_description: Raw job description text
            company_name: Optional company name override
            output_dir: Output directory for generated files
            resume_only: Only generate resume
            cover_letter_only: Only generate cover letter
            output_format: Output format (markdown, pdf, all)
            discovery_callback: Optional callback for skill discovery
            thought_pattern: Generate a thought pattern analysis document
            trace_enabled: Generate provenance trace document
            interview_prep: Generate interview prep study document and flashcards
            personal_connection: Optional personal connection to the company/product

        Returns:
            Dict with 'files' key containing list of generated file paths
        """
        # Parse job description
        self._log("Parsing job description...")
        job_info = self.parser.parse(job_description)

        if company_name:
            job_info['company'] = company_name

        self._log(f"[OK] Position: {job_info['title']} at {job_info['company']}")
        self._log(f"[OK] Found {len(job_info['required_skills'])} required skills")
        self._log(f"[OK] Found {len(job_info['responsibilities'])} key responsibilities")
        self._log("")

        # Optional: Run discovery callback
        if discovery_callback:
            self._log("Checking for missing skills...")
            try:
                discovery_callback(job_description, job_info)
                self._log("[OK] Discovery complete")
            except Exception as e:
                self._log(f"[Warning] Discovery skipped: {e}")
            self._log("")

        # Retrieve relevant context from career data
        self._log("Retrieving relevant experience from your career history...")
        context = self.retriever.retrieve_relevant_context(job_info)
        self._log("[OK] Context retrieved")
        self._log("")

        # Generate documents
        generated_files = []
        self._last_resume_content = None
        self._last_cover_letter_content = None
        self._last_interview_prep_content = None

        if not cover_letter_only:
            self._log("Generating tailored resume...")
            resume_path = self._generate_resume(job_info, context, output_dir, output_format)
            generated_files.append(resume_path)
            self._log(f"[OK] Resume generated: {resume_path}")
            self._log("")

        if not resume_only:
            self._log("Generating cover letter...")
            cover_letter_path = self._generate_cover_letter(job_info, context, output_dir, output_format, personal_connection)
            generated_files.append(cover_letter_path)
            self._log(f"[OK] Cover letter generated: {cover_letter_path}")
            self._log("")

        if thought_pattern and self.client:
            self._log("Generating thought pattern analysis...")
            tp_path = self._generate_thought_pattern(job_info, context, output_dir)
            generated_files.append(tp_path)
            self._log(f"[OK] Thought pattern generated: {tp_path}")
            self._log("")

        # Generate provenance trace if enabled
        if trace_enabled and PROVENANCE_AVAILABLE:
            self._log("Generating provenance trace...")
            trace_path = self._generate_provenance_trace(
                job_info, output_dir
            )
            if trace_path:
                generated_files.append(trace_path)
                self._log(f"[OK] Provenance trace generated: {trace_path}")
            else:
                self._log("[Warning] Could not generate provenance trace")
            self._log("")
        elif trace_enabled and not PROVENANCE_AVAILABLE:
            self._log("[Warning] Provenance tracing unavailable (missing modules)")
            self._log("")

        # Generate interview prep if requested
        if interview_prep and self.client:
            self._log("Generating interview prep package...")
            prep_files = self._generate_interview_prep(
                job_info, context, output_dir, output_format
            )
            generated_files.extend(prep_files)
            self._log(f"[OK] Interview prep package generated: {len(prep_files)} files")
            self._log("")
        elif interview_prep and not self.client:
            self._log("[Warning] Interview prep requires API key")
            self._log("")

        # Post-generation quality checks
        if self._last_resume_content:
            self._log("Running post-generation quality checks...")

            # Spell check
            spell_issues = self._spell_check(self._last_resume_content)
            if spell_issues:
                self._log(f"  [Spell Check] Found {len(spell_issues)} potential issues:")
                for issue in spell_issues[:10]:
                    self._log(f"    - {issue}")
            else:
                self._log("  [Spell Check] No issues found")

            # ATS keyword density check
            keyword_report = self._ats_keyword_check(
                self._last_resume_content, job_info
            )
            if keyword_report['missing']:
                self._log(f"  [ATS Keywords] Coverage: {keyword_report['coverage_pct']}%")
                self._log(f"    Missing keywords: {', '.join(keyword_report['missing'][:8])}")
            else:
                self._log(f"  [ATS Keywords] 100% keyword coverage")
            self._log("")

        return {"files": generated_files}

    def _spell_check(self, content: str) -> List[str]:
        """
        Run a basic spell check on generated content.
        Checks for common misspellings and formatting issues.
        Returns list of issue descriptions.
        """
        issues = []

        # Common misspellings in professional documents
        common_misspellings = {
            'managment': 'management',
            'developement': 'development',
            'implemntation': 'implementation',
            'implementaiton': 'implementation',
            'acheive': 'achieve',
            'acheivement': 'achievement',
            'occured': 'occurred',
            'occurence': 'occurrence',
            'recieve': 'receive',
            'seperate': 'separate',
            'definately': 'definitely',
            'accomodate': 'accommodate',
            'occassion': 'occasion',
            'neccessary': 'necessary',
            'succesful': 'successful',
            'sucessful': 'successful',
            'enviroment': 'environment',
            'experiance': 'experience',
            'responsibilty': 'responsibility',
            'maintainance': 'maintenance',
            'performace': 'performance',
            'efficency': 'efficiency',
            'proffesional': 'professional',
            'infrastucture': 'infrastructure',
            'colloboration': 'collaboration',
            'comunication': 'communication',
            'anayltics': 'analytics',
            'anaylsis': 'analysis',
            'optimzation': 'optimization',
            'straegy': 'strategy',
            'stakholders': 'stakeholders',
            'requirments': 'requirements',
            'specifcation': 'specification',
            'intergration': 'integration',
            'implmented': 'implemented',
            'delievered': 'delivered',
            'spearheaed': 'spearheaded',
        }

        content_lower = content.lower()
        for wrong, correct in common_misspellings.items():
            if wrong in content_lower:
                issues.append(f'"{wrong}" should be "{correct}"')

        # Check for double spaces (excluding markdown formatting)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if '  ' in line.strip() and not line.strip().startswith('#') and not line.strip().startswith('-'):
                # Ignore markdown list indentation
                stripped = line.strip()
                if '  ' in stripped:
                    issues.append(f"Line {i}: double space detected")

        # Check for inconsistent bullet styles
        bullet_styles = set()
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('- '):
                bullet_styles.add('dash')
            elif stripped.startswith('• '):
                bullet_styles.add('bullet')
            elif stripped.startswith('* '):
                bullet_styles.add('asterisk')
        if len(bullet_styles) > 1:
            issues.append(f"Inconsistent bullet styles: {', '.join(bullet_styles)}")

        return issues

    def _ats_keyword_check(
        self, content: str, job_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check how well the resume covers keywords from the job description.
        Returns a report with coverage percentage and missing keywords.
        """
        # Gather all keywords from job info
        all_keywords = set()
        for kw in job_info.get('required_skills', []):
            all_keywords.add(kw.strip().lower())
        for kw in job_info.get('keywords', []):
            all_keywords.add(kw.strip().lower())
        # Also include preferred skills but track them separately
        preferred = set()
        for kw in job_info.get('preferred_skills', []):
            preferred.add(kw.strip().lower())

        if not all_keywords:
            return {'coverage_pct': 100, 'found': [], 'missing': [], 'preferred_missing': []}

        content_lower = content.lower()
        found = []
        missing = []

        for kw in all_keywords:
            if not kw:
                continue
            # Check for exact match or close variant (e.g. "python" matches "Python 3")
            if kw in content_lower:
                found.append(kw)
            else:
                # Check individual words for multi-word keywords
                words = kw.split()
                if len(words) > 1 and all(w in content_lower for w in words):
                    found.append(kw)
                else:
                    missing.append(kw)

        # Check preferred skills coverage
        preferred_missing = []
        for kw in preferred:
            if kw and kw not in content_lower:
                words = kw.split()
                if len(words) <= 1 or not all(w in content_lower for w in words):
                    preferred_missing.append(kw)

        total = len(all_keywords)
        coverage = round((len(found) / total) * 100) if total > 0 else 100

        return {
            'coverage_pct': coverage,
            'found': sorted(found),
            'missing': sorted(missing),
            'preferred_missing': sorted(preferred_missing),
        }

    def _generate_resume(
        self,
        job_info: Dict[str, Any],
        context: Dict[str, str],
        output_dir: Path,
        output_format: str
    ) -> str:
        """Generate tailored resume using Claude and retrieved context."""

        company = job_info.get('company', 'Unknown')
        title = job_info.get('title', 'Unknown')

        # If API key available, use Claude to generate tailored content
        if self.client:
            return self._generate_resume_with_ai(job_info, context, output_dir, output_format)

        # Otherwise, use basic template
        return self._generate_basic_resume(job_info, output_dir)

    def _generate_resume_with_ai(
        self,
        job_info: Dict[str, Any],
        context: Dict[str, str],
        output_dir: Path,
        output_format: str
    ) -> str:
        """Use Claude to generate a tailored resume with per-job bullet isolation."""

        company = job_info.get('company', 'Unknown')
        title = job_info.get('title', 'Unknown')

        # === PHASE 1: Generate bullets for each job INDEPENDENTLY ===
        # This prevents cross-job contamination by only showing the LLM
        # one job's data at a time
        self._log("  [Phase 1] Generating job bullets with isolation...")

        jobs = self.retriever.get_jobs_list()
        pre_generated_experience = []

        # Select top 4 most recent/relevant jobs
        selected_jobs = jobs[:4] if jobs else []

        for job in selected_jobs:
            job_context = self.retriever.get_single_job_context(job)

            # Generate bullets for THIS JOB ONLY (LLM cannot see other jobs)
            bullets = self._generate_job_bullets(job_context, job_info, num_bullets=3)

            # Format for inclusion in final resume
            job_section = f"""### {job_context['company']}
**{job_context['title']}** | {job_context['dates']}

{chr(10).join(bullets)}"""
            pre_generated_experience.append(job_section)

            self._log(f"    Generated {len(bullets)} bullets for {job_context['company']}")

        # Join all pre-generated experience sections
        experience_sections = "\n\n".join(pre_generated_experience)

        # === PHASE 2: Generate the full resume using pre-generated bullets ===
        self._log("  [Phase 2] Assembling final resume...")

        prompt = f"""You are helping Watson Mulkey create an ATS-optimized resume for a {title} position at {company}.

CONTACT INFORMATION (USE EXACTLY AS PROVIDED - NEVER MODIFY):
Name: {CONTACT_INFO['name']}
Email: {CONTACT_INFO['email']}
Phone: {CONTACT_INFO['phone']}
LinkedIn: {CONTACT_INFO['linkedin']}
Location: {CONTACT_INFO['location']}

JOB DESCRIPTION ANALYSIS:
- Title: {title}
- Company: {company}
- Required Skills: {', '.join(job_info.get('required_skills', []))}
- Key Responsibilities: {', '.join(job_info.get('responsibilities', [])[:5])}

PRE-GENERATED EXPERIENCE SECTIONS (USE THESE VERBATIM - DO NOT MODIFY OR REORGANIZE):
===
{experience_sections}
===

IMPORTANT: The experience bullets above have been pre-validated for accuracy.
You MUST use them EXACTLY as provided. Do NOT:
- Move bullets between jobs
- Reword bullets
- Add new bullets with metrics not shown above
- Remove or skip any job sections

SKILLS:
{context['skills']}

CRITICAL ATS OPTIMIZATION REQUIREMENTS:
1. ZERO HALLUCINATIONS: ONLY use information provided above - NEVER invent or embellish facts
2. CONTACT INFO: Use contact information EXACTLY as provided at the top - DO NOT modify, add characters, or make any changes
3. KEYWORD MATCHING: Use exact keywords and phrases from the job description naturally throughout the resume (especially in Professional Summary, Skills, and Experience bullets)
4. NATURAL LANGUAGE: Write for humans first - modern ATS AI understands context, so avoid keyword stuffing. Use keywords where they make sense naturally.
5. SKILLS BALANCE: Include both soft skills (leadership, communication, collaboration) AND hard skills (technical tools, methodologies)
6. METRICS & ACHIEVEMENTS: Include specific quantified achievements (32%, 50%, etc.) exactly as provided
7. REVERSE CHRONOLOGICAL: List experience in reverse chronological order (most recent first)
8. STANDARD FORMATTING: Use simple, standard section headers. Avoid tables, graphics, or complex formatting
9. KEYWORD-RICH SUMMARY: Professional summary should incorporate 3-5 keywords from job description while reading naturally
10. RELEVANT EXPERIENCE: Focus on 3-4 most relevant roles that match job requirements
11. PUNCTUATION: Use semicolons to connect related independent clauses instead of em-dashes (Watson's personal writing style)

Generate a professional resume in Markdown format with these ATS-friendly sections:
- Header with name and contact info (USE EXACT CONTACT INFO PROVIDED ABOVE - no modifications)
- Professional Summary (2-3 sentences with natural keyword integration)
- Experience: COPY THE PRE-GENERATED EXPERIENCE SECTIONS EXACTLY AS PROVIDED ABOVE (do not modify bullets)
- Key Achievements (4-5 quantified wins extracted from the pre-generated experience bullets above)
- Skills (include both technical/hard skills AND soft skills, using exact keywords from job description)
- Education: {context['education']}
- Certifications: {context['certifications']}

CRITICAL: For the Experience section, you MUST copy the PRE-GENERATED EXPERIENCE SECTIONS exactly.
Do NOT rewrite, reorder, or invent new bullet points. The bullets have been pre-validated.

FORMATTING RULES FOR ATS COMPATIBILITY:
- Use standard section headers (## Experience, ## Skills, etc.)
- Use simple bullet points (-)
- No tables, columns, text boxes, or graphics
- Plain text formatting only
- CRITICAL: Keep it to EXACTLY 1 page worth of content (max ~50 lines total)
- Do NOT wrap the resume in code blocks (```) - output plain markdown only

Make this resume pass ATS keyword filters while remaining natural and compelling for human readers.
Focus on quality over quantity - be concise and impactful within the 1-page constraint."""

        try:
            response = call_claude_with_retry(
                self.client,
                model=config.CLAUDE_MODEL,
                max_tokens=2500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            resume_content = response.content[0].text

            # Validate for hallucinations
            validation_warnings = validate_generated_content(resume_content, job_info)
            if validation_warnings:
                self._log("⚠️  VALIDATION WARNINGS:")
                for warning in validation_warnings:
                    self._log(f"   {warning}")

            # CRITICAL: Inject correct contact info to prevent hallucination
            resume_content = inject_correct_contact_info(resume_content, title)

            # Add footer
            resume_content += f"\n\n---\n\n*This resume was tailored for: {title} at {company}*\n"

            # Store for thought pattern analysis
            self._last_resume_content = resume_content

        except Exception as e:
            self._log(f"Error generating with AI: {e}")
            # Fall back to basic template
            return self._generate_basic_resume(job_info, output_dir)

        # Save markdown file (temporary - used to generate other formats)
        filename = f"Watson_Mulkey_Resume_{sanitize_filename(company)}.md"
        md_file_path = output_dir / filename

        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(resume_content)

        files_to_cleanup = []

        # Parse resume content into structured data (used by both PDF and HTML)
        resume_data = self._parse_resume_for_html(resume_content, job_info, context)

        # Generate PDF if requested
        if output_format in ['pdf', 'all'] and PDF_AVAILABLE:
            pdf_filename = f"Watson_Mulkey_Resume_{sanitize_filename(company)}.pdf"
            pdf_path = output_dir / pdf_filename
            try:
                self._log(f"[DEBUG] Calling generate_pdf_from_data with {len(resume_data.get('experience', []))} jobs", force=True)
                generate_pdf_from_data(resume_data, pdf_path)
                self._log(f"[OK] PDF generated with NEW STYLING: {pdf_path}")
            except Exception as e:
                self._log(f"ERROR: PDF generation failed: {e}", force=True)
                import traceback
                self._log(f"Traceback: {traceback.format_exc()}", force=True)

        # Generate HTML if requested (temporary - not needed for final output)
        html_path = None
        if output_format in ['html', 'all'] and HTML_AVAILABLE:
            html_filename = f"Watson_Mulkey_Resume_{sanitize_filename(company)}.html"
            html_path = output_dir / html_filename
            try:
                generate_html_resume(resume_data, html_path)
                self._log(f"[OK] HTML generated: {html_path}")
                # Mark HTML for cleanup if we're generating all formats
                if output_format == 'all':
                    files_to_cleanup.append(html_path)
            except Exception as e:
                self._log(f"Warning: HTML generation failed: {e}")

        # DOCX generation disabled for resumes - PDF is sufficient
        # Users prefer PDF format only for resumes

        # Clean up intermediate files when generating all formats
        if output_format == 'all':
            # Always remove markdown file
            try:
                md_file_path.unlink()
                self._log(f"[OK] Removed temporary markdown file")
            except Exception as e:
                self._log(f"Warning: Could not remove markdown file: {e}")

            # Remove HTML file if marked for cleanup
            for cleanup_file in files_to_cleanup:
                try:
                    cleanup_file.unlink()
                    self._log(f"[OK] Removed temporary HTML file")
                except Exception as e:
                    self._log(f"Warning: Could not remove {cleanup_file.name}: {e}")

        return str(md_file_path)

    def _parse_resume_for_html(self, resume_text: str, job_info: Dict[str, Any], context: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Parse resume text into structured data for HTML template."""
        # Strip code block wrappers if present
        resume_text = resume_text.strip()
        if resume_text.startswith('```'):
            lines = resume_text.split('\n')
            # Remove first line (```) and last line (```)
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            resume_text = '\n'.join(lines)

        # Simple parser - extract sections from generated resume
        lines = resume_text.split('\n')

        data = {
            'name': CONTACT_INFO['name'].upper(),
            'title': 'Senior Product Manager',
            'contact_info': f"{CONTACT_INFO['phone']} • {CONTACT_INFO['email']} • {CONTACT_INFO['linkedin']} • {CONTACT_INFO['location']}",
            'experience': [],
            'education': self._get_education_data(context),
            'achievements': [],
            'skills': [],
            'certifications': []
        }

        # Extract job title from job_info if available
        if job_info.get('title'):
            target = job_info['title'].strip()
            base = "Senior Product Manager"

            # Normalize: strip "Senior " for comparison
            target_core = re.sub(r'^senior\s+', '', target, flags=re.IGNORECASE).strip()
            base_core = re.sub(r'^senior\s+', '', base, flags=re.IGNORECASE).strip()

            if target_core.lower() == base_core.lower():
                # Same core role -- use "Senior Product Manager"
                data['title'] = base
            else:
                # Different roles: "Senior Product Manager - Director of Product"
                data['title'] = f"{base} - {target}"

        # Parse experience section
        current_job = None
        in_experience = False
        in_skills = False
        in_achievements = False

        for line in lines:
            line_stripped = line.strip()

            if '## Experience' in line or '## EXPERIENCE' in line:
                in_experience = True
                continue
            elif line.startswith('##') and not line.startswith('###'):
                in_experience = False
                in_skills = False
                in_achievements = False
                if 'SKILLS' in line or 'Skills' in line:
                    in_skills = True
                elif 'ACHIEVEMENT' in line.upper():
                    in_achievements = True
                continue

            if in_experience and line.startswith('###'):
                if current_job:
                    data['experience'].append(current_job)

                # Parse company and dates from header like "### Registria (2024-2025)"
                header = line_stripped.replace('###', '').strip()
                company = header
                dates = ''

                # Extract dates from parentheses if present
                if '(' in header and ')' in header:
                    parts = header.split('(')
                    company = parts[0].strip()
                    dates = parts[1].rstrip(')').strip()

                current_job = {
                    'title': '',
                    'company': company,
                    'dates': dates,
                    'location': '',
                    'bullets': []
                }
            elif in_experience and line_stripped and '|' in line and not line.startswith('-'):
                # New format: **Job Title** | Company | Dates
                if current_job:
                    data['experience'].append(current_job)

                parts = [p.strip().strip('*') for p in line_stripped.split('|')]  # Strip markdown bold
                if len(parts) >= 3:
                    current_job = {
                        'title': parts[0],  # Job title is first
                        'company': parts[1],  # Company is second
                        'dates': parts[2],
                        'location': '',
                        'bullets': []
                    }
                elif len(parts) == 2:
                    current_job = {
                        'title': parts[0],  # Job title is first
                        'company': parts[1],  # Company is second
                        'dates': '',
                        'location': '',
                        'bullets': []
                    }
            elif in_experience and current_job:
                # Handle #### header as job title (fix for markdown leak)
                if line.startswith('####') and not current_job['title']:
                    current_job['title'] = line_stripped.replace('####', '').strip()
                elif line.startswith('# ') and not line.startswith('##') and not current_job['title']:
                    # Also handle single # as fallback
                    current_job['title'] = line_stripped[2:].strip()
                elif line.startswith('**') and line.endswith('**') and not current_job['title']:
                    # First bold line after header is the job title
                    current_job['title'] = line.strip('*')
                elif line.startswith('- '):
                    current_job['bullets'].append(line[2:])

            if in_skills and line_stripped.startswith('**'):
                data['skills'].append(line_stripped)

            if in_achievements and line_stripped and (line_stripped.startswith('-') or line_stripped.startswith('*') or line_stripped.startswith('★') or line_stripped.startswith('▶') or line_stripped.startswith('●')):
                ach_text = line_stripped.lstrip('-*★▶● ').strip()
                # Try **title** - description pattern
                m = re.match(r'\*\*(.+?)\*\*\s*[-–:]\s*(.*)', ach_text)
                if m:
                    data['achievements'].append({'title': m.group(1).strip(), 'description': m.group(2).strip()})
                else:
                    # Plain text -- use as title
                    data['achievements'].append({'title': re.sub(r'\*\*', '', ach_text), 'description': ''})

        if current_job:
            data['experience'].append(current_job)

        # Only use fallback if Claude's output had no achievements section
        if not data['achievements']:
            self._log("[WARN] No achievements parsed from Claude output -- using empty list")

        # Add certifications from context
        data['certifications'] = self._get_certifications_data(context)

        return data

    def _get_education_data(self, context: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get education data from context or fallback defaults."""
        if context and context.get('education') and context['education'] != "Bachelor of Arts - English, Hampden-Sydney College, 2004-2008":
            # Parse from context string
            edu_str = context['education'].split('\n')[0]
            parts = [p.strip() for p in edu_str.split(',')]
            if len(parts) >= 3:
                return {'degree': parts[0], 'school': parts[1], 'dates': parts[2]}
        return {'degree': 'Bachelor of Arts - English', 'school': 'Hampden-Sydney College', 'dates': '2004-2008'}

    def _get_certifications_data(self, context: Optional[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """Get certifications data from context or fallback defaults."""
        if context and context.get('certifications') and context['certifications'] != "Pragmatic Marketing - Focus, Foundations, Build":
            certs = []
            for line in context['certifications'].split('\n'):
                line = line.strip()
                if line:
                    certs.append({'title': line, 'description': ''})
            if certs:
                return certs
        return [
            {'title': 'Pragmatic Marketing - Focus', 'description': ''},
            {'title': 'Pragmatic Marketing - Foundations', 'description': ''},
            {'title': 'Pragmatic Marketing - Build', 'description': ''}
        ]

    def _generate_basic_resume(self, job_info: Dict[str, Any], output_dir: Path) -> str:
        """Generate basic template resume (fallback when no API)."""
        company = job_info.get('company', 'Unknown')
        title = job_info.get('title', 'Unknown')

        resume_content = f"""# M. WATSON MULKEY
Senior Product Manager

4348082493 | watsonmulkey@gmail.com | https://www.linkedin.com/in/watsonmulkey/ | Denver, Colorado

---

## PROFESSIONAL SUMMARY

Product Manager with 8+ years of experience leading cross-functional teams and delivering data-driven product solutions. Proven track record of improving user engagement, optimizing workflows, and building products that align with both business objectives and user needs.

---

## EXPERIENCE

### Senior Product Manager - ID/Onboarding/Platform
**Registria** | Denver, Colorado | 01/2024 - 03/2025

- Delivered comprehensive reporting suite for flagship product, providing actionable insights to major consumer brands including Sony and Whirlpool
- Developed and maintained multi-vertical dependency roadmap across sales, engineering, and customer success teams
- Created consensus between stakeholders for features that balanced value and scalability

### Product Manager - Teacher Tools
**Discovery Education** | Charlotte, North Carolina | 11/2021 - 12/2023

- **Improved user engagement by 32% YoY** on flagship product (1M+ MAU)
- Led cross-functional team of 4-7 members and managed projects across 5 teams, resulting in **15% increase in delivery rate YoY**
- Partnered with data team to identify user flow losing 33% of traffic; refactored flow to recapture 10% within first month
- Delivered monthly data presentations to C-Suite on A/B test results and usage metrics

### Product Consultant
**Bookshop.org** | New York, New York | 12/2020 - Present

- Refined product strategy for global e-commerce operations ($50M+ annual revenue)
- Created agile processes enabling globally distributed team to work asynchronously
- Trained internal employee to become product manager
- Established cross-functional product relations across business units

### Product Manager
**Simplifya** | Denver, Colorado | 01/2019 - 03/2021

- Refactored flagship auditing product, **reducing completion time by 50%** and increasing usage **40% YoY**
- Built 0-1 product addressing evolving state-by-state regulatory requirements
- Conducted user research across diverse segments to stay ahead of compliance needs

---

## KEY ACHIEVEMENTS

* **32% YoY engagement increase** - Overhauled UX based on user research with teachers
* **50% efficiency gain** - Refactored core product feature through user-centered design
* **15% delivery improvement** - Led cross-functional teams across multiple projects
* **0-1 Product Launch** - Built new compliance feature serving diverse client base

---

## SKILLS

**Product Management**: Product Strategy • Roadmapping • A/B Testing • User Research
**Leadership**: Cross-functional Team Leadership • Stakeholder Management
**Technical**: SQL • Looker • Fullstory • Google Analytics
**Specialties**: Voice of Customer • Data Analysis • Working with Non-technical Users

---

## EDUCATION

**Bachelor of Arts - English**
Hampden-Sydney College | 2004 - 2008

---

## CERTIFICATIONS

- Pragmatic Marketing - Focus
- Pragmatic Marketing - Foundations
- Pragmatic Marketing - Build

---

*This resume was tailored for: {title} at {company}*
"""

        # Save to file
        filename = f"Watson_Mulkey_Resume_{sanitize_filename(company)}.md"
        file_path = output_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(resume_content)

        return str(file_path)

    def _generate_cover_letter(
        self,
        job_info: Dict[str, Any],
        context: Dict[str, str],
        output_dir: Path,
        output_format: str,
        personal_connection: str = ""
    ) -> str:
        """Generate tailored cover letter with voice matching."""

        company = job_info.get('company', 'Unknown')
        title = job_info.get('title', 'Unknown')

        # If API key available, use Claude to generate tailored content
        if self.client:
            return self._generate_cover_letter_with_ai(job_info, context, output_dir, output_format, personal_connection)

        # Otherwise, use basic template
        return self._generate_basic_cover_letter(job_info, output_dir)

    def _generate_cover_letter_with_ai(
        self,
        job_info: Dict[str, Any],
        context: Dict[str, str],
        output_dir: Path,
        output_format: str,
        personal_connection: str = ""
    ) -> str:
        """Use Claude to generate a tailored, voice-matched cover letter with per-job isolation."""

        company = job_info.get('company', 'Unknown')
        title = job_info.get('title', 'Unknown')

        # === PHASE 1: Generate per-job talking points in isolation ===
        # Like resume bullets, each talking point is generated with ONLY that job's data
        self._log("  [Phase 1] Generating cover letter talking points with per-job isolation...")

        jobs = self.retriever.get_jobs_list()
        selected_jobs = jobs[:4] if jobs else []
        pre_generated_points = []

        for job in selected_jobs:
            job_context = self.retriever.get_single_job_context(job)
            talking_point = self._generate_cover_letter_talking_points(job_context, job_info)
            pre_generated_points.append(f"- {job_context['company']} ({job_context['title']}): {talking_point}")
            self._log(f"    Generated talking point for {job_context['company']}")

        talking_points_text = "\n".join(pre_generated_points) if pre_generated_points else "(No talking points generated)"

        # === PHASE 2: Assemble cover letter from pre-validated talking points ===
        self._log("  [Phase 2] Assembling cover letter from pre-validated talking points...")

        # Build personal connection section for the prompt
        personal_connection_section = ""
        if personal_connection:
            personal_connection_section = f"""
PERSONAL CONNECTION TO {company.upper()}:
Watson has provided this personal connection: "{personal_connection}"
This is REAL and VERIFIED - use it to open the cover letter authentically.
Lead with this connection in the opening paragraph - it's the strongest possible hook.
"""
        else:
            personal_connection_section = f"""
PERSONAL CONNECTION TO {company.upper()}:
None provided. Open with a direct, confident statement about fit for the role.
Do NOT fabricate a personal connection. Do NOT use generic openers like "As someone who's spent years..."
Instead, lead with a specific, compelling reason Watson is drawn to THIS role at THIS company.
"""

        prompt = f"""You are helping Watson Mulkey craft a compelling, authentic cover letter for a {title} position at {company}.

CONTACT INFORMATION (USE EXACTLY AS PROVIDED - NEVER MODIFY):
Name: {CONTACT_INFO['name']}
Email: {CONTACT_INFO['email']}
Phone: {CONTACT_INFO['phone']}
LinkedIn: {CONTACT_INFO['linkedin']}
Location: {CONTACT_INFO['location']}

JOB CONTEXT:
- Title: {title}
- Company: {company}
- Required Skills: {', '.join(job_info.get('required_skills', []))}
- Top Responsibilities: {', '.join(job_info.get('responsibilities', [])[:5])}
- Company Mission/Values: {job_info.get('company_mission', 'Not specified')}
{personal_connection_section}
PRE-VALIDATED TALKING POINTS (use ONLY these - do not invent new achievements or metrics):
{talking_points_text}

IMPORTANT: The talking points above have been pre-validated for accuracy.
You MUST use them as the basis for the body paragraphs. Do NOT:
- Invent new metrics or achievements not in the talking points
- Attribute achievements to a different company
- Add embellishments beyond what's stated

SKILLS & EVIDENCE:
{context['skills']}

WATSON'S AUTHENTIC WRITING VOICE:
{context['writing_style']}

PERSONAL VALUES & MOTIVATIONS:
{context['personal_values']}

CRITICAL RULE - PERSONAL ANECDOTES:
Personal stories/anecdotes should ONLY be used when they are DIRECTLY RELEVANT to the company's product domain or mission, OR when Watson has provided a personal connection above.

ACCEPTABLE Personal Connections:
- When Watson explicitly provides one (see PERSONAL CONNECTION section above)
- Mental health company (Headway) → Therapist story about how therapy changed Watson's life
- Audio hardware company (Universal Audio) → Watson being a hobbyist producer/composer who uses their products
- Social platform (Reddit) → Watson being a long-time user of the platform
- Customer engagement product (Iterable) → Watson's career starting in Customer Engagement/Support

UNACCEPTABLE Personal Connections:
- DO NOT fabricate personal connections Watson didn't provide
- DO NOT use hobby/personal interest stories unless directly related to company's product
- When in doubt, USE PROFESSIONAL EXPERIENCE ONLY - no personal stories

COVER LETTER STRUCTURE & REQUIREMENTS:

**Opening (2 short paragraphs, not 1 dense block):**
- Paragraph 1 (2-3 sentences): The hook. If Watson provided a personal connection, lead with it naturally. Otherwise, lead with a specific, compelling reason for interest in THIS role. State the role being applied for.
- Paragraph 2 (1-2 sentences): The qualification statement. Briefly establish credibility and relevant experience. Keep it tight.
- NEVER open with "As someone who's spent X years doing Y" - this is generic and forgettable

**Body Paragraphs (2-3 focused examples):**
Each body paragraph should use a DIFFERENT structural approach. You MUST use at least 2 different structures across the body paragraphs. Choose from:

1. **Story-first**: Open with the situation/challenge, then reveal actions and results.
   Example: "When Discovery Education's engagement plateaued, I dug into the data and realized our teacher-side UX was the bottleneck. I led a complete overhaul grounded in user research, driving a 32% YoY increase in engagement."

2. **Result-first**: Lead with the quantified outcome, then explain how you got there.
   Example: "A 32% YoY engagement increase doesn't happen by accident. At Discovery Education, it took months of user interviews, prototype testing, and cross-functional alignment to overhaul our teacher-side app."

3. **Insight-first**: Start with a lesson or principle, then ground it in a specific example.
   Example: "The best product decisions come from talking to actual users. At Discovery Education, that principle drove me to conduct 50+ teacher interviews, which ultimately informed a UX overhaul that boosted engagement 32%."

4. **Contrast**: Set up the before/problem, then show the transformation.
   Example: "Simplifya's auditing tool was losing users to manual workarounds. By rethinking the core workflow and cutting unnecessary steps, I turned a frustration point into the product's strongest feature; efficiency jumped 50%."

ANTI-PATTERNS - Do NOT do any of these:
- Do NOT start more than one paragraph with "At [Company]..."
- Do NOT quote JD requirements verbatim in more than one paragraph
- Do NOT use "mirrors my experience" or "aligns perfectly with"
- Do NOT use the same sentence-level structure to open consecutive paragraphs
- Do NOT use "Your requirement X" framing to open any paragraph

**Closing Paragraph:**
- Synthesize why you're uniquely positioned for THIS role
- Express genuine interest in contributing to their specific mission/goals
- If the company has stated values, you may reference them BRIEFLY and naturally (1 clause, not a whole paragraph) - only if it genuinely connects to Watson's approach
- Clear, confident call to action (e.g., "I'd love the opportunity to discuss...")
- Do NOT dedicate an entire paragraph to company values - it reads as performative

CRITICAL WRITING GUIDELINES:
1. ZERO HALLUCINATIONS: Only use provided facts, metrics, and experiences
2. CONTACT INFO: If contact info is included, use EXACTLY as provided above - DO NOT modify
3. TONE: Direct, conversational, and human. Write like a real person, not a template. Avoid corporate phrases like "combining my passion for X with my expertise in Y" or "I bring a unique blend of..."
4. NATURAL FLOW: Don't list achievements robotically - weave them into natural storytelling
5. SPECIFICITY: Use exact metrics (32%, 50%, $50M, 20+ people) - they're powerful
6. CONNECTION: Every example should explicitly tie back to job requirements
7. AUTHENTICITY: Avoid corporate jargon - use Watson's natural phrases
8. PUNCTUATION: Use semicolons to connect related independent clauses instead of em-dashes (Watson's personal writing style)
9. LENGTH: 350-450 words (concise but substantive)
10. SCANNABILITY: Keep paragraphs short. The opening should be two separate paragraphs, not one dense block.
11. STRUCTURAL VARIETY: Each body paragraph MUST open with a different structure (see the 4 approaches above). Never repeat the same opening pattern in consecutive paragraphs.

Generate a cover letter that sounds like Watson actually wrote it - not like an AI optimized for keywords.
"""

        try:
            response = call_claude_with_retry(
                self.client,
                model=config.CLAUDE_MODEL,
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            cover_letter_content = response.content[0].text

            # Validate for hallucinations BEFORE saving
            validation_warnings = validate_generated_content(cover_letter_content, job_info)

            # Check for CRITICAL warnings (placeholders, templates, etc.)
            critical_warnings = [w for w in validation_warnings if 'CRITICAL' in w]

            if critical_warnings:
                # Log critical warnings and RAISE instead of falling back silently
                self._log("❌ CRITICAL VALIDATION FAILURES:", force=True)
                for warning in critical_warnings:
                    self._log(f"   {warning}", force=True)
                raise ValueError(f"Cover letter generation failed validation: {critical_warnings[0]}")

            # Log non-critical warnings but continue
            if validation_warnings:
                self._log("⚠️  COVER LETTER VALIDATION WARNINGS:", force=True)
                for warning in validation_warnings:
                    self._log(f"   {warning}", force=True)

            # Store for thought pattern analysis
            self._last_cover_letter_content = cover_letter_content

        except Exception as e:
            # Log error with force=True so it ALWAYS shows (even with verbose=False)
            error_msg = f"CRITICAL ERROR: Cover letter AI generation failed: {str(e)}"
            self._log(error_msg, force=True)
            # Re-raise instead of falling back silently - user needs to know
            raise RuntimeError(error_msg) from e

        # Save markdown file (temporary - will be used to generate other formats)
        filename = f"Watson_Mulkey_{sanitize_filename(company)}_CoverLetter.md"
        md_file_path = output_dir / filename

        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(cover_letter_content)

        generated_files = [str(md_file_path)]

        # Generate DOCX if requested (ATS-friendly Word format)
        if output_format in ['docx', 'all'] and DOCX_AVAILABLE:
            docx_filename = f"Watson_Mulkey_{sanitize_filename(company)}_CoverLetter.docx"
            docx_path = output_dir / docx_filename
            try:
                generate_docx_cover_letter(cover_letter_content, docx_path)
                self._log(f"[OK] Cover letter DOCX generated: {docx_path}", force=True)
                generated_files.append(str(docx_path))
            except Exception as e:
                self._log(f"Warning: Cover letter DOCX generation failed: {e}", force=True)

        # Generate PDF if requested - using cover letter specific PDF generator
        if output_format in ['pdf', 'all'] and PDF_AVAILABLE:
            pdf_filename = f"Watson_Mulkey_{sanitize_filename(company)}_CoverLetter.pdf"
            pdf_path = output_dir / pdf_filename
            try:
                # Use cover letter specific PDF generator with proper formatting
                generate_cover_letter_pdf(md_file_path, pdf_path)
                self._log(f"[OK] Cover letter PDF generated: {pdf_path}", force=True)
                generated_files.append(str(pdf_path))
            except Exception as e:
                self._log(f"Warning: Cover letter PDF generation failed: {e}", force=True)

        # Delete markdown file if other formats were generated successfully
        if output_format == 'all' and len(generated_files) > 1:
            try:
                md_file_path.unlink()
                self._log(f"[OK] Removed temporary markdown file", force=True)
                generated_files.remove(str(md_file_path))
            except Exception as e:
                self._log(f"Warning: Could not remove markdown file: {e}", force=True)

        return generated_files[0] if generated_files else str(md_file_path)

    def _generate_thought_pattern(
        self,
        job_info: Dict[str, Any],
        context: Dict[str, str],
        output_dir: Path
    ) -> str:
        """Generate a thought pattern analysis document explaining resume/cover letter choices."""

        company = job_info.get('company', 'Unknown')
        title = job_info.get('title', 'Unknown')

        resume_section = ""
        if self._last_resume_content:
            resume_section = f"""
GENERATED RESUME:
{self._last_resume_content}
"""

        cover_letter_section = ""
        if self._last_cover_letter_content:
            cover_letter_section = f"""
GENERATED COVER LETTER:
{self._last_cover_letter_content}
"""

        prompt = f"""You are analyzing the strategic choices made when tailoring Watson Mulkey's resume and cover letter for a {title} position at {company}.

Your job is to produce a "Thought Pattern" document that explains WHY each choice was made, mapping specific career bullet points to job description requirements.

JOB DESCRIPTION ANALYSIS:
- Title: {title}
- Company: {company}
- Required Skills: {', '.join(job_info.get('required_skills', []))}
- Key Responsibilities: {', '.join(job_info.get('responsibilities', [])[:8])}
- Preferred Qualifications: {', '.join(job_info.get('preferred_skills', []))}
- Company Mission: {job_info.get('company_mission', 'Not specified')}

WATSON'S FULL CAREER DATA (what was available to choose from):

ACHIEVEMENTS:
{context['achievements']}

SKILLS:
{context['skills']}

JOB HISTORY:
{context['jobs']}

PERSONAL VALUES:
{context['personal_values']}
{resume_section}{cover_letter_section}
Generate a structured markdown analysis with these exact sections:

# Thought Pattern Analysis
## Watson Mulkey → {title} at {company}

### Job Requirement → Experience Mapping

Create a markdown table with columns: Job Requirement | Your Experience | Where Used (Resume/CL/Both) | Why Selected

Include EVERY key requirement from the job description and map it to the most relevant experience. If there's no direct match, note it as a gap.

### Resume Decisions

For each major choice in the resume, explain:
- Why specific roles were included or emphasized
- Why specific bullet points/achievements were selected
- How metrics were chosen to highlight
- Why the professional summary was framed the way it was

### Cover Letter Strategy

Explain the strategic reasoning behind:
- The opening approach (personal connection vs professional)
- Which examples were chosen and why
- How the closing ties everything together
- Any personal values or mission alignment used

### Deliberately Excluded

List career data that was available but NOT used, and explain why:
- Roles that were de-emphasized or omitted
- Achievements that weren't mentioned
- Skills that weren't highlighted

### Keyword Strategy

List the top keywords from the job description and where they appear in the generated documents.

### Match Assessment

Provide an honest assessment:
- **Strong matches**: Where Watson's experience directly aligns
- **Moderate matches**: Where experience is adjacent/transferable
- **Gaps**: Where the job asks for something Watson doesn't have direct experience in
- **Overall fit**: A candid 1-2 sentence assessment

Be specific and reference actual content from both the job description and the generated documents. Do not be generic."""

        try:
            response = call_claude_with_retry(
                self.client,
                model=config.CLAUDE_MODEL,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            thought_pattern_content = response.content[0].text

        except Exception as e:
            self._log(f"Warning: Thought pattern generation failed: {e}", force=True)
            thought_pattern_content = f"# Thought Pattern Analysis\n\nGeneration failed: {e}\n"

        filename = f"Watson_Mulkey_{sanitize_filename(company)}_ThoughtPattern.md"
        tp_path = output_dir / filename

        with open(tp_path, 'w', encoding='utf-8') as f:
            f.write(thought_pattern_content)

        return str(tp_path)

    def _generate_provenance_trace(
        self,
        job_info: Dict[str, Any],
        output_dir: Path
    ) -> Optional[str]:
        """
        Generate a provenance trace document showing source attribution for each claim.

        Args:
            job_info: Parsed job description info
            output_dir: Output directory

        Returns:
            Path to trace document or None if failed
        """
        if not PROVENANCE_AVAILABLE:
            return None

        company = job_info.get('company', 'Unknown')
        title = job_info.get('title', 'Unknown')

        try:
            import hashlib

            # Create session ID from job info
            session_hash = hashlib.md5(f"{company}{title}".encode()).hexdigest()[:8]

            # Initialize validator
            validator = ProvenanceValidator()

            # Create provenance trace object
            trace = ProvenanceTrace(
                session_id=session_hash,
                target_company=company,
                target_title=title,
                job_description_summary=f"{title} at {company}",
                jd_required_skills=job_info.get('required_skills', []) or [],
                jd_responsibilities=(job_info.get('responsibilities', []) or [])[:5]
            )

            # Validate resume if generated
            if self._last_resume_content:
                self._log("  Validating resume claims...")
                resume_provenance = validator.validate_resume(self._last_resume_content)
                trace.resume_provenance = resume_provenance
                self._log(f"  [OK] Resume: {resume_provenance.verified_claims} verified, "
                         f"{resume_provenance.warning_claims} warnings, "
                         f"{resume_provenance.error_claims} errors")

            # Validate cover letter if generated
            if self._last_cover_letter_content:
                self._log("  Validating cover letter claims...")
                cl_provenance = validator.parse_resume_for_validation(self._last_cover_letter_content)
                cl_provenance.document_type = "cover_letter"
                cl_provenance = validator.validate_document(self._last_cover_letter_content, cl_provenance)
                trace.cover_letter_provenance = cl_provenance
                self._log(f"  [OK] Cover letter: {cl_provenance.verified_claims} verified, "
                         f"{cl_provenance.warning_claims} warnings, "
                         f"{cl_provenance.error_claims} errors")

            # Generate trace document
            filename = f"Watson_Mulkey_{sanitize_filename(company)}_Trace.md"
            trace_path = output_dir / filename

            generate_trace_document(trace, trace_path)

            return str(trace_path)

        except Exception as e:
            self._log(f"  Warning: Provenance trace generation failed: {e}", force=True)
            return None

    # =========================================================================
    # Interview Prep Methods
    # =========================================================================

    # Bank of common behavioral questions - LLM selects the most relevant
    BEHAVIORAL_QUESTION_BANK = [
        "Tell me about a time you had to influence without authority.",
        "Describe a situation where you had to make a difficult product decision with incomplete data.",
        "Tell me about a time you managed competing stakeholder priorities.",
        "Describe a time you turned around a struggling project or product.",
        "Tell me about a time you used data to drive a product decision.",
        "Describe a situation where you had to push back on a request from leadership.",
        "Tell me about a time you had to build alignment across multiple teams.",
        "Describe a time you identified and solved a critical user problem.",
        "Tell me about a time you failed and what you learned from it.",
        "Describe a situation where you had to rapidly learn a new domain.",
        "Tell me about a time you successfully launched a product from scratch (0-1).",
        "Describe a time you improved a process or workflow significantly.",
        "Tell me about a time you had to manage a difficult stakeholder relationship.",
        "Describe a situation where you had to balance speed with quality.",
        "Tell me about a time you conducted user research that changed the product direction.",
    ]

    def _generate_interview_prep(
        self,
        job_info: Dict[str, Any],
        context: Dict[str, str],
        output_dir: Path,
        output_format: str
    ) -> List[str]:
        """
        Orchestrate interview prep package generation.

        Phase 1: Select 8 behavioral questions relevant to this role
        Phase 2: Per-job STAR generation (isolated, same pattern as _generate_job_bullets)
        Phase 3: Parallel section generation (technical, company, questions, strengths)
        Phase 4: Template-based assembly into study document markdown
        Phase 5: LLM condensation into flashcard format

        Returns list of generated file paths.
        """
        from config import INTERVIEW_BEHAVIORAL_QUESTION_COUNT

        company = job_info.get('company', 'Unknown')
        title = job_info.get('title', 'Unknown')
        generated_files = []

        # === PHASE 1: Select behavioral questions relevant to this role ===
        self._log("  [Phase 1] Selecting behavioral questions for this role...")
        questions = self._select_behavioral_questions(job_info, INTERVIEW_BEHAVIORAL_QUESTION_COUNT)
        self._log(f"    Selected {len(questions)} questions")

        # === PHASE 2: Per-job STAR generation (isolated) ===
        self._log("  [Phase 2] Generating STAR answers with per-job isolation...")
        star_answers = self._generate_interview_star_answers(job_info, questions)
        self._log(f"    Generated answers for {len(star_answers)} questions")

        # === PHASE 3: Generate remaining sections ===
        self._log("  [Phase 3] Generating interview prep sections...")

        role_overview = self._generate_role_overview(job_info, context)
        self._log("    Role overview complete")

        technical_qa = self._generate_interview_technical_qa(job_info, context)
        self._log("    Technical Q&A complete")

        company_alignment = self._generate_interview_company_alignment(job_info, context)
        self._log("    Company alignment complete")

        questions_to_ask = self._generate_interview_questions_to_ask(job_info)
        self._log("    Questions to ask complete")

        strengths_weaknesses = self._generate_interview_strengths_weaknesses(job_info, context)
        self._log("    Strengths & weaknesses complete")

        # === PHASE 4: Assemble study document ===
        self._log("  [Phase 4] Assembling study document...")

        # Salary section is template-based (no LLM call)
        salary_section = self._get_salary_negotiation_template()

        # Format STAR answers
        star_section = ""
        for q, answer in star_answers.items():
            star_section += f"### {q}\n\n{answer}\n\n"

        study_doc = f"""# Interview Prep: {title} at {company}

---

## 1. Role Overview

{role_overview}

---

## 2. Behavioral Questions (STAR Format)

{star_section}

---

## 3. Technical Q&A

{technical_qa}

---

## 4. Company Research & Alignment

{company_alignment}

---

## 5. Questions to Ask the Interviewer

{questions_to_ask}

---

## 6. Strengths & Weaknesses

{strengths_weaknesses}

---

## 7. Salary & Negotiation Context

{salary_section}

---

*Generated for: {title} at {company}*
"""

        # Save study document
        study_filename = f"Watson_Mulkey_{sanitize_filename(company)}_InterviewPrep.md"
        study_path = output_dir / study_filename
        with open(study_path, 'w', encoding='utf-8') as f:
            f.write(study_doc)

        # Store for provenance tracing
        self._last_interview_prep_content = study_doc

        # Generate PDF if requested
        if output_format in ['pdf', 'all'] and PDF_AVAILABLE:
            pdf_filename = f"Watson_Mulkey_{sanitize_filename(company)}_InterviewPrep.pdf"
            pdf_path = output_dir / pdf_filename
            try:
                markdown_to_pdf(study_doc, str(pdf_path))
                self._log(f"    [OK] Interview prep PDF: {pdf_path}")
                generated_files.append(str(pdf_path))
                # Clean up markdown if generating all formats
                if output_format == 'all':
                    study_path.unlink(missing_ok=True)
            except Exception as e:
                self._log(f"    Warning: Interview prep PDF failed: {e}")
                generated_files.append(str(study_path))
        else:
            generated_files.append(str(study_path))

        # === PHASE 5: Generate flashcards via LLM condensation ===
        self._log("  [Phase 5] Generating flashcards...")
        flashcard_files = self._generate_flashcards(study_doc, job_info, output_dir, output_format)
        generated_files.extend(flashcard_files)
        self._log(f"    Flashcards complete: {len(flashcard_files)} files")

        return generated_files

    def _select_behavioral_questions(
        self,
        job_info: Dict[str, Any],
        count: int = 8
    ) -> List[str]:
        """Use a quick LLM call to select the most relevant behavioral questions for this role."""
        if not self.client:
            return self.BEHAVIORAL_QUESTION_BANK[:count]

        questions_list = "\n".join(f"{i+1}. {q}" for i, q in enumerate(self.BEHAVIORAL_QUESTION_BANK))
        required_skills = ', '.join(job_info.get('required_skills', [])[:8])
        responsibilities = ', '.join(job_info.get('responsibilities', [])[:5])

        prompt = f"""From the following list of behavioral interview questions, select the {count} most likely to be asked for this specific role.

ROLE: {job_info.get('title', 'Unknown')} at {job_info.get('company', 'Unknown')}
KEY SKILLS: {required_skills}
KEY RESPONSIBILITIES: {responsibilities}

AVAILABLE QUESTIONS:
{questions_list}

Return ONLY the question numbers, comma-separated (e.g., "1,3,5,7,9,11,13,15").
Select the {count} questions most relevant to this specific role."""

        try:
            response = call_claude_with_retry(
                self.client,
                model=config.CLAUDE_MODEL,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse selected question numbers
            text = response.content[0].text.strip()
            numbers = [int(n.strip()) for n in re.findall(r'\d+', text)]
            selected = []
            for n in numbers:
                if 1 <= n <= len(self.BEHAVIORAL_QUESTION_BANK) and len(selected) < count:
                    selected.append(self.BEHAVIORAL_QUESTION_BANK[n - 1])

            # Pad if needed
            if len(selected) < count:
                for q in self.BEHAVIORAL_QUESTION_BANK:
                    if q not in selected and len(selected) < count:
                        selected.append(q)

            return selected

        except Exception as e:
            self._log(f"    Warning: Question selection failed ({e}), using defaults")
            return self.BEHAVIORAL_QUESTION_BANK[:count]

    def _generate_interview_star_answers(
        self,
        job_info: Dict[str, Any],
        questions: List[str]
    ) -> Dict[str, str]:
        """
        Generate STAR-format answers using per-job isolation.

        For each job, the LLM sees ONLY that job's achievements (same pattern
        as _generate_job_bullets). After all jobs are processed, best answer
        per question is selected (preferring answers with metrics).
        """
        from config import MAX_INTERVIEW_STAR_TOKENS

        if not self.client:
            return {q: "*(No API key available)*" for q in questions}

        # Collect candidate answers per question across all jobs
        candidates: Dict[str, List[Dict[str, str]]] = {q: [] for q in questions}

        jobs = self.retriever.get_jobs_list()
        selected_jobs = jobs[:4] if jobs else []

        for job in selected_jobs:
            job_context = self.retriever.get_single_job_context(job)
            company = job_context['company']

            # Target job requirements for relevance
            required_skills = ', '.join(job_info.get('required_skills', [])[:5])
            responsibilities = ', '.join(job_info.get('responsibilities', [])[:3])

            questions_text = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))

            prompt = f"""Generate STAR-format behavioral interview answers using ONLY this job's experience.

JOB TO DRAW FROM:
Company: {company}
Title: {job_context['title']}
Dates: {job_context['dates']}
Context: {job_context['context'] or 'N/A'}

AVAILABLE ACHIEVEMENTS (use ONLY these - do not invent):
{job_context['achievements']}

AVAILABLE RESPONSIBILITIES:
{job_context['responsibilities'] or '(None recorded)'}

TARGET POSITION (for relevance):
- Title: {job_info.get('title', 'Unknown')} at {job_info.get('company', 'Unknown')}
- Required Skills: {required_skills}
- Key Responsibilities: {responsibilities}

QUESTIONS TO ANSWER:
{questions_text}

INSTRUCTIONS:
- For each question where you have relevant experience from THIS JOB, provide a STAR answer
- If this job has no relevant experience for a question, write "NO_MATCH" for that question
- Include [ACH:xxx] provenance tags when referencing specific achievements
- Preserve exact metrics from source data

FORMAT (for each question you can answer):
**Question N: [question text]**

**Situation:** [Context and challenge]
**Task:** [What you needed to accomplish]
**Action:** [What you specifically did]
**Result:** [Quantified outcome with exact metrics]

Generate answers for {company}:"""

            try:
                response = call_claude_with_retry(
                    self.client,
                    model=config.CLAUDE_MODEL,
                    max_tokens=MAX_INTERVIEW_STAR_TOKENS,
                    messages=[{"role": "user", "content": prompt}]
                )

                content = response.content[0].text

                # Parse answers by question number
                current_q_idx = None
                current_answer_lines = []

                for line in content.split('\n'):
                    # Check for question header
                    q_match = re.match(r'\*\*Question\s+(\d+)', line)
                    if q_match:
                        # Save previous answer
                        if current_q_idx is not None and current_answer_lines:
                            answer_text = '\n'.join(current_answer_lines).strip()
                            if 'NO_MATCH' not in answer_text:
                                q_idx = current_q_idx - 1
                                if 0 <= q_idx < len(questions):
                                    candidates[questions[q_idx]].append({
                                        'company': company,
                                        'answer': answer_text
                                    })
                        current_q_idx = int(q_match.group(1))
                        current_answer_lines = []
                    elif current_q_idx is not None:
                        current_answer_lines.append(line)

                # Don't forget last answer
                if current_q_idx is not None and current_answer_lines:
                    answer_text = '\n'.join(current_answer_lines).strip()
                    if 'NO_MATCH' not in answer_text:
                        q_idx = current_q_idx - 1
                        if 0 <= q_idx < len(questions):
                            candidates[questions[q_idx]].append({
                                'company': company,
                                'answer': answer_text
                            })

                self._log(f"    Processed STAR answers from {company}")

            except Exception as e:
                self._log(f"    Warning: STAR generation failed for {company}: {e}")

        # Deduplicate: select best answer per question (prefer ones with metrics)
        final_answers = {}
        for question, answer_list in candidates.items():
            if not answer_list:
                final_answers[question] = "*No matching experience found in career data for this question. Prepare a general answer.*"
                continue

            # Score answers: prefer ones with numbers/percentages (metrics)
            best = answer_list[0]
            best_score = len(re.findall(r'\d+%|\d+\+?', best['answer']))
            for candidate in answer_list[1:]:
                score = len(re.findall(r'\d+%|\d+\+?', candidate['answer']))
                if score > best_score:
                    best = candidate
                    best_score = score

            final_answers[question] = best['answer']

        return final_answers

    def _generate_role_overview(
        self,
        job_info: Dict[str, Any],
        context: Dict[str, str]
    ) -> str:
        """Generate a role overview section for the interview prep doc."""
        if not self.client:
            return f"**Position:** {job_info.get('title', 'Unknown')} at {job_info.get('company', 'Unknown')}\n\n*No API key available for detailed overview.*"

        required_skills = ', '.join(job_info.get('required_skills', []))
        responsibilities = '\n'.join(f"- {r}" for r in job_info.get('responsibilities', [])[:8])

        prompt = f"""Create a concise role overview for interview preparation.

POSITION: {job_info.get('title', 'Unknown')} at {job_info.get('company', 'Unknown')}
REQUIRED SKILLS: {required_skills}
KEY RESPONSIBILITIES:
{responsibilities}

COMPANY MISSION: {job_info.get('company_mission', 'Not specified')}

CANDIDATE'S KEY SKILLS:
{context['skills']}

Generate:
1. A 2-3 sentence position summary
2. The top 5 key requirements from the JD
3. 3-4 specific reasons Watson is a strong fit (based on real skills/experience above)

Keep it factual and specific. Do NOT invent experience."""

        try:
            response = call_claude_with_retry(
                self.client,
                model=config.CLAUDE_MODEL,
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            self._log(f"    Warning: Role overview generation failed: {e}")
            return f"**Position:** {job_info.get('title', 'Unknown')} at {job_info.get('company', 'Unknown')}\n\n*Generation failed. Review the job description manually.*"

    def _generate_interview_technical_qa(
        self,
        job_info: Dict[str, Any],
        context: Dict[str, str]
    ) -> str:
        """Generate likely technical questions with evidence-based talking points."""
        from config import MAX_INTERVIEW_SECTION_TOKENS

        if not self.client:
            return "*No API key available for technical Q&A generation.*"

        required_skills = ', '.join(job_info.get('required_skills', []))
        preferred_skills = ', '.join(job_info.get('preferred_skills', []))

        prompt = f"""Generate likely technical interview questions for this role with talking points.

POSITION: {job_info.get('title', 'Unknown')} at {job_info.get('company', 'Unknown')}
REQUIRED SKILLS: {required_skills}
PREFERRED SKILLS: {preferred_skills}

WATSON'S ACTUAL SKILLS & EVIDENCE:
{context['skills']}

For each required skill, generate:
1. A likely technical question the interviewer might ask
2. 2-3 bullet point talking points Watson can use, drawn from ACTUAL experience above
3. If Watson lacks direct experience with a skill, note it as a gap with a suggested preparation strategy

FORMAT:
### [Skill/Topic]
**Q:** [Likely question]
**Talking Points:**
- [Point 1 with specific evidence]
- [Point 2 with specific evidence]

STRICT RULES:
- ONLY reference skills and experience from the data above
- Do NOT invent projects or metrics
- Be honest about gaps"""

        try:
            response = call_claude_with_retry(
                self.client,
                model=config.CLAUDE_MODEL,
                max_tokens=MAX_INTERVIEW_SECTION_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            self._log(f"    Warning: Technical Q&A generation failed: {e}")
            return "*Technical Q&A generation failed. Review required skills from the job description.*"

    def _generate_interview_company_alignment(
        self,
        job_info: Dict[str, Any],
        context: Dict[str, str]
    ) -> str:
        """Generate company research and alignment section."""
        from config import MAX_INTERVIEW_SECTION_TOKENS

        if not self.client:
            return "*No API key available for company alignment generation.*"

        prompt = f"""Generate a company research and alignment section for interview preparation.

COMPANY: {job_info.get('company', 'Unknown')}
ROLE: {job_info.get('title', 'Unknown')}
COMPANY MISSION: {job_info.get('company_mission', 'Not specified')}
INDUSTRY: {job_info.get('industry', 'Not specified')}

WATSON'S PERSONAL VALUES:
{context['personal_values']}

WATSON'S CAREER HISTORY:
{context['jobs']}

Generate:

### What We Know from the JD
- Key company info and context extracted from the job description
- Industry positioning and market context (if evident)

### Value Alignment
- Specific ways Watson's values and career motivations align with this company
- Examples from past experience that demonstrate alignment

### Culture Fit Narrative
- A 2-3 sentence narrative Watson can use in "Why this company?" questions
- Reference specific company attributes and genuine personal motivations

### Key Talking Points
- 3-4 bullet points for demonstrating company knowledge in the interview

Be specific and authentic. Do NOT invent company information not present in the JD."""

        try:
            response = call_claude_with_retry(
                self.client,
                model=config.CLAUDE_MODEL,
                max_tokens=MAX_INTERVIEW_SECTION_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            self._log(f"    Warning: Company alignment generation failed: {e}")
            return "*Company alignment generation failed. Research the company independently.*"

    def _generate_interview_questions_to_ask(
        self,
        job_info: Dict[str, Any]
    ) -> str:
        """Generate smart, role-specific questions to ask the interviewer."""
        if not self.client:
            return "*No API key available for question generation.*"

        required_skills = ', '.join(job_info.get('required_skills', [])[:5])
        responsibilities = ', '.join(job_info.get('responsibilities', [])[:5])

        prompt = f"""Generate 8-10 smart, specific questions Watson should ask in an interview.

POSITION: {job_info.get('title', 'Unknown')} at {job_info.get('company', 'Unknown')}
KEY SKILLS: {required_skills}
KEY RESPONSIBILITIES: {responsibilities}
COMPANY MISSION: {job_info.get('company_mission', 'Not specified')}

Categorize questions into:

### About the Role
- 2-3 questions about day-to-day responsibilities, success metrics, team structure

### About the Team
- 2 questions about team dynamics, collaboration, cross-functional work

### About Growth & Impact
- 2 questions about career growth, impact measurement, learning opportunities

### About Technology & Process
- 2-3 questions about tech stack, product process, development methodology

Make questions specific to THIS role, not generic.
Each question should demonstrate Watson's experience and genuine curiosity."""

        try:
            response = call_claude_with_retry(
                self.client,
                model=config.CLAUDE_MODEL,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            self._log(f"    Warning: Questions to ask generation failed: {e}")
            return "*Question generation failed. Prepare your own questions about the role, team, and company.*"

    def _generate_interview_strengths_weaknesses(
        self,
        job_info: Dict[str, Any],
        context: Dict[str, str]
    ) -> str:
        """Generate strengths and weaknesses framed from career data."""
        from config import MAX_INTERVIEW_SECTION_TOKENS

        if not self.client:
            return "*No API key available for strengths/weaknesses generation.*"

        prompt = f"""Generate a strengths and weaknesses section for interview preparation.

POSITION: {job_info.get('title', 'Unknown')} at {job_info.get('company', 'Unknown')}
REQUIRED SKILLS: {', '.join(job_info.get('required_skills', []))}

WATSON'S SKILLS & EVIDENCE:
{context['skills']}

WATSON'S CAREER HISTORY:
{context['jobs']}

WATSON'S ACHIEVEMENTS:
{context['achievements']}

Generate:

### Strengths (Top 4)
For each strength:
- **[Strength Name]**: One-sentence description
  - *Evidence*: Specific example with metrics from career data
  - *How to frame*: A suggested 1-2 sentence answer for the interview

### Weaknesses (Top 2-3)
For each weakness:
- **[Weakness Name]**: Honest description
  - *Growth narrative*: How Watson is actively addressing this
  - *How to frame*: A suggested 1-2 sentence answer that shows self-awareness

RULES:
- Strengths MUST be backed by real evidence from the data above
- Weaknesses should be genuine but framed with growth narratives
- Do NOT use cliche weaknesses ("I work too hard", "I'm a perfectionist")
- Focus on areas where the JD requires skills Watson is still developing"""

        try:
            response = call_claude_with_retry(
                self.client,
                model=config.CLAUDE_MODEL,
                max_tokens=MAX_INTERVIEW_SECTION_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            self._log(f"    Warning: Strengths/weaknesses generation failed: {e}")
            return "*Strengths/weaknesses generation failed. Prepare your own based on career experience.*"

    def _generate_flashcards(
        self,
        study_document: str,
        job_info: Dict[str, Any],
        output_dir: Path,
        output_format: str
    ) -> List[str]:
        """
        Condense the full study document into Q/A flashcard format via LLM.

        Appends a one-page cheat sheet with top metrics, keywords, questions to ask,
        and a "why this company" one-liner.
        """
        from config import MAX_FLASHCARD_TOKENS

        company = job_info.get('company', 'Unknown')
        title = job_info.get('title', 'Unknown')
        generated_files = []

        if not self.client:
            fallback = f"# Flashcards: {title} at {company}\n\n*No API key available for flashcard generation.*\n"
            filename = f"Watson_Mulkey_{sanitize_filename(company)}_Flashcards.md"
            path = output_dir / filename
            with open(path, 'w', encoding='utf-8') as f:
                f.write(fallback)
            return [str(path)]

        prompt = f"""Condense this interview prep study document into a flashcard format for self-quizzing.

STUDY DOCUMENT:
{study_document}

OUTPUT FORMAT:

# Interview Flashcards: {title} at {company}

## Behavioral Questions

For each STAR answer in the study doc, create a flashcard:
**Q:** [The behavioral question]
**A:** [2-3 sentence condensed version of the STAR answer, keeping the key metric/result]

## Technical Questions

For each technical question, create a flashcard:
**Q:** [Technical question]
**A:** [Key talking points condensed to 1-2 sentences]

## Company Knowledge

**Q:** Why do you want to work at {company}?
**A:** [1-2 sentence answer from alignment section]

**Q:** What do you know about {company}?
**A:** [Key facts from company research section]

## Quick Self-Quiz

For strengths, weaknesses, and other prep topics:
**Q:** [Question]
**A:** [Condensed answer]

---

## One-Page Cheat Sheet

### Top 5 Metrics to Remember
[List the 5 most impressive quantified achievements]

### Top 5 Keywords from JD
[List the 5 most important keywords/skills to weave into answers]

### Top 3 Questions to Ask
[The 3 strongest questions from the questions-to-ask section]

### "Why This Company" One-Liner
[A single compelling sentence]

### "Why This Role" One-Liner
[A single compelling sentence]

---

RULES:
- Preserve exact metrics (32%, 50%, etc.)
- Keep flashcard answers concise (2-3 sentences max)
- The cheat sheet should fit on one printed page
- Do NOT add information not in the study document"""

        try:
            response = call_claude_with_retry(
                self.client,
                model=config.CLAUDE_MODEL,
                max_tokens=MAX_FLASHCARD_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )

            flashcard_content = response.content[0].text.strip()

        except Exception as e:
            self._log(f"    Warning: Flashcard generation failed: {e}")
            flashcard_content = f"# Interview Flashcards: {title} at {company}\n\n*Flashcard generation failed. Review the study document instead.*\n"

        # Save flashcard file
        md_filename = f"Watson_Mulkey_{sanitize_filename(company)}_Flashcards.md"
        md_path = output_dir / md_filename
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(flashcard_content)

        # Generate PDF if requested
        if output_format in ['pdf', 'all'] and PDF_AVAILABLE:
            pdf_filename = f"Watson_Mulkey_{sanitize_filename(company)}_Flashcards.pdf"
            pdf_path = output_dir / pdf_filename
            try:
                markdown_to_pdf(flashcard_content, str(pdf_path))
                self._log(f"    [OK] Flashcard PDF: {pdf_path}")
                generated_files.append(str(pdf_path))
                if output_format == 'all':
                    md_path.unlink(missing_ok=True)
            except Exception as e:
                self._log(f"    Warning: Flashcard PDF failed: {e}")
                generated_files.append(str(md_path))
        else:
            generated_files.append(str(md_path))

        return generated_files

    def _get_salary_negotiation_template(self) -> str:
        """Return template-based salary negotiation frameworks (no LLM call, no specific numbers)."""
        return """### General Negotiation Framework

1. **Research Phase**: Before the interview, research market rates for this role on Glassdoor, Levels.fyi, and LinkedIn Salary Insights
2. **Deflect Early**: If asked about salary expectations early, redirect: "I'd love to learn more about the role first to understand the full picture before discussing compensation"
3. **Let Them Go First**: When pressed, ask: "What's the budgeted range for this position?"
4. **Anchor High**: If you must give a number, provide a range anchored above your target
5. **Total Comp**: Always consider the full package - base, bonus, equity, benefits, PTO, remote flexibility

### Framework for "What Are Your Salary Expectations?"

"Based on my research and experience level, I'm looking at the market range for this type of role. I'm flexible and more focused on finding the right fit; I'm confident we can find a number that works for both of us once we determine I'm the right person for the role."

### After Receiving an Offer

1. Express enthusiasm but don't accept immediately
2. Ask for the full offer in writing
3. Take 24-48 hours to evaluate
4. Negotiate on multiple dimensions (base, signing bonus, equity, start date, PTO)
5. Be collaborative, not adversarial: "I'm excited about this opportunity. Is there flexibility on...?"

### Key Principles

- Never lie about current compensation
- Know your walkaway number before negotiating
- Silence is powerful; let the other side fill it
- Get everything in writing before accepting"""

    def _generate_basic_cover_letter(self, job_info: Dict[str, Any], output_dir: Path) -> str:
        """Generate basic template cover letter (fallback when no API)."""
        company = job_info.get('company', 'Unknown')
        title = job_info.get('title', 'Unknown')

        cover_letter_content = f"""Dear Hiring Team,

I'm excited to submit my application for the {title} position at {company}. With 8 years of product management experience and a proven track record in [relevant area], I believe I'd be an excellent fit for this role.

## Why I'm a Great Fit

**[Key Requirement from Job Description]**
- [Specific achievement or experience that demonstrates this]
- Quantified outcome: [metric]

**[Another Key Requirement]**
- [Relevant experience]
- Impact: [specific result]

**[Third Key Requirement]**
- [Supporting experience]
- Context: [how this applies to the role]

## What Excites Me About {company}

[Company mission alignment or values connection]

## What I'll Bring

With experience at companies like Discovery Education (50M users), Bookshop.org ($50M revenue), and Simplifya (compliance software), I've developed expertise in:
- Building products for diverse user segments
- Data-driven decision making and A/B testing
- Leading cross-functional teams to ship valuable features
- Working with less technical stakeholders to solve complex problems

I'd love an opportunity to discuss how my experience aligns with {company}'s needs. Thank you for your time and consideration, and I look forward to speaking soon.

Best regards,

Watson Mulkey
watsonmulkey@gmail.com
434-808-2493
"""

        # Save to file
        filename = f"Watson_Mulkey_{sanitize_filename(company)}_CoverLetter.md"
        file_path = output_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cover_letter_content)

        return str(file_path)


if __name__ == '__main__':
    # Quick test
    generator = ResumeGenerator(verbose=True)
    print("Generator initialized successfully")
