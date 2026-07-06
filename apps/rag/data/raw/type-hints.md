# Type hints e tipagem estática em Python

Type hints foram introduzidos pela PEP 484 e permitem anotar tipos de variáveis, parâmetros
de função e retornos sem alterar o comportamento em tempo de execução — Python continua
sendo uma linguagem de tipagem dinâmica, e as anotações são, por padrão, apenas metadados
ignorados pelo interpretador. Quem de fato verifica essas anotações são ferramentas externas
como `mypy`, `pyright` ou `pyrefly`, rodadas separadamente (geralmente no CI ou no editor).

Uma anotação simples se parece com `def add(a: int, b: int) -> int: return a + b`. Para tipos
mais complexos, o módulo `typing` (e, a partir do Python 3.9+, os próprios genéricos nativos
como `list[int]`, `dict[str, int]`) oferece construções como `Optional[str]` (equivalente a
`str | None` no Python 3.10+), `Union`, `Sequence`, `Protocol` e `TypeVar`.

`Protocol` merece destaque especial: permite tipagem estrutural (duck typing tipado) — uma
classe não precisa herdar explicitamente de um `Protocol` para satisfazê-lo, basta implementar
os métodos com a assinatura esperada. Isso é muito usado em arquiteturas hexagonais/DDD em
Python para definir "portas" (interfaces) sem acoplar o domínio a uma implementação concreta.

Bibliotecas como Pydantic e FastAPI levam type hints além da simples documentação: usam as
anotações em tempo de execução para validar dados de entrada, gerar JSON Schema e documentação
OpenAPI automaticamente. Isso é possível porque o módulo `typing` expõe as anotações via
`__annotations__` e `typing.get_type_hints()`, permitindo introspecção em runtime quando
necessário — algo que difere de linguagens onde tipos existem só em tempo de compilação.

Um ponto importante: type hints não tornam o código mais rápido nem adicionam checagem em
runtime por padrão. Se você precisa de validação real durante a execução (por exemplo, rejeitar
uma requisição HTTP com payload de tipo errado), é necessário usar uma biblioteca como Pydantic,
ou escrever a validação manualmente com `isinstance`.
