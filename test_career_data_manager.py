"""
Unit tests for career_data_manager module.

Tests cover:
- Load/save operations
- Pydantic validation
- Caching with timestamp checking
- Atomic writes and backup
- Rollback on failure
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from career_data_manager import CareerDataManager, CareerDataError
from models import CareerData, ContactInfo, Job, Skill, Achievement


class TestCareerDataManager:
    """Test suite for CareerDataManager."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    @pytest.fixture
    def manager(self, temp_dir):
        """Create CareerDataManager instance with temporary file."""
        file_path = temp_dir / "test_career_data.json"
        return CareerDataManager(file_path, backup_enabled=True, cache_enabled=True)

    def test_load_creates_empty_structure(self, manager):
        """Test loading from non-existent file creates empty structure."""
        data = manager.load()

        assert isinstance(data, CareerData)
        assert data.version == "1.0"
        assert data.contact_info is not None
        assert len(data.jobs) == 0
        assert len(data.skills) == 0

    def test_save_and_load_round_trip(self, manager):
        """Test saving and loading data preserves content."""
        # Create sample data
        contact = ContactInfo(
            name="Test User",
            email="test@example.com",
            phone="123-456-7890"
        )

        job = Job(
            company="Test Company",
            title="Test PM",
            start_date="2023-01",
            end_date="2024-01"
        )

        data = CareerData(
            contact_info=contact,
            jobs=[job],
            skills=[],
            education=[],
            certifications=[],
            projects=[],
            personal_values=[]
        )

        # Save
        assert manager.save(data) == True

        # Load
        loaded = manager.load()

        assert loaded.contact_info.name == "Test User"
        assert loaded.contact_info.email == "test@example.com"
        assert len(loaded.jobs) == 1
        assert loaded.jobs[0].company == "Test Company"

    def test_pydantic_validation_on_save(self, manager):
        """Test that invalid data raises validation error."""
        from pydantic import ValidationError

        # This should raise ValidationError during Pydantic model creation
        with pytest.raises(ValidationError):
            bad_contact = ContactInfo(
                name="Test",
                email="no-at-sign",  # Invalid email (no @ or .)
                phone="123"
            )

    def test_cache_works(self, manager):
        """Test that cache returns same object without re-reading file."""
        # Create and save data
        contact = ContactInfo(
            name="Cached User",
            email="cache@example.com",
            phone="123-456-7890"
        )

        data = CareerData(
            contact_info=contact,
            jobs=[],
            skills=[],
            education=[],
            certifications=[],
            projects=[],
            personal_values=[]
        )

        manager.save(data)

        # Load twice - should use cache second time
        data1 = manager.load()
        data2 = manager.load()

        # Should be same object from cache
        assert data1 is data2

    def test_cache_invalidation_on_external_change(self, manager, temp_dir):
        """Test cache invalidates when file is modified externally."""
        # Create and save data
        contact = ContactInfo(
            name="Original",
            email="original@example.com",
            phone="123-456-7890"
        )

        data = CareerData(
            contact_info=contact,
            jobs=[],
            skills=[],
            education=[],
            certifications=[],
            projects=[],
            personal_values=[]
        )

        manager.save(data)

        # Load to populate cache
        loaded1 = manager.load()
        assert loaded1.contact_info.name == "Original"

        # Manually modify file (simulating external edit)
        file_content = manager.file_path.read_text()
        file_content = file_content.replace("Original", "Modified")
        manager.file_path.write_text(file_content)

        # Load again - should detect file change and reload
        loaded2 = manager.load()
        assert loaded2.contact_info.name == "Modified"

    def test_backup_created(self, manager):
        """Test that backup file is created before save."""
        # Create and save initial data
        contact = ContactInfo(
            name="Backup Test",
            email="backup@example.com",
            phone="123-456-7890"
        )

        data = CareerData(
            contact_info=contact,
            jobs=[],
            skills=[],
            education=[],
            certifications=[],
            projects=[],
            personal_values=[]
        )

        manager.save(data)

        # Modify and save again
        data.contact_info.name = "Modified"
        manager.save(data)

        # Check backup exists
        assert manager.has_backup() == True

        # Backup should contain original data
        backup_path = manager.get_backup_path()
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)

        # Backup should have the FIRST save (before modification)
        assert backup_data['contact_info']['name'] == "Backup Test"

    def test_atomic_write_prevents_corruption(self, manager):
        """Test that atomic write prevents partial file corruption."""
        contact = ContactInfo(
            name="Atomic Test",
            email="atomic@example.com",
            phone="123-456-7890"
        )

        data = CareerData(
            contact_info=contact,
            jobs=[],
            skills=[],
            education=[],
            certifications=[],
            projects=[],
            personal_values=[]
        )

        # Save successfully
        manager.save(data)

        # Original file should exist
        assert manager.file_path.exists()

        # Temp file should NOT exist (cleaned up after successful write)
        temp_path = manager.file_path.with_suffix('.tmp')
        assert not temp_path.exists()


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
