# Comparacao V1 e V2

Referencia oficial fornecida pelo usuario: busca local V1 = 2.96; melhor leaderboard informado = 2.62.
A V2 ainda nao tem nota oficial.

Resultados sinteticos: 117 grafos, tres familias e sementes novas 23, 47 e 89.
Cada soma abaixo e a media de tres series com treze grafos cada.

| Familia | V1 | V2 |
| --- | ---: | ---: |
| G(n,m) | 3.972667 | 3.808000 |
| Arvore + arestas | 3.255333 | 3.058000 |
| Ciclo + arestas | 2.808000 | 2.720000 |

71 grafos melhoraram; 46 empataram; nenhum piorou.
Maior tempo medido no ZIP final: 1.083065 segundo por grafo.

Esses grafos nao sao os grafos oficiais e suas somas nao predizem a nota no Codabench.
A V2 guarda a melhor resposta V1, garantindo score menor ou igual para o mesmo grafo.

Validacao: 14 testes passaram; o atlas com 1253 grafos de ate sete vertices manteve validade e nao regressao.
A reconstrucao limitada foi conferida contra otimos exaustivos em todos os grafos simples de ate cinco vertices.
O ZIP autonomo foi importado diretamente e reavaliado nos 117 grafos de benchmark e em oito casos adicionais.
A sintaxe foi conferida para Python 3.7; a execucao local usou Python 3.14.4 e NetworkX 2.6.3.

Submissao nova: `../../submissions/improved_search_v2.zip` (identica a `../../submission.zip`).
Os quatro ZIPs V1 foram preservados sem alteracao e copiados para `../../submissions/archive_v1/`.
