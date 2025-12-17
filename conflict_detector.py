"""
Conflict Detection System for Career Data

Detects when new career information contradicts existing data in supermemory.
Prompts user to resolve conflicts before allowing updates.
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime
import re


class DataConflict:
    """Represents a detected conflict between new and existing data."""

    def __init__(
        self,
        conflict_type: str,
        field: str,
        existing_value: str,
        new_value: str,
        severity: str = "medium",
        context: str = ""
    ):
        self.conflict_type = conflict_type
        self.field = field
        self.existing_value = existing_value
        self.new_value = new_value
        self.severity = severity  # "low", "medium", "high"
        self.context = context

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.conflict_type} in {self.field}:\n  Existing: {self.existing_value}\n  New: {self.new_value}\n  Context: {self.context}"


class ConflictDetector:
    """Detects conflicts in career data updates."""

    def __init__(self, existing_data: Dict[str, Any]):
        """
        Initialize with existing career data.

        Args:
            existing_data: Dictionary from import_career_data.CAREER_DATA
        """
        self.existing_data = existing_data
        self.conflicts: List[DataConflict] = []

    def check_contact_info(self, new_contact: Dict[str, str]) -> List[DataConflict]:
        """Check for conflicts in contact information."""
        conflicts = []
        existing_contact = self.existing_data.get("contact_info", {})

        for field in ["email", "phone", "linkedin", "name"]:
            if field in new_contact:
                new_val = new_contact[field].strip()
                existing_val = existing_contact.get(field, "").strip()

                if existing_val and new_val and new_val != existing_val:
                    conflicts.append(DataConflict(
                        conflict_type="Contact Info Changed",
                        field=field,
                        existing_value=existing_val,
                        new_value=new_val,
                        severity="high",  # Contact info changes are critical
                        context="Contact information should rarely change"
                    ))

        return conflicts

    def check_job_dates(self, new_job: Dict[str, Any]) -> List[DataConflict]:
        """Check for date conflicts in job history."""
        conflicts = []
        company = new_job.get("company", "")
        new_dates = new_job.get("dates", "")

        # Find existing job at same company
        for existing_job in self.existing_data.get("job_history", []):
            if existing_job.get("company") == company:
                existing_dates = existing_job.get("dates", "")

                if existing_dates and new_dates and existing_dates != new_dates:
                    conflicts.append(DataConflict(
                        conflict_type="Job Dates Changed",
                        field=f"{company} employment dates",
                        existing_value=existing_dates,
                        new_value=new_dates,
                        severity="high",
                        context=f"Dates for {company} don't match"
                    ))

                # Check for date overlaps with other jobs
                date_conflict = self._check_date_overlap(new_job, self.existing_data.get("job_history", []))
                if date_conflict:
                    conflicts.append(date_conflict)

        return conflicts

    def _check_date_overlap(self, new_job: Dict[str, Any], existing_jobs: List[Dict]) -> DataConflict | None:
        """Check if new job dates overlap with existing jobs (indicating impossible timeline)."""
        new_dates = new_job.get("dates", "")
        new_company = new_job.get("company", "")

        # Parse date range (simple parser for common formats like "01/2024 - 03/2025")
        new_start, new_end = self._parse_date_range(new_dates)
        if not new_start:
            return None

        for job in existing_jobs:
            if job.get("company") == new_company:
                continue  # Skip same company

            existing_dates = job.get("dates", "")
            existing_start, existing_end = self._parse_date_range(existing_dates)

            if existing_start and self._dates_overlap(new_start, new_end, existing_start, existing_end):
                return DataConflict(
                    conflict_type="Date Overlap",
                    field="employment timeline",
                    existing_value=f"{job.get('company')}: {existing_dates}",
                    new_value=f"{new_company}: {new_dates}",
                    severity="high",
                    context="Cannot work at two places simultaneously"
                )

        return None

    def _parse_date_range(self, date_str: str) -> Tuple[str | None, str | None]:
        """Parse date range string into (start, end) tuple."""
        if not date_str:
            return None, None

        # Handle formats like "01/2024 - 03/2025" or "2024-2025"
        parts = re.split(r'[-–—]', date_str)
        if len(parts) == 2:
            start = parts[0].strip()
            end = parts[1].strip() if parts[1].strip().lower() not in ["present", "current"] else "present"
            return start, end

        return None, None

    def _dates_overlap(self, start1: str, end1: str, start2: str, end2: str) -> bool:
        """Check if two date ranges overlap."""
        # Simplified overlap detection - could be enhanced with actual date parsing
        # For now, just check for obvious overlaps
        if end1 == "present" or end2 == "present":
            return True  # Current jobs might overlap with contract/consulting work

        return False  # More sophisticated logic would go here

    def check_achievement_metrics(self, new_achievement: Dict[str, Any]) -> List[DataConflict]:
        """Check for conflicts in achievement metrics."""
        conflicts = []
        company = new_achievement.get("company", "")
        new_metric = new_achievement.get("metrics", "")

        # Find similar achievements at same company
        for existing_achievement in self.existing_data.get("achievements", []):
            if existing_achievement.get("company") == company:
                existing_metric = existing_achievement.get("metrics", "")

                # Check if both mention the same type of metric (e.g., both mention "engagement")
                if self._similar_metrics(new_metric, existing_metric):
                    # Extract percentages
                    new_pct = self._extract_percentage(new_metric)
                    existing_pct = self._extract_percentage(existing_metric)

                    if new_pct and existing_pct and new_pct != existing_pct:
                        conflicts.append(DataConflict(
                            conflict_type="Metric Mismatch",
                            field=f"{company} achievement metric",
                            existing_value=existing_metric,
                            new_value=new_metric,
                            severity="high",
                            context="Same achievement reported with different numbers"
                        ))

        return conflicts

    def _similar_metrics(self, metric1: str, metric2: str) -> bool:
        """Check if two metrics are talking about the same thing."""
        keywords = ["engagement", "completion", "usage", "revenue", "reduction", "increase"]
        metric1_lower = metric1.lower()
        metric2_lower = metric2.lower()

        for keyword in keywords:
            if keyword in metric1_lower and keyword in metric2_lower:
                return True

        return False

    def _extract_percentage(self, text: str) -> str | None:
        """Extract percentage from text (e.g., "32%" from "32% increase")."""
        match = re.search(r'(\d+)%', text)
        return match.group(1) if match else None

    def check_all(self, new_data: Dict[str, Any]) -> List[DataConflict]:
        """
        Check all types of conflicts in new data.

        Args:
            new_data: Dictionary with new career data to check

        Returns:
            List of detected conflicts
        """
        all_conflicts = []

        # Check contact info
        if "contact_info" in new_data:
            all_conflicts.extend(self.check_contact_info(new_data["contact_info"]))

        # Check job history
        if "job_history" in new_data:
            for job in new_data["job_history"]:
                all_conflicts.extend(self.check_job_dates(job))

        # Check achievements
        if "achievements" in new_data:
            for achievement in new_data["achievements"]:
                all_conflicts.extend(self.check_achievement_metrics(achievement))

        return all_conflicts

    def generate_conflict_report(self, conflicts: List[DataConflict]) -> str:
        """Generate a human-readable conflict report."""
        if not conflicts:
            return "✅ No conflicts detected - data is consistent."

        report = f"⚠️  DETECTED {len(conflicts)} CONFLICT(S):\n\n"

        # Group by severity
        high = [c for c in conflicts if c.severity == "high"]
        medium = [c for c in conflicts if c.severity == "medium"]
        low = [c for c in conflicts if c.severity == "low"]

        for severity, conflict_list in [("HIGH", high), ("MEDIUM", medium), ("LOW", low)]:
            if conflict_list:
                report += f"=== {severity} PRIORITY ===\n\n"
                for i, conflict in enumerate(conflict_list, 1):
                    report += f"{i}. {conflict}\n\n"

        report += "\n📋 ACTION REQUIRED:\n"
        report += "Please review these conflicts and confirm which values are correct.\n"
        report += "Update import_career_data.py with the correct information before proceeding.\n"

        return report


def detect_conflicts_in_new_data(new_data: Dict[str, Any]) -> List[DataConflict]:
    """
    Convenience function to detect conflicts in new data.

    Args:
        new_data: New career data to check against existing data

    Returns:
        List of detected conflicts
    """
    try:
        from import_career_data import CAREER_DATA
        detector = ConflictDetector(CAREER_DATA)
        return detector.check_all(new_data)
    except ImportError:
        print("Warning: Could not import CAREER_DATA for conflict detection")
        return []
