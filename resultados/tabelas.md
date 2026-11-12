## Parte 1 - caminho na grade

| Inst. | Otimo | Custo A* | Custo guloso | Nos A* | Nos guloso | Guloso/A* (%) | Custo extra (%) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 60 | 60 | 74 | 212 | 59 | 27.8 | 23.3 |
| 7 | 62 | 62 | 105 | 473 | 75 | 15.9 | 69.4 |
| 11 | 60 | 60 | 70 | 400 | 64 | 16.0 | 16.7 |
| 19 | 58 | 58 | 97 | 441 | 59 | 13.4 | 67.2 |
| 23 | 48 | 48 | 88 | 140 | 56 | 40.0 | 83.3 |
| 42 | 53 | 53 | 81 | 268 | 55 | 20.5 | 52.8 |
| 99 | 59 | 59 | 102 | 150 | 58 | 38.7 | 72.9 |
| 123 | 49 | 49 | 84 | 165 | 80 | 48.5 | 71.4 |

Media de nos expandidos: **A\* 281.1** vs **guloso 63.2** (27.6% do A*). Custo extra medio do guloso: **57.13%** (maximo 83.33%).

## Parte 2 - instancia detalhada (semente 7, 10 entregas)

| Algoritmo | Custo da rota | Gap vs otimo (%) | Expansoes | Tempo (ms) |
|---|---:|---:|---:|---:|
| A* (otimo) | 137 | 0.00 | 116 | 4.85 |
| Guloso (vizinho mais proximo) | 157 | 14.6 | - | 0.02 |
| AG (melhor de 20) | 137 | 0.0 | - | 79.5 |
| AG (media de 20) | 139.45 | 1.8 | - | 79.5 |
| AG (pior de 20) | 144 | 5.1 | - | 79.5 |
| Forca bruta (verdade) | 137 | 0.00 | 10 entregas | - |

## Parte 2 - resumo em 5 instancias

| Inst. | Otimo | Guloso | Gap guloso (%) | AG melhor | AG media | Gap AG medio (%) | Otimos do AG |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 7 | 137 | 157 | 14.6 | 137 | 139.4 | 1.8 | 7/20 |
| 21 | 178 | 198 | 11.2 | 178 | 178.3 | 0.2 | 19/20 |
| 34 | 140 | 177 | 26.4 | 140 | 142.0 | 1.4 | 14/20 |
| 55 | 152 | 156 | 2.6 | 152 | 152.0 | 0.0 | 20/20 |
| 89 | 147 | 147 | 0.0 | 147 | 147.0 | 0.0 | 20/20 |

Gap medio do AG: **0.68%**; otimo em **80/100** execucoes.
