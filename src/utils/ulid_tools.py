from ulid import ULID
import datetime


def get_current_ulid() -> str:
    """Generate a new ULID based on the current time with timezone info."""
    # Get timezone-aware datetime using local timezone
    tz_aware_now = datetime.datetime.now().astimezone()
    return str(ULID.from_datetime(tz_aware_now))
