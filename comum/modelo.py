# -*- coding: utf-8 -*-
"""Infraestrutura compartilhada pelos tres algoritmos.

* Resultado / Rota : estruturas de retorno
* heuristicas      : Manhattan (admissivel) e nula
* custos_minimos   : Dijkstra usado para montar a matriz de distancias
* matriz_distancias: custo minimo entre todos os pontos de entrega
* custo_da_ordem   : funcao objetivo da roteirizacao
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence

from comum.problema import INF, Coord, Grade

Heuristica = Callable[[Coord, Coord], float]


@dataclass
class Resultado:
    sucesso: bool
    caminho: List[Coord]
    custo: float
    expandidos: int
    gerados: int
    fronteira_maxima: int
    tempo: float


@dataclass
class Rota:
    ordem: List[int]
    custo: float
    expandidos: int = 0
    tempo: float = 0.0


def manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def heuristica_manhattan(grade: Grade) -> Heuristica:
    """h(n) = distancia de Manhattan * custo minimo de entrada.

    Admissivel e consistente: todo passo custa pelo menos custo_minimo.
    """
    c = grade.custo_minimo()
    return lambda a, b: c * manhattan(a, b)


def heuristica_nula(grade: Grade) -> Heuristica:
    return lambda a, b: 0.0


def custos_minimos(grade: Grade, origem: Coord) -> Dict[Coord, float]:
    """Dijkstra: custo minimo da origem ate todas as celulas.

    Usado apenas no pre-processamento (montar a matriz de distancias).
    """
    dist: Dict[Coord, float] = {origem: 0.0}
    fila = [(0.0, origem)]
    while fila:
        d, no = heapq.heappop(fila)
        if d > dist.get(no, INF):
            continue
        for viz in grade.vizinhos(no):
            novo = d + grade.custo_entrada(viz)
            if novo < dist.get(viz, INF):
                dist[viz] = novo
                heapq.heappush(fila, (novo, viz))
    return dist


def matriz_distancias(grade: Grade, nos: Sequence[Coord]) -> List[List[float]]:
    """D[i][j] = custo minimo na grade entre nos[i] e nos[j]."""
    n = len(nos)
    D = [[INF] * n for _ in range(n)]
    for i, origem in enumerate(nos):
        dist = custos_minimos(grade, origem)
        for j, destino in enumerate(nos):
            D[i][j] = dist.get(destino, INF)
    return D


def custo_da_ordem(D: List[List[float]], ordem: Sequence[int]) -> float:
    """Custo de sair do deposito (0) e visitar `ordem` em sequencia."""
    total = 0.0
    for a, b in zip(ordem, ordem[1:]):
        total += D[a][b]
    return total
