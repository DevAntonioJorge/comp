#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projeto 10 — O Avaliador de Teoremas (Indecidibilidade em Lógica de Primeira Ordem)
Componente Curricular: Computabilidade e Complexidade Computacional

Uso:  python avaliador_teoremas.py
  Parte A roda e termina sozinha; em seguida a parte B roda até você apertar Ctrl+C.

──────────────────────────── RESUMO DA TEORIA ────────────────────────────
• Domínio FINITO (Versão A): ∀ e ∃ viram laços finitos (all/any). Custo O(|D|^k) para
  k quantificadores aninhados → sempre termina → a avaliação é decidível.

• Domínio INFINITO (Versão B): all() só devolve True quando o laço ACABA, ou seja, ao
  esgotar o gerador. ℕ não tem último elemento → tempo infinito. O programa não "erra":
  ele simplesmente nunca responde.

• Assimetria: um ∀ FALSO é refutável em tempo finito (basta 1 contraexemplo; ex.:
  ∀x (x < 1000) para em x = 1000). Um ∀ VERDADEIRO nunca é confirmado por força bruta.
  Com ∃ é o inverso. Com ∀∃ alternados (classe Π₂ da hierarquia aritmética) nem a
  refutação é garantida.

• Teorema de Church (1936) / Turing (1936): não existe algoritmo que decida a VALIDADE de
  fórmulas arbitrárias da LPO (Entscheidungsproblem). A validade é apenas semi-decidível
  (Completude de Gödel): se a fórmula é válida, há prova finita e uma busca sistemática a
  acha; se não for, a busca pode rodar para sempre — o que a Versão B reproduz.

• Como a matemática e os verificadores modernos contornam (dedução simbólica, não força
  bruta):
    - regras de inferência, resolução + unificação (Robinson, 1965), tableaux;
    - Skolemização: ∀x ∃y (x < y)  ⟹  ∀x (x < f(x)) com f(x) = x + 1; resta provar
      x < x + 1, uma identidade algébrica de 1 passo válida para QUALQUER x;
    - indução (Coq, Lean): P(0) ∧ ∀n (P(n) → P(n+1)) ⊢ ∀n P(n) — dois casos finitos
      cobrem infinitos valores;
    - fragmentos decidíveis, como a aritmética de Presburger (só +, sem ×), que provadores
      SMT como o Z3 resolvem por eliminação de quantificadores;
    - limites de tempo e a resposta honesta "unknown". Nenhum algoritmo infere tudo (com
      + e × juntos vale também a Incompletude de Gödel).
"""

import sys
import time

PAUSA = 0.05  # segundos entre cada "Testando X..." (0 = velocidade máxima / "congela")

try:  # garante ∀ ∃ ℕ no terminal (inclusive no Windows)
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ─────────────────────────── Quantificadores ───────────────────────────

def _iterar(dominio):
    # Lista (finita) → percorre. Função geradora (ex.: gerador_naturais, SEM parênteses) →
    # cria um gerador novo a cada uso, pois ∀x ∃y precisa recomeçar o domínio de y
    # para cada x (um gerador já consumido não volta ao início).
    return dominio() if callable(dominio) else iter(dominio)


def para_todo(dominio, predicado):
    # ∀x ∈ dominio : predicado(x)
    # "Momento do clique": all() equivale a este laço interno:
    #     for x in dominio:            # na Versão B: x = 0, 1, 2, 3, ...
    #         if not predicado(x):     # um contraexemplo encerra com False
    #             return False
    #     return True                  # só é alcançado SE o laço terminar
    # Em ℕ o laço nunca termina (não há "fim do infinito"): `return True` é inalcançável.
    return all(predicado(x) for x in _iterar(dominio))


def existe(dominio, predicado):
    # ∃x ∈ dominio : predicado(x) — any() para na primeira testemunha encontrada.
    return any(predicado(x) for x in _iterar(dominio))


def gerador_naturais():
    # Domínio infinito: 0, 1, 2, 3, ...
    n = 0
    while True:
        yield n
        n += 1


# ───────────────────── Versão A: domínio finito ─────────────────────

def versao_a():
    dominio = list(range(1, 11))  # "Mundo Fechado" de 10 elementos
    t0 = time.perf_counter()
    # ∀x ∃y (x < y): False, pois para x = 10 não existe y maior em D.
    resultado = para_todo(dominio, lambda x: existe(dominio, lambda y: x < y))
    ms = (time.perf_counter() - t0) * 1000
    print(f"[Versão A] ∀x ∃y (x < y) em {dominio}  →  {resultado}  ({ms:.3f} ms)")


# ───────────────────── Versão B: domínio infinito ─────────────────────

def versao_b():
    avaliacoes = 0  # quantas vezes o ∀ tentou avaliar um x

    def testar(x):
        nonlocal avaliacoes
        avaliacoes += 1
        print(f"Testando {x}...", flush=True)
        time.sleep(PAUSA)
        # ∃y (x < y) é achado rápido (y = x + 1); o problema é o ∀ externo, que
        # precisaria repetir isso para TODOS os x.
        # Alternativa de fórmula falsa complexa (também nunca termina):
        #   ∃x ∀y (y ≤ x) → existe(gerador_naturais, lambda x: para_todo(gerador_naturais,
        #                                                       lambda y: y <= x))
        return existe(gerador_naturais, lambda y: x < y)

    print("\n[Versão B] ∀x ∃y (x < y) em ℕ (gerador infinito). Ctrl+C para abortar.\n")
    try:
        resultado = para_todo(gerador_naturais, testar)
        print(resultado)  # nunca é alcançado
    except KeyboardInterrupt:
        print(f"\nAbortado após {avaliacoes} avaliações de infinitas → resultado INDETERMINADO.")


if __name__ == "__main__":
    versao_a()
    time.sleep(2)  # tempo para a plateia ler o resultado da Versão A
    versao_b()