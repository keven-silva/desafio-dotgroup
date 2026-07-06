from library_api.shared.exceptions import ConflictError


class BookNotAvailableError(ConflictError):
    """Levantada quando não há cópias disponíveis para empréstimo."""
