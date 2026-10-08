from app.services.resume.parse_errors import USER_PARSE_FAILED, public_parse_error


def test_public_parse_error_hides_ollama_url() -> None:
    stored = (
        "Ollama request failed: Client error '404 Not Found' "
        "for url 'http://localhost:11434/api/generate'"
    )
    assert public_parse_error(stored) == USER_PARSE_FAILED


def test_public_parse_error_keeps_user_message() -> None:
    message = "No text could be read from this PDF. Try another file."
    assert public_parse_error(message) == message


def test_public_parse_error_empty() -> None:
    assert public_parse_error(None) is None
    assert public_parse_error("   ") is None
