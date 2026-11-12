# Roteiro de apresentação (6–8 minutos)

> 10 slides. Fala sugerida em cada um + números para citar de cabeça.
> Todos os números estão em `resultados/tabelas.md`.

---

## Slide 1 — Título (15 s)

**Fala:** "O trabalho resolve um problema de entrega de pacotes usando busca
heurística: A\*, busca gulosa e algoritmo genético. A pergunta central é: quanto de
qualidade vale quanto de esforço computacional?"

---

## Slide 2 — O problema (40 s)

**Fala:** "Uma cidade em grade 25 por 25. Células escuras são prédios; cada célula
livre tem custo de 1 a 5, que representa congestionamento. O entregador sai do
depósito e precisa entregar 10 pacotes, sem precisar voltar."

**Mostrar:** Figura 1 (`mapa_parte1.png`), apontando as zonas vermelhas.

---

## Slide 3 — Modelagem (50 s)

**Fala:** "São dois níveis. Primeiro, caminho mínimo entre dois pontos — um estado é
uma célula. Segundo, a ordem das entregas — um estado é `(ponto atual, conjunto de
entregas restantes)`. Para 10 entregas são 3.628.800 ordens possíveis, então isso é
um problema combinatório de verdade."

**Escrever no slide:** Estado · Ação · Custo · Teste de objetivo.

---

## Slide 4 — A\* (50 s)

**Fala:** "O A\* ordena por `f = g + h`. A heurística da grade é a distância de
Manhattan vezes o custo mínimo de uma célula — ela nunca superestima o custo real,
então o A\* é ótimo. Na roteirização, a heurística é o peso da árvore geradora mínima
das entregas que faltam, que também é um limite inferior."

**Ponto forte:** "Isso derruba o espaço de 6.144 estados para 116 expansões."

---

## Slide 5 — Busca gulosa (35 s)

**Fala:** "A busca gulosa usa só `h`: vai sempre para o que parece mais perto.
É rapidíssima, mas não tem garantia nenhuma de ótimo. Na grade ela entra na zona de
congestionamento só porque é geometricamente mais curta."

**Mostrar:** o caminho rosa tracejado atravessando o vermelho na Figura 1.

---

## Slide 6 — Algoritmo genético (50 s)

**Fala:** "Para a ordem das entregas, o indivíduo é uma permutação. A aptidão é
1 sobre o custo. Seleção por torneio, crossover OX — que preserva a ordem relativa
das entregas —, mutação por troca/inversão, elitismo de 2. População 80, até 300
gerações, 20 execuções independentes."

**Por que OX:** "O que importa é a ordem de visita, não a posição absoluta do gene."

---

## Slide 7 — Resultados da Parte 1 (40 s)

**Fala:** "Em 8 cidades: o A\* acertou o ótimo nas 8, confirmado pelo Dijkstra.
O guloso expandiu só 27,6 % dos nós do A\* — mas o custo médio ficou 57 % maior,
chegando a 83 %."

| A\* | Guloso |
|---|---|
| ótimo 8/8 | subótimo 8/8 |
| 281 nós | 63 nós (27,6 %) |
| — | +57,1 % de custo |

---

## Slide 8 — Resultados da Parte 2 (50 s)

**Fala:** "Na instância principal: ótimo 137. O guloso fez 157, 14,6 % pior. O AG
genético acertou 137 na melhor execução e ficou em 139,45 na média — 1,8 % acima do
ótimo. O A\* precisou de 116 expansões e 7,6 ms; a força bruta, que é a verdade,
gastou 3,3 segundos."

| Algoritmo | Custo | Gap | Tempo |
|---|---:|---:|---:|
| A\* | 137 | 0 % | 7,6 ms |
| Guloso | 157 | +14,6 % | 0,02 ms |
| AG (média) | 139,45 | +1,8 % | 83 ms |
| Força bruta | 137 | 0 % | 3.308 ms |

**Nas 5 cidades:** AG com gap médio de 0,68 % e ótimo em 80 de 100 execuções.

---

## Slide 9 — Conclusão (30 s)

**Fala:** "A\* é o único que garante o ótimo e, com heurística boa, é barato. O guloso
é o mais rápido e o menos confiável. O AG genético é o melhor custo-benefício quando
o espaço cresce: quase ótimo, com tempo controlado e escalando melhor que o A\* sobre
subconjuntos."

---

## Slide 10 — Perguntas prováveis (não mostrar, ter na ponta da língua)

**"Por que o A\* é ótimo?"**
Porque `h` é admissível (nunca superestima) e consistente; assim, quando um estado é
retirado da fronteira, seu custo `g` já é o menor possível.

**"O guloso é completo?"**
Em grafo finito com conjunto de fechados ele termina, mas não garante ótimo — e pode
ser exponencial no pior caso.

**"Por que usar AGM como heurística?"**
Toda rota que visita um conjunto de pontos contém uma árvore geradora desse conjunto;
logo o peso da AGM é um limite inferior para o custo da rota. É admissível.

**"Por que o AG não acha o ótimo sempre?"**
É estocástico: depende da população inicial e das taxas de crossover/mutação. Aumentar
população/gerações ou usar busca local (2-opt) melhora, mas não garante.

**"Como vocês sabem que o resultado está certo?"**
Comparando com Dijkstra (Parte 1) e força bruta sobre todas as permutações (Parte 2),
além de asserções no código que quebram a execução se os custos divergirem.

**"O que mudariam?"**
Trânsito dinâmico, diagonais, vários veículos (VRP), e 2-opt/memético no AG.
