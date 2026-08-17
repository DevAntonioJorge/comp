# ============================================================
# OPÇÃO 2 - PROVA VISUAL E INTERATIVA
# A Diagonalização de Cantor e o Problema da Parada
# ============================================================


class LoopSimulado(Exception):
    """Representa um loop sem deixar a demonstração travar a aplicação."""


def validar_matriz(programas, entradas, matriz):
    if not programas or len(programas) != len(entradas):
        raise ValueError("A matriz precisa ter a mesma quantidade de programas e entradas.")

    if len(matriz) != len(programas):
        raise ValueError("A matriz precisa ter uma linha para cada programa.")

    for linha in matriz:
        if len(linha) != len(entradas):
            raise ValueError("Todas as linhas da matriz precisam ter o mesmo tamanho.")

        if any(valor not in (0, 1) for valor in linha):
            raise ValueError("A matriz deve conter apenas 0 e 1.")


def mostrar_matriz(programas, entradas, matriz):
    validar_matriz(programas, entradas, matriz)

    print("\n" + "=" * 60)
    print("MATRIZ DE PROGRAMAS x ENTRADAS")
    print("=" * 60)

    largura_programa = max(8, max(len(str(programa)) for programa in programas) + 2)
    largura_entrada = max(8, max(len(str(entrada)) for entrada in entradas) + 2)

    print(f"{'':>{largura_programa}}", end="")
    for entrada in entradas:
        print(f"{entrada:^{largura_entrada}}", end="")
    print()

    for programa, linha in zip(programas, matriz):
        print(f"{programa:>{largura_programa}}", end="")
        for valor in linha:
            print(f"{valor:^{largura_entrada}}", end="")
        print()

    print("\n0 = não para")
    print("1 = para")


def diagonalizacao(sequencias):
    if not sequencias:
        raise ValueError("A lista de sequências não pode ser vazia.")

    tamanho = len(sequencias)

    for sequencia in sequencias:
        if len(sequencia) != tamanho:
            raise ValueError(
                "É necessário informar N sequências, cada uma com exatamente N bits."
            )
        if any(bit not in "01" for bit in sequencia):
            raise ValueError("As sequências devem conter apenas os bits 0 e 1.")

    print("\n" + "=" * 60)
    print("DIAGONALIZAÇÃO DE CANTOR")
    print("=" * 60)
    print("\nEsta é uma visualização finita da ideia 2^ℵ₀ > ℵ₀.")

    print("\nLista original:")
    for i, sequencia in enumerate(sequencias):
        print(f"{i + 1}: {sequencia}")

    print("\nConstruindo a nova sequência...")
    print("Cada bit diagonal será invertido.\n")

    nova_sequencia = []

    for i, sequencia in enumerate(sequencias):
        bit = sequencia[i]
        novo_bit = "1" if bit == "0" else "0"
        nova_sequencia.append(novo_bit)

        print(
            f"Posição {i + 1}: sequência {i + 1} possui "
            f"bit {bit} -> novo bit = {novo_bit}"
        )

    resultado = "".join(nova_sequencia)

    print("\nNova sequência:")
    print(resultado)

    print("\n" + "-" * 60)
    print("VERIFICAÇÃO")
    print("-" * 60)

    pertence = resultado in sequencias
    if pertence:
        print("A nova sequência seria igual a uma sequência da lista.")
        print("Isso indica que os dados fornecidos não formam uma matriz N x N válida.")
        return resultado

    print("A nova sequência NÃO pertence à lista original.")
    for i in range(tamanho):
        print(
            f"Ela é diferente da sequência {i + 1} na posição {i + 1}."
        )

    print("\nPortanto, a lista original estava incompleta.")
    print(
        "Na prova geral, o mesmo argumento é aplicado a uma suposta "
        "enumeração de sequências infinitas."
    )

    return resultado


def programa_para(entrada):
    """Programa fictício que sempre termina."""
    return "HALT"


def programa_loop(entrada):
    """Programa fictício que representa um loop sem executá-lo de verdade."""
    return "LOOP"


def programa_condicional(entrada):
    """Programa fictício que para apenas quando recebe '1'."""
    if entrada == "1":
        return "HALT"

    return "LOOP"


def analisador_halting(programa, entrada):
    """
    Simula um suposto analisador perfeito do problema da parada.

    A demonstração usa programas fictícios que retornam HALT ou LOOP
    imediatamente. Um analisador real não poderia executar um programa
    arbitrário dessa maneira sem correr o risco de ficar preso em um loop.
    """
    resultado = programa(entrada)

    if resultado not in ("HALT", "LOOP"):
        raise ValueError("O programa fictício deve retornar HALT ou LOOP.")

    return resultado == "HALT"


def comportamento_diagonal(resposta_analisador):
    """Executa o comportamento inverso definido pelo programa diagonal."""
    if resposta_analisador:
        raise LoopSimulado("DIAGONAL entrou em loop.")

    return "HALT"


def diagonal(programa):
    """
    Programa fictício usado na prova de Turing.

    Ele pergunta ao analisador se o próprio programa recebido para quando
    recebe a si mesmo como entrada e faz o contrário da resposta. A chamada
    diagonal(diagonal) não é executada diretamente, pois ela representa o
    paradoxo que a demonstração simula de forma controlada.
    """
    resultado = analisador_halting(programa, programa)
    return comportamento_diagonal(resultado)


def demonstrar_contradicao():
    print("\n" + "=" * 60)
    print("SIMULAÇÃO DO PROBLEMA DA PARADA")
    print("=" * 60)

    print("\nSuponha que exista um analisador perfeito:")
    print("analisador_halting(programa, entrada)")
    print("\nEle deveria responder HALT ou LOOP para qualquer programa e entrada.")

    print("\nAgora definimos o programa diagonal:")
    print("1. Consulta o analisador sobre o próprio programa.")
    print("2. Se a resposta for HALT, entra em LOOP.")
    print("3. Se a resposta for LOOP, termina.")
    print("\nA chamada problemática seria equivalente a:")
    print("analisador_halting(diagonal, diagonal)")
    print(
        "\nA chamada não é executada literalmente para não travar a CLI; "
        "os dois resultados possíveis são simulados abaixo."
    )

    print("\n" + "-" * 60)
    print("CASO 1: o analisador responde HALT")
    print("-" * 60)
    try:
        comportamento_diagonal(True)
    except LoopSimulado as erro:
        print("Resposta do analisador: HALT")
        print(f"Comportamento de DIAGONAL: {erro}")
        print("Contradição: o analisador disse HALT, mas DIAGONAL não para.")

    print("\n" + "-" * 60)
    print("CASO 2: o analisador responde LOOP")
    print("-" * 60)
    resultado = comportamento_diagonal(False)
    print("Resposta do analisador: LOOP")
    print(f"Comportamento de DIAGONAL: {resultado}")
    print("Contradição: o analisador disse LOOP, mas DIAGONAL termina.")

    print("\n" + "=" * 60)
    print("CONCLUSÃO")
    print("=" * 60)
    print(
        "\nNão pode existir um algoritmo perfeito capaz de determinar, "
        "para qualquer programa e qualquer entrada, se o programa irá parar."
    )
    print(
        "Isso também impede a existência de um analisador estático perfeito "
        "de código que resolva essa pergunta para todos os programas."
    )


def testar_analisador():
    print("\n" + "=" * 60)
    print("TESTANDO O ANALISADOR FICTÍCIO")
    print("=" * 60)

    programas = [
        ("Programa que sempre para", programa_para),
        ("Programa que sempre entra em loop", programa_loop),
        ("Programa condicional", programa_condicional),
    ]

    entradas = ["0", "1"]

    for nome, programa in programas:
        print(f"\n{nome}")

        for entrada in entradas:
            resultado = analisador_halting(programa, entrada)
            resposta = "HALT" if resultado else "LOOP"
            print(f"Entrada {entrada}: {resposta}")


def ler_inteiro(mensagem):
    while True:
        try:
            valor = int(input(mensagem))
        except ValueError:
            print("Digite um número inteiro positivo.")
            continue

        if valor > 0:
            return valor

        print("Digite um número inteiro positivo.")


def ler_bits(mensagem, tamanho):
    while True:
        bits = input(mensagem).strip().replace(" ", "")

        if len(bits) == tamanho and all(bit in "01" for bit in bits):
            return bits

        print(f"Digite exatamente {tamanho} bits, usando apenas 0 e 1.")


def ler_matriz():
    print("\nInforme os dados da matriz N x N.")
    tamanho = ler_inteiro("Quantidade de programas e entradas: ")

    programas = []
    entradas = []

    for i in range(tamanho):
        nome = input(f"Nome do programa {i + 1} [P{i + 1}]: ").strip()
        programas.append(nome or f"P{i + 1}")

    for i in range(tamanho):
        nome = input(f"Nome da entrada {i + 1} [E{i + 1}]: ").strip()
        entradas.append(nome or f"E{i + 1}")

    matriz = []
    for programa in programas:
        bits = ler_bits(
            f"Resultados de {programa} para {', '.join(entradas)} "
            f"(0/1): ",
            tamanho,
        )
        matriz.append([int(bit) for bit in bits])

    mostrar_matriz(programas, entradas, matriz)


def ler_sequencias():
    print("\nInforme uma matriz N x N de bits para a diagonalização.")
    tamanho = ler_inteiro("Quantidade de sequências (N): ")
    sequencias = []

    for i in range(tamanho):
        sequencias.append(
            ler_bits(f"Sequência {i + 1} ({tamanho} bits): ", tamanho)
        )

    return sequencias


def exemplo_matriz():
    programas = ["P1", "P2", "P3", "P4"]
    entradas = ["E1", "E2", "E3", "E4"]
    matriz = [
        [1, 0, 1, 1],
        [0, 1, 0, 1],
        [1, 1, 0, 0],
        [0, 1, 1, 0],
    ]

    mostrar_matriz(programas, entradas, matriz)


def executar_diagonalizacao():
    try:
        sequencias = ler_sequencias()
        diagonalizacao(sequencias)
    except ValueError as erro:
        print(f"\nErro: {erro}")


def menu():
    while True:
        print("\n")
        print("=" * 60)
        print("PROJETO - DIAGONALIZAÇÃO DE CANTOR")
        print("E PROBLEMA DA PARADA")
        print("=" * 60)

        print("\n1 - Criar e mostrar matriz N x N")
        print("2 - Executar diagonalização de Cantor")
        print("3 - Testar analisador de parada")
        print("4 - Demonstrar contradição de Turing")
        print("5 - Executar demonstração completa")
        print("0 - Sair")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            ler_matriz()

        elif opcao == "2":
            executar_diagonalizacao()

        elif opcao == "3":
            testar_analisador()

        elif opcao == "4":
            demonstrar_contradicao()

        elif opcao == "5":
            exemplo_matriz()
            diagonalizacao(["0000", "1010", "1100", "0111"])
            testar_analisador()
            demonstrar_contradicao()

        elif opcao == "0":
            print("\nPrograma encerrado.")
            break

        else:
            print("\nOpção inválida.")


if __name__ == "__main__":
    menu()
