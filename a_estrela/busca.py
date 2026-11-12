# -*- coding: utf-8 -*-
"""A* e custo uniforme (Dijkstra) na grade."""
from __future__ import annotations

import heapq
import itertools
import time
from typing import Dict, List, Optional, Tuple

from comum.modelo import (
    Heuristica,
    Resultado,
    heuristica_manhattan,
    heuristica_nula,
)
from comum.problema import INF, Coord, Grade


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


def custo_uniforme(grade: Grade, inicio: Coord, objetivo: Coord) -> Resultado:
    """Dijkstra (A* com h = 0): referencia de otimalidade."""
    return busca_a_estrela(grade, inicio, objetivo, h=heuristica_nula(grade))
