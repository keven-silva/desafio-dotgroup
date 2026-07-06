# Injeção de dependências no FastAPI

O sistema de dependências do FastAPI, exposto através da função `Depends`, é um dos recursos
mais poderosos do framework e vai muito além de simplesmente "reaproveitar código". Uma
dependência é qualquer callable (função, método ou classe com `__call__`) que o FastAPI chama
automaticamente antes de executar a rota, injetando o resultado como parâmetro.

O caso de uso mais comum é obter uma sessão de banco de dados por request: uma função
geradora como `async def get_db(): async with SessionLocal() as session: yield session` permite
que o FastAPI abra a sessão antes da rota executar e feche (ou commite) depois que a resposta
for gerada, mesmo em caso de exceção — isso é possível porque o FastAPI trata dependências que
usam `yield` como gerenciadores de contexto implícitos.

Dependências também podem depender de outras dependências, formando uma árvore. É comum, em
arquiteturas em camadas (ou hexagonais/DDD), ter uma dependência que constrói um repositório
a partir da sessão de banco, e outra que constrói um "service" (caso de uso) a partir do
repositório — cada camada só enxerga a camada imediatamente abaixo, e o FastAPI resolve toda
a árvore automaticamente, com cache por request (a mesma dependência não é executada duas
vezes na mesma requisição, a menos que `use_cache=False` seja especificado).

Outro recurso importante é `app.dependency_overrides`, usado principalmente em testes: permite
substituir uma dependência real (por exemplo, uma conexão com Postgres) por uma versão de
teste (como SQLite em memória) sem alterar o código da aplicação — os testes chamam a mesma
rota, mas o FastAPI injeta a dependência substituta durante aquele teste específico.

Dependências também servem para autenticação e autorização: uma dependência que extrai e
valida um token JWT do header `Authorization` pode ser declarada uma vez e reutilizada em
todas as rotas que precisam de um usuário autenticado, geralmente combinada com `Security()`
para integrar com o esquema de segurança documentado automaticamente no OpenAPI/Swagger.
