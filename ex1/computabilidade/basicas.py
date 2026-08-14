"""Módulo 1: funções básicas iniciais da computabilidade."""


def Z(_x: int) -> int:
    """Função zero: ``Z(x) = 0``."""
    return 0


def S(x: int) -> int:
    """Função sucessor: ``S(x) = x + 1``."""
    return x + 1


def P(i: int, n: int, *args: int) -> int:
    """
    Função projeção: ``P_i^n(x_1, ..., x_n) = x_i``.

    ``i`` usa indexação baseada em 1, de acordo com a definição teórica.
    """
    if len(args) != n:
        raise ValueError(f"Esperado {n} argumentos, recebido {len(args)}")
    if i < 1 or i > n:
        raise IndexError(f"Índice i={i} fora dos limites para n={n}")
    return args[i - 1]
