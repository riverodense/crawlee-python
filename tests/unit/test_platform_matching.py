"""Unit tests for the platform matching module."""

from __future__ import annotations

import pytest

from crawlee import Match, PlatformMatcher, Task, Worker


class TestTask:
    """Test the Task dataclass."""

    def test_task_creation(self) -> None:
        """Test creating a basic task."""
        task = Task(id='test1', url='https://example.com')
        assert task.id == 'test1'
        assert task.url == 'https://example.com'
        assert task.priority == 1.0  # default
        assert task.estimated_complexity == 1.0  # default
        assert task.metadata is None  # default

    def test_task_with_metadata(self) -> None:
        """Test creating a task with metadata."""
        task = Task(
            id='test1',
            url='https://example.com',
            priority=5.0,
            estimated_complexity=0.7,
            metadata={'type': 'api', 'retry_count': 0},
        )
        assert task.priority == 5.0
        assert task.estimated_complexity == 0.7
        assert task.metadata == {'type': 'api', 'retry_count': 0}


class TestWorker:
    """Test the Worker dataclass."""

    def test_worker_creation(self) -> None:
        """Test creating a basic worker."""
        worker = Worker(id='worker1')
        assert worker.id == 'worker1'
        assert worker.capacity == 1.0  # default
        assert worker.specialization is None  # default
        assert worker.performance_score == 1.0  # default
        assert worker.metadata is None  # default

    def test_worker_with_specialization(self) -> None:
        """Test creating a worker with specialization."""
        worker = Worker(
            id='worker1',
            capacity=0.8,
            specialization='javascript',
            performance_score=0.9,
            metadata={'region': 'us-east-1'},
        )
        assert worker.capacity == 0.8
        assert worker.specialization == 'javascript'
        assert worker.performance_score == 0.9
        assert worker.metadata == {'region': 'us-east-1'}


class TestPlatformMatcher:
    """Test the PlatformMatcher class."""

    def test_matcher_initialization_default(self) -> None:
        """Test matcher initialization with default weights."""
        matcher = PlatformMatcher()
        # Default weights should sum to 1.0
        assert matcher._capacity_weight == 0.3
        assert matcher._performance_weight == 0.3
        assert matcher._priority_weight == 0.4

    def test_matcher_initialization_custom(self) -> None:
        """Test matcher initialization with custom weights."""
        matcher = PlatformMatcher(
            capacity_weight=0.4,
            performance_weight=0.4,
            priority_weight=0.2,
        )
        assert matcher._capacity_weight == 0.4
        assert matcher._performance_weight == 0.4
        assert matcher._priority_weight == 0.2

    def test_matcher_invalid_weights_range(self) -> None:
        """Test that invalid weight ranges raise errors."""
        with pytest.raises(ValueError, match='capacity_weight must be between 0 and 1'):
            PlatformMatcher(capacity_weight=-0.1)

        with pytest.raises(ValueError, match='capacity_weight must be between 0 and 1'):
            PlatformMatcher(capacity_weight=1.5)

    def test_matcher_invalid_weights_sum(self) -> None:
        """Test that weights not summing to 1.0 raise errors."""
        with pytest.raises(ValueError, match=r'Weights must sum to 1\.0'):
            PlatformMatcher(
                capacity_weight=0.5,
                performance_weight=0.5,
                priority_weight=0.5,
            )

    def test_calculate_match_quality_basic(self) -> None:
        """Test basic match quality calculation."""
        matcher = PlatformMatcher()
        task = Task(id='task1', url='https://example.com', priority=5.0, estimated_complexity=0.5)
        worker = Worker(id='worker1', capacity=0.5, performance_score=0.8)

        quality = matcher.calculate_match_quality(task, worker)
        assert 0.0 <= quality <= 1.0
        # With perfect complexity match, quality should be reasonably high
        assert quality > 0.4

    def test_calculate_match_quality_with_specialization(self) -> None:
        """Test match quality with specialization bonus."""
        matcher = PlatformMatcher()
        task = Task(
            id='task1',
            url='https://example.com',
            priority=5.0,
            estimated_complexity=0.5,
            metadata={'type': 'api'},
        )
        worker_specialized = Worker(
            id='worker1',
            capacity=0.5,
            specialization='api',
            performance_score=0.8,
        )
        worker_general = Worker(
            id='worker2',
            capacity=0.5,
            performance_score=0.8,
        )

        quality_specialized = matcher.calculate_match_quality(task, worker_specialized)
        quality_general = matcher.calculate_match_quality(task, worker_general)

        # Specialized worker should have better quality
        assert quality_specialized > quality_general

    def test_match_tasks_to_workers_empty(self) -> None:
        """Test matching with empty inputs."""
        matcher = PlatformMatcher()

        # Empty tasks
        matches = matcher.match_tasks_to_workers([], [Worker(id='w1')])
        assert len(matches) == 0

        # Empty workers
        matches = matcher.match_tasks_to_workers([Task(id='t1', url='http://test.com')], [])
        assert len(matches) == 0

        # Both empty
        matches = matcher.match_tasks_to_workers([], [])
        assert len(matches) == 0

    def test_match_tasks_to_workers_basic(self) -> None:
        """Test basic task-worker matching."""
        matcher = PlatformMatcher()
        tasks = [
            Task(id='task1', url='https://example.com', priority=5.0),
            Task(id='task2', url='https://example.com', priority=3.0),
        ]
        workers = [
            Worker(id='worker1', capacity=0.8),
            Worker(id='worker2', capacity=0.5),
        ]

        matches = matcher.match_tasks_to_workers(tasks, workers)

        assert len(matches) == 2
        # Higher priority task should be matched first
        assert matches[0].task.id == 'task1'
        assert matches[0].task.priority == 5.0
        # Each match should have a quality score
        for match in matches:
            assert 0.0 <= match.quality <= 1.0

    def test_match_tasks_to_workers_priority_order(self) -> None:
        """Test that higher priority tasks are matched first."""
        matcher = PlatformMatcher()
        tasks = [
            Task(id='low', url='https://example.com', priority=1.0),
            Task(id='high', url='https://example.com', priority=10.0),
            Task(id='medium', url='https://example.com', priority=5.0),
        ]
        workers = [
            Worker(id='worker1'),
            Worker(id='worker2'),
        ]

        matches = matcher.match_tasks_to_workers(tasks, workers)

        # Should match high priority first, then medium
        assert len(matches) == 2
        assert matches[0].task.id == 'high'
        assert matches[1].task.id == 'medium'

    def test_match_tasks_to_workers_capacity_constraint(self) -> None:
        """Test that workers with insufficient capacity are skipped."""
        matcher = PlatformMatcher()
        tasks = [
            Task(id='heavy', url='https://example.com', priority=5.0, estimated_complexity=0.9),
        ]
        workers = [
            Worker(id='small', capacity=0.3),  # Too small for this task
            Worker(id='large', capacity=0.9),  # Sufficient capacity
        ]

        matches = matcher.match_tasks_to_workers(tasks, workers)

        # Should skip small worker and match with large
        assert len(matches) == 1
        assert matches[0].worker.id == 'large'

    def test_match_tasks_to_workers_one_to_one(self) -> None:
        """Test that each worker is only assigned once."""
        matcher = PlatformMatcher()
        tasks = [
            Task(id='task1', url='https://example.com', priority=5.0),
            Task(id='task2', url='https://example.com', priority=4.0),
            Task(id='task3', url='https://example.com', priority=3.0),
        ]
        workers = [
            Worker(id='worker1'),
        ]

        matches = matcher.match_tasks_to_workers(tasks, workers)

        # Only one task can be matched to one worker
        assert len(matches) == 1
        assert matches[0].task.id == 'task1'  # Highest priority

    def test_calculate_platform_efficiency_empty(self) -> None:
        """Test efficiency calculation with no matches."""
        matcher = PlatformMatcher()
        efficiency = matcher.calculate_platform_efficiency([])
        assert efficiency == 0.0

    def test_calculate_platform_efficiency_perfect(self) -> None:
        """Test efficiency calculation with perfect matches."""
        matcher = PlatformMatcher()
        matches = [
            Match(
                task=Task(id='t1', url='http://test.com'),
                worker=Worker(id='w1'),
                quality=1.0,
            ),
            Match(
                task=Task(id='t2', url='http://test.com'),
                worker=Worker(id='w2'),
                quality=1.0,
            ),
        ]
        efficiency = matcher.calculate_platform_efficiency(matches)
        assert efficiency == 1.0

    def test_calculate_platform_efficiency_average(self) -> None:
        """Test efficiency calculation with average matches."""
        matcher = PlatformMatcher()
        matches = [
            Match(
                task=Task(id='t1', url='http://test.com'),
                worker=Worker(id='w1'),
                quality=0.8,
            ),
            Match(
                task=Task(id='t2', url='http://test.com'),
                worker=Worker(id='w2'),
                quality=0.6,
            ),
        ]
        efficiency = matcher.calculate_platform_efficiency(matches)
        assert efficiency == 0.7  # (0.8 + 0.6) / 2


class TestIntegration:
    """Integration tests for the platform matching system."""

    def test_realistic_matching_scenario(self) -> None:
        """Test a realistic matching scenario with multiple tasks and workers."""
        matcher = PlatformMatcher(
            capacity_weight=0.3,
            performance_weight=0.3,
            priority_weight=0.4,
        )

        tasks = [
            Task(
                id='api-scrape',
                url='https://api.example.com',
                priority=8.0,
                estimated_complexity=0.6,
                metadata={'type': 'api'},
            ),
            Task(
                id='js-heavy',
                url='https://spa.example.com',
                priority=6.0,
                estimated_complexity=0.9,
                metadata={'type': 'javascript'},
            ),
            Task(
                id='simple-page',
                url='https://example.com',
                priority=4.0,
                estimated_complexity=0.3,
            ),
        ]

        workers = [
            Worker(
                id='api-specialist',
                capacity=0.7,
                specialization='api',
                performance_score=0.95,
            ),
            Worker(
                id='js-specialist',
                capacity=0.9,
                specialization='javascript',
                performance_score=0.9,
            ),
            Worker(
                id='generalist',
                capacity=0.5,
                performance_score=0.8,
            ),
        ]

        matches = matcher.match_tasks_to_workers(tasks, workers)

        # All tasks should be matched
        assert len(matches) == 3

        # API task should be matched with API specialist
        api_match = next(m for m in matches if m.task.id == 'api-scrape')
        assert api_match.worker.id == 'api-specialist'

        # JS task should be matched with JS specialist
        js_match = next(m for m in matches if m.task.id == 'js-heavy')
        assert js_match.worker.id == 'js-specialist'

        # Simple task gets the generalist
        simple_match = next(m for m in matches if m.task.id == 'simple-page')
        assert simple_match.worker.id == 'generalist'

        # Efficiency should be high with good matches
        efficiency = matcher.calculate_platform_efficiency(matches)
        assert efficiency > 0.7
