# Programação assíncrona com async/await em Python

Python oferece suporte nativo a programação assíncrona através das palavras-chave `async`
e `await`, introduzidas de forma completa a partir do módulo `asyncio`. Uma função declarada
com `async def` é chamada de coroutine: ao invocá-la, você não executa o código imediatamente,
mas obtém um objeto coroutine que precisa ser agendado em um event loop.

O `await` é usado dentro de uma coroutine para ceder o controle de volta ao event loop
enquanto uma operação assíncrona (como uma requisição de rede ou leitura de arquivo) está
em andamento. Isso permite que outras tarefas sejam executadas nesse meio tempo, sem bloquear
a thread principal — diferente de código síncrono, que trava esperando a operação terminar.

Um erro comum é achar que `async`/`await` torna o código mais rápido por si só. Na verdade,
o ganho de performance vem da concorrência: enquanto uma tarefa está esperando I/O (rede,
disco, banco de dados), o event loop pode avançar outras tarefas. Para código CPU-bound
(cálculos pesados), `asyncio` não ajuda — nesse caso, o caminho é usar `multiprocessing` ou
bibliotecas como `concurrent.futures.ProcessPoolExecutor`.

Frameworks como FastAPI aproveitam `async`/`await` nativamente: rotas declaradas com
`async def` podem lidar com muitas requisições concorrentes usando poucas threads, desde que
as chamadas de I/O dentro delas também sejam assíncronas (ex: um driver de banco async como
`asyncpg`, em vez de um driver síncrono como `psycopg2`). Misturar chamadas síncronas
bloqueantes dentro de uma rota `async def` anula esse benefício e pode até piorar a
performance, pois bloqueia o event loop inteiro.

Para rodar uma coroutine de forma independente, usa-se `asyncio.run(main())` como ponto de
entrada. Para rodar várias coroutines concorrentemente, `asyncio.gather(*tasks)` é a forma
mais comum, retornando os resultados na mesma ordem em que as tasks foram passadas.
