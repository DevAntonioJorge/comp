"""Demonstração dos conceitos de computabilidade do projeto.

O código foi dividido em módulos no pacote :mod:`computabilidade`. Este
arquivo permanece como ponto de entrada para executar as demonstrações que
antes estavam misturadas no notebook Jupyter.
"""

import sys

from computabilidade.ackermann import ackermann, mu_operator
from computabilidade.basicas import P, S, Z
from computabilidade.benchmark import benchmark
from computabilidade.frp import add_frp, mult_frp
from computabilidade.grafico import testar_limites_ackermann_v3
from computabilidade.raiz import sqrt_frp_bounded, sqrt_mu_unbounded

# Limite usado na demonstração de Ackermann e no gráfico de profundidade.
STACK_LIMIT = 100_000


def demonstrar_funcoes_basicas() -> None:
    """Executa os exemplos do módulo de funções básicas iniciais."""
    print("--- Testes das Funções Básicas ---")
    print(f"Z(10) = {Z(10)}")
    print(f"S(5) = {S(5)}")
    print(f"P_2^3(10, 20, 30) = {P(2, 3, 10, 20, 30)}")


def demonstrar_frp() -> None:
    """Executa os exemplos das funções recursivas primitivas."""
    print("--- Testes das Funções Recursivas Primitivas ---")
    print(f"add_frp(7, 8) = {add_frp(7, 8)}")
    print(f"mult_frp(4, 5) = {mult_frp(4, 5)}")


def demonstrar_ackermann_e_mu() -> None:
    """Executa os exemplos de Ackermann e do operador de minimização."""
    print("--- Testes da Função de Ackermann ---")
    print(f"A(1, 2) = {ackermann(1, 2)}")
    print(f"A(2, 2) = {ackermann(2, 2)}")
    print(f"A(3, 3) = {ackermann(3, 3)}")
    print(f"A(3, 4) = {ackermann(3, 4)}")

    x_test = 49
    raiz_exata = mu_operator(lambda y: mult_frp(y, y) - x_test)
    print("\n--- Teste do Operador μ ---")
    print(f"Menor y tal que y^2 = {x_test} -> y = {raiz_exata}")


def demonstrar_raizes() -> None:
    """Compara as duas implementações da raiz quadrada de piso."""
    test_val = 20
    print(f"Raiz de piso (FRP Bounded) de {test_val}: {sqrt_frp_bounded(test_val)}")
    print(f"Raiz de piso (μ Unbounded) de {test_val}: {sqrt_mu_unbounded(test_val)}")


def executar_demonstracoes() -> None:
    """Executa os módulos 1 a 4 em sequência."""
    demonstrar_funcoes_basicas()
    demonstrar_frp()
    demonstrar_ackermann_e_mu()
    demonstrar_raizes()


def main() -> None:
    """Executa demonstrações, benchmark e gráfico do projeto."""
    sys.setrecursionlimit(STACK_LIMIT)

    executar_demonstracoes()
    benchmark()
    _ = testar_limites_ackermann_v3(
        m_max=4,
        n_max=2,
        stack_limit=STACK_LIMIT,
    )


if __name__ == "__main__":
    main()
