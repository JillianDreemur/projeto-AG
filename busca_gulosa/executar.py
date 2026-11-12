# -*- coding: utf-8 -*-
"""Demonstracao isolada da busca gulosa (grade + vizinho mais proximo).

O A* aparece apenas como referencia de otimo, para medir o gap.

Rode a partir da raiz do projeto:
    python busca_gulosa/executar.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from a_estrela.busca import busca_a_estrela
from a_estrela.roteirizacao import a_estrela_entregas, forca_bruta
from busca_gulosa.guloso import busca_gulosa, guloso_vizinho_mais_proximo
from comum.modelo import heuristica_manhattan, matriz_distancias
from comum.problema import cidade_aleatoria


def main():
    grade, inicio, alvo, pontos = cidade_aleatoria(semente=7, n_entregas=10)
    h = heuristica_manhattan(grade)

    otimo = busca_a_estrela(grade, inicio, alvo, h=h)
    guloso = busca_gulosa(grade, inicio, alvo, h=h)
    print("PARTE 1 - busca gulosa na grade")
    print(f"  custo do A* .......... {otimo.custo:.0f}  ({otimo.expandidos} nos)")
    print(f"  custo do guloso ...... {guloso.custo:.0f}  ({guloso.expandidos} nos)")
    print(f"  custo extra .......... {(guloso.custo / otimo.custo - 1) * 100:.1f}%")

    nos = [inicio] + pontos
    D = matriz_distancias(grade, nos)
    otimo_rota = a_estrela_entregas(D)
    nn = guloso_vizinho_mais_proximo(D)
    print("\nPARTE 2 - vizinho mais proximo nas entregas")
    print(f"  custo do A* .......... {otimo_rota.custo:.0f}")
    print(f"  custo do guloso ...... {nn.custo:.0f}")
    print(f"  gap .................. {(nn.custo / otimo_rota.custo - 1) * 100:.1f}%")
    print(f"  ordem ................ {nn.ordem}")
    print(f"  otimo (forca bruta) .. {forca_bruta(D).custo:.0f}")


if __name__ == "__main__":
    main()
