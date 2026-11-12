# -*- coding: utf-8 -*-
"""A* no espaco de estados da roteirizacao + forca bruta de verificacao.

Estado = (ponto_atual, conjunto_de_entregas_restantes).
Heuristica = peso da arvore geradora minima (AGM) sobre {atual} U restantes,
que e um limite inferior para o custo de visitar todas as entregas.
"""
from __future__ import annotations

import heapq
import itertools
import time
from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

from a_estrela.busca import busca_a_estrela
from comum.modelo import INF, Rota, custo_da_ordem, heuristica_manhattan
from comum.problema import Coord, Grade


def _mst(nos: Sequence[int], D: List[List[float]]) -> float:
    """Peso da arvore geradora minima sobre `nos` (Prim, grafo completo)."""
    if len(nos) <= 1:
        return 0.0
    dentro = {nos[0]}
    total = 0.0
    while len(dentro) < len(nos):
        melhor = INF
        escolhido = None
        for u in nos:
            if u in dentro:
                continue
            for v in dentro:
                if D[u][v] < melhor:
                    melhor, escolhido = D[u][v], u
        total += melhor
        dentro.add(escolhido)  # type: ignore[arg-type]
    return total


def heuristica_mst(D: List[List[float]]):
    """h(estado) = AGM sobre {atual} U restantes (admissivel)."""
    cache: Dict[Tuple[int, FrozenSet[int]], float] = {}

    def h(estado: Tuple[int, FrozenSet[int]]) -> float:
        atual, restantes = estado
        if not restantes:
            return 0.0
        chave = (atual, restantes)
        if chave not in cache:
            cache[chave] = _mst((atual,) + tuple(sorted(restantes)), D)
        return cache[chave]

    return h


def a_estrela_entregas(D: List[List[float]]) -> Rota:
    """A* sobre (ponto_atual, entregas_restantes). Devolve a ordem otima."""
    n = len(D)
    t0 = time.perf_counter()
    inicio: Tuple[int, FrozenSet[int]] = (0, frozenset(range(1, n)))
    h = heuristica_mst(D)
    contador = itertools.count()
    g: Dict[Tuple[int, FrozenSet[int]], float] = {inicio: 0.0}
    pai: Dict[Tuple[int, FrozenSet[int]], Optional[Tuple[int, FrozenSet[int]]]] = {
        inicio: None
    }
    aberto: List[Tuple[float, float, int, Tuple[int, FrozenSet[int]]]] = [
        (h(inicio), 0.0, next(contador), inicio)
    ]
    expandidos = 0

    while aberto:
        _, gs, _, estado = heapq.heappop(aberto)
        if gs > g.get(estado, INF) + 1e-12:
            continue
        expandidos += 1
        atual, restantes = estado
        if not restantes:
            ordem = []
            e: Optional[Tuple[int, FrozenSet[int]]] = estado
            while e is not None:
                ordem.append(e[0])
                e = pai[e]
            ordem.reverse()
            return Rota(ordem, gs, expandidos, time.perf_counter() - t0)
        for prox in sorted(restantes):
            novo_estado = (prox, restantes - {prox})
            novo_g = gs + D[atual][prox]
            if novo_g < g.get(novo_estado, INF) - 1e-12:
                g[novo_estado] = novo_g
                pai[novo_estado] = estado
                heapq.heappush(
                    aberto,
                    (novo_g + h(novo_estado), novo_g, next(contador), novo_estado),
                )
    raise RuntimeError("instancia sem solucao (grafo desconexo)")


def forca_bruta(D: List[List[float]]) -> Rota:
    """Otimo por enumeracao (apenas para instancias pequenas, ate ~11 entregas)."""
    n = len(D)
    melhor = INF
    melhor_ordem: List[int] = []
    for perm in itertools.permutations(range(1, n)):
        ordem = [0, *perm]
        c = custo_da_ordem(D, ordem)
        if c < melhor:
            melhor, melhor_ordem = c, ordem
    return Rota(melhor_ordem, melhor, 0, 0.0)


def caminho_completo(
    grade: Grade, nos: Sequence[Coord], ordem: Sequence[int]
) -> List[Coord]:
    """Concatena os caminhos minimos entre pontos consecutivos da ordem."""
    h = heuristica_manhattan(grade)
    caminho: List[Coord] = []
    for a, b in zip(ordem, ordem[1:]):
        trecho = busca_a_estrela(grade, nos[a], nos[b], h=h).caminho
        caminho.extend(trecho if not caminho else trecho[1:])
    return caminho
