from library_api.shared.exceptions import ConflictError


class LoanAlreadyReturnedError(ConflictError):
    """Levantada ao tentar devolver um empréstimo que já foi devolvido."""
