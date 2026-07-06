import pytest

from library_api.shared.validation import normalize_optional_text, normalize_required_text


def test_normalize_required_text_strips_whitespace() -> None:
    assert normalize_required_text("  Robert C. Martin  ") == "Robert C. Martin"


def test_normalize_required_text_rejects_blank_string() -> None:
    with pytest.raises(ValueError, match="vazio"):
        normalize_required_text("   ")


def test_normalize_optional_text_passes_through_none() -> None:
    assert normalize_optional_text(None) is None


def test_normalize_optional_text_strips_whitespace() -> None:
    assert normalize_optional_text("  bio aqui  ") == "bio aqui"
