def normalize_required_text(value: str) -> str:
    """Remove espaços das pontas e rejeita strings vazias/só-espaço.

    Usado em campos de identidade (nome, título, ISBN, categoria, e-mail) para que
    " Robert C. Martin " e "Robert C. Martin" sejam tratados como o mesmo valor, e para
    que `min_length=1` não seja satisfeito trivialmente por uma string só de espaços.
    """
    stripped = value.strip()
    if not stripped:
        raise ValueError("não pode ser vazio ou conter apenas espaços")
    return stripped


def normalize_optional_text(value: str | None) -> str | None:
    """Como `normalize_required_text`, mas para campos opcionais (`None` continua `None`)."""
    if value is None:
        return None
    return value.strip()
