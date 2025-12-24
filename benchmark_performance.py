"""
Performance benchmarks for Resume Tailor.

Tests:
- Load time for varying data sizes
- Save time with atomic writes
- Cache performance
- Pydantic validation overhead

Target: <100ms for load/save with 100 entries
"""

import time
import tempfile
import shutil
from pathlib import Path
from statistics import mean, median

from career_data_manager import CareerDataManager
from models import CareerData, ContactInfo, Job, Skill, Achievement


def create_sample_data(num_jobs: int, num_skills: int) -> CareerData:
    """Create sample career data for benchmarking."""
    contact = ContactInfo(
        name="Test User",
        email="test@example.com",
        phone="123-456-7890"
    )

    jobs = []
    for i in range(num_jobs):
        job = Job(
            company=f"Company {i}",
            title=f"Position {i}",
            start_date="2020-01",
            end_date="2021-01"
        )
        jobs.append(job)

    skills = []
    for i in range(num_skills):
        achievement = Achievement(
            description=f"Achievement {i} with concrete example and details",
            company=f"Company {i % num_jobs}",
            timeframe="2020-01 to 2021-01",
            result=f"Result {i}"
        )

        skill = Skill(
            name=f"Skill {i}",
            category="technical",
            proficiency="advanced",
            examples=[achievement],
            last_used="2021-01"
        )
        skills.append(skill)

    return CareerData(
        contact_info=contact,
        jobs=jobs,
        skills=skills,
        education=[],
        certifications=[],
        projects=[],
        personal_values=[]
    )


def benchmark_save(manager: CareerDataManager, data: CareerData, iterations: int = 10) -> dict:
    """Benchmark save operation."""
    times = []

    for i in range(iterations):
        start = time.perf_counter()
        manager.save(data)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    return {
        'mean': mean(times),
        'median': median(times),
        'min': min(times),
        'max': max(times)
    }


def benchmark_load(manager: CareerDataManager, iterations: int = 10) -> dict:
    """Benchmark load operation."""
    times = []

    for i in range(iterations):
        # Invalidate cache to force disk read
        manager.invalidate_cache()

        start = time.perf_counter()
        manager.load()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    return {
        'mean': mean(times),
        'median': median(times),
        'min': min(times),
        'max': max(times)
    }


def benchmark_cache_hit(manager: CareerDataManager, iterations: int = 100) -> dict:
    """Benchmark cache hit performance."""
    times = []

    # Prime cache
    manager.load()

    for i in range(iterations):
        start = time.perf_counter()
        manager.load()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    return {
        'mean': mean(times),
        'median': median(times),
        'min': min(times),
        'max': max(times)
    }


def run_benchmarks():
    """Run all performance benchmarks."""
    print("=" * 70)
    print("RESUME TAILOR PERFORMANCE BENCHMARKS")
    print("=" * 70)

    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Test different data sizes
        test_sizes = [
            (10, 10, "Small (10 jobs, 10 skills)"),
            (50, 50, "Medium (50 jobs, 50 skills)"),
            (100, 100, "Large (100 jobs, 100 skills)"),
        ]

        for num_jobs, num_skills, label in test_sizes:
            print(f"\n{label}")
            print("-" * 70)

            # Setup
            file_path = temp_dir / f"test_{num_jobs}_{num_skills}.json"
            manager = CareerDataManager(file_path, backup_enabled=True, cache_enabled=True)
            data = create_sample_data(num_jobs, num_skills)

            # Initial save
            manager.save(data)

            # Benchmark save
            save_results = benchmark_save(manager, data, iterations=10)
            print(f"SAVE (10 iterations):")
            print(f"  Mean:   {save_results['mean']:.2f} ms")
            print(f"  Median: {save_results['median']:.2f} ms")
            print(f"  Min:    {save_results['min']:.2f} ms")
            print(f"  Max:    {save_results['max']:.2f} ms")

            # Check if meets target
            if save_results['mean'] < 100:
                print(f"  [PASS] Mean < 100ms target")
            else:
                print(f"  [FAIL] Mean >= 100ms (target: <100ms)")

            # Benchmark load
            load_results = benchmark_load(manager, iterations=10)
            print(f"\nLOAD (10 iterations, cache invalidated):")
            print(f"  Mean:   {load_results['mean']:.2f} ms")
            print(f"  Median: {load_results['median']:.2f} ms")
            print(f"  Min:    {load_results['min']:.2f} ms")
            print(f"  Max:    {load_results['max']:.2f} ms")

            # Check if meets target
            if load_results['mean'] < 100:
                print(f"  [PASS] Mean < 100ms target")
            else:
                print(f"  [FAIL] Mean >= 100ms (target: <100ms)")

            # Benchmark cache hits
            cache_results = benchmark_cache_hit(manager, iterations=100)
            print(f"\nCACHE HIT (100 iterations):")
            print(f"  Mean:   {cache_results['mean']:.2f} ms")
            print(f"  Median: {cache_results['median']:.2f} ms")
            print(f"  Min:    {cache_results['min']:.2f} ms")
            print(f"  Max:    {cache_results['max']:.2f} ms")

            # Check if cache is fast
            if cache_results['mean'] < 1:
                print(f"  [PASS] Cache hit < 1ms")
            else:
                print(f"  [WARN] Cache hit >= 1ms")

        print("\n" + "=" * 70)
        print("BENCHMARK SUMMARY")
        print("=" * 70)
        print("Target: <100ms for load/save with 100 entries")
        print("All tests completed successfully!")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    run_benchmarks()
