import sys


# =============================================================================
# VERSÃO A (Tradicional/Pragmática)
# =============================================================================

def soma_tradicional(x, y):
    """Soma pragmática: apenas delega ao operador nativo do Python."""
    return x + y


def rodar_versao_a(x, y):
    print("=" * 60)
    print("VERSÃO A - Tradicional/Pragmática")
    print("=" * 60)

    # Chamada de teste 1: dados válidos (os números digitados pelo usuário).
    print(f"[Teste 1] Dados válidos ({x}, {y}):")
    print("Resultado:", soma_tradicional(x, y))

    # Chamada de teste 2: dados corrompidos -- simula falha catastrófica.
    # Loop infinito descuidado: em caso de erro de validação, o programa
    # simplesmente trava (busca ingênua sem critério de parada), pois não
    # existe nenhum "Guardião" limitando as tentativas.
    print("\n[Teste 2] Dados corrompidos (None, 7):")
    x_corrompido, y_corrompido = None, 7

    while True:
        if x_corrompido is None or y_corrompido is None:
            # Sem critério de parada real: apenas re-tenta a validação
            # indefinidamente, travando o programa de propósito.
            print("Erro de validação: dado corrompido. Tentando novamente...")
            break  # removido o 'break' abaixo demonstraria o travamento real
        else:
            print("Resultado:", soma_tradicional(x_corrompido, y_corrompido))
            break

    # Para demonstrar de fato o travamento catastrófico (sem interromper
    # a execução do restante do script), descomente as linhas abaixo:
    #
    # while True:
    #     if x is None or y is None:
    #         pass  # nunca sai daqui -- trava o programa de propósito
    print("(Loop de validação sem limite, travaria aqui.)")


# =============================================================================
# VERSÃO B (O Pipeline Teórico de Computabilidade)
# =============================================================================

# --- Fase 1: Cardinalidade e Conjuntos -- Função de Emparelhamento de Cantor ---

def cantor_pairing(x, y):
    """
    Função de Emparelhamento de Cantor: pi(x, y) = (x+y)(x+y+1)/2 + y

    Codifica um par (x, y) em N x N em um único número natural z,
    demonstrando a enumerabilidade de N x N -> N.
    """
    return (x + y) * (x + y + 1) // 2 + y


def cantor_unpairing(z):
    """
    Inversa da Função de Cantor: recupera (x, y) a partir de z.
    """
    w = int((( (8 * z + 1) ** 0.5 - 1) / 2))
    t = (w * w + w) // 2
    y = z - t
    x = w - y
    return x, y


# --- Fase 2: Máquina de Turing e Decidibilidade ---

class TimeoutError(Exception):
    """Exceção segura levantada pelo Guardião de Parada."""


def maquina_de_turing_validador(z, max_passos=10000):
    fita = "1" * z
    cabeca = 0
    passos = 0

    fita_exibicao = fita if len(fita) <= 50 else fita[:50] + f"...' (+{len(fita) - 50} símbolos)"
    print(f"[Fase 2] Fita gerada (notação unária): '{fita_exibicao} (tamanho={len(fita)})")

    while cabeca < len(fita):
        passos += 1

        if passos > max_passos:
            # O Guardião de Parada: aborta e levanta exceção segura.
            raise TimeoutError(
                f"Guardião de Parada acionado: excedidos {max_passos} passos. "
                "Halting Problem -- não é possível decidir se a fita terminaria."
            )

        if fita[cabeca] != "1":
            raise ValueError("Símbolo inválido encontrado na fita.")

        cabeca += 1

    print(f"[Fase 2] Fita validada com sucesso em {passos} passos "
          f"(dentro do limite de {max_passos}).")
    return True


# --- Fase 3: O Motor Recursivo Primitivo (axiomas de Peano) ---

def ZERO():
    """Constante de Peano: zero."""
    return 0


def SUCESSOR(n):
    """Função sucessora de Peano: n -> n + 1 (sem usar o operador '+')."""
    return n + 1 if False else _sucessor_puro(n)


def _sucessor_puro(n):
    """
    Implementação pura do sucessor, construída apenas incrementando via
    contagem de unidades (evita literalmente o uso do operador '+').
    """
    unidades = [1 for _ in range(n)]
    unidades.append(1)
    return len(unidades)


def soma_recursiva(x, y):
    """
    Motor Recursivo Primitivo: soma x + y usando apenas ZERO e SUCESSOR,
    guiado pelo operador de Recursão Primitiva, sem usar '+'.

        soma(x, 0)        = x
        soma(x, SUCESSOR(y)) = SUCESSOR(soma(x, y - base))
    """
    if y == ZERO():
        return x
    return SUCESSOR(soma_recursiva(x, y - 1))


# --- Fase 4: O Motor Lambda-Calculus (numerais de Church) ---

# Numerais de Church construídos como abstrações lambda anônimas.
ZERO_CHURCH = lambda f: lambda x: x
UM_CHURCH = lambda f: lambda x: f(x)
DOIS = lambda f: lambda x: f(f(x))

# Operador de soma via beta-redução pura no cálculo lambda.
SOMA_LAMBDA = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))


def int_para_church(n):
    """Converte um inteiro Python em numeral de Church (n aplicações de f)."""
    if n == 0:
        return ZERO_CHURCH
    return lambda f: lambda x: f(int_para_church(n - 1)(f)(x))


def church_para_int(numeral_church):
    """Converte um numeral de Church de volta em inteiro Python (aplicando
    f = sucessor sobre x = 0)."""
    return numeral_church(lambda n: n + 1)(0)


def soma_lambda(x, y):
    """
    Motor Lambda-Calculus: instancia x e y como numerais de Church e
    executa a beta-redução pura via SOMA_LAMBDA para obter x + y.
    """
    church_x = int_para_church(x)
    church_y = int_para_church(y)
    resultado_church = SOMA_LAMBDA(church_x)(church_y)
    return church_para_int(resultado_church)


# --- Pipeline unificado da Versão B ---

def rodar_versao_b(x, y):
    print("=" * 60)
    print("VERSÃO B - Pipeline Teórico de Computabilidade")
    print("=" * 60)

    # Fase 1: Cardinalidade e Conjuntos
    z = cantor_pairing(x, y)
    print(f"\n[Fase 1] ID de Cantor gerado: pi({x}, {y}) = {z}")

    # Fase 2: Máquina de Turing e Decidibilidade
    maquina_de_turing_validador(z, max_passos=10000)

    # Recupera o par original a partir do ID via inversa de Cantor
    x_recuperado, y_recuperado = cantor_unpairing(z)
    print(f"[Fase 2] Par recuperado pela inversa de Cantor: "
          f"({x_recuperado}, {y_recuperado})")

    # Fase 3: Motor Recursivo Primitivo
    resultado_recursivo = soma_recursiva(x_recuperado, y_recuperado)
    print(f"\n[Fase 3] Motor Recursivo (Peano) -> Resultado: {resultado_recursivo}")

    # Fase 4: Motor Lambda-Calculus
    resultado_lambda = soma_lambda(x_recuperado, y_recuperado)
    print(f"[Fase 4] Motor Lambda-Calculus (Church) -> Resultado: {resultado_lambda}")

    # Prova final: ambos os motores, com paradigmas opostos, geram o
    # mesmo valor, unidos pela Tese de Church-Turing.
    print("\n" + "=" * 60)
    print("RESULTADO FINAL (impresso pelos dois motores):")
    print(f"  Motor Recursivo -> {resultado_recursivo}")
    print(f"  Motor Lambda    -> {resultado_lambda}")
    assert resultado_recursivo == resultado_lambda, "Divergência entre os motores!"
    print("Os dois motores concordam. Tese de Church-Turing demonstrada.")
    print("=" * 60)


# =============================================================================
# Ponto de entrada
# =============================================================================

''' if __name__ == "__main__":
        x = int(input("Digite o primeiro número (x): "))
        y = int(input("Digite o segundo número (y): "))

    rodar_versao_a(x, y)

    print("\n")

    try:
        rodar_versao_b(x, y)
    except TimeoutError as e:
        print(f"\n[ERRO CONTROLADO - Versão B] {e}")
    except ValueError as e:
        print(f"\n[ERRO - Versão B] {e}")'''
