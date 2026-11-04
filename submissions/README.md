# Submissoes para o Codabench

Cada ZIP contem somente `algorithm.py` na raiz e expoe `dominant(g)`.

| Arquivo | Estrategia executada por dominant(g) |
| --- | --- |
| `bfs.zip` | BFS por paridade |
| `duplicated_greedy.zip` | Guloso duplicado |
| `joint_greedy.zip` | Guloso conjunto |
| `local_search.zip` | Busca local a partir das tres construcoes |
| `improved_search_v2.zip` | V2: multiplas construcoes e remocao/reconstrucao |

Os quatro ZIPs V1 estao preservados tambem em `archive_v1/`.
O ZIP combinado V1 anterior esta em `archive_v1/best_of_all.zip`.

Os ZIPs individuais mantem as funcoes auxiliares no mesmo arquivo, mas
o ponto de entrada executa somente a estrategia indicada. A busca local
usa as tres construcoes como pontos de partida.

`improved_search_v2.zip` e identico a `../submission.zip` e preserva a
melhor resposta V1 como ponto de partida. Seus resultados locais e suas
verificacoes estao em `../results/improved/`.

Para reconstruir a V2 a partir da pasta `algoPlus`:

```sh
python3 projet1/build_improved_submission.py
```

Para reconstruir os cinco ZIPs atuais a partir da pasta `algoPlus`:

```sh
python3 projet1/build_submissions.py
```

O script V1 atualiza tambem `../submission.zip` com a versao V1.
Para preparar a V2 novamente, executar depois `build_improved_submission.py`.
`manifest.json` registra a estrategia e o SHA-256 de cada arquivo gerado.
