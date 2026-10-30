"""
PROJETO 12 - O MOTOR DE ROTEAMENTO DECLARATIVO
Componente: Computabilidade e Complexidade Computacional

O arquivo contém as duas versões solicitadas no enunciado:
  VERSÃO A: cálculo iterativo/imperativo com Busca em Largura (BFS).
  VERSÃO B: representação lógica com fatos e regras, usando prova recursiva
            por encadeamento regressivo (backward chaining).

As duas versões utilizam o mesmo grafo e consultam a mesma rota.
Não é necessária a instalação de bibliotecas externas.
"""

from collections import deque


# ==============================================================
# DADOS COMPARTILHADOS PELAS DUAS VERSÕES
# ==============================================================

# Cada par (origem, destino) representa uma ligação direta no grafo.
LIGACOES = [
    ("Aracaju", "Itabaiana"),
    ("Aracaju", "Estancia"),
    ("Itabaiana", "Nossa Senhora da Gloria"),
    ("Estancia", "Lagarto"),
    ("Nossa Senhora da Gloria", "Propria"),
    ("Lagarto", "Propria"),
    ("Propria", "Caninde de Sao Francisco"),
    ("Estancia", "Itabaiana"),  # ligação adicional
]

ORIGEM = "Aracaju"
DESTINO = "Caninde de Sao Francisco"


# ==============================================================
# VERSÃO A - CÁLCULO ITERATIVO / IMPERATIVO TRADICIONAL
# ==============================================================

def construir_grafo(ligacoes):
    """Transforma a lista de ligações em uma lista de adjacência."""
    grafo = {}

    for origem, destino in ligacoes:
        if origem not in grafo:
            grafo[origem] = []
        if destino not in grafo:
            grafo[destino] = []

        grafo[origem].append(destino)

    return grafo


def encontrar_rota(origem, destino, ligacoes):
    """
    Encontra um caminho usando Busca em Largura (BFS).

    A fila controla os caminhos que ainda serão explorados.
    O conjunto visitados evita ciclos infinitos em grafos cíclicos.
    """
    grafo = construir_grafo(ligacoes)

    if origem == destino:
        return [origem]

    fila = deque([[origem]])
    visitados = {origem}

    while fila:
        caminho_atual = fila.popleft()
        no_atual = caminho_atual[-1]

        for vizinho in grafo.get(no_atual, []):
            if vizinho in visitados:
                continue

            novo_caminho = caminho_atual + [vizinho]

            if vizinho == destino:
                return novo_caminho

            visitados.add(vizinho)
            fila.append(novo_caminho)

    return None


def executar_versao_a():
    print("=" * 65)
    print("VERSÃO A - CÁLCULO ITERATIVO / IMPERATIVO (BFS)")
    print("=" * 65)

    rota = encontrar_rota(ORIGEM, DESTINO, LIGACOES)

    if rota:
        print("Rota encontrada:")
        print(" -> ".join(rota))
        print(f"Quantidade de conexões: {len(rota) - 1}")
    else:
        print(f"Não existe rota de {ORIGEM} até {DESTINO}.")

    return rota


# ==============================================================
# VERSÃO B - MAPEAMENTO EM LÓGICA DE PRIMEIRA ORDEM
# ==============================================================

# FATOS LÓGICOS:
# Ligado(A, B) significa que existe uma ligação direta de A para B.
#
# AXIOMA 1 - REGRA BASE:
# Para todos x e y:
#     Ligado(x, y) -> Rota(x, y)
#
# AXIOMA 2 - REGRA RECURSIVA (TRANSITIVIDADE):
# Para todos x, y e z:
#     (Ligado(x, z) e Rota(z, y)) -> Rota(x, y)
#
# O motor abaixo realiza encadeamento regressivo: para provar Rota(x, y),
# procura primeiro um fato Ligado(x, y). Caso não encontre, tenta provar
# a regra recursiva, escolhendo um z ligado diretamente a x e provando
# Rota(z, y). O conjunto de visitados impede ciclos durante a prova.


def provar_rota(origem, destino, fatos, visitados=None):
    """
    Motor lógico simplificado para a consulta Rota(origem, destino).

    Retorna uma lista com o caminho que constitui a prova, ou None
    quando não consegue provar a existência da rota.
    """
    if visitados is None:
        visitados = set()

    # Evita tentar provar novamente o mesmo objetivo no mesmo ramo.
    objetivo = (origem, destino)
    if objetivo in visitados:
        return None

    # Regra de identidade: um nó possui caminho até ele mesmo.
    if origem == destino:
        return [origem]

    novos_visitados = visitados | {objetivo}

    # AXIOMA 1: Regra base - Ligado(x, y) -> Rota(x, y)
    # Se o fato direto existir, a consulta está provada.
    if (origem, destino) in fatos:
        return [origem, destino]

    # AXIOMA 2: Regra recursiva:
    # Ligado(x, z) e Rota(z, y) -> Rota(x, y)
    # Para cada ligação que sai de x, tenta provar Rota(z, destino).
    for no_intermediario, proximo in fatos:
        if no_intermediario != origem:
            continue

        subprova = provar_rota(
            proximo,
            destino,
            fatos,
            novos_visitados
        )

        if subprova is not None:
            return [origem] + subprova

    return None


def executar_versao_b():
    print()
    print("=" * 65)
    print("VERSÃO B - MOTOR LÓGICO (LPO / REGRAS RECURSIVAS)")
    print("=" * 65)

    print("Fatos disponíveis: Ligado(origem, destino)")
    for origem, destino in LIGACOES:
        print(f"  Ligado({origem}, {destino})")

    print("\nRegras utilizadas:")
    print("  1. Ligado(x, y) -> Rota(x, y)")
    print("  2. Ligado(x, z) e Rota(z, y) -> Rota(x, y)")

    print(f"\nConsulta: Rota({ORIGEM}, {DESTINO})?")
    rota = provar_rota(ORIGEM, DESTINO, LIGACOES)

    if rota:
        print("Resultado: VERDADEIRO (a rota foi provada).")
        print("Caminho obtido:")
        print(" -> ".join(rota))
        print(f"Quantidade de conexões: {len(rota) - 1}")
    else:
        print("Resultado: FALSO (não foi possível provar a rota).")

    return rota


# ==============================================================
# EXECUÇÃO E COMPARAÇÃO DAS DUAS VERSÕES
# ==============================================================

def main():
    rota_a = executar_versao_a()
    rota_b = executar_versao_b()

    print()
    print("=" * 65)
    print("COMPARAÇÃO DOS RESULTADOS")
    print("=" * 65)

    if rota_a is not None and rota_b is not None:
        print("Versão A encontrou uma rota.")
        print("Versão B provou a existência de uma rota.")
        print("As duas versões chegaram ao mesmo destino.")

        # BFS garante caminho mínimo em número de arestas.
        # A prova lógica pode encontrar outro caminho válido, dependendo
        # da ordem dos fatos. Por isso, comparamos também a validade.
        if rota_a == rota_b:
            print("Os caminhos encontrados são idênticos.")
        else:
            print("Os caminhos são diferentes, mas ambos são válidos.")
            print("Versão A:", " -> ".join(rota_a))
            print("Versão B:", " -> ".join(rota_b))
    else:
        print("Pelo menos uma das versões não encontrou/provou a rota.")

    print("\nFIM DO PROJETO 12.")


if __name__ == "__main__":
    main()
