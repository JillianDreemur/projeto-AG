# -*- coding: utf-8 -*-
"""Busca em grade: A*, busca gulosa (best-first) e custo uniforme (Dijkstra)."""
from __future__ import annotations

import heapq
import itertools
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from problema import INF, Coord, Grade

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


def manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def heuristica_manhattan(grade: Grade) -> Heuristica:
    """h(n) = distancia de Manhattan * custo minimo de entrada (admissivel e
    consistente, pois todo passo custa pelo menos custo_minimo)."""
    c = grade.custo_minimo()
    return lambda a, b: c * manhattan(a, b)


def heuristica_nula(grade: Grade) -> Heuristica:
    return lambda a, b: 0.0


def _reconstruir(pai: Dict[Coord, Optional[Coord]], objetivo: Coord) -> List[Coord]:
    caminho = []
    atual: Optional[Coord] = objetivo
    while atual is not None:
        caminho.append(atual)
        atual = pai[atual]
    caminho.reverse()
    return caminho


def busca_a_estrela(
    grade: Grade,
    inicio: Coord,
    objetivo: Coord,
    h: Optional[Heuristica] = None,
    peso: float = 1.0,
) -> Resultado:
    """A* classico. peso > 1 => Weighted A* (mais rapido, sem garantia de otimo)."""
    if h is None:
        h = heuristica_manhattan(grade)
    t0 = time.perf_counter()
    contador = itertools.count()
    g: Dict[Coord, float] = {inicio: 0.0}
    pai: Dict[Coord, Optional[Coord]] = {inicio: None}
    aberto: List[Tuple[float, float, int, Coord]] = [
        (peso * h(inicio, objetivo), 0.0, next(contador), inicio)
    ]
    fechado = set()
    expandidos = 0
    gerados = 1
    fronteira_max = 1

    while aberto:
        _, _, _, no = heapq.heappop(aberto)
        if no in fechado:
            continue
        fechado.add(no)
        expandidos += 1
        if no == objetivo:
            return Resultado(
                True,
                _reconstruir(pai, objetivo),
                g[no],
                expandidos,
                gerados,
                fronteira_max,
                time.perf_counter() - t0,
            )
        for viz in grade.vizinhos(no):
            if viz in fechado:
                continue
            novo_g = g[no] + grade.custo_entrada(viz)
            if novo_g < g.get(viz, INF) - 1e-12:
                g[viz] = novo_g
                pai[viz] = no
                heapq.heappush(
                    aberto,
                    (novo_g + peso * h(viz, objetivo), novo_g, next(contador), viz),
                )
                gerados += 1
        fronteira_max = max(fronteira_max, len(aberto))

    return Resultado(
        False, [], INF, expandidos, gerados, fronteira_max, time.perf_counter() - t0
    )


def busca_gulosa(
    grade: Grade, inicio: Coord, objetivo: Coord, h: Optional[Heuristica] = None
) -> Resultado:
    """Busca gulosa (greedy best-first): ordena a fronteira SOMENTE por h(n).

    Rapida, mas nao garante caminho de custo minimo.
    """
    if h is None:
        h = heuristica_manhattan(grade)
    t0 = time.perf_counter()
    contador = itertools.count()
    g: Dict[Coord, float] = {inicio: 0.0}
    pai: Dict[Coord, Optional[Coord]] = {inicio: None}
    aberto: List[Tuple[float, int, Coord]] = [
        (h(inicio, objetivo), next(contador), inicio)
    ]
    fechado = set()
    expandidos = 0
    gerados = 1
    fronteira_max = 1

    while aberto:
        _, _, no = heapq.heappop(aberto)
        if no in fechado:
            continue
        fechado.add(no)
        expandidos += 1
        if no == objetivo:
            return Resultado(
                True,
                _reconstruir(pai, objetivo),
                g[no],
                expandidos,
                gerados,
                fronteira_max,
                time.perf_counter() - t0,
            )
        for viz in grade.vizinhos(no):
            if viz in fechado:
                continue
            novo_g = g[no] + grade.custo_entrada(viz)
            if viz not in g:
                g[viz] = novo_g
                pai[viz] = no
                heapq.heappush(aberto, (h(viz, objetivo), next(contador), viz))
                gerados += 1
        fronteira_max = max(fronteira_max, len(aberto))

    return Resultado(
        False, [], INF, expandidos, gerados, fronteira_max, time.perf_counter() - t0
    )


def custo_uniforme(
    grade: Grade, inicio: Coord, objetivo: Coord
) -> Resultado:
    """Dijkstra (A* com h = 0): referencia de otimalidade."""
    return busca_a_estrela(grade, inicio, objetivo, h=heuristica_nula(grade))


def custos_dijkstra(grade: Grade, origem: Coord) -> Dict[Coord, float]:
    """Custo minimo de origem ate TODAS as celulas (para a matriz de distancias)."""
    dist: Dict[Coord, float] = {origem: 0.0}
    fila: List[Tuple[float, Coord]] = [(0.0, origem)]
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
