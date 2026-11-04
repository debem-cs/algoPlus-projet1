# Por que a V2 pode melhorar a nota

A melhor submissao V1 informada foi `local_search.zip`, com score 2.96.
O melhor score do leaderboard informado pelo usuario foi 2.62. Os arquivos
`results/official_v1_scores.json` registram esses dados; a V2 ainda precisa
ser executada no Codabench para sabermos sua nota oficial.

## Limite da busca anterior

A V1 usa tres construcoes iniciais e trocas que melhoram imediatamente a
qualidade. Quando uma melhora exige mudar varios vertices ou atravessar
uma resposta intermediaria pior, ela pode parar num otimo local.

## Pipeline da V2

1. Guardar a melhor resposta das quatro estrategias V1 como referencia.
2. Construir ate 64 respostas adicionais com ordens de desempate e custos
   auxiliares diferentes. Cada resposta continua sendo avaliada pela
   formula verdadeira do professor.
3. Melhorar ate dez pontos de partida distintos com a busca local V1.
4. Executar ate 256 perturbacoes: retirar de um a tres vertices de cada
   conjunto, reparar a cobertura e remover redundancias. A exploracao
   pode aceitar temporariamente um numerador ate uma unidade pior; a
   melhor resposta encontrada fica guardada separadamente.
5. A cada oito perturbacoes, tentar uma reconstrucao com ramificacoes,
   limitada a 1200 estados. Ela procura uma melhora de uma unidade no
   numerador, escolhendo primeiro um vertice descoberto com poucos vizinhos.
6. Equilibrar as orientacoes das componentes desconectadas. Trocar D1 e D2
   numa componente preserva dominacao e intersecao; uma programacao dinamica
   escolhe as trocas que equilibram melhor os tamanhos para aquelas escolhas.

Para grafos pequenos, ha menos construcoes e perturbacoes. Acima de 1000
vertices, a V2 usa a referencia V1 com equilibrio de componentes. Os limites
sao operacionais; nao representam propriedades dos dados oficiais.

As escolhas sao deterministicas e nao usam sorteio nem relogio para decidir
o resultado. O grafo recebido nao e modificado. A implementacao submetida
usa apenas a biblioteca padrao e sintaxe compativel com Python 3.7.

## O que esta garantido

- Os dois conjuntos devolvidos dominam o grafo inteiro.
- O score da V2 para um mesmo grafo e menor ou igual ao da melhor resposta V1.
- O equilibrio de componentes e otimo apenas entre as orientacoes das
  escolhas de vertices ja fixadas. Isso nao prova o otimo global do projeto.
- O limite de ramificacoes torna a reconstrucao uma busca parcial. Esgotar
  esse limite nao prova que uma resposta melhor nao existe.

Os tempos locais devem ser confrontados com a execucao do Codabench; o
servidor e a versao de Python podem ter velocidades diferentes.

## Validacao

As 14 verificacoes incluem os 1253 grafos do atlas com ate sete vertices,
regressoes, rotulos mistos, lacos, determinismo e preservacao da resposta V1.
A reconstrucao por ramificacoes foi confrontada com enumeracao exaustiva
do otimo em todos os grafos simples com ate cinco vertices.

O benchmark usa tres sementes novas (23, 47 e 89), treze tamanhos e tres
familias: grafos G(n,m), arvores aleatorias com arestas adicionais e ciclos
com arestas adicionais. Sao 117 grafos sinteticos, distintos dos grafos
oficiais. `results/improved/summary.json` e `comparison.csv` contem os
resultados; `submission_validation.json` registra a verificacao do ZIP final.
