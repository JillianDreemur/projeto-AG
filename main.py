# -*- coding: utf-8 -*-
"""Executa os experimentos das duas partes e gera tabelas, CSV e figuras."""
from __future__ import annotations

import csv
import os
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from busca import busca_a_estrela, busca_gulosa, custo_uniforme, heuristica_manhattan
from genetico import executar_varias_vezes
from problema import Grade, cidade_aleatoria
from roteirizacao import (
    a_estrela_entregas,
    caminho_completo,
    forca_bruta,
    guloso_vizinho_mais_proximo,
    matriz_distancias,
)

SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
os.makedirs(SAIDA, exist_ok=True)


def desenhar_mapa(
    grade: Grade, caminhos, arquivo, inicio, alvo, pontos=(), titulo="",
    rotulos_pontos=None,
):
    grid = np.array(grade.custo, dtype=float)
    mascara = np.zeros_like(grid)
    for x, y in grade.bloqueado:
        mascara[y, x] = 1.0

    fig, ax = plt.subplots(figsize=(8.4, 8.4), dpi=140)
    ax.imshow(grid, cmap="YlOrRd", vmin=1, vmax=5)
    ax.imshow(
        np.ma.masked_where(mascara == 0, mascara),
        cmap=matplotlib.colors.ListedColormap(["#303030"]),
    )
    for caminho, cor, rotulo, estilo in caminhos:
        if not caminho:
            continue
        xs = [p[0] for p in caminho]
        ys = [p[1] for p in caminho]
        ax.plot(xs, ys, color=cor, lw=2.4, label=rotulo, linestyle=estilo, alpha=0.95)

    ax.scatter(
        [inicio[0]], [inicio[1]], s=160, c="#1f77b4", edgecolors="white",
        zorder=5, label="Deposito (S)",
    )
    if alvo is not None:
        ax.scatter(
            [alvo[0]], [alvo[1]], s=200, marker="*", c="#2ca02c",
            edgecolors="black", zorder=5, label="Alvo (G)",
        )
    if pontos:
        ax.scatter(
            [p[0] for p in pontos], [p[1] for p in pontos], s=110, marker="s",
            c="#9467bd", edgecolors="white", zorder=5, label="Entregas",
        )
    if pontos and rotulos_pontos:
        for p, r in zip(pontos, rotulos_pontos):
            ax.annotate(
                str(r), (p[0], p[1]), xytext=(7, -11), textcoords="offset points",
                fontsize=9, fontweight="bold", color="#2b0a4a",
            )

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(titulo, fontsize=11)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.9)
    ax.set_xlim(-0.5, grade.largura - 0.5)
    ax.set_ylim(grade.altura - 0.5, -0.5)
    fig.tight_layout()
    fig.savefig(arquivo, bbox_inches="tight")
    plt.close(fig)


def desenhar_convergencia(historico_melhor, historico_medio, arquivo):
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=140)
    ax.plot(historico_melhor, label="melhor individuo", color="#1f77b4", lw=2)
    ax.plot(
        historico_medio, label="media da populacao", color="#ff7f0e", lw=1.4, alpha=0.85
    )
    ax.set_xlabel("geracao")
    ax.set_ylabel("custo da rota")
    ax.set_title("Convergencia do Algoritmo Genetico")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(arquivo, bbox_inches="tight")
    plt.close(fig)


def desenhar_barras(rotulos, serie_a, serie_b, arquivo):
    x = np.arange(len(rotulos))
    largura = 0.38
    fig, ax = plt.subplots(figsize=(8.4, 4.2), dpi=140)
    ax.bar(x - largura / 2, serie_a, largura, label="A*", color="#1f77b4")
    ax.bar(x + largura / 2, serie_b, largura, label="Busca gulosa", color="#ff7f0e")
    ax.set_xticks(x)
    ax.set_xticklabels(rotulos)
    ax.set_ylabel("nos expandidos")
    ax.set_title("Esforco de busca por instancia (Parte 1)")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(arquivo, bbox_inches="tight")
    plt.close(fig)


def parte1():
    sementes = [3, 7, 11, 19, 23, 42, 99, 123]
    linhas = []
    instancias = []
    for s in sementes:
        grade, inicio, alvo, pontos = cidade_aleatoria(semente=s)
        h = heuristica_manhattan(grade)
        r_a = busca_a_estrela(grade, inicio, alvo, h=h)
        r_g = busca_gulosa(grade, inicio, alvo, h=h)
        r_d = custo_uniforme(grade, inicio, alvo)
        assert r_a.sucesso and r_g.sucesso and r_d.sucesso
        assert abs(r_a.custo - r_d.custo) < 1e-9  # A* otimo
        linhas.append(
            {
                "instancia": s,
                "otimo": r_d.custo,
                "custo_a": r_a.custo,
                "custo_g": r_g.custo,
                "exp_a": r_a.expandidos,
                "exp_g": r_g.expandidos,
                "exp_d": r_d.expandidos,
                "ms_a": r_a.tempo * 1000,
                "ms_g": r_g.tempo * 1000,
                "taxa_g": (r_g.expandidos / r_a.expandidos) * 100,
                "extra_g": (r_g.custo / r_d.custo - 1) * 100,
                "caminho_a": r_a.caminho,
                "caminho_g": r_g.caminho,
                "objetivo": alvo,
                "pontos": pontos,
            }
        )
        instancias.append((grade, inicio, alvo, pontos))

    cab = (
        "| Inst. | Otimo | Custo A* | Custo guloso | Nos A* | Nos guloso | "
        "Guloso/A* (%) | Custo extra (%) |\n"
        "|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    )
    corpo = "".join(
        f"| {l['instancia']} | {l['otimo']:.0f} | {l['custo_a']:.0f} | "
        f"{l['custo_g']:.0f} | {l['exp_a']} | {l['exp_g']} | "
        f"{l['taxa_g']:.1f} | {l['extra_g']:.1f} |\n"
        for l in linhas
    )
    medias = {
        "exp_a": statistics.fmean(l["exp_a"] for l in linhas),
        "exp_g": statistics.fmean(l["exp_g"] for l in linhas),
        "taxa": statistics.fmean(l["taxa_g"] for l in linhas),
        "extra": statistics.fmean(l["extra_g"] for l in linhas),
        "extra_max": max(l["extra_g"] for l in linhas),
        "subotimos": sum(1 for l in linhas if l["custo_g"] > l["otimo"] + 1e-9),
        "ms_a": statistics.fmean(l["ms_a"] for l in linhas),
        "ms_g": statistics.fmean(l["ms_g"] for l in linhas),
    }

    with open(
        os.path.join(SAIDA, "parte1_instancias.csv"), "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.writer(f)
        w.writerow(
            ["instancia", "otimo", "custo_a_estrela", "custo_guloso", "nos_a_estrela",
             "nos_guloso", "nos_dijkstra", "ms_a_estrela", "ms_guloso",
             "guloso_sobre_a_pct", "custo_extra_pct"]
        )
        for l in linhas:
            w.writerow(
                [l["instancia"], l["otimo"], l["custo_a"], l["custo_g"], l["exp_a"],
                 l["exp_g"], l["exp_d"], round(l["ms_a"], 3), round(l["ms_g"], 3),
                 round(l["taxa_g"], 2), round(l["extra_g"], 2)]
            )

    grade, inicio, alvo, pontos = instancias[1]
    desenhar_mapa(
        grade,
        [
            (linhas[1]["caminho_a"], "#1f77b4", "A* (otimo)", "-"),
            (linhas[1]["caminho_g"], "#ff1493", "Busca gulosa", "--"),
        ],
        os.path.join(SAIDA, "mapa_parte1.png"),
        inicio,
        alvo,
        pontos,
        "Parte 1 - caminho ate o alvo (custo de trafego em cores)",
    )
    desenhar_barras(
        [str(l["instancia"]) for l in linhas],
        [l["exp_a"] for l in linhas],
        [l["exp_g"] for l in linhas],
        os.path.join(SAIDA, "comparacao_expansoes.png"),
    )
    return cab + corpo, medias, linhas


def experimento_entrega(semente: int, n_entregas: int = 10, execucoes: int = 20):
    grade, inicio, _, pontos = cidade_aleatoria(semente=semente, n_entregas=n_entregas)
    nos = [inicio] + pontos
    D = matriz_distancias(grade, nos)
    r_astar = a_estrela_entregas(D)
    r_nn = guloso_vizinho_mais_proximo(D)
    r_bruta = forca_bruta(D)
    assert abs(r_astar.custo - r_bruta.custo) < 1e-9, "A* nao achou o otimo"
    resultados_ag, stats = executar_varias_vezes(
        D, execucoes=execucoes, tam_pop=80, geracoes=300, paciencia=60
    )
    return {
        "semente": semente,
        "grade": grade,
        "nos": nos,
        "D": D,
        "otimo": r_astar.custo,
        "exp_astar": r_astar.expandidos,
        "ms_astar": r_astar.tempo * 1000,
        "nn_custo": r_nn.custo,
        "nn_ordem": r_nn.ordem,
        "nn_gap": (r_nn.custo / r_astar.custo - 1) * 100,
        "bruta": r_bruta.custo,
        "ag": resultados_ag,
        "ag_stats": stats,
        "ag_gap_media": (stats["media"] / r_astar.custo - 1) * 100,
        "ag_gap_melhor": (stats["melhor"] / r_astar.custo - 1) * 100,
        "ordem_otima": r_astar.ordem,
        "ms_nn": r_nn.tempo * 1000,
    }


def parte2():
    sementes = [7, 21, 34, 55, 89]
    experimentos = [experimento_entrega(s, n_entregas=10) for s in sementes]

    resumo_cab = (
        "| Inst. | Otimo | Guloso | Gap guloso (%) | AG melhor | AG media | "
        "Gap AG medio (%) | Otimos do AG |\n"
        "|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    )
    resumo = "".join(
        f"| {e['semente']} | {e['otimo']:.0f} | {e['nn_custo']:.0f} | "
        f"{e['nn_gap']:.1f} | {e['ag_stats']['melhor']:.0f} | "
        f"{e['ag_stats']['media']:.1f} | {e['ag_gap_media']:.1f} | "
        f"{e['ag_stats']['otimos']}/{e['ag_stats']['execucoes']} |\n"
        for e in experimentos
    )
    agregado = {
        "gap_nn_medio": statistics.fmean(e["nn_gap"] for e in experimentos),
        "gap_ag_medio": statistics.fmean(e["ag_gap_media"] for e in experimentos),
        "gap_ag_max": max(e["ag_gap_melhor"] for e in experimentos),
        "otimos_ag": sum(e["ag_stats"]["otimos"] for e in experimentos),
        "total_ag": sum(e["ag_stats"]["execucoes"] for e in experimentos),
    }

    detalhe = experimentos[0]
    stats = detalhe["ag_stats"]
    gap = lambda c: (c / detalhe["otimo"] - 1) * 100  # noqa: E731

    tab_detalhe = (
        "| Algoritmo | Custo da rota | Gap vs otimo (%) | Expansoes | Tempo (ms) |\n"
        "|---|---:|---:|---:|---:|\n"
        f"| A* (otimo) | {detalhe['otimo']:.0f} | 0.00 | "
        f"{detalhe['exp_astar']} | {detalhe['ms_astar']:.2f} |\n"
        f"| Guloso (vizinho mais proximo) | {detalhe['nn_custo']:.0f} | "
        f"{gap(detalhe['nn_custo']):.1f} | - | {detalhe['ms_nn']:.2f} |\n"
        f"| AG (melhor de {stats['execucoes']}) | {stats['melhor']:.0f} | "
        f"{gap(stats['melhor']):.1f} | - | {stats['tempo_medio']*1000:.1f} |\n"
        f"| AG (media de {stats['execucoes']}) | {stats['media']:.2f} | "
        f"{gap(stats['media']):.1f} | - | {stats['tempo_medio']*1000:.1f} |\n"
        f"| AG (pior de {stats['execucoes']}) | {stats['pior']:.0f} | "
        f"{gap(stats['pior']):.1f} | - | {stats['tempo_medio']*1000:.1f} |\n"
        f"| Forca bruta (verdade) | {detalhe['bruta']:.0f} | 0.00 | "
        f"{len(detalhe['ordem_otima']) - 1} entregas | - |\n"
    )

    with open(
        os.path.join(SAIDA, "parte2_resumo.csv"), "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.writer(f)
        w.writerow(
            ["instancia", "otimo", "guloso", "gap_guloso_pct", "ag_melhor",
             "ag_media", "gap_ag_medio_pct", "ag_otimos", "ag_execucoes",
             "expansoes_astar"]
        )
        for e in experimentos:
            w.writerow(
                [e["semente"], e["otimo"], e["nn_custo"], round(e["nn_gap"], 2),
                 round(e["ag_stats"]["melhor"], 2), round(e["ag_stats"]["media"], 2),
                 round(e["ag_gap_media"], 2), e["ag_stats"]["otimos"],
                 e["ag_stats"]["execucoes"], e["exp_astar"]]
            )

    with open(
        os.path.join(SAIDA, "parte2_ag_execucoes.csv"), "w", newline="",
        encoding="utf-8",
    ) as f:
        w = csv.writer(f)
        w.writerow(["execucao", "custo", "geracoes", "tempo_s"])
        for i, r in enumerate(detalhe["ag"], 1):
            w.writerow([i, round(r.custo, 3), r.geracoes, round(r.tempo, 4)])

    with open(
        os.path.join(SAIDA, "parte2_distancias.csv"), "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.writer(f)
        w.writerow(["de\\para"] + [f"no{j}" for j in range(len(detalhe["nos"]))])
        for i, linha in enumerate(detalhe["D"]):
            w.writerow([f"no{i}"] + [round(v, 1) for v in linha])

    melhor_ag = min(detalhe["ag"], key=lambda r: r.custo)
    caminho_otimo = caminho_completo(
        detalhe["grade"], detalhe["nos"], detalhe["ordem_otima"]
    )
    rotulos = [0] * len(detalhe["nos"])
    for posicao, indice in enumerate(detalhe["ordem_otima"][1:], 1):
        rotulos[indice] = posicao
    desenhar_mapa(
        detalhe["grade"],
        [(caminho_otimo, "#1f77b4", "Rota A* (otima)", "-")],
        os.path.join(SAIDA, "mapa_parte2_rota.png"),
        detalhe["nos"][0],
        None,
        detalhe["nos"][1:],
        "Parte 2 - rota otima de entregas (A*), numerada na ordem de visita",
        rotulos_pontos=rotulos[1:],
    )
    desenhar_convergencia(
        melhor_ag.historico_melhor,
        melhor_ag.historico_medio,
        os.path.join(SAIDA, "convergencia_ag.png"),
    )
    return tab_detalhe, resumo_cab + resumo, agregado, detalhe


def main():
    print("=" * 70)
    print("PARTE 1 - CAMINHO MINIMO NA GRADE (A* x BUSCA GULOSA)")
    print("=" * 70)
    tab1, medias, linhas = parte1()
    print(tab1)
    print(
        f"Media de nos expandidos: A* = {medias['exp_a']:.1f} | "
        f"guloso = {medias['exp_g']:.1f} ({medias['taxa']:.1f}% do A*)"
    )
    print(
        f"Custo extra medio do guloso: {medias['extra']:.2f}% "
        f"(maximo {medias['extra_max']:.2f}%), subotimo em "
        f"{medias['subotimos']}/{len(linhas)} instancias"
    )
    print(f"Tempo medio: A* = {medias['ms_a']:.2f} ms | guloso = {medias['ms_g']:.2f} ms")

    print()
    print("=" * 70)
    print("PARTE 2 - MELHOR ORDEM DE ENTREGA (A* x GULOSO x AG)")
    print("=" * 70)
    tab2, tab_resumo, ag, det = parte2()
    print(tab2)
    print("Resumo em 5 instancias:")
    print(tab_resumo)
    print(f"Ordem otima (A*): {det['ordem_otima']}")
    print(f"Ordem guloso   : {det['nn_ordem']}  (gap {det['nn_gap']:.1f}%)")
    print(
        f"AG: gap medio {ag['gap_ag_medio']:.2f}% | pior melhor-execucao "
        f"{ag['gap_ag_max']:.2f}% | otimo em {ag['otimos_ag']}/{ag['total_ag']} execucoes"
    )

    with open(os.path.join(SAIDA, "tabelas.md"), "w", encoding="utf-8") as f:
        f.write("## Parte 1 - caminho na grade\n\n")
        f.write(tab1)
        f.write(
            f"\nMedia de nos expandidos: **A\\* {medias['exp_a']:.1f}** vs "
            f"**guloso {medias['exp_g']:.1f}** ({medias['taxa']:.1f}% do A*). "
            f"Custo extra medio do guloso: **{medias['extra']:.2f}%** "
            f"(maximo {medias['extra_max']:.2f}%).\n"
        )
        f.write("\n## Parte 2 - instancia detalhada (semente 7, 10 entregas)\n\n")
        f.write(tab2)
        f.write("\n## Parte 2 - resumo em 5 instancias\n\n")
        f.write(tab_resumo)
        f.write(
            f"\nGap medio do AG: **{ag['gap_ag_medio']:.2f}%**; "
            f"otimo em **{ag['otimos_ag']}/{ag['total_ag']}** execucoes.\n"
        )

    print("\nArquivos gerados em:", SAIDA)


if __name__ == "__main__":
    main()
