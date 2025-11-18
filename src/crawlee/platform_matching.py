# Inspiration: Two-sided platform optimal design for matching tasks to workers
# Reference: https://arxiv.org/pdf/2102.09017.pdf

"""Two-sided platform matching for optimal task-to-worker assignment.

This module implements optimal matching algorithms for assigning crawling tasks to workers
in a distributed crawling environment. It's based on two-sided platform design principles
where one side (tasks/URLs) needs to be optimally matched with the other side (workers/crawlers).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class Task:
    """Represents a crawling task in the platform."""

    id: str
    """Unique identifier for the task."""

    url: str
    """URL to be crawled."""

    priority: float = 1.0
    """Priority of the task (higher is more important)."""

    estimated_complexity: float = 1.0
    """Estimated complexity/resource requirement for the task."""

    metadata: dict[str, Any] | None = None
    """Additional metadata for the task."""


@dataclass
class Worker:
    """Represents a worker/crawler in the platform."""

    id: str
    """Unique identifier for the worker."""

    capacity: float = 1.0
    """Available capacity of the worker (0.0 to 1.0)."""

    specialization: str | None = None
    """Optional specialization of the worker (e.g., 'javascript', 'api')."""

    performance_score: float = 1.0
    """Performance score of the worker (higher is better)."""

    metadata: dict[str, Any] | None = None
    """Additional metadata for the worker."""


@dataclass
class Match:
    """Represents a match between a task and a worker."""

    task: Task
    """The task to be executed."""

    worker: Worker
    """The worker assigned to execute the task."""

    quality: float
    """Quality score of this match (higher is better)."""


class PlatformMatcher:
    """Optimal matcher for two-sided platform task-worker assignment.

    This class implements a greedy matching algorithm that optimizes the assignment of tasks
    to workers based on multiple factors including priority, capacity, and compatibility.
    """

    def __init__(
        self,
        *,
        capacity_weight: float = 0.3,
        performance_weight: float = 0.3,
        priority_weight: float = 0.4,
    ) -> None:
        """Initialize the platform matcher.

        Args:
            capacity_weight: Weight for worker capacity in quality calculation.
            performance_weight: Weight for worker performance in quality calculation.
            priority_weight: Weight for task priority in quality calculation.
        """
        if not 0 <= capacity_weight <= 1:
            raise ValueError('capacity_weight must be between 0 and 1')
        if not 0 <= performance_weight <= 1:
            raise ValueError('performance_weight must be between 0 and 1')
        if not 0 <= priority_weight <= 1:
            raise ValueError('priority_weight must be between 0 and 1')

        # Constants for weight validation
        epsilon = 0.01  # Tolerance for floating point comparison
        target_sum = 1.0

        total = capacity_weight + performance_weight + priority_weight
        if not (target_sum - epsilon) <= total <= (target_sum + epsilon):
            raise ValueError('Weights must sum to 1.0')

        self._capacity_weight = capacity_weight
        self._performance_weight = performance_weight
        self._priority_weight = priority_weight

    def calculate_match_quality(self, task: Task, worker: Worker) -> float:
        """Calculate the quality score for a potential task-worker match.

        Args:
            task: The task to be matched.
            worker: The worker to be matched.

        Returns:
            A quality score between 0 and 1 (higher is better).
        """
        # Normalize priority to [0, 1] range (assuming max priority of 10)
        normalized_priority = min(task.priority / 10.0, 1.0)

        # Calculate compatibility based on complexity vs capacity
        complexity_fit = 1.0 - abs(task.estimated_complexity - worker.capacity)

        # Combine factors with weights
        quality = (
            self._priority_weight * normalized_priority
            + self._capacity_weight * complexity_fit
            + self._performance_weight * worker.performance_score
        )

        # Apply specialization bonus if applicable
        if (
            worker.specialization
            and task.metadata
            and 'type' in task.metadata
            and worker.specialization == task.metadata['type']
        ):
            quality *= 1.1  # 10% bonus for specialization match

        return min(quality, 1.0)  # Cap at 1.0

    def match_tasks_to_workers(
        self,
        tasks: Sequence[Task],
        workers: Sequence[Worker],
    ) -> list[Match]:
        """Perform optimal matching of tasks to workers.

        This implements a greedy matching algorithm that assigns each task to the best
        available worker based on the calculated match quality.

        Args:
            tasks: List of tasks to be matched.
            workers: List of available workers.

        Returns:
            A list of Match objects representing the optimal assignments.
        """
        if not tasks:
            return []
        if not workers:
            return []

        matches: list[Match] = []
        available_workers = list(workers)

        # Sort tasks by priority (descending)
        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)

        for task in sorted_tasks:
            if not available_workers:
                break  # No more workers available

            # Find best worker for this task
            best_worker = None
            best_quality = -1.0

            for worker in available_workers:
                # Skip workers without sufficient capacity
                if worker.capacity < task.estimated_complexity * 0.5:
                    continue

                quality = self.calculate_match_quality(task, worker)
                if quality > best_quality:
                    best_quality = quality
                    best_worker = worker

            # If we found a suitable worker, create the match
            if best_worker is not None:
                matches.append(
                    Match(
                        task=task,
                        worker=best_worker,
                        quality=best_quality,
                    )
                )
                # Remove matched worker from available pool
                available_workers.remove(best_worker)

        return matches

    def calculate_platform_efficiency(self, matches: Sequence[Match]) -> float:
        """Calculate overall platform efficiency based on matches.

        Args:
            matches: List of task-worker matches.

        Returns:
            Efficiency score between 0 and 1 (higher is better).
        """
        if not matches:
            return 0.0

        total_quality = sum(match.quality for match in matches)
        return total_quality / len(matches)
