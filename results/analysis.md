# Comparacao local das quatro estrategias

Dados sinteticos: NetworkX gnm_random_graph, sementes 0, 1 e 2.
Cada serie contem as 13 combinacoes de vertices e arestas do placar.
**Estas nao sao as instancias oficiais do Codabench.**

| Estrategia | Soma media dos scores por serie de 13 grafos |
| --- | ---: |
| bfs | 8.598667 |
| duplicated_greedy | 6.301333 |
| joint_greedy | 4.156000 |
| local_search | 4.081333 |

Maior tempo medido para executar todas as estrategias num grafo: 0.103786 s.

As 39 instancias produziram dois conjuntos validos em cada estrategia.
A busca local melhorou ou manteve o melhor score das tres construcoes em cada instancia.

A nota oficial anterior da BFS foi 7.89 (submissao 1032586), conforme a linha do placar enviada pelo usuario.
A nova nota oficial depende da execucao desta submissao no Codabench.

Validacao: 9 testes passaram, incluindo os 1253 grafos simples do atlas com ate 7 vertices, casos de regressao do score e grafos maiores.
A sintaxe foi validada para Python 3.7; a execucao local usou Python 3.14.4 e NetworkX 2.6.3.
O ZIP foi importado diretamente e conferido com exemplos de estrelas, cliques, caminhos e grafo aleatorio.
