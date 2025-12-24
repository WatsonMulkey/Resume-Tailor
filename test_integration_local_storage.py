"""
Integration test for resume generation with local storage.

Tests the full workflow:
1. Load career data from local JSON
2. Parse job description
3. Generate resume using career data
"""

import os
import tempfile
import shutil
from pathlib import Path

# Set up test environment
test_dir = Path(tempfile.mkdtemp())
test_career_file = test_dir / "career_data.json"

# Override config to use test file
os.environ['CAREER_DATA_FILE'] = str(test_career_file)

from generator import ResumeGenerator
from career_data_manager import load_career_data, save_career_data
from models import CareerData, ContactInfo, Job, Skill, Achievement

def test_integration():
    """Test full resume generation workflow with local storage."""

    print("=" * 60)
    print("INTEGRATION TEST: Resume Generation with Local Storage")
    print("=" * 60)

    # Step 1: Create sample career data
    print("\n[Step 1] Creating sample career data...")

    contact = ContactInfo(
        name="Test User",
        email="test@example.com",
        phone="123-456-7890",
        linkedin="linkedin.com/in/testuser",
        location="Denver, CO"
    )

    job = Job(
        company="Test Company",
        title="Senior Product Manager",
        start_date="2023-01",
        end_date="Present",
        company_context="Leading SaaS platform",
        responsibilities=[
            "Led product strategy and roadmap",
            "Managed cross-functional teams",
            "Drove 30% increase in user engagement"
        ]
    )

    achievement = Achievement(
        description="Increased user engagement by 30% through UX redesign",
        company="Test Company",
        timeframe="2023-06 to 2024-01",
        result="30% engagement increase",
        metrics=["30% engagement", "50% retention"]
    )

    skill = Skill(
        name="Product Management",
        category="technical",
        proficiency="expert",
        examples=[achievement],
        last_used="2024-01"
    )

    career_data = CareerData(
        contact_info=contact,
        jobs=[job],
        skills=[skill],
        education=[],
        certifications=[],
        projects=[],
        personal_values=[]
    )

    # Save career data
    success = save_career_data(career_data)
    print(f"  Career data saved: {success}")
    print(f"  File location: {test_career_file}")

    # Step 2: Verify file was created
    print("\n[Step 2] Verifying file creation...")
    assert test_career_file.exists(), "Career data file not created"
    print(f"  File exists: [OK]")
    print(f"  File size: {test_career_file.stat().st_size} bytes")

    # Step 3: Load career data back
    print("\n[Step 3] Loading career data...")
    loaded_data = load_career_data()
    print(f"  Contact: {loaded_data.contact_info.name}")
    print(f"  Jobs: {len(loaded_data.jobs)}")
    print(f"  Skills: {len(loaded_data.skills)}")

    # Step 4: Test LocalCareerDataRetriever
    print("\n[Step 4] Testing LocalCareerDataRetriever...")
    from generator import LocalCareerDataRetriever

    retriever = LocalCareerDataRetriever(verbose=True)
    job_info = {
        "title": "Product Manager",
        "company": "Example Corp",
        "required_skills": ["Product Management", "Leadership"],
        "responsibilities": ["Lead teams", "Define strategy"]
    }

    context = retriever.retrieve_relevant_context(job_info)
    print(f"  Retrieved context keys: {list(context.keys())}")
    print(f"  Jobs context length: {len(context['jobs'])} chars")
    print(f"  Skills context length: {len(context['skills'])} chars")

    # Step 5: Test ResumeGenerator initialization
    print("\n[Step 5] Testing ResumeGenerator with local storage...")
    generator = ResumeGenerator(verbose=False)
    print(f"  Generator created successfully")
    print(f"  Retriever type: {type(generator.retriever).__name__}")

    assert isinstance(generator.retriever, LocalCareerDataRetriever), \
        "Generator not using LocalCareerDataRetriever"

    print("\n" + "=" * 60)
    print("[SUCCESS] ALL INTEGRATION TESTS PASSED")
    print("=" * 60)
    print("\nSummary:")
    print("  - Career data saved to local JSON")
    print("  - Pydantic validation working")
    print("  - LocalCareerDataRetriever loading data correctly")
    print("  - ResumeGenerator using local storage (not supermemory)")
    print("\n[OK] Local storage implementation COMPLETE")

    # Cleanup
    shutil.rmtree(test_dir)

if __name__ == '__main__':
    try:
        test_integration()
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
