#!/usr/bin/env python3
"""
Projeto 13 - O Otimizador de Carga e a Assimetria da Verificação (P vs. NP)

Problema: Subset Sum (Soma de Subconjuntos).
  Dada uma lista de N pesos e uma capacidade K, existe um subconjunto cuja
  soma seja exatamente K?

  Versão A -> ENCONTRAR a resposta (busca em NP): força bruta, O(2^N).
  Versão B -> VERIFICAR uma resposta (certificado, classe P): laço simples, O(N).

Uso:
  python carga_p_vs_np.py
  Ajuste as variáveis globais de CONFIGURAÇÃO logo abaixo dos imports.
"""

import random
import time

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO (variáveis globais)
# ---------------------------------------------------------------------------
# Maior N testado na Parte 2 (valores usados: 10, 15, 20, 22, 25, 28, 30).
# 22 = demonstração curta | 25 = padrão (~10 s) | 30 = demora vários minutos.
MAX_N = 25

# Se for um inteiro (ex.: 30), roda APENAS a Versão A, no pior caso, com esse N
# e ignora as demais partes. Deixe None para a demonstração completa.
N_UNICO = None


# ---------------------------------------------------------------------------
# VERSÃO A - O Pesadelo da Resolução (busca em NP)
# ---------------------------------------------------------------------------
def encontrar_carga_perfeita(lista_pesos, capacidade_alvo):
    """
    Força bruta recursiva. Para cada contêiner há duas decisões:
    colocá-lo no avião ou deixá-lo de fora. Isso gera uma árvore binária
    de altura N com 2^N folhas = todas as combinações possíveis.

    Sem poda proposital: o objetivo é expor o custo O(2^N) do caso geral.

    Retorna a lista de pesos escolhidos (ou None se não existir solução).
    O total de chamadas recursivas fica em encontrar_carga_perfeita.chamadas.
    """
    n = len(lista_pesos)
    escolhidos = []
    contador = [0]  # lista para poder alterar dentro da função aninhada

    def explorar(i, soma):
        contador[0] += 1
        if i == n:  # folha: uma combinação completa foi montada
            return soma == capacidade_alvo

        # Ramo 1: INCLUI o contêiner i
        escolhidos.append(lista_pesos[i])
        if explorar(i + 1, soma + lista_pesos[i]):
            return True
        escolhidos.pop()

        # Ramo 2: NÃO inclui o contêiner i
        return explorar(i + 1, soma)

    achou = explorar(0, 0)
    encontrar_carga_perfeita.chamadas = contador[0]
    return list(escolhidos) if achou else None


encontrar_carga_perfeita.chamadas = 0


# ---------------------------------------------------------------------------
# VERSÃO B - O Certificado Polinomial (classe P)
# ---------------------------------------------------------------------------
def verificar_manifesto(lista_proposta, capacidade_alvo):
    """
    Recebe um Manifesto de Carga (certificado) e apenas confere se a soma
    bate com o alvo. Um único laço: O(N) tempo, O(1) memória extra.
    """
    soma = 0
    for peso in lista_proposta:
        soma += peso
    return soma == capacidade_alvo


# ---------------------------------------------------------------------------
# Utilitários de demonstração
# ---------------------------------------------------------------------------
def humanizar(segundos):
    """Converte segundos em uma unidade legível (s, min, h, dias, anos)."""
    if segundos < 1e-3:
        return f"{segundos * 1e6:.1f} µs"
    if segundos < 1:
        return f"{segundos * 1e3:.1f} ms"
    if segundos < 60:
        return f"{segundos:.2f} s"
    if segundos < 3600:
        return f"{segundos / 60:.1f} min"
    if segundos < 86400:
        return f"{segundos / 3600:.1f} h"
    if segundos < 86400 * 365:
        return f"{segundos / 86400:.1f} dias"
    anos = segundos / (86400 * 365)
    return f"{anos:.2e} anos" if anos >= 1e6 else f"{anos:,.1f} anos"


def gerar_instancia_sem_solucao(n, semente=42):
    """
    Pior caso: pesos pares e alvo ímpar => nenhuma combinação satisfaz o
    alvo, então a busca é obrigada a percorrer TODAS as 2^N combinações.
    """
    rng = random.Random(semente)
    pesos = [rng.randrange(2, 200, 2) for _ in range(n)]
    alvo = sum(pesos) // 2 | 1  # força ímpar
    return pesos, alvo


def gerar_instancia_com_solucao(n, semente=7):
    """Instância em que existe solução (soma de um subconjunto sorteado)."""
    rng = random.Random(semente)
    pesos = [rng.randint(1, 100) for _ in range(n)]
    subconjunto = rng.sample(pesos, k=max(1, n // 2))
    return pesos, sum(subconjunto)


def medir_versao_a(pesos, alvo):
    inicio = time.perf_counter()
    resultado = encontrar_carga_perfeita(pesos, alvo)
    tempo = time.perf_counter() - inicio
    return resultado, encontrar_carga_perfeita.chamadas, tempo


# ---------------------------------------------------------------------------
# Demonstrações
# ---------------------------------------------------------------------------
def parte_1_exemplo_pequeno():
    print("=" * 72)
    print("PARTE 1 - Versão A com 10 pacotes (caso com solução)")
    print("=" * 72)
    pesos, alvo = gerar_instancia_com_solucao(10)
    print(f"Pesos: {pesos}")
    print(f"Capacidade alvo K = {alvo}")

    resultado, chamadas, tempo = medir_versao_a(pesos, alvo)
    print(f"Manifesto encontrado: {resultado}")
    print(f"Chamadas recursivas: {chamadas:,} | Tempo: {humanizar(tempo)}")

    # O certificado encontrado é validado pela Versão B
    print(f"Versão B confirma o manifesto? {verificar_manifesto(resultado, alvo)}")
    print()


def parte_2_crescimento_exponencial(max_n):
    print("=" * 72)
    print("PARTE 2 - Versão A: o tempo explode com N (pior caso, sem solução)")
    print("=" * 72)
    print(f"{'N':>4} | {'2^N':>14} | {'chamadas':>14} | {'tempo':>10} | {'x anterior':>10}")
    print("-" * 66)

    tamanhos = [n for n in (10, 15, 20, 22, 25, 28, 30) if n <= max_n]
    tempo_anterior = None
    custo_por_chamada = None

    for n in tamanhos:
        pesos, alvo = gerar_instancia_sem_solucao(n)
        _, chamadas, tempo = medir_versao_a(pesos, alvo)
        razao = f"{tempo / tempo_anterior:.0f}x" if tempo_anterior else "-"
        print(f"{n:>4} | {2 ** n:>14,} | {chamadas:>14,} | {humanizar(tempo):>10} | {razao:>10}")
        tempo_anterior = tempo
        custo_por_chamada = tempo / chamadas  # usa a medição do maior N

    # Extrapolação: T(N) ≈ custo_por_chamada * (2^(N+1) - 1)
    print("\nProjeção para N maiores (T(N) ≈ t_chamada * (2^(N+1) - 1)):")
    print(f"  custo medido por chamada ≈ {custo_por_chamada * 1e9:.0f} ns")
    for n in (30, 40, 50, 64, 100):
        estimado = custo_por_chamada * (2 ** (n + 1) - 1)
        print(f"  N = {n:>3} -> {humanizar(estimado)}")
    print()


def parte_3_verificacao_linear():
    print("=" * 72)
    print("PARTE 3 - Versão B: verificar manifestos gigantes (classe P)")
    print("=" * 72)
    n = 1_000_000
    rng = random.Random(1)
    manifesto = [rng.randint(1, 100) for _ in range(n)]
    alvo_correto = sum(manifesto)

    inicio = time.perf_counter()
    ok = verificar_manifesto(manifesto, alvo_correto)
    t1 = time.perf_counter() - inicio
    print(f"Manifesto com {n:,} pacotes, alvo correto   -> {ok} em {humanizar(t1)}")

    inicio = time.perf_counter()
    ok = verificar_manifesto(manifesto, alvo_correto + 1)
    t2 = time.perf_counter() - inicio
    print(f"Manifesto com {n:,} pacotes, alvo incorreto -> {ok} em {humanizar(t2)}")

    # Crescimento linear: dobrar N ~ dobra o tempo
    print("\nCrescimento linear O(N):")
    for tam in (250_000, 500_000, 1_000_000, 2_000_000):
        lista = [rng.randint(1, 100) for _ in range(tam)]
        alvo = sum(lista)
        inicio = time.perf_counter()
        verificar_manifesto(lista, alvo)
        print(f"  N = {tam:>9,} -> {humanizar(time.perf_counter() - inicio)}")
    print()


def parte_4_comparacao():
    print("=" * 72)
    print("PARTE 4 - Assimetria: encontrar x verificar com o MESMO N = 25")
    print("=" * 72)
    pesos, alvo = gerar_instancia_com_solucao(25)
    # Pior caso para a busca: mesma lista, alvo impossível
    alvo_impossivel = sum(pesos) + 1

    inicio = time.perf_counter()
    verificar_manifesto(pesos, alvo)
    t_verificar = time.perf_counter() - inicio

    _, chamadas, t_buscar = medir_versao_a(pesos, alvo_impossivel)
    print(f"Verificar (Versão B): {humanizar(t_verificar)} ({len(pesos)} somas)")
    print(f"Buscar    (Versão A): {humanizar(t_buscar)} ({chamadas:,} chamadas)")
    if t_verificar > 0:
        print(f"Assimetria: a busca foi ~{t_buscar / t_verificar:,.0f}x mais lenta.")
    print()


def main():
    if N_UNICO is not None:
        print(f"Versão A, pior caso, N = {N_UNICO} (aguarde...)")
        pesos, alvo = gerar_instancia_sem_solucao(N_UNICO)
        _, chamadas, tempo = medir_versao_a(pesos, alvo)
        print(f"Chamadas: {chamadas:,} | Tempo: {humanizar(tempo)}")
        return

    parte_1_exemplo_pequeno()
    parte_2_crescimento_exponencial(MAX_N)
    parte_3_verificacao_linear()
    parte_4_comparacao()


if __name__ == "__main__":
    main()
