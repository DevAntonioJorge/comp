"""Módulo 4: raiz quadrada por FRP e por minimização (μ)."""

from .ackermann import mu_operator
from .basicas import S
from .frp import mult_frp


def sqrt_frp_bounded(x: int) -> int:
    """
    Raiz quadrada de piso usando uma busca limitada por FRP.

    Retorna o maior ``y`` tal que ``y² <= x``. O limite ``x`` garante a
    parada para entradas naturais.
    """
    ans = 0
    for y in range(x + 1):
        if mult_frp(y, y) <= x:
            ans = y
        else:
            break
    return ans


def sqrt_mu_unbounded(x: int) -> int:
    """
    Raiz quadrada de piso usando busca não limitada (operador μ).

    Procura o menor ``y`` tal que ``(y + 1)² > x``. Esse valor é a raiz
    quadrada de piso. A forma usada no código representa a busca por um
    predicado com valores 0 e 1.
    """
    def pred(y):
        return 0 if mult_frp(S(y), S(y)) > x else 1

    return mu_operator(pred, target=0)
