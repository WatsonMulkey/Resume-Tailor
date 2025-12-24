"""
Career Data Manager - Local storage for Resume Tailor.

Handles all file I/O operations for career data with:
- Pydantic validation
- In-memory caching with timestamp invalidation
- Atomic writes (temp file + rename)
- Automatic backup before each write
- Rollback capability on failure

Replaces supermemory dependency with privacy-first local JSON storage.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import ValidationError

from models import CareerData, ContactInfo


class CareerDataError(Exception):
    """Base exception for career data operations."""
    def __init__(self, message: str, user_message: Optional[str] = None):
        super().__init__(message)
        self.user_message = user_message or message


class CareerDataValidationError(CareerDataError):
    """Raised when data fails Pydantic validation."""
    pass


class CareerDataFileError(CareerDataError):
    """Raised when file operations fail."""
    pass


class CareerDataManager:
    """Manages local career data with caching, validation, and backup."""

    def __init__(self, file_path: Path, backup_enabled: bool = True, cache_enabled: bool = True):
        """
        Initialize career data manager.

        Args:
            file_path: Path to career_data.json file
            backup_enabled: Whether to create .bak file before each write
            cache_enabled: Whether to use in-memory caching
        """
        self.file_path = Path(file_path)
        self.backup_enabled = backup_enabled
        self.cache_enabled = cache_enabled

        # Cache state
        self._cache: Optional[CareerData] = None
        self._cache_timestamp: Optional[float] = None

        # Ensure parent directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> CareerData:
        """
        Load career data with caching and timestamp validation.

        Returns:
            CareerData instance

        Raises:
            FileError: If file cannot be read
            ValidationError: If data doesn't match schema
        """
        # Check cache first
        if self.cache_enabled and self._cache and self._is_cache_valid():
            return self._cache

        # File doesn't exist - create empty structure
        if not self.file_path.exists():
            return self._create_empty_career_data()

        # Load from file
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate with Pydantic
            career_data = CareerData(**data)

            # Update cache
            if self.cache_enabled:
                self._update_cache(career_data)

            return career_data

        except json.JSONDecodeError as e:
            raise CareerDataFileError(
                f"Invalid JSON in {self.file_path}: {e}",
                user_message=f"Your career data file has invalid formatting.\n\n"
                            f"File: {self.file_path}\n\n"
                            f"You can:\n"
                            f"1. Restore from backup (career_data.json.bak)\n"
                            f"2. Fix the JSON manually\n"
                            f"3. Start fresh"
            )
        except ValidationError as e:
            raise CareerDataValidationError(
                f"Data validation failed: {e}",
                user_message=f"Your career data file has validation errors.\n\n"
                            f"The data doesn't match the expected format.\n\n"
                            f"You can restore from backup:\n"
                            f"{self.get_backup_path()}"
            )
        except Exception as e:
            raise CareerDataFileError(
                f"Failed to load career data: {e}",
                user_message=f"Could not load career data.\n\n"
                            f"Error: {str(e)}\n\n"
                            f"Check that the file exists and is readable."
            )

    def save(self, data: CareerData) -> bool:
        """
        Save career data with atomic write and backup.

        Process:
        1. Validate data with Pydantic
        2. Create backup (career_data.json.bak)
        3. Write to temp file (career_data.json.tmp)
        4. Validate temp file can be read
        5. Atomic rename (replaces original)
        6. Update cache timestamp

        Args:
            data: CareerData instance to save

        Returns:
            True if successful

        Raises:
            ValidationError: If data fails validation
            FileError: If write fails
        """
        try:
            # 1. Validate data (Pydantic will raise if invalid)
            data.last_updated = datetime.now()

            # Convert to JSON-serializable dict
            data_dict = json.loads(data.model_dump_json())

            # 2. Create backup if file exists
            if self.backup_enabled and self.file_path.exists():
                self._create_backup()

            # 3. Write to temp file
            temp_path = self.file_path.with_suffix('.tmp')
            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data_dict, f, indent=2, ensure_ascii=False)

                # 4. Validate temp file can be read
                with open(temp_path, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                    # Quick validation
                    CareerData(**test_data)

                # 5. Atomic rename
                shutil.move(str(temp_path), str(self.file_path))

                # 6. Update cache
                if self.cache_enabled:
                    self._update_cache(data)

                return True

            except Exception as e:
                # Clean up temp file if it exists
                if temp_path.exists():
                    temp_path.unlink()
                raise e

        except ValidationError as e:
            # Validation failed - restore from backup if available
            if self.backup_enabled:
                restored = self._restore_from_backup()
                restore_msg = "Original data restored from backup." if restored else "No backup available to restore."
            else:
                restore_msg = "Backup disabled."

            raise CareerDataValidationError(
                f"Save failed - data validation error: {e}",
                user_message=f"Failed to save career data - validation error.\n\n"
                            f"{restore_msg}\n\n"
                            f"The data you tried to save doesn't match the expected format."
            )

        except Exception as e:
            # Write failed - restore from backup if available
            if self.backup_enabled:
                restored = self._restore_from_backup()
                restore_msg = "Original data restored from backup." if restored else "No backup available to restore."
            else:
                restore_msg = "Backup disabled."

            raise CareerDataFileError(
                f"Save failed: {e}",
                user_message=f"Failed to save career data.\n\n"
                            f"Error: {str(e)}\n\n"
                            f"{restore_msg}"
            )

    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid (file hasn't changed)."""
        if not self._cache or not self._cache_timestamp:
            return False

        if not self.file_path.exists():
            return False

        # Check if file was modified since cache
        file_mtime = self.file_path.stat().st_mtime
        return file_mtime <= self._cache_timestamp

    def _update_cache(self, data: CareerData):
        """Update cache with new data and timestamp."""
        self._cache = data
        if self.file_path.exists():
            self._cache_timestamp = self.file_path.stat().st_mtime
        else:
            self._cache_timestamp = datetime.now().timestamp()

    def invalidate_cache(self):
        """Manually invalidate cache (useful for testing)."""
        self._cache = None
        self._cache_timestamp = None

    def _create_backup(self):
        """Create backup file (.bak)."""
        if not self.file_path.exists():
            return

        backup_path = self.file_path.with_suffix('.json.bak')
        shutil.copy2(self.file_path, backup_path)

    def _restore_from_backup(self) -> bool:
        """
        Restore from backup file.

        Returns:
            True if restored successfully, False if no backup available
        """
        backup_path = self.file_path.with_suffix('.json.bak')

        if not backup_path.exists():
            return False

        try:
            shutil.copy2(backup_path, self.file_path)
            # Invalidate cache since we restored old data
            self.invalidate_cache()
            return True
        except Exception:
            return False

    def _create_empty_career_data(self) -> CareerData:
        """
        Create empty career data structure and save it.

        Uses default contact info from config.py if available.
        """
        try:
            from config import get_contact_info
            contact = get_contact_info()
        except ImportError:
            # Fallback contact info
            contact = {
                "name": "Your Name",
                "email": "your.email@example.com",
                "phone": "000-000-0000",
                "linkedin": "linkedin.com/in/yourprofile",
                "location": "Your Location"
            }

        career_data = CareerData(
            version="1.0",
            contact_info=ContactInfo(**contact),
            jobs=[],
            skills=[],
            education=[],
            certifications=[],
            projects=[],
            personal_values=[]
        )

        # Save the empty structure to disk
        self.save(career_data)

        return career_data

    def get_backup_path(self) -> Path:
        """Get backup file path."""
        return self.file_path.with_suffix('.json.bak')

    def has_backup(self) -> bool:
        """Check if backup file exists."""
        return self.get_backup_path().exists()


# Singleton instance (initialized lazily)
_manager: Optional[CareerDataManager] = None


def get_manager() -> CareerDataManager:
    """
    Get singleton CareerDataManager instance.

    Uses configuration from config.py for file location and settings.
    """
    global _manager

    if _manager is None:
        try:
            from config import CAREER_DATA_FILE, BACKUP_ENABLED, CACHE_ENABLED
        except ImportError:
            # Fallback defaults
            CAREER_DATA_FILE = Path.home() / ".resume_tailor" / "career_data.json"
            BACKUP_ENABLED = True
            CACHE_ENABLED = True

        _manager = CareerDataManager(
            file_path=Path(CAREER_DATA_FILE),
            backup_enabled=BACKUP_ENABLED,
            cache_enabled=CACHE_ENABLED
        )

    return _manager


def load_career_data() -> CareerData:
    """
    Load career data (convenience function).

    Returns:
        CareerData instance
    """
    return get_manager().load()


def save_career_data(data: CareerData) -> bool:
    """
    Save career data (convenience function).

    Args:
        data: CareerData instance to save

    Returns:
        True if successful
    """
    return get_manager().save(data)


def invalidate_cache():
    """Invalidate cache (convenience function)."""
    return get_manager().invalidate_cache()


# Example usage and testing
if __name__ == '__main__':
    # Test basic functionality
    manager = get_manager()

    print(f"Career data file: {manager.file_path}")
    print(f"Backup enabled: {manager.backup_enabled}")
    print(f"Cache enabled: {manager.cache_enabled}")

    try:
        # Try to load
        data = manager.load()
        print(f"\n[OK] Loaded career data successfully")
        print(f"  Contact: {data.contact_info.name}")
        print(f"  Jobs: {len(data.jobs)}")
        print(f"  Skills: {len(data.skills)}")
        print(f"  Last updated: {data.last_updated}")

    except Exception as e:
        print(f"\n[ERROR] Failed to load: {e}")
