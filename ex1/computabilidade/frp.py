"""Módulo 2: funções recursivas primitivas (FRP)."""

from .basicas import S, Z


def add_frp(x: int, y: int) -> int:
    """
    Adição definida via FRP:

    - ``add(x, 0) = x``
    - ``add(x, y + 1) = S(add(x, y))``
    """
    result = x
    for _ in range(y):
        result = S(result)
    return result


def mult_frp(x: int, y: int) -> int:
    """
    Multiplicação definida via FRP:

    - ``mult(x, 0) = 0``
    - ``mult(x, y + 1) = add(mult(x, y), x)``
    """
    result = Z(x)
    for _ in range(y):
        result = add_frp(result, x)
    return result
