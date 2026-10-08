"""User-facing resume parse failures. Internal causes stay in server logs."""

USER_PARSE_FAILED = "Parsing failed. Upload the resume again or choose another file."
USER_PARSE_EMPTY = "No text could be read from this PDF. Try another file."

_INTERNAL_MARKERS = (
    "http://",
    "https://",
    "ollama",
    "traceback",
    "client error",
    "localhost",
)


def public_parse_error(stored: str | None) -> str | None:
    """Return a message safe to show in the app.

    Older rows stored the raw exception, including Ollama URLs. Those are
    replaced here so a refresh does not reveal them.
    """
    if stored is None or not stored.strip():
        return None
    lowered = stored.lower()
    if any(marker in lowered for marker in _INTERNAL_MARKERS):
        return USER_PARSE_FAILED
    return stored
