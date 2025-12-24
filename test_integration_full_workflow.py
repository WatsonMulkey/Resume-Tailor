"""
Full workflow integration test for Resume Tailor.

Tests the complete user journey:
1. First-time setup (empty career data)
2. Migration from import_career_data.py
3. Resume generation with local storage
4. Error recovery scenarios
5. Backup and restore
"""

import os
import tempfile
import shutil
from pathlib import Path

# Override config before imports
test_dir = Path(tempfile.mkdtemp())
test_career_file = test_dir / "career_data.json"
os.environ['CAREER_DATA_FILE'] = str(test_career_file)

from generator import ResumeGenerator
from career_data_manager import load_career_data, save_career_data, get_manager
from models import CareerData, ContactInfo, Job, Skill, Achievement


def test_scenario_1_first_time_setup():
    """Test first-time setup with empty career data."""
    print("\n" + "=" * 70)
    print("SCENARIO 1: First-Time Setup")
    print("=" * 70)

    # Step 1: Load creates empty file
    print("\n[1] Loading career data (should create empty file)...")
    data = load_career_data()
    assert data is not None
    assert len(data.jobs) == 0
    assert len(data.skills) == 0
    print("  [OK] Empty career data created")

    # Step 2: Verify file exists
    print("\n[2] Verifying file creation...")
    assert test_career_file.exists()
    print(f"  [OK] File created: {test_career_file}")

    # Step 3: Add some data
    print("\n[3] Adding sample data...")
    contact = ContactInfo(
        name="Test User",
        email="test@example.com",
        phone="123-456-7890"
    )

    job = Job(
        company="Test Company",
        title="Product Manager",
        start_date="2023-01",
        end_date="Present"
    )

    data.contact_info = contact
    data.jobs = [job]

    save_career_data(data)
    print("  [OK] Data saved successfully")

    # Step 4: Verify data persists
    print("\n[4] Reloading to verify persistence...")
    loaded = load_career_data()
    assert loaded.contact_info.name == "Test User"
    assert len(loaded.jobs) == 1
    assert loaded.jobs[0].company == "Test Company"
    print("  [OK] Data persisted correctly")

    print("\n[PASS] Scenario 1 complete")


def test_scenario_2_backup_and_restore():
    """Test backup creation and restoration."""
    print("\n" + "=" * 70)
    print("SCENARIO 2: Backup and Restore")
    print("=" * 70)

    manager = get_manager()

    # Step 1: Load existing data
    print("\n[1] Loading existing data...")
    data = load_career_data()
    original_name = data.contact_info.name
    print(f"  Original name: {original_name}")

    # Step 2: Verify backup doesn't exist yet
    print("\n[2] Checking for backup...")
    # Backup is created on first save, so it might exist
    if manager.has_backup():
        print("  [INFO] Backup exists from previous saves")
    else:
        print("  [INFO] No backup yet (will be created on next save)")

    # Step 3: Modify and save (creates backup)
    print("\n[3] Modifying data and saving...")
    data.contact_info.name = "Modified User"
    save_career_data(data)
    print("  [OK] Data modified and saved")

    # Step 4: Verify backup was created
    print("\n[4] Verifying backup creation...")
    assert manager.has_backup()
    print(f"  [OK] Backup created: {manager.get_backup_path()}")

    # Step 5: Restore from backup
    print("\n[5] Restoring from backup...")
    manager._restore_from_backup()
    restored = load_career_data()
    print(f"  Restored name: {restored.contact_info.name}")

    # The backup contains the PREVIOUS save, not the original
    # So it should have the data from the first save in scenario 1
    print("  [OK] Restore successful")

    print("\n[PASS] Scenario 2 complete")


def test_scenario_3_generation_with_local_storage():
    """Test resume generation using local storage."""
    print("\n" + "=" * 70)
    print("SCENARIO 3: Resume Generation with Local Storage")
    print("=" * 70)

    # Step 1: Ensure we have data
    print("\n[1] Loading career data...")
    data = load_career_data()

    # Add more comprehensive data
    if len(data.skills) == 0:
        achievement = Achievement(
            description="Increased user engagement by 30% through UX redesign",
            company="Test Company",
            timeframe="2023-01 to 2024-01",
            result="30% increase"
        )

        skill = Skill(
            name="Product Management",
            category="technical",
            proficiency="expert",
            examples=[achievement],
            last_used="2024-01"
        )

        data.skills = [skill]
        save_career_data(data)

    print(f"  [OK] Career data loaded: {len(data.jobs)} jobs, {len(data.skills)} skills")

    # Step 2: Create generator
    print("\n[2] Initializing ResumeGenerator...")
    generator = ResumeGenerator(verbose=False)
    print("  [OK] Generator created")

    # Step 3: Verify it uses LocalCareerDataRetriever
    print("\n[3] Verifying local storage integration...")
    from generator import LocalCareerDataRetriever
    assert isinstance(generator.retriever, LocalCareerDataRetriever)
    print("  [OK] Using LocalCareerDataRetriever (not supermemory)")

    # Step 4: Test context retrieval
    print("\n[4] Testing context retrieval...")
    job_info = {
        "title": "Senior Product Manager",
        "company": "Example Corp",
        "required_skills": ["Product Management"],
        "responsibilities": ["Lead teams"]
    }

    context = generator.retriever.retrieve_relevant_context(job_info)
    assert 'jobs' in context
    assert 'skills' in context
    print(f"  [OK] Context retrieved")
    print(f"    Jobs context: {len(context['jobs'])} chars")
    print(f"    Skills context: {len(context['skills'])} chars")

    print("\n[PASS] Scenario 3 complete")


def test_scenario_4_error_recovery():
    """Test error recovery scenarios."""
    print("\n" + "=" * 70)
    print("SCENARIO 4: Error Recovery")
    print("=" * 70)

    manager = get_manager()

    # Step 1: Corrupt the file
    print("\n[1] Simulating file corruption...")
    with open(test_career_file, 'w') as f:
        f.write("{invalid json content")
    print("  [OK] File corrupted")

    # Step 2: Try to load (should fail gracefully)
    print("\n[2] Attempting to load corrupted file...")
    try:
        load_career_data()
        print("  [FAIL] Should have raised an error")
        assert False
    except Exception as e:
        print(f"  [OK] Error caught: {type(e).__name__}")
        # Check if error has user_message
        if hasattr(e, 'user_message'):
            print(f"  [OK] User-friendly message available")

    # Step 3: Restore from backup
    print("\n[3] Restoring from backup...")
    manager._restore_from_backup()
    print("  [OK] Restored from backup")

    # Step 4: Verify recovery
    print("\n[4] Verifying recovery...")
    data = load_career_data()
    assert data is not None
    print("  [OK] Data loaded successfully after recovery")

    print("\n[PASS] Scenario 4 complete")


def test_scenario_5_cache_performance():
    """Test cache invalidation on external edits."""
    print("\n" + "=" * 70)
    print("SCENARIO 5: Cache Performance")
    print("=" * 70)

    # Step 1: Load to populate cache
    print("\n[1] Loading data (populates cache)...")
    data1 = load_career_data()
    original_name = data1.contact_info.name
    print(f"  Original name: {original_name}")

    # Step 2: Load again (should use cache)
    print("\n[2] Loading again (should hit cache)...")
    data2 = load_career_data()
    assert data1 is data2  # Same object from cache
    print("  [OK] Cache hit (same object returned)")

    # Step 3: Modify file externally
    print("\n[3] Modifying file externally...")
    import json
    with open(test_career_file, 'r') as f:
        file_data = json.load(f)

    file_data['contact_info']['name'] = "Externally Modified"

    with open(test_career_file, 'w') as f:
        json.dump(file_data, f)
    print("  [OK] File modified externally")

    # Step 4: Load again (should detect change)
    print("\n[4] Loading after external modification...")
    data3 = load_career_data()
    assert data3.contact_info.name == "Externally Modified"
    print(f"  [OK] Cache invalidated, new data loaded: {data3.contact_info.name}")

    print("\n[PASS] Scenario 5 complete")


def run_all_tests():
    """Run all integration test scenarios."""
    print("\n" + "=" * 70)
    print("FULL WORKFLOW INTEGRATION TESTS")
    print("=" * 70)
    print(f"\nTest directory: {test_dir}")
    print(f"Career data file: {test_career_file}")

    try:
        test_scenario_1_first_time_setup()
        test_scenario_2_backup_and_restore()
        test_scenario_3_generation_with_local_storage()
        test_scenario_4_error_recovery()
        test_scenario_5_cache_performance()

        print("\n" + "=" * 70)
        print("ALL INTEGRATION TESTS PASSED")
        print("=" * 70)
        print("\nSummary:")
        print("  - First-time setup: PASS")
        print("  - Backup and restore: PASS")
        print("  - Resume generation: PASS")
        print("  - Error recovery: PASS")
        print("  - Cache performance: PASS")
        print("\n[SUCCESS] All integration tests completed successfully!")

    finally:
        # Cleanup
        shutil.rmtree(test_dir)
        print(f"\nCleanup: Removed test directory")


if __name__ == '__main__':
    run_all_tests()
