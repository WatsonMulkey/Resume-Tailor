"""
Core generation logic for resume and cover letter tailoring.

This module handles:
- Job description parsing and keyword extraction
- Supermemory retrieval for relevant experience
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

try:
    from pdf_generator import markdown_to_pdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

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
            model="claude-sonnet-4-20250514",  # Sonnet 4 - most capable model
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


class SupermemoryRetriever:
    """Retrieve relevant career information from supermemory."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def _log(self, message: str):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"  [Search] {message}")

    def retrieve_relevant_context(self, job_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Query supermemory for relevant experience based on job requirements.

        Returns:
            Dict with categories of relevant information as combined strings
        """
        context = {
            "achievements": "",
            "skills": "",
            "jobs": "",
            "writing_style": "",
            "personal_values": ""
        }

        # Search for relevant achievements and skills
        all_results = []

        # Build comprehensive search query
        search_terms = []

        # Add skills from job description
        for skill in job_info.get("required_skills", [])[:5]:  # Top 5 skills
            search_terms.append(skill)

        # Add key responsibilities
        for resp in job_info.get("responsibilities", [])[:3]:  # Top 3 responsibilities
            search_terms.append(resp[:50])  # First 50 chars

        # Add job title keywords
        title_keywords = job_info.get("title", "").split()[:3]
        search_terms.extend(title_keywords)

        # Perform searches
        if search_terms:
            # Search for achievements
            self._log("Searching for relevant achievements...")
            query = " ".join(search_terms[:10])  # Limit query length

            try:
                # Try to use MCP supermemory search if available
                from mcp__supermemory__search import search as supermemory_search

                # Search for achievements
                achievement_results = supermemory_search(informationToGet=f"achievements metrics results for {query}")
                context["achievements"] = achievement_results if achievement_results else self._get_fallback_achievements()

                # Search for skills
                skill_results = supermemory_search(informationToGet=f"skills experience evidence for {query}")
                context["skills"] = skill_results if skill_results else self._get_fallback_skills()

                # Search for job history
                job_results = supermemory_search(informationToGet=f"job history experience for {query}")
                context["jobs"] = job_results if job_results else self._get_fallback_jobs()

                # Search for writing style
                writing_results = supermemory_search(informationToGet="cover letter writing style tone")
                context["writing_style"] = writing_results if writing_results else self._get_fallback_writing_style()

                # Search for personal values (filter for domain-appropriateness)
                values_results = supermemory_search(informationToGet="personal values mission alignment career motivation")
                context["personal_values"] = values_results if values_results else self._get_fallback_personal_values()

            except ImportError:
                # Fall back to hardcoded context if MCP not available
                self._log("MCP supermemory not available, using fallback data")
                context = self._get_fallback_context()

        else:
            # No search terms, use all fallback data
            context = self._get_fallback_context()

        return context

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

    def _get_fallback_context(self) -> Dict[str, str]:
        """Complete fallback context when supermemory unavailable."""
        return {
            "achievements": self._get_fallback_achievements(),
            "skills": self._get_fallback_skills(),
            "jobs": self._get_fallback_jobs(),
            "writing_style": self._get_fallback_writing_style(),
            "personal_values": self._get_fallback_personal_values()
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
        self.retriever = SupermemoryRetriever(verbose=verbose)
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None

    def _log(self, message: str, force: bool = False):
        """Print message if verbose mode is enabled or force is True. Always call callback if provided."""
        if self.verbose or force:
            print(message)
        if self.log_callback:
            self.log_callback(message)

    def generate(
        self,
        job_description: str,
        company_name: Optional[str] = None,
        output_dir: Path = Path("./output"),
        resume_only: bool = False,
        cover_letter_only: bool = False,
        output_format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Generate tailored resume and/or cover letter.

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

        # Retrieve relevant context from supermemory
        self._log("Retrieving relevant experience from your career history...")
        context = self.retriever.retrieve_relevant_context(job_info)
        self._log("[OK] Context retrieved")
        self._log("")

        # Generate documents
        generated_files = []

        if not cover_letter_only:
            self._log("Generating tailored resume...")
            resume_path = self._generate_resume(job_info, context, output_dir, output_format)
            generated_files.append(resume_path)
            self._log(f"[OK] Resume generated: {resume_path}")
            self._log("")

        if not resume_only:
            self._log("Generating cover letter...")
            cover_letter_path = self._generate_cover_letter(job_info, context, output_dir, output_format)
            generated_files.append(cover_letter_path)
            self._log(f"[OK] Cover letter generated: {cover_letter_path}")
            self._log("")

        return {"files": generated_files}

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
        """Use Claude to generate a tailored resume."""

        company = job_info.get('company', 'Unknown')
        title = job_info.get('title', 'Unknown')

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

WATSON'S FACTUAL CAREER DATA (USE ONLY THIS - NEVER INVENT):

ACHIEVEMENTS:
{context['achievements']}

SKILLS:
{context['skills']}

JOB HISTORY:
{context['jobs']}

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
- Experience (3-4 most relevant roles in reverse chronological order, with achievement-focused bullet points)
- Key Achievements (4-5 quantified wins that match job requirements)
- Skills (include both technical/hard skills AND soft skills, using exact keywords from job description)
- Education: Bachelor of Arts - English, Hampden-Sydney College, 2004-2008
- Certifications: Pragmatic Marketing (Focus, Foundations, Build)

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
                model="claude-sonnet-4-20250514",  # Sonnet 4 - most capable model
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

        except Exception as e:
            self._log(f"Error generating with AI: {e}")
            # Fall back to basic template
            return self._generate_basic_resume(job_info, output_dir)

        # Save markdown file (temporary - used to generate other formats)
        filename = f"Watson_Mulkey_Resume_{company.replace(' ', '_')}.md"
        md_file_path = output_dir / filename

        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(resume_content)

        files_to_cleanup = []

        # Generate PDF if requested
        if output_format in ['pdf', 'all'] and PDF_AVAILABLE:
            pdf_filename = f"Watson_Mulkey_Resume_{company.replace(' ', '_')}.pdf"
            pdf_path = output_dir / pdf_filename
            try:
                markdown_to_pdf(md_file_path, pdf_path)
                self._log(f"[OK] PDF generated: {pdf_path}")
            except Exception as e:
                self._log(f"Warning: PDF generation failed: {e}")

        # Generate HTML if requested (temporary - not needed for final output)
        html_path = None
        if output_format in ['html', 'all'] and HTML_AVAILABLE:
            html_filename = f"Watson_Mulkey_Resume_{company.replace(' ', '_')}.html"
            html_path = output_dir / html_filename
            try:
                # Parse resume content into structured data for HTML template
                resume_data = self._parse_resume_for_html(resume_content, job_info)
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

    def _parse_resume_for_html(self, resume_text: str, job_info: Dict[str, Any]) -> Dict[str, Any]:
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
            'education': {
                'degree': 'Bachelor of Arts - English',
                'school': 'Hampden-Sydney College',
                'dates': '2004-2008'
            },
            'achievements': [],
            'skills': [],
            'certifications': []
        }

        # Extract job title from job_info if available
        if job_info.get('title'):
            data['title'] = f"Senior Product Manager - {job_info['title']}"

        # Parse experience section
        current_job = None
        in_experience = False
        in_skills = False

        for line in lines:
            line_stripped = line.strip()

            if '## Experience' in line or '## EXPERIENCE' in line:
                in_experience = True
                continue
            elif line.startswith('##') and not line.startswith('###'):
                in_experience = False
                if 'SKILLS' in line or 'Skills' in line:
                    in_skills = True
                else:
                    in_skills = False
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

            if in_skills and line.startswith('**'):
                # Extract skill
                skill = line.strip('*')
                if skill:
                    data['skills'].append(skill)

        if current_job:
            data['experience'].append(current_job)

        # Add achievements (sample - these come from context)
        data['achievements'] = [
            {
                'title': '32% YoY engagement increase',
                'description': 'Overhauled teacher-side app based on user research at Discovery Education'
            },
            {
                'title': '50% efficiency gain',
                'description': 'Refactored flagship auditing product at Simplifya'
            },
            {
                'title': '15% delivery improvement',
                'description': 'Led cross-functional teams across multiple projects at Discovery Education'
            }
        ]

        # Add certifications
        data['certifications'] = [
            {
                'title': 'Pragmatic Marketing - Focus',
                'description': 'Find strategic business opportunities in market problems and build effective product roadmaps'
            },
            {
                'title': 'Pragmatic Marketing - Foundations',
                'description': 'Learn how to decode market needs and build irresistible products'
            },
            {
                'title': 'Pragmatic Marketing - Build',
                'description': 'Master the art of aligning product development with market needs'
            }
        ]

        return data

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
        filename = f"Watson_Mulkey_Resume_{company.replace(' ', '_')}.md"
        file_path = output_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(resume_content)

        return str(file_path)

    def _generate_cover_letter(
        self,
        job_info: Dict[str, Any],
        context: Dict[str, str],
        output_dir: Path,
        output_format: str
    ) -> str:
        """Generate tailored cover letter with voice matching."""

        company = job_info.get('company', 'Unknown')
        title = job_info.get('title', 'Unknown')

        # If API key available, use Claude to generate tailored content
        if self.client:
            return self._generate_cover_letter_with_ai(job_info, context, output_dir, output_format)

        # Otherwise, use basic template
        return self._generate_basic_cover_letter(job_info, output_dir)

    def _generate_cover_letter_with_ai(
        self,
        job_info: Dict[str, Any],
        context: Dict[str, str],
        output_dir: Path,
        output_format: str
    ) -> str:
        """Use Claude to generate a tailored, voice-matched cover letter."""

        company = job_info.get('company', 'Unknown')
        title = job_info.get('title', 'Unknown')

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

WATSON'S FACTUAL CAREER DATA (ZERO HALLUCINATIONS - USE ONLY THIS):

ACHIEVEMENTS:
{context['achievements']}

SKILLS & EVIDENCE:
{context['skills']}

RELEVANT EXPERIENCE:
{context['jobs']}

WATSON'S AUTHENTIC WRITING VOICE:
{context['writing_style']}

PERSONAL VALUES & MOTIVATIONS:
{context['personal_values']}

CRITICAL RULE - PERSONAL ANECDOTES:
Personal stories/anecdotes should ONLY be used when they are DIRECTLY RELEVANT to the company's product domain or mission.

ACCEPTABLE Personal Connections:
- Mental health company (Headway) → Therapist story about how therapy changed Watson's life
- Audio hardware company (Universal Audio) → Watson being a hobbyist producer/composer who uses their products
- Social platform (Reddit) → Watson being a long-time user of the platform
- Customer engagement product (Iterable) → Watson's career starting in Customer Engagement/Support

UNACCEPTABLE Personal Connections:
- DO NOT use the therapist/mental health story for non-mental-health companies
- DO NOT use hobby/personal interest stories unless directly related to company's product
- When in doubt, USE PROFESSIONAL EXPERIENCE ONLY - no personal stories

COVER LETTER STRUCTURE & REQUIREMENTS:

**Opening Paragraph (Hook + Interest):**
- Start with genuine enthusiasm OR a DOMAIN-APPROPRIATE personal connection (see rules above)
- Immediately state the role you're applying for
- Include ONE sentence that shows you understand what makes this role unique
- AVOID generic "I'm excited to apply" - be specific about WHY this role/company
- DEFAULT to professional experience if no clear personal connection exists

**Body Paragraphs (2-3 focused examples):**
For each job requirement, provide ONE concrete story/example:
- Lead with the requirement/challenge
- Describe what you did (action)
- Quantify the impact with exact metrics from the data
- Connect explicitly to how this prepares you for their needs

Example flow: "At Discovery Education, I tackled a similar challenge with user engagement. By overhauling the teacher-side app based on user research, I drove a 32% year-over-year increase in engagement - exactly the kind of data-driven, user-focused approach that would translate well to [specific company challenge]."

**Closing Paragraph:**
- Synthesize why you're uniquely positioned for THIS role
- Express genuine interest in contributing to their specific mission/goals
- Clear, confident call to action (e.g., "I'd love the opportunity to discuss...")

CRITICAL WRITING GUIDELINES:
1. ZERO HALLUCINATIONS: Only use provided facts, metrics, and experiences
2. CONTACT INFO: If contact info is included, use EXACTLY as provided above - DO NOT modify
3. VOICE MATCHING: Sound like Watson - warm, professional, results-oriented, slightly conversational
4. NATURAL FLOW: Don't list achievements robotically - weave them into natural storytelling
5. SPECIFICITY: Use exact metrics (32%, 50%, $50M, 20+ people) - they're powerful
6. CONNECTION: Every example should explicitly tie back to job requirements
7. AUTHENTICITY: Avoid corporate jargon - use Watson's natural phrases
8. PUNCTUATION: Use semicolons to connect related independent clauses instead of em-dashes (Watson's personal writing style)
9. LENGTH: 350-450 words (concise but substantive)
10. PERSONALIZATION: Reference specific aspects of {company} or the role that genuinely align with Watson's experience/values

Generate a cover letter that feels genuinely written by Watson and makes hiring managers think "This person gets it."
"""

        try:
            response = call_claude_with_retry(
                self.client,
                model="claude-sonnet-4-20250514",  # Sonnet 4 - most capable model
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

        except Exception as e:
            # Log error with force=True so it ALWAYS shows (even with verbose=False)
            error_msg = f"CRITICAL ERROR: Cover letter AI generation failed: {str(e)}"
            self._log(error_msg, force=True)
            # Re-raise instead of falling back silently - user needs to know
            raise RuntimeError(error_msg) from e

        # Save markdown file (temporary - will be used to generate other formats)
        filename = f"Watson_Mulkey_{company.replace(' ', '_')}_CoverLetter.md"
        md_file_path = output_dir / filename

        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(cover_letter_content)

        generated_files = [str(md_file_path)]

        # Generate DOCX if requested (ATS-friendly Word format)
        if output_format in ['docx', 'all'] and DOCX_AVAILABLE:
            docx_filename = f"Watson_Mulkey_{company.replace(' ', '_')}_CoverLetter.docx"
            docx_path = output_dir / docx_filename
            try:
                generate_docx_cover_letter(cover_letter_content, docx_path)
                self._log(f"[OK] Cover letter DOCX generated: {docx_path}", force=True)
                generated_files.append(str(docx_path))
            except Exception as e:
                self._log(f"Warning: Cover letter DOCX generation failed: {e}", force=True)

        # Generate PDF if requested
        if output_format in ['pdf', 'all'] and PDF_AVAILABLE:
            pdf_filename = f"Watson_Mulkey_{company.replace(' ', '_')}_CoverLetter.pdf"
            pdf_path = output_dir / pdf_filename
            try:
                markdown_to_pdf(md_file_path, pdf_path)
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
        filename = f"Watson_Mulkey_{company.replace(' ', '_')}_CoverLetter.md"
        file_path = output_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cover_letter_content)

        return str(file_path)


if __name__ == '__main__':
    # Quick test
    generator = ResumeGenerator(verbose=True)
    print("Generator initialized successfully")
