# -*- coding: utf-8 -*-
"""Busca gulosa (greedy best-first) na grade e vizinho mais proximo nas entregas."""
from __future__ import annotations

import heapq
import itertools
import time
from typing import Dict, List, Optional, Tuple

from comum.modelo import Heuristica, Resultado, Rota, heuristica_manhattan
from comum.problema import INF, Coord, Grade


def busca_gulosa(
    grade: Grade, inicio: Coord, objetivo: Coord, h: Optional[Heuristica] = None
) -> Resultado:
    """Ordena a fronteira SOMENTE por h(n). Rapida, mas sem garantia de otimo."""
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
            caminho = []
            atual: Optional[Coord] = no
            while atual is not None:
                caminho.append(atual)
                atual = pai[atual]
            caminho.reverse()
            return Resultado(
                True,
                caminho,
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


def guloso_vizinho_mais_proximo(D: List[List[float]]) -> Rota:
    """Heuristica construtiva: do ponto atual, vai para a entrega mais proxima."""
    t0 = time.perf_counter()
    atual = 0
    restantes = set(range(1, len(D)))
    ordem = [0]
    custo = 0.0
    while restantes:
        prox = min(restantes, key=lambda j: D[atual][j])
        custo += D[atual][prox]
        ordem.append(prox)
        restantes.discard(prox)
        atual = prox
    return Rota(ordem, custo, 0, time.perf_counter() - t0)
