"""Example demonstrating two-sided platform optimal design for task-worker matching.

This example shows how to use the PlatformMatcher to optimally assign crawling tasks
to workers based on their capabilities, capacity, and task requirements.
"""

from crawlee import PlatformMatcher, Task, Worker


def main() -> None:
    """Demonstrate optimal task-worker matching in a two-sided platform."""
    # Create tasks with different priorities and complexities
    tasks = [
        Task(
            id='task1',
            url='https://example.com/api',
            priority=8.0,
            estimated_complexity=0.7,
            metadata={'type': 'api'},
        ),
        Task(
            id='task2',
            url='https://example.com/heavy-js',
            priority=6.0,
            estimated_complexity=0.9,
            metadata={'type': 'javascript'},
        ),
        Task(
            id='task3',
            url='https://example.com/simple',
            priority=4.0,
            estimated_complexity=0.3,
        ),
        Task(
            id='task4',
            url='https://example.com/medium',
            priority=7.0,
            estimated_complexity=0.5,
        ),
    ]

    # Create workers with different capabilities
    workers = [
        Worker(
            id='worker1',
            capacity=0.8,
            specialization='javascript',
            performance_score=0.9,
        ),
        Worker(
            id='worker2',
            capacity=0.5,
            performance_score=0.8,
        ),
        Worker(
            id='worker3',
            capacity=0.9,
            specialization='api',
            performance_score=0.95,
        ),
    ]

    # Create matcher with custom weights
    matcher = PlatformMatcher(
        capacity_weight=0.3,
        performance_weight=0.3,
        priority_weight=0.4,
    )

    # Perform optimal matching
    matches = matcher.match_tasks_to_workers(tasks, workers)

    # Display results
    print('Optimal Task-Worker Matches:')
    print('=' * 60)
    for match in matches:
        print(f'\nTask: {match.task.id} ({match.task.url})')
        print(f'  Priority: {match.task.priority}')
        print(f'  Complexity: {match.task.estimated_complexity}')
        print(f'Worker: {match.worker.id}')
        print(f'  Capacity: {match.worker.capacity}')
        print(f'  Performance: {match.worker.performance_score}')
        if match.worker.specialization:
            print(f'  Specialization: {match.worker.specialization}')
        print(f'Match Quality: {match.quality:.2f}')

    # Calculate platform efficiency
    efficiency = matcher.calculate_platform_efficiency(matches)
    print('\n' + '=' * 60)
    print(f'Overall Platform Efficiency: {efficiency:.2%}')
    print(f'Tasks Matched: {len(matches)} / {len(tasks)}')
    print(f'Workers Utilized: {len(matches)} / {len(workers)}')


if __name__ == '__main__':
    main()
