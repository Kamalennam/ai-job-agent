from app.collectors.greenhouse.collector import _slug_from_board_url, _strip_html


def test_slug_from_board_url():
    assert _slug_from_board_url("https://boards.greenhouse.io/stripe") == "stripe"
    assert _slug_from_board_url("stripe") == "stripe"


def test_strip_html():
    assert _strip_html("<p>Hello <strong>world</strong></p>") == "Hello world"
