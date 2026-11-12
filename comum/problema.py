# -*- coding: utf-8 -*-
"""Problema de busca: entregas numa cidade em grade com custo de trafego.

Modelagem
---------
* Cidade = grade L x A. Cada celula livre tem custo de ENTRADA >= 1
  (1 = via livre; 2..5 = congestionamento). Celulas bloqueadas = predios.
* Deposito = (0,0).
* Parte 1 (caminho): sair do deposito e chegar ao alvo minimizando custo.
* Parte 2 (roteirizacao): visitar todos os pontos de entrega (sem voltar
  ao deposito), na melhor ordem possivel.
"""
from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Tuple

Coord = Tuple[int, int]
INF = float("inf")
MOVIMENTOS = ((1, 0), (-1, 0), (0, 1), (0, -1))


@dataclass(frozen=True)
class Grade:
    largura: int
    altura: int
    custo: Tuple[Tuple[int, ...], ...]
    bloqueado: FrozenSet[Coord]

    def dentro(self, p: Coord) -> bool:
        x, y = p
        return 0 <= x < self.largura and 0 <= y < self.altura

    def livre(self, p: Coord) -> bool:
        return self.dentro(p) and p not in self.bloqueado

    def vizinhos(self, p: Coord) -> List[Coord]:
        x, y = p
        saida = []
        for dx, dy in MOVIMENTOS:
            q = (x + dx, y + dy)
            if self.livre(q):
                saida.append(q)
        return saida

    def custo_entrada(self, p: Coord) -> int:
        return self.custo[p[1]][p[0]]

    def custo_minimo(self) -> int:
        return min(
            self.custo[y][x]
            for y in range(self.altura)
            for x in range(self.largura)
            if (x, y) not in self.bloqueado
        )

    def celulas_livres(self) -> List[Coord]:
        return [
            (x, y)
            for y in range(self.altura)
            for x in range(self.largura)
            if (x, y) not in self.bloqueado
        ]


def distancias_bfs(grade: Grade, origem: Coord) -> Dict[Coord, int]:
    """Menor numero de passos (ignora custo) de origem ate cada celula."""
    dist = {origem: 0}
    fila = deque([origem])
    while fila:
        no = fila.popleft()
        for viz in grade.vizinhos(no):
            if viz not in dist:
                dist[viz] = dist[no] + 1
                fila.append(viz)
    return dist


def _escolher_pontos(
    alcancaveis: Dict[Coord, int], n: int, rng: random.Random
) -> Optional[List[Coord]]:
    """Escolhe n pontos espalhados (distancia euclidiana minima decrescente)."""
    candidatos = [(p, d) for p, d in alcancaveis.items() if d >= 8]
    rng.shuffle(candidatos)
    for dist_min in (8, 6, 4, 2, 0):
        escolhidos: List[Coord] = []
        for p, _ in candidatos:
            if p == (0, 0):
                continue
            if all(
                abs(p[0] - q[0]) + abs(p[1] - q[1]) >= dist_min for q in escolhidos
            ):
                escolhidos.append(p)
                if len(escolhidos) == n:
                    return sorted(escolhidos)
    return None


def cidade_aleatoria(
    semente: int = 7,
    largura: int = 25,
    altura: int = 25,
    densidade: float = 0.20,
    n_entregas: int = 7,
):
    """Gera uma cidade conexa, com predios e zonas de congestionamento."""
    rng = random.Random(semente)
    inicio = (0, 0)
    for _ in range(300):
        bloqueado = {
            (x, y)
            for y in range(altura)
            for x in range(largura)
            if rng.random() < densidade
        }
        bloqueado.discard(inicio)
        custo = [[1] * largura for _ in range(altura)]
        for _ in range(10):
            cx, cy = rng.randrange(largura), rng.randrange(altura)
            raio = rng.randint(2, 4)
            pico = rng.randint(1, 3)
            for y in range(max(0, cy - raio), min(altura, cy + raio + 1)):
                for x in range(max(0, cx - raio), min(largura, cx + raio + 1)):
                    if (x, y) in bloqueado:
                        continue
                    d = abs(x - cx) + abs(y - cy)
                    if d <= raio:
                        custo[y][x] = min(5, custo[y][x] + max(1, pico - d // 2))
        grade = Grade(
            largura,
            altura,
            tuple(tuple(linha) for linha in custo),
            frozenset(bloqueado),
        )
        alcancaveis = distancias_bfs(grade, inicio)
        if len(alcancaveis) < 0.6 * largura * altura:
            continue
        alvo = max(alcancaveis.items(), key=lambda kv: kv[1])[0]
        if alvo == inicio:
            continue
        pontos = _escolher_pontos(alcancaveis, n_entregas, rng)
        if pontos is not None and alvo not in pontos:
            return grade, inicio, alvo, pontos
    raise RuntimeError("nao foi possivel gerar uma cidade valida")


def imprimir_ascii(grade: Grade, caminho=None, inicio=None, alvo=None, pontos=()):
    """Mapa em texto: # predio, . via livre, ~ trafego, S inicio, G alvo, * caminho."""
    caminho = set(caminho or ())
    pontos = set(pontos)
    linhas = []
    for y in range(grade.altura):
        linha = []
        for x in range(grade.largura):
            p = (x, y)
            if p == inicio:
                linha.append("S")
            elif p == alvo:
                linha.append("G")
            elif p in pontos:
                linha.append("P")
            elif p in caminho:
                linha.append("*")
            elif p in grade.bloqueado:
                linha.append("#")
            elif grade.custo[y][x] > 2:
                linha.append("~")
            else:
                linha.append(".")
        linhas.append("".join(linha))
    return "\n".join(linhas)
