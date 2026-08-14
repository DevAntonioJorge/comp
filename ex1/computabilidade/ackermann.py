"""Módulo 3: função de Ackermann e operador de minimização (μ)."""

from .basicas import S


def ackermann(m: int, n: int) -> int:
    """
    Função de Ackermann-Péter:

    - ``A(0, n) = n + 1``
    - ``A(m, 0) = A(m - 1, 1)``
    - ``A(m, n) = A(m - 1, A(m, n - 1))``
    """
    if m == 0:
        return n + 1
    if n == 0:
        return ackermann(m - 1, 1)
    return ackermann(m - 1, ackermann(m, n - 1))


def mu_operator(f, target=0):
    """
    Operador de minimização não limitado (μ).

    Retorna o menor ``y ∈ ℕ`` tal que ``f(y) == target``. Como a busca é
    deliberadamente não limitada, a função não termina se tal ``y`` não
    existir.
    """
    y = 0
    while True:
        if f(y) == target:
            return y
        y = S(y)
