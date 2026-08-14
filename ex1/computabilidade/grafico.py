"""Módulo 6: gráfico de consumo da pilha para a função de Ackermann."""

import sys
from importlib import import_module


def testar_limites_ackermann_v3(m_max: int, n_max: int, stack_limit: int, mostrar=True):
    """Mede a profundidade de chamadas de Ackermann e pode exibir um gráfico."""
    sys.setrecursionlimit(stack_limit)

    casos = []
    picos_pilha = []
    estourou = False

    def ack_depth_fast(m, n, depth=1):
        nonlocal max_d
        max_d = max(max_d, depth)

        if m == 0:
            return n + 1
        if n == 0:
            return ack_depth_fast(m - 1, 1, depth + 1)
        return ack_depth_fast(
            m - 1,
            ack_depth_fast(m, n - 1, depth + 1),
            depth + 1,
        )

    entradas_teste = [
        (m, n) for m in range(m_max + 1) for n in range(n_max + 1)
    ]

    for m, n in entradas_teste:
        if estourou:
            break

        max_d = 0
        rotulo = f"$A({m}, {n})$"

        try:
            ack_depth_fast(m, n)
            casos.append(rotulo)
            picos_pilha.append(max_d)
        except RecursionError:
            casos.append(f"{rotulo}*")
            picos_pilha.append(stack_limit)
            estourou = True

    if mostrar:
        _plotar_consumo_pilha(casos, picos_pilha, stack_limit)

    return casos, picos_pilha


def _importar_pyplot():
    """Importa matplotlib apenas quando o gráfico é solicitado."""
    try:
        return import_module("matplotlib.pyplot")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "A visualização requer matplotlib. Instale-o com: "
            "python -m pip install matplotlib"
        ) from exc


def _plotar_consumo_pilha(casos, picos_pilha, stack_limit):
    """Renderiza os resultados da medição de profundidade da pilha."""
    plt = _importar_pyplot()

    plt.figure(figsize=(12, 6))
    cores = [
        "#3498db" if pico < stack_limit else "#e74c3c"
        for pico in picos_pilha
    ]
    barras = plt.bar(casos, picos_pilha, color=cores, width=0.55)

    plt.yscale("log")
    plt.axhline(
        y=stack_limit,
        color="#2c3e50",
        linestyle="--",
        linewidth=1.5,
        label=f"Limite da Pilha ({stack_limit})",
    )
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.title(
        f"Pico Máximo de Profundidade da Pilha (Limite: {stack_limit})",
        fontsize=12,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel(
        "Entrada $A(m, n)$ (* = Estouro de Pilha / Crash)",
        fontsize=10,
        labelpad=10,
    )
    plt.ylabel("Profundidade Máxima de Chamadas (Escala Log10)", fontsize=10)
    plt.grid(True, which="both", linestyle=":", alpha=0.4)
    plt.ylim(bottom=0.8, top=stack_limit * 4)

    for barra in barras:
        valor = barra.get_height()
        plt.text(
            barra.get_x() + barra.get_width() / 2.0,
            valor * 1.25,
            f"{valor:,}",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
        )

    plt.legend(loc="upper left", frameon=True)
    plt.tight_layout()
    plt.show()
