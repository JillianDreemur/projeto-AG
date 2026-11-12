# -*- coding: utf-8 -*-
"""Algoritmo Genetico (AG) para a ordem de entrega.

Representacao : permutacao das entregas (deposito fixo no inicio).
Aptidao       : 1 / custo total da rota (minimizacao).
Selecao       : torneio.
Crossover     : OX (order crossover), preserva a ordem relativa.
Mutacao       : troca de duas posicoes (swap) ou inversao de trecho.
Elitismo      : os `elitismo` melhores passam intactos.
"""
from __future__ import annotations

import random
import statistics
import time
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

from busca_gulosa.guloso import guloso_vizinho_mais_proximo
from comum.modelo import custo_da_ordem


@dataclass
class ResultadoAG:
    ordem: List[int]
    custo: float
    geracoes: int
    historico_melhor: List[float] = field(default_factory=list)
    historico_medio: List[float] = field(default_factory=list)
    tempo: float = 0.0


def _torneio(pop, avaliar, k: int, rng: random.Random):
    competidores = rng.sample(pop, min(k, len(pop)))
    return min(competidores, key=avaliar)


def _ox(p1: Sequence[int], p2: Sequence[int], rng: random.Random) -> List[int]:
    n = len(p1)
    if n < 2:
        return list(p1)
    a, b = sorted(rng.sample(range(n), 2))
    filho: List[Optional[int]] = [None] * n
    filho[a : b + 1] = p1[a : b + 1]
    usados = set(p1[a : b + 1])
    resto = [g for g in p2 if g not in usados]
    idx = 0
    for i in range(n):
        if filho[i] is None:
            filho[i] = resto[idx]
            idx += 1
    return [g for g in filho if g is not None]


def _mutacao(individuo: List[int], rng: random.Random) -> None:
    n = len(individuo)
    if n < 2:
        return
    i, j = rng.sample(range(n), 2)
    if rng.random() < 0.5:
        individuo[i], individuo[j] = individuo[j], individuo[i]
    else:
        if i > j:
            i, j = j, i
        individuo[i : j + 1] = reversed(individuo[i : j + 1])


def algoritmo_genetico(
    D: List[List[float]],
    tam_pop: int = 80,
    geracoes: int = 300,
    taxa_crossover: float = 0.9,
    taxa_mutacao: float = 0.30,
    elitismo: int = 2,
    tam_torneio: int = 3,
    semente: int = 1,
    paciencia: int = 60,
) -> ResultadoAG:
    rng = random.Random(semente)
    t0 = time.perf_counter()
    n = len(D)
    entregas = list(range(1, n))

    def avaliar(ordem: Sequence[int]) -> float:
        return custo_da_ordem(D, [0, *ordem])

    # Populacao inicial: 1 individuo do guloso + permutacoes aleatorias
    pop: List[List[int]] = [guloso_vizinho_mais_proximo(D).ordem[1:]]
    while len(pop) < tam_pop:
        perm = entregas[:]
        rng.shuffle(perm)
        pop.append(perm)

    hist_melhor: List[float] = []
    hist_medio: List[float] = []
    melhor = min(pop, key=avaliar)
    melhor_custo = avaliar(melhor)
    sem_melhora = 0
    geracoes_exec = 0

    for ger in range(geracoes):
        pop.sort(key=avaliar)
        custos = [avaliar(i) for i in pop]
        hist_melhor.append(custos[0])
        hist_medio.append(statistics.fmean(custos))
        geracoes_exec = ger + 1

        if custos[0] < melhor_custo - 1e-9:
            melhor = pop[0][:]
            melhor_custo = custos[0]
            sem_melhora = 0
        else:
            sem_melhora += 1
        if sem_melhora >= paciencia:
            break

        nova: List[List[int]] = [p[:] for p in pop[:elitismo]]
        while len(nova) < tam_pop:
            p1 = _torneio(pop, avaliar, tam_torneio, rng)
            p2 = _torneio(pop, avaliar, tam_torneio, rng)
            if rng.random() < taxa_crossover and len(entregas) > 1:
                f1, f2 = _ox(p1, p2, rng), _ox(p2, p1, rng)
            else:
                f1, f2 = list(p1), list(p2)
            if rng.random() < taxa_mutacao:
                _mutacao(f1, rng)
            if rng.random() < taxa_mutacao:
                _mutacao(f2, rng)
            nova.append(f1)
            nova.append(f2)
        pop = nova[:tam_pop]

    return ResultadoAG(
        [0, *melhor],
        melhor_custo,
        geracoes_exec,
        hist_melhor,
        hist_medio,
        time.perf_counter() - t0,
    )


def executar_varias_vezes(
    D: List[List[float]], execucoes: int = 30, **kwargs
) -> Tuple[List[ResultadoAG], dict]:
    """Roda o AG com sementes diferentes e devolve estatisticas."""
    resultados = [
        algoritmo_genetico(D, semente=s, **kwargs) for s in range(1, execucoes + 1)
    ]
    custos = [r.custo for r in resultados]
    stats = {
        "melhor": min(custos),
        "media": statistics.fmean(custos),
        "pior": max(custos),
        "desvio": statistics.pstdev(custos),
        "otimos": sum(1 for c in custos if abs(c - min(custos)) < 1e-9),
        "geracoes_media": statistics.fmean(r.geracoes for r in resultados),
        "tempo_medio": statistics.fmean(r.tempo for r in resultados),
        "execucoes": execucoes,
    }
    return resultados, stats
