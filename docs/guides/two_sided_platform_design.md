# Two-sided Platform Optimal Design

## Overview

Crawlee includes a two-sided platform matching system for optimal task-worker assignment. This feature is particularly useful in distributed crawling scenarios where you need to efficiently match crawling tasks with available workers.

## Concept

A two-sided platform connects two distinct groups:
- **Tasks (Side 1)**: URLs or crawling tasks that need to be processed
- **Workers (Side 2)**: Crawler instances or workers that process the tasks

The matching algorithm optimally assigns tasks to workers based on multiple factors:
- Task priority
- Worker capacity and availability
- Task complexity
- Worker performance scores
- Specialization matching

## Basic Usage

```python
from crawlee import PlatformMatcher, Task, Worker

# Create tasks with priorities and complexity
tasks = [
    Task(
        id='task1',
        url='https://api.example.com',
        priority=8.0,
        estimated_complexity=0.7,
        metadata={'type': 'api'},
    ),
    Task(
        id='task2',
        url='https://example.com/page',
        priority=5.0,
        estimated_complexity=0.4,
    ),
]

# Create workers with different capabilities
workers = [
    Worker(
        id='worker1',
        capacity=0.8,
        specialization='api',
        performance_score=0.95,
    ),
    Worker(
        id='worker2',
        capacity=0.6,
        performance_score=0.85,
    ),
]

# Create a matcher with custom weights
matcher = PlatformMatcher(
    capacity_weight=0.3,      # Weight for capacity matching
    performance_weight=0.3,   # Weight for performance
    priority_weight=0.4,      # Weight for task priority
)

# Perform optimal matching
matches = matcher.match_tasks_to_workers(tasks, workers)

# Process matches
for match in matches:
    print(f'Task {match.task.id} → Worker {match.worker.id}')
    print(f'Match quality: {match.quality:.2f}')

# Calculate platform efficiency
efficiency = matcher.calculate_platform_efficiency(matches)
print(f'Platform efficiency: {efficiency:.2%}')
```

## Components

### Task

Represents a crawling task or URL to be processed.

**Attributes:**
- `id`: Unique identifier
- `url`: URL to crawl
- `priority`: Task priority (higher values = higher priority)
- `estimated_complexity`: Resource requirement estimate (0.0 to 1.0)
- `metadata`: Optional metadata dictionary

### Worker

Represents a crawler instance or worker.

**Attributes:**
- `id`: Unique identifier
- `capacity`: Available capacity (0.0 to 1.0)
- `specialization`: Optional specialization type
- `performance_score`: Performance rating (0.0 to 1.0)
- `metadata`: Optional metadata dictionary

### PlatformMatcher

Performs optimal task-worker matching.

**Parameters:**
- `capacity_weight`: Weight for capacity matching (default: 0.3)
- `performance_weight`: Weight for performance (default: 0.3)
- `priority_weight`: Weight for task priority (default: 0.4)

**Methods:**
- `calculate_match_quality(task, worker)`: Calculate quality score for a match
- `match_tasks_to_workers(tasks, workers)`: Perform optimal matching
- `calculate_platform_efficiency(matches)`: Calculate overall efficiency

## Algorithm Details

The matching algorithm works as follows:

1. **Priority Ordering**: Tasks are sorted by priority (highest first)
2. **Greedy Matching**: For each task, find the best available worker
3. **Quality Calculation**: Match quality is based on:
   - Task priority (normalized)
   - Capacity fit (how well worker capacity matches task complexity)
   - Worker performance score
   - Specialization bonus (10% if specializations match)
4. **One-to-One Assignment**: Each worker is assigned at most one task
5. **Capacity Constraint**: Workers must have at least 50% of required capacity

## Use Cases

### Distributed Crawling

Assign URLs to crawler instances based on their capabilities:

```python
# Create tasks from a URL queue
tasks = [
    Task(id=f'task{i}', url=url, priority=calculate_priority(url))
    for i, url in enumerate(url_queue)
]

# Create workers representing different crawler instances
workers = [
    Worker(id=f'crawler{i}', capacity=get_capacity(i))
    for i in range(num_crawlers)
]

# Match and distribute
matches = matcher.match_tasks_to_workers(tasks, workers)
```

### Specialized Crawling

Match tasks requiring specific capabilities to specialized workers:

```python
# JavaScript-heavy site
js_task = Task(
    id='spa',
    url='https://spa.example.com',
    metadata={'type': 'javascript'},
)

# API endpoint
api_task = Task(
    id='api',
    url='https://api.example.com',
    metadata={'type': 'api'},
)

# Specialized workers
js_worker = Worker(id='playwright', specialization='javascript')
api_worker = Worker(id='api-client', specialization='api')

matches = matcher.match_tasks_to_workers([js_task, api_task], [js_worker, api_worker])
```

### Load Balancing

Balance load across workers based on capacity and performance:

```python
# High-complexity task
heavy_task = Task(
    id='heavy',
    url='https://heavy.example.com',
    estimated_complexity=0.9,
)

# Workers with different capacities
workers = [
    Worker(id='strong', capacity=0.95, performance_score=0.9),
    Worker(id='medium', capacity=0.6, performance_score=0.85),
    Worker(id='light', capacity=0.3, performance_score=0.8),
]

# Heavy task will be matched to strong worker
matches = matcher.match_tasks_to_workers([heavy_task], workers)
```

## Performance Considerations

- **Time Complexity**: O(n×m) where n = tasks, m = workers
- **Space Complexity**: O(n + m)
- **Greedy Approach**: Provides good results in O(n×m) time
- **Optimal for**: Moderate-sized task/worker sets (hundreds to thousands)

## Best Practices

1. **Set Appropriate Priorities**: Use priority to ensure critical tasks are matched first
2. **Estimate Complexity**: Accurate complexity estimates improve matching quality
3. **Use Specialization**: Leverage specialization for type-specific tasks
4. **Monitor Efficiency**: Track platform efficiency to optimize weights
5. **Balance Weights**: Adjust weights based on your specific requirements

## Example

See the complete example at `docs/examples/code_examples/two_sided_platform_matching.py`.

## References

This implementation is based on research in two-sided platform design and matching theory:
- [Designing Approximately Optimal Search on Matching Platforms](https://arxiv.org/pdf/2102.09017.pdf)
- Economic theory of two-sided markets and platform design
