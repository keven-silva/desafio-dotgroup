"""Garante que as migrations do Alembic aplicam limpo contra um Postgres vazio.

Requer um Postgres acessível via DATABASE_URL (ex: `docker compose up -d postgres`).
Se não houver conexão disponível, o teste é pulado — ele não deve travar a suíte
unitária no CI/local sem infraestrutura.
"""

import subprocess
import sys
from pathlib import Path

import asyncpg
import pytest

from library_api.shared.config import get_settings

APP_DIR = Path(__file__).resolve().parent.parent


async def _postgres_is_reachable() -> bool:
    settings = get_settings()
    dsn = settings.database_url.replace("postgresql+asyncpg", "postgresql")
    try:
        conn = await asyncpg.connect(dsn, timeout=2)
    except Exception:
        return False
    await conn.close()
    return True


async def test_alembic_upgrade_head_runs_clean() -> None:
    if not await _postgres_is_reachable():
        pytest.skip("Postgres indisponível — rode `docker compose up -d postgres` para validar migrations")

    # Não faz downgrade ao final: este comando roda contra o Postgres configurado em
    # DATABASE_URL (tipicamente o de desenvolvimento), e desfazer o schema surpreenderia
    # quem estiver com dados nele. `upgrade head` é idempotente, então é seguro repetir.
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=APP_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
