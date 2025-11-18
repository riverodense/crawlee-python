from importlib import metadata

from ._request import Request, RequestOptions
from ._service_locator import service_locator
from ._types import ConcurrencySettings, EnqueueStrategy, HttpHeaders, RequestTransformAction, SkippedReason
from ._utils.globs import Glob
from .platform_matching import Match, PlatformMatcher, Task, Worker

__version__ = metadata.version('crawlee')

__all__ = [
    'ConcurrencySettings',
    'EnqueueStrategy',
    'Glob',
    'HttpHeaders',
    'Match',
    'PlatformMatcher',
    'Request',
    'RequestOptions',
    'RequestTransformAction',
    'SkippedReason',
    'Task',
    'Worker',
    'service_locator',
]
