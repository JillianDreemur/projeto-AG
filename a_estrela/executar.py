# -*- coding: utf-8 -*-
"""Demonstracao isolada do A* nas duas partes do problema.

Rode a partir da raiz do projeto:
    python a_estrela/executar.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from a_estrela.busca import busca_a_estrela
from a_estrela.roteirizacao import a_estrela_entregas, forca_bruta
from comum.modelo import heuristica_manhattan, matriz_distancias
from comum.problema import cidade_aleatoria


def main():
    grade, inicio, alvo, pontos = cidade_aleatoria(semente=7, n_entregas=10)
    h = heuristica_manhattan(grade)

    r = busca_a_estrela(grade, inicio, alvo, h=h)
    print("PARTE 1 - A* na grade")
    print(f"  custo otimo .......... {r.custo:.0f}")
    print(f"  nos expandidos ....... {r.expandidos}")
    print(f"  celulas no caminho ... {len(r.caminho)}")

    nos = [inicio] + pontos
    D = matriz_distancias(grade, nos)
    rota = a_estrela_entregas(D)
    bruta = forca_bruta(D)
    print("\nPARTE 2 - A* na ordem das entregas")
    print(f"  custo otimo .......... {rota.custo:.0f}")
    print(f"  ordem ................ {rota.ordem}")
    print(f"  estados expandidos ... {rota.expandidos}")
    print(f"  conferido pela forca bruta: {bruta.custo:.0f}")


if __name__ == "__main__":
    main()
