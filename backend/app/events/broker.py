"""Fast check that the Celery broker port accepts a connection.

Celery's own retry loop can block an HTTP request for tens of seconds when
Redis is down. Callers probe first, then queue, or fall back immediately.
"""

import socket
from urllib.parse import urlparse

from app.config import get_settings

_PROBE_TIMEOUT_SECONDS = 0.15


def broker_reachable() -> bool:
    parsed = urlparse(get_settings().celery_broker_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 6379
    try:
        with socket.create_connection((host, port), timeout=_PROBE_TIMEOUT_SECONDS):
            return True
    except OSError:
        return False
