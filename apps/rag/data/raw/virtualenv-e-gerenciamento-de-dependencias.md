# Ambientes virtuais e gerenciamento de dependências em Python

Um dos problemas centrais ao trabalhar com Python é isolar as dependências de cada projeto:
sem isolamento, instalar um pacote globalmente (`pip install`) pode gerar conflitos de versão
entre projetos diferentes que dependem da mesma biblioteca em versões incompatíveis. A solução
tradicional é o módulo `venv` da biblioteca padrão, que cria um ambiente isolado com seu próprio
interpretador Python e diretório `site-packages`.

Um ambiente virtual criado com `python -m venv .venv` precisa ser ativado (`source
.venv/bin/activate` no Linux/macOS) para que o `pip install` e a execução de scripts usem
o Python e os pacotes daquele ambiente, em vez do Python global do sistema. Esquecer de
ativar o ambiente antes de instalar pacotes é uma fonte comum de bugs — "funciona na minha
máquina" muitas vezes significa "os pacotes foram instalados no ambiente errado".

Ferramentas mais modernas foram criadas para simplificar esse fluxo. O `uv`, por exemplo,
é um gerenciador de pacotes e projetos escrito em Rust que substitui `pip`, `pip-tools`,
`virtualenv` e parte do `poetry` em uma única ferramenta muito mais rápida. Com `uv`, comandos
como `uv add fastapi` já resolvem a dependência, atualizam o `pyproject.toml`, geram/atualizam
um `uv.lock` (lockfile determinístico) e instalam no `.venv` automaticamente — sem precisar
ativar o ambiente manualmente para a maioria dos fluxos, já que `uv run` cuida disso.

`uv` também suporta "workspaces": um monorepo onde múltiplos pacotes Python (cada um com seu
próprio `pyproject.toml`) compartilham um único lockfile na raiz, mas continuam podendo ser
instalados, testados e rodados de forma independente (`uv run --package nome-do-pacote ...`).
Isso é útil para organizar um sistema em múltiplos serviços relacionados sem duplicar a
resolução de dependências para cada um.

Independentemente da ferramenta, a prática recomendada é sempre versionar um arquivo de
lock (`uv.lock`, `poetry.lock` ou `requirements.txt` com hashes) junto do código-fonte, para
garantir que todo mundo — e o ambiente de produção — instale exatamente as mesmas versões
de cada dependência transitiva, evitando o clássico "build reproduzível hoje, quebrado amanhã".
