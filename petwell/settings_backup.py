"""Compatibility alias for old local launch commands; use petwell.settings."""

# Keep one authoritative configuration so an old module name cannot silently
# restore retired hosts, deprecated authentication or missing payment settings.
from .settings import *  # noqa: F403
