"""Módulo 5: benchmark e análise de desempenho."""

import time

from .ackermann import ackermann
from .raiz import sqrt_frp_bounded, sqrt_mu_unbounded


def benchmark():
    """Compara o tempo de Ackermann e das duas implementações de raiz."""
    ack_inputs = [(0, 0), (1, 2), (2, 2), (3, 3), (3, 4)]
    numeros = [100, 1000, 5000]

    print("==================================================")
    print("          BENCHMARK DE DESEMPENHO               ")
    print("==================================================\n")

    print("[1] Testando Limites de Crescimento da Função de Ackermann:")
    for m, n in ack_inputs:
        start = time.perf_counter()
        res = ackermann(m, n)
        elapsed = time.perf_counter() - start
        print(f"  A({m}, {n}) = {res:<10} | Tempo: {elapsed:.6f} segundos")

    print("\n[2] Comparando Busca FRP (Limitada) vs Busca μ (Minimização):")
    for n in numeros:
        start = time.perf_counter()
        r_frp = sqrt_frp_bounded(n)
        t_frp = time.perf_counter() - start

        start = time.perf_counter()
        r_mu = sqrt_mu_unbounded(n)
        t_mu = time.perf_counter() - start

        print(f"  Número: {n:<5}")
        print(f"    - FRP Bounded  : resultado={r_frp}, tempo={t_frp:.6f}s")
        print(f"    - μ Unbounded  : resultado={r_mu}, tempo={t_mu:.6f}s")
