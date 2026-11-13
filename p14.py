#!/usr/bin/env python3
"""
Projeto 14 - O Gerenciador de Dependencias e a Prova de Falha (NP-Completude e coNP)
Componente: Computabilidade e Complexidade Computacional

Representacao:
  - Um literal e uma tupla (pacote, valor): ("A", True) = "instalar A", ("A", False) = "nao instalar A" (!A)
  - Uma regra (clausula) e uma lista de literais ligados por OR.
  - O conjunto de regras e um AND de clausulas (forma CNF).
"""

import time
from collections import deque
from itertools import product


# ----------------------------------------------------------------------------
# Utilitarios
# ----------------------------------------------------------------------------
def neg(literal):
    """Nega um literal: A vira !A e !A vira A."""
    return (literal[0], not literal[1])


def fmt(literal):
    return literal[0] if literal[1] else "!" + literal[0]


def fmt_regra(clausula):
    return "(" + " or ".join(fmt(l) for l in clausula) + ")"


def regra_satisfeita(clausula, config):
    return any(config[nome] == valor for nome, valor in clausula)


# ----------------------------------------------------------------------------
# VERSAO A - NP-Completude: a busca pelo "SAT"
# ----------------------------------------------------------------------------
def verificar_certificado(regras, config):
    """
    Verificador de NP: dado um certificado (a lista final de pacotes
    instalados), checar se ele serve custa tempo POLINOMIAL (linear no
    tamanho das regras). Esta e a parte facil.
    """
    return all(regra_satisfeita(r, config) for r in regras)


def tentar_instalar(regras, pacotes):
    """
    Busca por forca bruta: gera a tabela verdade (2^n linhas) ate achar uma
    configuracao True/False em que todas as regras sao satisfeitas.
    Retorna (configuracao ou None, linhas_testadas).
    ACHAR a solucao e o lado dificil (exponencial no pior caso).
    """
    testadas = 0
    for valores in product([True, False], repeat=len(pacotes)):
        testadas += 1
        config = dict(zip(pacotes, valores))
        if verificar_certificado(regras, config):
            return config, testadas
    return None, testadas


# ----------------------------------------------------------------------------
# VERSAO B - coNP: a refutacao e o certificado de insatisfatibilidade
# ----------------------------------------------------------------------------
def construir_grafo_implicacoes(regras):
    """
    Cada regra vira implicacoes (arestas):
      (x or y)  equivale a  !x -> y  e  !y -> x
      (x)       equivale a  !x -> x     (x e obrigatorio)
    Retorna o grafo e um dicionario aresta -> indice da regra de origem.
    So aceita regras com 1 ou 2 literais (2-SAT).
    """
    grafo, origem = {}, {}
    for i, clausula in enumerate(regras):
        if not 1 <= len(clausula) <= 2:
            raise ValueError(
                f"Regra {fmt_regra(clausula)} nao suportada: use 1 ou 2 literais por regra."
            )
        if len(clausula) == 1:
            pares = [(neg(clausula[0]), clausula[0])]
        else:
            a, b = clausula
            pares = [(neg(a), b), (neg(b), a)]
        for u, v in pares:
            origem.setdefault((u, v), i)
            grafo.setdefault(u, []).append(v)
            grafo.setdefault(v, [])
    return grafo, origem


def caminho_mais_curto(grafo, inicio, fim):
    """BFS: devolve o menor caminho inicio -> fim, ou None se nao existir."""
    anterior = {inicio: None}
    fila = deque([inicio])
    while fila:
        u = fila.popleft()
        if u == fim:
            break
        for v in grafo.get(u, []):
            if v not in anterior:
                anterior[v] = u
                fila.append(v)
    if fim not in anterior:
        return None
    caminho, no = [], fim
    while no is not None:
        caminho.append(no)
        no = anterior[no]
    return caminho[::-1]


def extrair_contraexemplo_reduzido(regras):
    """
    Em vez de testar as 2^n linhas, procura o "ciclo fechado" que prova o
    conflito: um pacote X tal que  X -> ... -> !X  e  !X -> ... -> X.
    Ou seja, instalar X obriga a nao instalar X, e vice-versa: contradicao.

    Retorna (ciclo, indices_das_regras_usadas) ou None se NAO houver conflito.
    O ciclo e o CERTIFICADO POLINOMIAL de insatisfatibilidade.
    """
    grafo, origem = construir_grafo_implicacoes(regras)
    melhor = None
    for nome in sorted({n for n, _ in grafo}):
        x = (nome, True)
        ida = caminho_mais_curto(grafo, x, neg(x))
        if not ida:
            continue
        volta = caminho_mais_curto(grafo, neg(x), x)
        if not volta:
            continue
        ciclo = ida + volta[1:]
        if melhor is None or len(ciclo) < len(melhor):
            melhor = ciclo
    if melhor is None:
        return None
    usadas = sorted({origem[(u, v)] for u, v in zip(melhor, melhor[1:])})
    return melhor, usadas


def verificar_contraexemplo(regras, ciclo):
    """
    Verificador de coNP COM certificado: conferir o ciclo e trivial.
    Basta checar que (1) cada passo u -> v vem de alguma regra e (2) o ciclo
    fecha e contem um pacote junto com sua negacao. Tempo polinomial, sem
    precisar repassar a tabela verdade.
    """
    _, origem = construir_grafo_implicacoes(regras)
    if ciclo[0] != ciclo[-1]:
        return False
    if not all((u, v) in origem for u, v in zip(ciclo, ciclo[1:])):
        return False
    nos = set(ciclo)
    return any(neg(n) in nos for n in nos)


# ----------------------------------------------------------------------------
# Demonstracao
# ----------------------------------------------------------------------------
def separador(titulo):
    print("\n" + "=" * 70)
    print(titulo)
    print("=" * 70)


def demo_versao_a():
    separador("VERSAO A (NP): existe uma instalacao valida?")
    pacotes = ["A", "B", "C"]
    regra_1 = [("A", True), ("B", True)]    # (A or B): pelo menos um instalado
    regra_2 = [("B", False), ("C", True)]   # (not B or C): se instalar B, exige C
    regras = [regra_1, regra_2]

    for i, r in enumerate(regras, 1):
        print(f"  regra_{i} = {fmt_regra(r)}")

    config, testadas = tentar_instalar(regras, pacotes)
    if config is None:
        print("  Nenhuma configuracao valida encontrada.")
        return
    print(f"\n  Configuracao valida encontrada apos {testadas} linha(s) da tabela verdade:")
    for nome in pacotes:
        print(f"    {nome} = {config[nome]}")

    # [O CLIQUE - NP]
    # O certificado e a propria lista de pacotes (A=True, B=True, C=True).
    # Conferir se ele serve e rapido: uma passada pelas regras (tempo
    # polinomial). Ja ACHAR a configuracao pode exigir testar ate 2^n linhas.
    print(f"\n  verificar_certificado -> {verificar_certificado(regras, config)}")


def demo_versao_b():
    separador("VERSAO B (coNP): conflito irreparavel")
    pacotes = ["A", "B", "C"]
    regras = [
        [("A", False), ("B", True)],    # A exige B      = (!A or B)
        [("B", False), ("C", True)],    # B exige C      = (!B or C)
        [("C", False), ("A", False)],   # C conflita com A = (!C or !A)
        [("A", True)],                  # o usuario pediu: instalar A
    ]
    nomes = [
        "A exige B", "B exige C", "C conflita com A", "usuario pediu A",
    ]
    for i, (r, n) in enumerate(zip(regras, nomes), 1):
        print(f"  regra_{i} = {fmt_regra(r):<16} # {n}")

    config, testadas = tentar_instalar(regras, pacotes)
    print(f"\n  Forca bruta: {testadas} de {2 ** len(pacotes)} linhas testadas, "
          f"{'solucao achada' if config else 'todas falharam'}.")

    resultado = extrair_contraexemplo_reduzido(regras)
    if resultado is None:
        print("  Sem conflito.")
        return
    ciclo, usadas = resultado

    print("\n  ERRO: Impossivel resolver dependencias (Conflito Irreparavel)")
    print("  Ciclo logico proibido:")
    print("    " + " -> ".join(fmt(l) for l in ciclo))
    print("  Regras envolvidas no conflito:")
    for i in usadas:
        print(f"    regra_{i + 1} = {fmt_regra(regras[i])}  # {nomes[i]}")

    # [O CLIQUE - coNP]
    # Provar que NENHUMA combinacao serve, sem certificado, exigiria testar
    # as 2^n linhas da tabela verdade (trabalho exponencial). Com o
    # contraexemplo (o ciclo A -> B -> C -> !A -> A), qualquer pessoa
    # confere a prova em segundos, sem repassar a tabela verdade.
    print(f"\n  verificar_contraexemplo -> {verificar_contraexemplo(regras, ciclo)}")


def demo_escala(n=16):
    separador(f"ESCALA: cadeia de {n} pacotes (forca bruta vs. certificado)")
    nomes = [f"P{i}" for i in range(n)]
    regras = [[(nomes[i], False), (nomes[i + 1], True)] for i in range(n - 1)]
    regras.append([(nomes[-1], False), (nomes[0], False)])  # ultimo conflita com o primeiro
    regras.append([(nomes[0], True)])                       # primeiro e obrigatorio

    t0 = time.perf_counter()
    config, testadas = tentar_instalar(regras, nomes)
    t_bruta = time.perf_counter() - t0

    t0 = time.perf_counter()
    ciclo, _ = extrair_contraexemplo_reduzido(regras)
    ok = verificar_contraexemplo(regras, ciclo)
    t_ciclo = time.perf_counter() - t0

    print(f"  Forca bruta : {testadas:>7} linhas testadas em {t_bruta:.4f}s (cresce como 2^n)")
    print(f"  Contraexemplo: ciclo de {len(ciclo)} nos extraido e verificado ({ok}) em {t_ciclo:.5f}s")


if __name__ == "__main__":
    demo_versao_a()
    demo_versao_b()
    demo_escala()