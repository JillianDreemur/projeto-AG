# -*- coding: utf-8 -*-
"""Demonstracao isolada do AG genetico na ordem das entregas.

Rode a partir da raiz do projeto:
    python ag_genetico/executar.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ag_genetico.genetico import executar_varias_vezes
from comum.modelo import matriz_distancias
from comum.problema import cidade_aleatoria
from a_estrela.roteirizacao import forca_bruta


def main():
    grade, inicio, _, pontos = cidade_aleatoria(semente=7, n_entregas=10)
    nos = [inicio] + pontos
    D = matriz_distancias(grade, nos)

    resultados, stats = executar_varias_vezes(D, execucoes=10)
    otimo = forca_bruta(D).custo

    print("AG GENETICO - ordem das entregas (10 execucoes)")
    print(f"  otimo (forca bruta) .. {otimo:.0f}")
    print(f"  melhor execucao ...... {stats['melhor']:.0f}")
    print(f"  media ................ {stats['media']:.2f}")
    print(f"  pior ................. {stats['pior']:.0f}")
    print(f"  geracoes medias ...... {stats['geracoes_media']:.0f}")
    print(f"  tempo medio .......... {stats['tempo_medio'] * 1000:.0f} ms")
    print(f"  melhor ordem ......... {min(resultados, key=lambda r: r.custo).ordem}")


if __name__ == "__main__":
    main()
