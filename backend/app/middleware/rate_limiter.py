"""
Rate-limiting configuration using slowapi.

Limits are applied per client IP address.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Central limiter instance — import this in route files
limiter = Limiter(key_func=get_remote_address)

# ── Limit strings (reusable across routes) ──────────────────────
CHAT_LIMIT = "10/minute"       # AI calls are expensive
DATA_LIMIT = "30/minute"       # Data queries are lighter
USER_LIMIT = "5/minute"        # Registration / profile updates
