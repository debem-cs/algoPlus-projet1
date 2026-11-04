# Projet1: dois conjuntos dominantes

Este projeto implementa algoritmos para o concurso de **Minimum intersecting dominant sets** do [Codabench](https://www.codabench.org/competitions/18251/). O repositório indicado para o projeto é [debem-cs/algoPlus-projet1](https://github.com/debem-cs/algoPlus-projet1).

**Versão preparada para envio:** [submissions/improved_search_v2.zip](submissions/improved_search_v2.zip). O arquivo [submission.zip](submission.zip) tem o mesmo conteúdo. Cada ZIP contém apenas `algorithm.py` na raiz, com a função `dominant(g)` exigida pela plataforma.

A V2 reutiliza as quatro estratégias da V1 e amplia a busca. A melhor nota oficial recebida até agora foi **2,96**, da busca local V1. A nota **2,62** foi informada como a melhor do leaderboard; isso não é uma prova do ótimo matemático. **Ainda não há nota oficial registrada para a V2.**

## 1. O problema

A entrada é um grafo não orientado e sem pesos `g`, representado por um objeto NetworkX. Os vértices podem representar cidades e as arestas, estradas diretas.

Um conjunto de vértices `D` é **dominante** quando todo vértice do grafo:

- pertence a `D`; ou
- tem pelo menos um vizinho em `D`.

Cada vértice escolhido cobre **a si mesmo e seus vizinhos imediatos**. Um caminho de duas ou mais arestas não basta para essa cobertura.

Chamamos de **vizinhança fechada** de `v` o conjunto:

```text
N[v] = {v} ∪ vizinhos(v)
```

Assim, `D` domina o grafo quando a união de `N[v]`, para todos os `v` escolhidos em `D`, contém todos os vértices.

A saída precisa ter **dois conjuntos dominantes**, `D1` e `D2`. Cada um deve dominar o grafo inteiro por conta própria. Eles podem compartilhar vértices, ter tamanhos diferentes e deixar vértices fora de ambos.

### Exemplo: um vértice com vários vizinhos

```text
    B
    |
C — A — D
    |
    E
   / \
  F   G
```

`A` tem quatro vizinhos: `B`, `C`, `D` e `E`. `E` tem três: `A`, `F` e `G`.

Uma resposta válida é:

```text
D1 = {A, F, G}
D2 = {B, C, D, E}
```

Em `D1`, `A` cobre `A`, `B`, `C`, `D` e `E`; `F` e `G` cobrem a si mesmos. Em `D2`, os escolhidos cobrem a si mesmos, algum vizinho cobre `A`, e `E` cobre `F` e `G`.

### Não precisamos escolher todos os vértices

Neste caminho:

```text
A — B — C — D — E
```

Os conjuntos `D1 = {A, D}` e `D2 = {B, E}` são dominantes. O vértice `C` não está em nenhuma lista: ele é coberto por `D` no primeiro conjunto e por `B` no segundo.

### Vértices isolados e laços

Um vértice sem vizinhos precisa pertencer aos dois conjuntos, pois ninguém mais pode cobri-lo. A implementação também trata corretamente um vértice cuja única aresta é um laço para ele mesmo: o laço não fornece outro vértice que possa cobri-lo.

## 2. A fórmula corrigida do score

O professor informou a seguinte fórmula, que devemos **minimizar**:

```text
score(D1, D2) = (max(|D1|, |D2|) + |D1 ∩ D2|) / |V|
```

Em Python:

```python
(max(len(D1), len(D2)) + len(set(D1) & set(D2))) / len(g)
```

| Termo | O que representa |
| --- | --- |
| `max(len(D1), len(D2))` | Tamanho do maior conjunto |
| `len(set(D1) & set(D2))` | Quantos vértices aparecem nos dois conjuntos |
| `len(g)` | Número de vértices do grafo |

Não existem custos individuais diferentes para os vértices neste modelo. O custo vem das quantidades de elementos escolhidos.

Para um mesmo grafo, o denominador é constante. Por isso, o algoritmo compara o **numerador**:

```text
F(D1, D2) = max(|D1|, |D2|) + |D1 ∩ D2|
```

Uma melhora de uma unidade em `F` reduz o score em `1 / |V|`. Em um grafo de 50 vértices, isso equivale a `0,02`; em um de 500, a `0,002`.

O score não é uma porcentagem: por exemplo, escolher todos os vértices nos dois conjuntos produz score `2`. Nos testes, convencionamos score `0` para o grafo vazio, evitando divisão por zero. Essa convenção local não é uma regra de avaliação obtida do Codabench.

### Por que minimizar somente a interseção não basta

Considere uma estrela:

```text
    B
    |
C — A — D
    |
    E
```

| Resposta | Maior conjunto | Interseção | Score |
| --- | ---: | ---: | ---: |
| `D1 = {A}`, `D2 = {B, C, D, E}` | 4 | 0 | `4 / 5 = 0,8` |
| `D1 = {A}`, `D2 = {A}` | 1 | 1 | `2 / 5 = 0,4` |

As duas respostas são válidas. A segunda compartilha um vértice, mas obtém score menor porque os dois conjuntos ficam muito pequenos.

**O alvo é equilibrar o tamanho do maior conjunto com a penalidade da interseção.** A construção por BFS resolve a minimização da interseção, mas não garante o ótimo dessa fórmula corrigida.

### Desempates internos

A função `_quality` compara as respostas pela tupla:

```text
(F, |D1| + |D2|, |D1 ∩ D2|)
```

Primeiro vem o score verdadeiro, por meio de `F`. Somente quando ele empata tentamos reduzir o total de elementos e, depois, a interseção. Esses dois critérios secundários não alteram a fórmula do professor.

## 3. Regras e formato da submissão

As regras consultadas pedem:

- `algorithm.py` com uma função `dominant(g)`;
- retorno de duas listas de vértices do próprio grafo;
- execução em menos de 20 segundos por grafo;
- algoritmo determinístico, permitindo aleatoriedade apenas em desempates;
- envio do arquivo Python compactado em ZIP;
- consideração da última submissão na competição.

A estrutura enviada é:

```text
submission.zip
└── algorithm.py
```

O código de produção usa somente a biblioteca padrão do Python. O objeto NetworkX é fornecido pela plataforma. Não é necessário colocar NetworkX, testes, relatórios ou outros módulos dentro do ZIP.

A implementação não modifica o grafo recebido e não devolve vértices repetidos na mesma lista. Ela não usa sorteio. O resultado é determinístico para a mesma entrada, incluindo sua ordem de iteração dos vértices e vizinhos; não se promete a mesma escolha de vértices para toda reordenação de um grafo equivalente.

## 4. As quatro estratégias da V1

A implementação está em [solution/algorithm.py](solution/algorithm.py).

### 4.1. BFS por paridade: `bfs_dominants(g)`

Percorremos cada componente conexa por busca em largura, ou BFS. A raiz vai para `D1`; cada vértice descoberto vai para o conjunto oposto ao de seu pai na busca.

```text
Profundidade par   → D1
Profundidade ímpar → D2
Vértice isolado    → ambos
```

Na árvore construída pela busca, todo vértice de uma componente com pelo menos dois vértices tem um vizinho da outra classe: seu pai ou um filho. Assim, cada classe domina a outra, além de cobrir seus próprios vértices.

Essa separação se aplica à **árvore da busca**. O grafo original pode conter ciclos ímpares e arestas entre vértices da mesma classe; ele não precisa ser bipartido.

A interseção contém exatamente os vértices sem outros vizinhos. Isso é ótimo para a interseção, pois eles precisam aparecer em qualquer dominante. Os tamanhos dos conjuntos, porém, podem ficar ruins para o score corrigido.

A travessia BFS em si custa `O(|V| + |E|)`. O programa também prepara representações auxiliares, descritas adiante.

### 4.2. Guloso duplicado: `duplicated_greedy(g)`

Construímos um conjunto dominante pequeno `D` e devolvemos `(D, D)`.

```text
D = vazio
R = todos os vértices ainda descobertos

Enquanto R não estiver vazio:
    escolher v que maximiza |N[v] ∩ R|
    adicionar v a D
    retirar de R os vértices de N[v]

Remover vértices redundantes de D
Devolver D nas duas listas
```

A escolha considera **cobertura nova**, não apenas o grau original do vértice. Um vértice com muitos vizinhos já cobertos pode ser menos útil que outro de grau menor.

Como os conjuntos são iguais, o score dessa estratégia é:

```text
2 × |D| / |V|
```

A estratégia funciona bem quando há um dominante muito pequeno, como o centro de uma estrela. Ela também fornece uma candidata válida para comparação com as demais.

A ideia gulosa está ligada à cobertura de conjuntos, ou *set cover*, estudada no exercício 3 do TD1. A garantia de aproximação para um dominante pequeno não se transfere automaticamente para o score conjunto deste concurso.

### 4.3. Guloso conjunto: `joint_greedy(g)`

Construímos os dois conjuntos simultaneamente. Em cada passo, consideramos adicionar um vértice a um deles, avaliando a cobertura nova e o aumento do numerador.

Se `a` é o tamanho do conjunto que vai receber `v` e `b` o tamanho do outro, o custo marginal é:

```text
ΔF = max(a + 1, b) - max(a, b) + indicador(v pertence ao outro conjunto)
```

| Situação antes da adição | Aumento de `F` |
| --- | ---: |
| O conjunto ainda é menor e `v` não é compartilhado | 0 |
| O conjunto ainda é menor e `v` é compartilhado | 1 |
| O conjunto já tem tamanho igual ou maior e `v` não é compartilhado | 1 |
| O conjunto já tem tamanho igual ou maior e `v` é compartilhado | 2 |

A V1 prioriza adições de custo zero que cubram algo novo. Entre adições de custo positivo, prioriza a razão `cobertura nova / ΔF`, com desempates fixos.

Quando os dois conjuntos já dominam o grafo, removemos redundâncias. Essa estratégia já leva em conta a fórmula completa do score, mas continua sendo uma heurística gulosa: uma boa escolha imediata pode impedir uma combinação melhor mais tarde.

### 4.4. Busca local: `local_search(g, pair=None)`

A busca local melhora uma resposta válida. Sem uma resposta inicial fornecida, ela considera as três construções anteriores, compartilhando um orçamento fixo de trabalho entre os pontos de partida distintos.

As operações são:

1. Remover vértices redundantes.
2. Escolher um vértice ainda ausente de um dos conjuntos.
3. Adicioná-lo temporariamente.
4. Remover vértices antigos que se tornaram redundantes.
5. Aceitar a troca se a tupla `_quality` melhorar.

Uma adição pode permitir remover vários vértices. Por isso, essa operação também pode reduzir o tamanho de um conjunto.

Para entender quais trocas são promissoras, usamos os **vértices privados** de um escolhido `v`: os vértices que somente ele cobre dentro daquele conjunto. Um substituto que cubra esses vértices pode tornar `v` dispensável.

Durante a remoção de redundâncias, mantemos contadores de cobertura. Só retiramos `v` quando todos os vértices de `N[v]` têm outra cobertura disponível. Isso preserva a validade. Priorizamos a remoção de vértices compartilhados, pois ela também pode reduzir a interseção.

A busca V1 só aceita melhorias da tupla: não aceita piorar o score nem uma troca completamente neutra. Por isso, pode parar em um **ótimo local**, mesmo que uma sequência maior de alterações leve a uma resposta melhor.

### Seleção final da V1

`algorithm.dominant(g)` executa as quatro estratégias e escolhe a melhor pela tupla `_quality`. A função `all_strategies(g)` expõe as quatro respostas para estudo e comparação.

## 5. A busca ampliada da V2

A implementação está em [solution/improved_search.py](solution/improved_search.py). Sua função pública também se chama `dominant(g)`, mas pertence a outro módulo.

A V2 começa guardando a melhor resposta V1. A exploração pode passar por outras respostas, porém o programa devolve a melhor resposta válida que guardou. Portanto, para o mesmo grafo, **o score devolvido pela V2 é menor ou igual ao da seleção V1**.

### 5.1. Construções com vários pontos de partida

A V2 tenta até 64 construções adicionais usando `_repair` a partir de dois conjuntos vazios. Ela varia de forma determinística:

- a ordem usada nos desempates;
- o peso auxiliar de compartilhar um vértice;
- o tratamento de adições que não aumentam o maior conjunto.

Os pesos auxiliares explorados para compartilhamento são `0,5`, `1`, `2` e `4`. Para as adições de custo zero, as variantes usam prioridade especial ou denominadores auxiliares positivos na razão entre ganho e custo.

Esses custos servem **apenas para construir candidatas diferentes**. A decisão de qual resposta é melhor sempre usa a fórmula verdadeira do concurso.

Guardamos as candidatas distintas e aplicamos a busca local V1 a até dez pontos de partida promissores.

### 5.2. Remover e reconstruir

Depois, a V2 executa até 256 perturbações:

1. Escolher deterministicamente uma região do grafo.
2. Retirar de um a três vértices escolhidos de cada conjunto, quando disponíveis.
3. Reconstruir a cobertura dos dois conjuntos com `_repair`.
4. Remover redundâncias e avaliar a resposta válida.

A resposta danificada do passo 2 pode deixar vértices descobertos. Ela é apenas um estado interno de trabalho: **não é devolvida ao Codabench**.

Uma reconstrução pode mudar vários vértices ao mesmo tempo. A exploração também pode aceitar respostas novas com o mesmo numerador e, em algumas iterações, com numerador até uma unidade maior que o melhor guardado. Isso permite sair de certas configurações em que a busca local V1 pararia.

Há um conjunto de estados visitados, retornos periódicos à melhor resposta e refinamentos adicionais com a busca local. A melhor resposta fica separada da resposta usada para explorar: aceitar temporariamente uma pior não piora a saída final.

### 5.3. Reconstrução limitada por ramificações

A cada oito perturbações, `_bounded_repair` tenta reparar a resposta danificada procurando um numerador pelo menos uma unidade menor que o melhor atual.

O procedimento escolhe um vértice ainda descoberto com poucos vizinhos e tenta as opções que poderiam cobri-lo. Cada opção cria uma ramificação. As escolhas precisam restaurar a dominação dos dois conjuntos.

Para descartar ramos inviáveis, usamos um limite inferior simples. Se um conjunto ainda tem vértices descobertos, ele precisa receber pelo menos mais um escolhido:

```text
limite = max(a + indicador(D1 incompleto),
             b + indicador(D2 incompleto)) + interseção atual
```

Se esse limite já excede o numerador pretendido, não vale continuar naquele ramo. Também limitamos cada chamada a 1.200 estados distintos.

Essa é uma busca **limitada a uma vizinhança da resposta atual**. Ela mantém os vértices que não foram retirados e tem orçamento finito. Esgotar o orçamento ou não encontrar uma melhora não prova que o ótimo global foi atingido.

### 5.4. Equilíbrio entre componentes desconectadas

Em uma componente conexa inteira, podemos trocar os papéis de `D1` e `D2`. A dominação continua válida e a quantidade de vértices compartilhados não muda.

Por exemplo, duas componentes com tamanhos locais `(1, 3)` e `(1, 3)` resultam em tamanhos globais `(2, 6)`. Inverter as cores na segunda componente produz `(4, 4)`, reduzindo o maior conjunto sem alterar os vértices utilizados.

A V2 escolhe essas inversões por programação dinâmica. Se `d_i` é a diferença entre os tamanhos na componente `i` e `Δ` a diferença global, inverter um subconjunto de componentes muda a diferença para:

```text
Δ - 2 × soma(d_i das componentes invertidas)
```

Como o total de elementos e a interseção permanecem constantes, minimizar o valor absoluto dessa diferença minimiza o maior conjunto. A programação dinâmica considera as somas alcançáveis e escolhe a melhor orientação.

Esse equilíbrio é ótimo **para aquelas escolhas de vértices já fixadas**. Ele não resolve a escolha global dos vértices.

### 5.5. Limites operacionais

| Parâmetro | Valor | Função |
| --- | ---: | --- |
| `LOCAL_WORK_LIMIT` | 2.000.000 | Orçamento de trabalho compartilhado pelas buscas locais da V1 |
| `LOCAL_PASS_LIMIT` | 24 | Máximo de passagens de cada busca local |
| `MULTISTART_VARIANTS` | 64 | Construções adicionais da V2 |
| `LOCAL_STARTS` | 10 | Máximo de pontos de partida refinados na V2 |
| `LOCAL_START_WORK` | 750.000 | Orçamento de cada refinamento local da V2 |
| `REPAIR_ROUNDS` | 256 | Perturbações da V2 |
| `REPAIR_BRANCH_LIMIT` | 1.200 | Estados por chamada de reconstrução com ramificações |

Para grafos com até 12 vértices, a V2 reduz a exploração a seis construções e 12 perturbações. Acima de 1.000 vértices, ela usa a resposta V1 com equilíbrio de componentes, sem a exploração adicional. Esses limiares são escolhas de implementação.

Os orçamentos são limites fixos de trabalho, passagens ou estados, **não cronômetros nem garantias universais de tempo**. A submissão não consulta o relógio para escolher sua resposta. O limite externo continua sendo de 20 segundos por grafo no Codabench.

## 6. Representação e eficiência

### Índices internos

`_Graph` mapeia os rótulos originais para índices `0, 1, ..., n - 1`. Isso permite trabalhar com índices inteiros mesmo que os rótulos sejam strings, tuplas ou tipos misturados. No retorno, os índices são convertidos novamente para os rótulos originais.

### Conjuntos de bits

Um inteiro representa um conjunto: o bit de posição `i` informa se o vértice `i` está presente.

```text
1 << i           → conjunto que contém apenas o vértice i
mask_a | mask_b  → união
mask_a & mask_b  → interseção
full & ~mask_a   → vértices fora de mask_a
```

As vizinhanças fechadas também são armazenadas assim. Portanto, a cobertura nova de um candidato pode ser calculada por:

```text
ganho(v) = quantidade de bits 1 em (closed[v] & uncovered)
```

A função `_count` usa `bin(mask).count("1")`, compatível com o Python 3.7, em vez de depender de `int.bit_count()`.

### Filas de prioridade

Os gulosos usam filas de prioridade para encontrar candidatos com grande ganho. Conforme a cobertura avança, os ganhos antigos só podem diminuir. Assim, o programa pode manter estimativas antigas como limites superiores e recalcular os ganhos sob demanda antes de escolher o candidato.

Há filas separadas para candidatos compartilhados e não compartilhados, pois eles têm custos diferentes.

### Complexidade e tempo

A BFS tem travessia linear, mas o programa completo também usa máscaras, filas de prioridade, múltiplas construções e buscas limitadas. O custo das operações com inteiros depende do número de bits; a V2 inteira não tem a complexidade linear da BFS.

Os limites de exploração controlam o trabalho adicional. O tempo precisa ser medido nos tamanhos relevantes, e o servidor do concurso pode ter desempenho diferente da máquina local.

## 7. Organização dos arquivos

| Caminho | Conteúdo |
| --- | --- |
| [solution/algorithm.py](solution/algorithm.py) | Quatro estratégias V1, score e funções auxiliares |
| [solution/improved_search.py](solution/improved_search.py) | Busca ampliada V2 |
| [build_submissions.py](build_submissions.py) | Empacotamento das estratégias V1 |
| [build_improved_submission.py](build_improved_submission.py) | Empacotamento da V2 em um único arquivo |
| [compare.py](compare.py) | Comparação das quatro estratégias V1 em grafos sintéticos |
| [evaluate_improved.py](evaluate_improved.py) | Comparação V1/V2 em três famílias de grafos |
| [tests/test_algorithm.py](tests/test_algorithm.py) | Testes da V1 e da fórmula corrigida |
| [tests/test_improved_search.py](tests/test_improved_search.py) | Testes da V2 e das reconstruções |
| [submissions/](submissions/) | ZIPs individuais e V2 |
| [submissions/archive_v1/](submissions/archive_v1/) | ZIPs V1 preservados |
| [results/](results/) | Comparações e referências de notas recebidas |
| [results/improved/](results/improved/) | Benchmark e validação da V2 |
| [solution.zip](solution.zip) | Modelo original fornecido pelo concurso |
| [IMPROVEMENTS.md](IMPROVEMENTS.md) | Explicação complementar da V2 |

### Qual função `dominant` usar?

| Entrada | Versão |
| --- | --- |
| `algorithm.dominant(g)` | Seleção das quatro estratégias V1 |
| `improved_search.dominant(g)` | V2, incluindo a referência V1 |
| `dominant(g)` dentro de `improved_search_v2.zip` | V2 autônoma para o Codabench |

O empacotador V2 junta as funções auxiliares da V1 com o refinamento V2, removendo a necessidade de importar um arquivo local chamado `algorithm`. O ZIP final contém apenas um arquivo.

## 8. Executar e estudar localmente

Os comandos desta seção devem ser executados **dentro da pasta `projet1`**. Use um Python local recente para os scripts de empacotamento. A sintaxe do arquivo submetido é verificada para Python 3.7; a validação local registrada usou Python 3.14.4 e NetworkX 2.6.3.

### Preparar um ambiente

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install networkx==2.6.3
```

Essa dependência é necessária para criar grafos e executar testes localmente. A lógica dos algoritmos submetidos usa apenas a biblioteca padrão.

### Comparar as respostas de um exemplo

```sh
PYTHONPATH=solution python3 - <<'PY'
import networkx as nx
from algorithm import all_strategies, score
from improved_search import dominant as dominant_v2

g = nx.Graph([
    ("A", "B"), ("A", "C"), ("A", "D"), ("A", "E"),
    ("E", "F"), ("E", "G"),
])

respostas = all_strategies(g)
respostas["v2"] = dominant_v2(g)

for nome, (d1, d2) in respostas.items():
    print(nome, "D1 =", d1, "D2 =", d2, "score =", score(g, (d1, d2)))
PY
```

`all_strategies(g)` devolve um dicionário com `bfs`, `duplicated_greedy`, `joint_greedy` e `local_search`. `local_search(g, pair)` permite estudar a melhoria de uma candidata válida escolhida por você.

Respostas diferentes podem ter o mesmo score, como acontece nesse exemplo. Para observar diferenças entre as estratégias, experimente substituir a construção de `g` por `g = nx.star_graph(4)` ou `g = nx.complete_graph(5)`.

A função `score(g, pair)` apenas calcula a métrica: ela não verifica se os conjuntos são dominantes. Não se deve comparar como solução uma resposta que deixa vértices descobertos.

### Rodar os testes

```sh
python3 -m unittest discover -s tests -v
```

### Reproduzir a comparação V1

```sh
python3 compare.py --seeds 3
```

O script usa sementes `0`, `1` e `2` e grava `results/comparison.csv` e `results/summary.json`.

### Reproduzir a comparação V1/V2

```sh
python3 evaluate_improved.py --seeds 23 47 89
```

Esse script grava `results/improved/comparison.csv` e `results/improved/summary.json`. Esses comandos executam novamente os experimentos e atualizam os respectivos resultados locais. O resumo específico da validação do ZIP final foi produzido separadamente.

## 9. Gerar os arquivos para submissão

### Preparar a V2

Dentro de `projet1`:

```sh
python3 build_improved_submission.py
```

O script gera ou atualiza:

```text
submissions/improved_search_v2.zip
submission.zip
results/improved/submission_manifest.json
```

Os dois ZIPs têm os mesmos bytes. O manifesto registra, entre outras informações, o SHA-256 do arquivo. Os ZIPs individuais V1 permanecem preservados.

Para conferir a estrutura:

```sh
python3 -m zipfile -l submissions/improved_search_v2.zip
```

A listagem deve mostrar somente `algorithm.py` na raiz.

### Preparar novamente as estratégias V1

```sh
python3 build_submissions.py
```

| ZIP gerado | Estratégia executada pela entrada `dominant(g)` |
| --- | --- |
| `submissions/bfs.zip` | BFS por paridade |
| `submissions/duplicated_greedy.zip` | Guloso duplicado |
| `submissions/joint_greedy.zip` | Guloso conjunto |
| `submissions/local_search.zip` | Busca local a partir das três construções |
| `submissions/best_of_all.zip` | Melhor entre as quatro estratégias V1 |

Esse script também atualiza `submission.zip` com a **V1**. Para deixar o ZIP principal novamente na **V2**, execute depois:

```sh
python3 build_improved_submission.py
```

As cópias preservadas das quatro estratégias e do combinado V1 estão em [submissions/archive_v1/](submissions/archive_v1/).

Depois de alterar os arquivos-fonte, regenere o ZIP da versão que deseja enviar. O Codabench executa o código compactado, não os arquivos Python que ficaram na sua pasta local.

## 10. Resultados oficiais recebidos

Os dados abaixo vieram das linhas do placar e da captura de tela fornecidas pelo usuário. Eles estão registrados em [results/official_v1_scores.json](results/official_v1_scores.json).

| Estratégia enviada | ID | Score total oficial informado |
| --- | ---: | ---: |
| BFS inicial, enviada na época como `submission.zip` | 1032586 | 7,89 |
| Guloso duplicado | 1032671 | 5,91 |
| Guloso conjunto | 1032670 | 3,09 |
| Busca local V1 | 1032669 | **2,96** |
| V2 | Ainda não registrado | Ainda não registrado |

A melhor nota do leaderboard informada foi **2,62**. A diferença para a melhor submissão V1 é `0,34`. Os resultados sintéticos seguintes ajudam a comparar mudanças no algoritmo, mas não permitem deduzir a nota oficial da V2.

## 11. Resultados locais e como interpretá-los

### Comparação das quatro estratégias V1

O primeiro experimento usou 39 grafos sintéticos: três sementes e as 13 combinações de número de vértices e arestas exibidas no placar.

| Estratégia | Soma média dos scores por série de 13 grafos |
| --- | ---: |
| BFS | 8,598667 |
| Guloso duplicado | 6,301333 |
| Guloso conjunto | 4,156000 |
| Busca local | 4,081333 |

Dados: [results/summary.json](results/summary.json) e [results/comparison.csv](results/comparison.csv).

### Comparação V1/V2 com novas sementes

O segundo experimento usou sementes `23`, `47` e `89`, com três famílias:

- **G(n,m):** grafo aleatório com `n` vértices e `m` arestas, podendo ser desconectado.
- **Árvore + arestas:** árvore aleatória, completada com arestas até atingir `m`.
- **Ciclo + arestas:** ciclo inicial, completado com arestas até atingir `m`.

Cada família tem três séries de 13 grafos: são **117 grafos no total**. As combinações usadas foram:

```text
(50, 50),   (50, 250),   (50, 500),   (50, 1000)
(100, 100), (100, 250),  (100, 500),  (100, 1000)
(250, 250), (250, 500),  (250, 1000)
(500, 500), (500, 1000)
```

| Família | V1: soma média por série | V2: soma média por série |
| --- | ---: | ---: |
| G(n,m) | 3,972667 | **3,808000** |
| Árvore + arestas | 3,255333 | **3,058000** |
| Ciclo + arestas | 2,808000 | **2,720000** |

A V2 melhorou **71 grafos**, empatou em **46** e não piorou nenhum. O maior tempo medido foi aproximadamente **1,08 segundo por grafo**, importando diretamente o ZIP final.

Esses são grafos sintéticos, não as instâncias oficiais. As famílias ligadas por uma árvore ou um ciclo foram incluídas para avaliar também entradas conectadas, não porque conheçamos o gerador do concurso. Os totais do primeiro e do segundo experimento usam entradas diferentes; a comparação V1/V2 deve ser feita dentro da mesma linha da segunda tabela.

Dados e descrição da execução: [results/improved/summary.json](results/improved/summary.json), [results/improved/comparison.csv](results/improved/comparison.csv) e [results/improved/analysis.md](results/improved/analysis.md).

## 12. Validação e garantias

A execução registrada passou em **14 testes**. Eles verificam:

- validade dos dois dominantes e ausência de vértices repetidos;
- preservação do grafo de entrada;
- determinismo;
- fórmula corrigida em exemplos em que compartilhar compensa ou prejudica;
- seleção e preservação das melhores candidatas;
- os 1.253 grafos simples do atlas NetworkX com até sete vértices;
- grafos vazios, isolados, estrelas, caminhos, ciclos, cliques, laços e rótulos mistos;
- exemplos maiores da implementação de base;
- equilíbrio de componentes, comparado com enumeração de todas as orientações em um caso de teste.

A reconstrução por ramificações também foi comparada com o ótimo obtido por enumeração exaustiva em todos os grafos simples com até cinco vértices. Nesses testes da rotina, o limite de estados é aumentado para 20.000. Isso verifica seu funcionamento em casos pequenos; não transforma o limite de 1.200 estados da submissão em uma garantia de ótimo geral.

O ZIP V2 foi importado diretamente e conferido em oito casos adicionais e nos 117 grafos do benchmark. A sintaxe foi verificada para Python 3.7, mas as execuções locais registradas usaram Python 3.14.4 e NetworkX 2.6.3. Elas não substituem uma execução no ambiente do Codabench.

As garantias do algoritmo são:

1. As duas listas devolvidas representam conjuntos dominantes válidos.
2. Os rótulos retornados pertencem ao grafo original, que é preservado.
3. A V2 guarda uma resposta com score menor ou igual ao da seleção V1 para o mesmo grafo.
4. A BFS minimiza a interseção; o equilíbrio de componentes minimiza o desequilíbrio para escolhas fixas.

Não há certificado de ótimo global para o score corrigido. O valor `2,62` do placar é uma referência de desempenho, não uma prova desse ótimo. Os tempos locais também não garantem o limite de 20 segundos em qualquer tamanho de grafo ou servidor.

Registros: [results/improved/submission_validation.json](results/improved/submission_validation.json) e [results/improved/submission_manifest.json](results/improved/submission_manifest.json).

## 13. Ordem sugerida para entender o código

Para estudar por etapas:

1. Refaça os exemplos de cobertura e de score das seções 1 e 2.
2. Leia `score`, `_quality` e `_bfs` em `solution/algorithm.py`.
3. Leia `_duplicated_greedy` e relacione o ganho com a vizinhança fechada e o TD1.
4. Leia `_joint_greedy` e confira o custo marginal com a tabela da seção 4.3.
5. Entenda `_coverage_counts`, `_prune` e os vértices privados antes de ler `_local_search`.
6. Em `solution/improved_search.py`, leia `_repair`, `_destroy` e `_improve`.
7. Por último, estude `_bounded_repair` e `_balance_components`.

Os percursos de grafos sustentam a BFS; a relação entre dominante e cobertura de conjuntos sustenta o guloso. O TD1, especialmente os exercícios 2 e 3, é a referência mais direta para essa parte. As explorações da V2 são extensões para melhorar a qualidade prática das respostas no critério específico do projeto.
