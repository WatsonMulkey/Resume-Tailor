"""
Automated Tests for Hallucination Detection

These tests verify that the resume-tailor system never generates hallucinated
contact information, incorrect metrics, or inappropriate personal stories.
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generator import (
    validate_generated_content,
    inject_correct_contact_info,
    CONTACT_INFO
)
from conflict_detector import ConflictDetector, DataConflict
from import_career_data import CAREER_DATA


class TestContactInfoInjection:
    """Test that contact info injection prevents all hallucinations."""

    def test_removes_fake_phone_numbers(self):
        """Verify fake phone numbers are removed and replaced."""
        fake_resume = """# Watson Mulkey
555-555-1234 | fake@email.com | linkedin.com/in/fake

## Experience
..."""

        result = inject_correct_contact_info(fake_resume)

        # Check fake info is gone
        assert "555-555" not in result
        assert "@email.com" not in result

        # Check correct info is present
        assert CONTACT_INFO['email'] in result
        assert CONTACT_INFO['phone'] in result
        assert CONTACT_INFO['linkedin'] in result

    def test_removes_hallucinated_email(self):
        """Verify hallucinated emails are removed."""
        fake_resume = """# M. Watson Mulkey
Email: watson.mulkeyt@gmail.com | Phone: 434-808-2493

## Summary
..."""

        result = inject_correct_contact_info(fake_resume)

        # The extra 't' should be gone
        assert "watson.mulkeyt@gmail.com" not in result
        assert CONTACT_INFO['email'] in result

    def test_preserves_content_after_header(self):
        """Verify content after contact header is preserved."""
        resume = """# Watson Mulkey
old@email.com | 555-5555

## Professional Summary
Experienced PM with 8 years of product management.

## Experience
- Achievement here"""

        result = inject_correct_contact_info(resume)

        # Content should be preserved
        assert "Professional Summary" in result
        assert "Experienced PM" in result
        assert "Achievement here" in result

        # But contact should be correct
        assert CONTACT_INFO['email'] in result
        assert "old@email.com" not in result

    def test_handles_empty_resume(self):
        """Handle edge case of empty content."""
        result = inject_correct_contact_info("")
        assert CONTACT_INFO['name'] in result
        assert CONTACT_INFO['email'] in result

    def test_handles_resume_without_contact_block(self):
        """Inject contact info even if original had none."""
        resume = """## Professional Summary
PM with experience in edtech."""

        result = inject_correct_contact_info(resume)

        assert CONTACT_INFO['email'] in result
        assert "PM with experience" in result


class TestHallucinationValidation:
    """Test the validation function that detects hallucinations."""

    def test_detects_fake_phone_numbers(self):
        """Detect common fake phone number patterns."""
        content = "Contact: 555-555-1234"
        job_info = {"company": "TestCo", "description": ""}

        warnings = validate_generated_content(content, job_info)

        assert len(warnings) > 0
        assert any("phone" in w.lower() for w in warnings)

    def test_detects_generic_emails(self):
        """Detect generic placeholder emails."""
        content = "Email: user@email.com"
        job_info = {"company": "TestCo", "description": ""}

        warnings = validate_generated_content(content, job_info)

        assert len(warnings) > 0
        assert any("email" in w.lower() for w in warnings)

    def test_detects_therapist_story_for_non_mental_health(self):
        """Detect inappropriate use of therapist story."""
        content = "Finding a therapist changed my life..."
        job_info = {
            "company": "ClassDojo",
            "description": "classroom communication app"
        }

        warnings = validate_generated_content(content, job_info)

        assert len(warnings) > 0
        assert any("therapist" in w.lower() or "mental health" in w.lower() for w in warnings)

    def test_allows_therapist_story_for_mental_health_company(self):
        """Allow therapist story for mental health companies."""
        content = "Finding a therapist changed my life..."
        job_info = {
            "company": "Headway",
            "description": "mental health therapy platform"
        }

        warnings = validate_generated_content(content, job_info)

        # Should NOT flag therapist story for mental health company
        therapist_warnings = [w for w in warnings if "therapist" in w.lower()]
        assert len(therapist_warnings) == 0

    def test_validates_correct_contact_present(self):
        """Verify correct contact info is present."""
        content = f"""# Watson Mulkey
{CONTACT_INFO['email']} | {CONTACT_INFO['phone']}

Experience here..."""
        job_info = {"company": "TestCo", "description": ""}

        warnings = validate_generated_content(content, job_info)

        # Should have no warnings about missing contact info
        contact_warnings = [w for w in warnings if "contact" in w.lower() or "email" in w.lower()]
        assert len(contact_warnings) == 0


class TestConflictDetection:
    """Test career data conflict detection."""

    def test_detects_changed_email(self):
        """Detect when email address changes."""
        detector = ConflictDetector(CAREER_DATA)

        new_contact = {
            "email": "new.email@gmail.com",  # Different from existing
            "phone": CONTACT_INFO['phone'],
            "name": CONTACT_INFO['name']
        }

        conflicts = detector.check_contact_info(new_contact)

        assert len(conflicts) > 0
        assert any("email" in c.field.lower() for c in conflicts)
        assert any(c.severity == "high" for c in conflicts)

    def test_allows_matching_contact_info(self):
        """No conflict when contact info matches."""
        detector = ConflictDetector(CAREER_DATA)

        conflicts = detector.check_contact_info(CONTACT_INFO)

        assert len(conflicts) == 0

    def test_detects_changed_job_dates(self):
        """Detect when job dates don't match."""
        detector = ConflictDetector(CAREER_DATA)

        new_job = {
            "company": "Registria",
            "dates": "01/2023 - 03/2025",  # Wrong dates
            "title": "Senior PM"
        }

        conflicts = detector.check_job_dates(new_job)

        assert len(conflicts) > 0
        assert any("date" in c.field.lower() for c in conflicts)

    def test_detects_metric_mismatch(self):
        """Detect when same achievement has different metrics."""
        detector = ConflictDetector(CAREER_DATA)

        new_achievement = {
            "company": "Discovery Education",
            "achievement": "User engagement increase",
            "metrics": "25% YoY engagement increase"  # Wrong! Should be 32%
        }

        conflicts = detector.check_achievement_metrics(new_achievement)

        assert len(conflicts) > 0
        assert any("metric" in c.conflict_type.lower() for c in conflicts)


class TestEndToEndHallucinationPrevention:
    """Integration tests for complete hallucination prevention."""

    def test_no_hallucinations_in_sample_output(self):
        """Verify a complete generated resume has no hallucinations."""
        # Simulate a generated resume
        generated_resume = """# M. Watson Mulkey
watsonmulkey@gmail.com | 434-808-2493 | linkedin.com/in/watsonmulkey | Denver, Colorado

## Professional Summary
Experienced Product Manager with 8 years in edtech and ecommerce.

## Experience
### Discovery Education (2021-2023)
**Product Manager - Teacher Tools**
- Drove 32% YoY user engagement increase
- Led cross-functional teams of 20+ people

## Skills
Product Management, Data Analysis, User Research"""

        job_info = {
            "company": "TestCompany",
            "description": "product manager role"
        }

        # Validate no hallucinations
        warnings = validate_generated_content(generated_resume, job_info)

        # Filter out non-critical warnings
        critical_warnings = [w for w in warnings if "HALLUCINATION" in w or "555-555" in w or "@email.com" in w]

        assert len(critical_warnings) == 0, f"Found hallucinations: {critical_warnings}"

        # Verify correct contact info present
        assert CONTACT_INFO['email'] in generated_resume
        assert CONTACT_INFO['phone'] in generated_resume
        assert CONTACT_INFO['linkedin'] in generated_resume


class TestMetricAccuracy:
    """Test that metrics match source data exactly."""

    KNOWN_METRICS = {
        "Discovery Education engagement": "32%",
        "Simplifya completion time reduction": "50%",
        "Simplifya usage increase": "40%",
        "Discovery Education delivery rate": "15%",
        "Discovery Education traffic recovery": "10%",
    }

    def test_metrics_match_source_data(self):
        """Verify metrics in CAREER_DATA match known correct values."""
        for achievement in CAREER_DATA["achievements"]:
            company = achievement.get("company", "")
            metrics_text = achievement.get("metrics", "")

            # Check known metrics
            for key, expected_pct in self.KNOWN_METRICS.items():
                if company in key and any(keyword in achievement.get("achievement", "").lower()
                                         for keyword in key.split()[-2:]):
                    assert expected_pct in metrics_text, \
                        f"Metric mismatch: expected {expected_pct} in {metrics_text}"


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
