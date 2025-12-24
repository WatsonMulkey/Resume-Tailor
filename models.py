"""
Pydantic models for Resume Tailor career data.

These models ensure data validation, type safety, and prevent corruption.
All career data is validated against these schemas before saving.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
import re


class Achievement(BaseModel):
    """Represents a quantifiable achievement with context."""
    description: str = Field(min_length=20, max_length=500)
    company: str = Field(min_length=1)
    timeframe: str = Field(pattern=r"^\d{4}-\d{2}$|^\d{4}-\d{2} to \d{4}-\d{2}$|^\d{4}-\d{2} to Present$")
    result: Optional[str] = Field(default=None, max_length=200)
    metrics: Optional[List[str]] = Field(default_factory=list)

    @field_validator('description')
    @classmethod
    def validate_description_quality(cls, v: str) -> str:
        """Ensure description has substance."""
        if len(v.split()) < 5:
            raise ValueError("Description too short. Provide specific context (minimum 5 words).")
        return v


class Skill(BaseModel):
    """Represents a skill with evidence and proficiency."""
    name: str = Field(min_length=2, max_length=100)
    category: str  # technical, soft, domain
    proficiency: Optional[str] = Field(default="intermediate")  # beginner, intermediate, advanced, expert
    examples: List[Achievement] = Field(min_length=1)
    last_used: str = Field(pattern=r"^\d{4}-\d{2}$")

    @field_validator('name')
    @classmethod
    def validate_skill_name(cls, v: str) -> str:
        """Prevent generic skill names."""
        banned_generic = [
            'team player', 'hard worker', 'quick learner',
            'detail oriented', 'self motivated', 'go-getter',
            'results driven', 'passionate'
        ]
        if v.lower() in banned_generic:
            raise ValueError(f"'{v}' is too generic. Specify a concrete technical or domain skill.")

        # Ensure skill name doesn't contain special characters (except spaces, dots, hyphens, plus, hash, ampersand, slash)
        if not re.match(r"^[A-Za-z0-9\s\.\-\+#&/]+$", v):
            raise ValueError(f"Skill name contains invalid characters: '{v}'")

        return v


class Job(BaseModel):
    """Represents a job/position in work history."""
    company: str
    title: str
    start_date: str = Field(pattern=r"^\d{4}-\d{2}$|^\d{2}/\d{4}$")  # YYYY-MM or MM/YYYY
    end_date: Optional[str] = Field(default=None, pattern=r"^\d{4}-\d{2}$|^\d{2}/\d{4}$|^Present$")
    location: Optional[str] = None
    company_context: Optional[str] = None
    description: Optional[str] = None
    responsibilities: Optional[List[str]] = Field(default_factory=list)
    achievements: Optional[List[Achievement]] = Field(default_factory=list)
    skills_used: Optional[List[str]] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_dates(self):
        """Ensure end_date is after start_date."""
        if self.end_date and self.end_date != "Present":
            # Simple validation: extract year and month
            start = self.start_date.replace('/', '-')
            end = self.end_date.replace('/', '-')

            # Compare YYYY-MM format
            if end < start:
                raise ValueError(f"End date ({self.end_date}) cannot be before start date ({self.start_date})")

        return self


class PersonalValue(BaseModel):
    """Represents personal values, motivations, or stories."""
    content: str = Field(min_length=10)
    category: str  # values, personal_story, motivation


class Education(BaseModel):
    """Represents educational background."""
    degree: str
    school: str
    dates: str
    location: Optional[str] = None
    details: Optional[List[str]] = Field(default_factory=list)


class Certification(BaseModel):
    """Represents professional certifications."""
    title: str
    organization: str
    date_obtained: Optional[str] = None
    expiration: Optional[str] = None
    details: Optional[str] = None


class Project(BaseModel):
    """Represents side projects or volunteer work."""
    title: str
    description: str
    timeframe: str = Field(pattern=r"^\d{4}-\d{2}$|^\d{4}-\d{2} to \d{4}-\d{2}$|^\d{4}-\d{2} to Present$")
    role: Optional[str] = None
    technologies: Optional[List[str]] = Field(default_factory=list)
    achievements: Optional[List[str]] = Field(default_factory=list)


class ContactInfo(BaseModel):
    """Contact information."""
    name: str
    email: str
    phone: str
    linkedin: Optional[str] = None
    location: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email validation."""
        if '@' not in v or '.' not in v:
            raise ValueError(f"Invalid email format: {v}")
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Prevent placeholder phone numbers."""
        if '555-555' in v or 'XXX' in v:
            raise ValueError(f"Placeholder phone number detected: {v}")
        return v


class CareerData(BaseModel):
    """Root model for all career data."""
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )

    version: str = "1.0"
    last_updated: datetime = Field(default_factory=datetime.now)
    contact_info: ContactInfo
    jobs: List[Job] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    personal_values: List[PersonalValue] = Field(default_factory=list)
    skipped_skills: List[str] = Field(default_factory=list)  # Skills user explicitly rejected during discovery

    @model_validator(mode='after')
    def validate_data_completeness(self):
        """Ensure minimum data quality."""
        # At least some basic info should be present
        if not self.contact_info:
            raise ValueError("Contact information is required")

        return self


class DiscoveredSkill(BaseModel):
    """
    Model for skills discovered during generation (used by discovery mode).
    Stricter validation than regular Skill model.
    """
    name: str = Field(min_length=2, max_length=100, pattern=r"^[A-Za-z0-9\s\.\-\+#&/]+$")
    company: str = Field(min_length=1)
    timeframe: str = Field(pattern=r"^\d{4}-\d{2}( to \d{4}-\d{2})?$|^\d{4}-\d{2} to Present$")
    example: str = Field(min_length=20, max_length=500)
    result: Optional[str] = Field(default=None, max_length=200)
    category: Optional[str] = Field(default="technical")
    discovered_during: Optional[str] = None  # Job title user was applying for

    @field_validator('name')
    @classmethod
    def validate_skill_name(cls, v: str) -> str:
        """Prevent generic skill names."""
        banned_generic = [
            'team player', 'hard worker', 'quick learner',
            'detail oriented', 'self motivated', 'go-getter',
            'results driven', 'passionate', 'self-starter'
        ]
        if v.lower() in banned_generic:
            raise ValueError(f"'{v}' is too generic. Specify a concrete technical skill.")
        return v

    @field_validator('example')
    @classmethod
    def validate_example_quality(cls, v: str) -> str:
        """Ensure example has substance."""
        if len(v.split()) < 5:
            raise ValueError("Example too short. Provide specific context (minimum 5 words).")

        # Check for placeholder patterns
        placeholders = ['[...]', '{...}', 'TBD', 'TODO', '[relevant', '[specific']
        for pattern in placeholders:
            if pattern.lower() in v.lower():
                raise ValueError(f"Example contains placeholder text: {pattern}")

        return v
