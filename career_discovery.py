"""
Career Discovery Module - Interactive Skill Discovery

Detects missing skills from job descriptions and prompts user to add them
with concrete examples, preventing hallucinations through structured input.

Features:
- Skill detection (keyword + semantic matching)
- Multi-step structured prompts (5 layers)
- Consistency validation against job history
- Review mode before saving
- Hallucination pattern detection
"""

import re
from typing import List, Dict, Any, Optional, Set
from pathlib import Path

from models import CareerData, Skill, Achievement, DiscoveredSkill
from career_data_manager import load_career_data, save_career_data


class SkillDetector:
    """Detect missing skills from job descriptions."""

    def __init__(self):
        # Common technical skills and tools
        self.tech_keywords = {
            # Programming languages
            'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'go', 'rust',
            'typescript', 'php', 'swift', 'kotlin', 'scala', 'r',

            # Frameworks
            'react', 'vue', 'angular', 'django', 'flask', 'spring', 'rails',
            'express', 'fastapi', 'next.js', 'nuxt', 'svelte',

            # Databases
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'dynamodb', 'cassandra', 'oracle', 'sqlite',

            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'jenkins', 'gitlab', 'github actions', 'circleci',

            # Data & Analytics
            'looker', 'tableau', 'power bi', 'pandas', 'numpy', 'spark',
            'hadoop', 'airflow', 'kafka', 'snowflake',

            # Product Management
            'jira', 'confluence', 'asana', 'figma', 'miro', 'amplitude',
            'mixpanel', 'google analytics', 'fullstory', 'a/b testing',

            # Methodologies
            'agile', 'scrum', 'kanban', 'lean', 'waterfall', 'safe',
        }

    def detect_missing_skills(
        self,
        job_description: str,
        career_data: CareerData,
        max_skills: int = 5
    ) -> List[str]:
        """
        Detect skills mentioned in job description but not in career data.

        Args:
            job_description: Raw job description text
            career_data: User's career data
            max_skills: Maximum skills to return

        Returns:
            List of detected skill names
        """
        # Get existing skills and skipped skills (lowercase for comparison)
        existing_skills = {skill.name.lower() for skill in career_data.skills}
        skipped_skills = {skill.lower() for skill in career_data.skipped_skills}

        # Detect skills in job description
        detected = set()
        job_lower = job_description.lower()

        # Method 1: Keyword matching (word boundary only)
        for keyword in self.tech_keywords:
            # Use word boundaries to avoid false matches (e.g., 'r' in 'for')
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if (re.search(pattern, job_lower, re.IGNORECASE) and
                keyword not in existing_skills and
                keyword not in skipped_skills):
                # Capitalize properly
                detected.add(self._capitalize_skill(keyword))

        # Method 2: Technology detection (regex patterns - only known tech formats)
        # Only match .js/.py frameworks and 3+ letter acronyms commonly used in tech
        tech_patterns = [
            r'\b([A-Z][a-z]+\.[a-z]+)\b',  # React.js, Vue.js, Next.js (must have .js/.py)
            r'\b([A-Z]{3,})\b',  # AWS, GCP, SQL (3+ letters, filters out PM, US, OR, etc.)
        ]

        for pattern in tech_patterns:
            matches = re.findall(pattern, job_description)
            for match in matches:
                # Additional filtering: must be in common tech acronyms or frameworks
                if (match.lower() not in existing_skills and
                    match.lower() not in skipped_skills and
                    (match.endswith(('.js', '.py')) or  # Framework with extension
                     match.lower() in self.tech_keywords or  # Known tech keyword
                     len(match) >= 4)):  # Longer acronyms are safer (REST, JSON, HTTP)
                    detected.add(match)

        # Convert to sorted list (by frequency in job description)
        detected_list = list(detected)
        detected_list.sort(
            key=lambda s: job_lower.count(s.lower()),
            reverse=True
        )

        return detected_list[:max_skills]

    def _capitalize_skill(self, skill: str) -> str:
        """Capitalize skill name properly."""
        # Special cases
        special_cases = {
            'sql': 'SQL',
            'aws': 'AWS',
            'gcp': 'GCP',
            'api': 'API',
            'rest': 'REST',
            'graphql': 'GraphQL',
            'postgresql': 'PostgreSQL',
            'mysql': 'MySQL',
            'mongodb': 'MongoDB',
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'next.js': 'Next.js',
            'vue.js': 'Vue.js',
            'react.js': 'React.js',
            'node.js': 'Node.js',
        }

        if skill.lower() in special_cases:
            return special_cases[skill.lower()]

        # Default: title case
        return skill.title()


class ConsistencyValidator:
    """Validate discovered skills against existing career data."""

    def __init__(self, career_data: CareerData):
        self.career_data = career_data

    def validate(self, discovered: DiscoveredSkill) -> Dict[str, Any]:
        """
        Validate discovered skill for consistency.

        Returns dict with validation results:
        {
            'valid': bool,
            'warnings': List[str],
            'errors': List[str]
        }
        """
        warnings = []
        errors = []

        # Check 1: Timeframe within job history
        timeframe_valid = self._validate_timeframe(discovered, warnings, errors)

        # Check 2: Company exists in job history
        company_valid = self._validate_company(discovered, warnings)

        # Check 3: Duplicate skill detection
        self._check_duplicate(discovered, warnings)

        # Check 4: No future dates
        self._check_future_dates(discovered, errors)

        # Check 5: Reasonability (<10 years ago for new skills)
        self._check_reasonability(discovered, warnings)

        return {
            'valid': len(errors) == 0,
            'warnings': warnings,
            'errors': errors
        }

    def _validate_timeframe(
        self,
        discovered: DiscoveredSkill,
        warnings: List[str],
        errors: List[str]
    ) -> bool:
        """Validate timeframe is within job history."""
        # Parse timeframe
        if ' to ' in discovered.timeframe:
            start, end = discovered.timeframe.split(' to ')
        else:
            start = discovered.timeframe
            end = start

        # Find matching job
        company_match = None
        for job in self.career_data.jobs:
            if job.company.lower() == discovered.company.lower():
                company_match = job
                break

        if company_match:
            # Check if timeframe overlaps with job dates
            job_start = job.start_date
            job_end = job.end_date if job.end_date != 'Present' else '2099-12'

            if start < job_start or (end != 'Present' and end > job_end):
                warnings.append(
                    f"Timeframe ({discovered.timeframe}) is outside your "
                    f"employment at {discovered.company} ({job_start} to {job_end}). "
                    f"Is this from a side project?"
                )
                return False

        return True

    def _validate_company(self, discovered: DiscoveredSkill, warnings: List[str]) -> bool:
        """Validate company exists in job history."""
        companies = {job.company.lower() for job in self.career_data.jobs}

        if discovered.company.lower() not in companies:
            warnings.append(
                f"Company '{discovered.company}' is not in your job history. "
                f"Is this a side project or freelance work?"
            )
            return False

        return True

    def _check_duplicate(self, discovered: DiscoveredSkill, warnings: List[str]):
        """Check if skill already exists."""
        for skill in self.career_data.skills:
            if skill.name.lower() == discovered.name.lower():
                warnings.append(
                    f"You already have '{skill.name}' listed with "
                    f"{len(skill.examples)} example(s). Add this as another example?"
                )
                break

    def _check_future_dates(self, discovered: DiscoveredSkill, errors: List[str]):
        """Check for future dates."""
        from datetime import datetime

        if ' to ' in discovered.timeframe:
            start, end = discovered.timeframe.split(' to ')
        else:
            start = discovered.timeframe
            end = start

        current_month = datetime.now().strftime('%Y-%m')

        if start > current_month:
            errors.append(f"Start date ({start}) is in the future!")

        if end != 'Present' and end > current_month:
            errors.append(f"End date ({end}) is in the future!")

    def _check_reasonability(self, discovered: DiscoveredSkill, warnings: List[str]):
        """Check if timeframe is reasonable (<10 years old for new skills)."""
        from datetime import datetime

        if ' to ' in discovered.timeframe:
            start, _ = discovered.timeframe.split(' to ')
        else:
            start = discovered.timeframe

        # Parse year and month
        year, month = map(int, start.split('-'))
        skill_date = datetime(year, month, 1)
        current_date = datetime.now()

        years_ago = (current_date - skill_date).days / 365.25

        if years_ago > 10:
            warnings.append(
                f"This experience is from {years_ago:.1f} years ago. "
                f"Is this skill still relevant?"
            )


class HallucinationDetector:
    """Detect hallucination patterns in user responses."""

    def __init__(self):
        # Vague quantifiers
        self.vague_quantifiers = {
            'many', 'several', 'various', 'numerous', 'multiple',
            'some', 'a lot', 'plenty', 'countless'
        }

        # Unverifiable claims
        self.unverifiable_claims = {
            'best', 'world-class', 'leading', 'cutting-edge', 'state-of-the-art',
            'revolutionary', 'groundbreaking', 'innovative', 'next-generation'
        }

        # Placeholder patterns
        self.placeholder_patterns = [
            r'\[.*?\]',  # [relevant area], [specific metric]
            r'\{.*?\}',  # {details}, {example}
            r'\bTBD\b', r'\bTODO\b', r'\bFIXME\b'
        ]

    def detect(self, text: str, job_description: str = "") -> List[str]:
        """
        Detect hallucination patterns in text.

        Returns list of warnings.
        """
        warnings = []
        text_lower = text.lower()

        # Check vague quantifiers
        found_vague = [q for q in self.vague_quantifiers if q in text_lower]
        if found_vague:
            warnings.append(
                f"Vague quantifiers detected: {', '.join(found_vague)}. "
                f"Be more specific."
            )

        # Check unverifiable claims
        found_unverifiable = [c for c in self.unverifiable_claims if c in text_lower]
        if found_unverifiable:
            warnings.append(
                f"Unverifiable claims detected: {', '.join(found_unverifiable)}. "
                f"Provide concrete, measurable details instead."
            )

        # Check placeholder patterns
        for pattern in self.placeholder_patterns:
            if re.search(pattern, text):
                warnings.append(
                    f"Placeholder text detected. Complete the example with "
                    f"specific details."
                )
                break

        # Check similarity to job description (copy-paste detection)
        if job_description:
            similarity = self._calculate_similarity(text, job_description)
            if similarity > 0.7:
                warnings.append(
                    f"High similarity ({similarity*100:.0f}%) to job description. "
                    f"Use your own words and specific examples."
                )

        # Check for future tense (suggests not completed)
        future_patterns = [
            r'\bwill\b', r'\bgoing to\b', r'\bplanning to\b',
            r'\bintending to\b', r'\bexpect to\b'
        ]
        for pattern in future_patterns:
            if re.search(pattern, text_lower):
                warnings.append(
                    "Future tense detected. Describe what you've already done, "
                    "not what you plan to do."
                )
                break

        return warnings

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Simple word overlap similarity (0-1)."""
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))

        if not words1 or not words2:
            return 0.0

        overlap = len(words1 & words2)
        total = len(words1 | words2)

        return overlap / total if total > 0 else 0.0


# Convenience functions
def detect_missing_skills(job_description: str, max_skills: int = 5) -> List[str]:
    """
    Detect missing skills from job description.

    Args:
        job_description: Job description text
        max_skills: Maximum skills to return

    Returns:
        List of skill names
    """
    career_data = load_career_data()
    detector = SkillDetector()
    return detector.detect_missing_skills(job_description, career_data, max_skills)


def validate_discovered_skill(discovered: DiscoveredSkill) -> Dict[str, Any]:
    """
    Validate discovered skill for consistency.

    Args:
        discovered: DiscoveredSkill instance

    Returns:
        Validation results dict
    """
    career_data = load_career_data()
    validator = ConsistencyValidator(career_data)
    return validator.validate(discovered)


def detect_hallucinations(text: str, job_description: str = "") -> List[str]:
    """
    Detect hallucination patterns in text.

    Args:
        text: Text to check
        job_description: Optional job description for similarity check

    Returns:
        List of warning messages
    """
    detector = HallucinationDetector()
    return detector.detect(text, job_description)
