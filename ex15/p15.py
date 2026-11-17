# /// script
# requires-python = ">=3.10"
# dependencies = ["z3-solver"]
# ///
"""
Projeto 15 - O Auditor de Fraudes Bancárias e o Poder Expressivo da Lógica
Computabilidade e Complexidade Computacional

Como rodar:  uv run fraude_bancaria.py
(o uv lê o bloco acima e instala o z3-solver automaticamente)

=====================================================================
TEORIA
=====================================================================

1) Lógica Descritiva
--------------------
Ramo da teoria da complexidade que descreve problemas computacionais por
meio de FÓRMULAS LÓGICAS em vez de máquinas. A pergunta central é: qual o
poder expressivo mínimo de lógica necessário para dizer "esta propriedade
vale para o grafo"? Cada resposta corresponde a uma classe de complexidade.

Aqui o "mundo" (estrutura finita) é um grafo de transações:
  - domínio: o conjunto de contas
  - relação E(x, y): "a conta x transferiu para a conta y"

2) Lógica de Primeira Ordem (LPO / FO)
--------------------------------------
Os quantificadores (∃ "existe", ∀ "para todo") percorrem apenas ELEMENTOS
do domínio, isto é, linhas da tabela. Uma variável x, y ou z representa UMA
conta por vez. Exemplo (Versão A):

    ∃x ∃y ∃z ( E(x,y) ∧ E(y,z) ∧ titular(x) = titular(z) )

Toda consulta SQL básica (SELECT, JOIN, WHERE) equivale a uma fórmula de LPO.
Com k variáveis, a avaliação ingênua testa no máximo n^k combinações, ou
seja, tempo POLINOMIAL (aqui n^3). Na prática, índices e joins reduzem
ainda mais. LPO sobre estruturas finitas fica dentro de P (na verdade em
AC0, uma classe ainda menor).

3) Lógica Existencial de Segunda Ordem (∃SO)
--------------------------------------------
Permite quantificar sobre CONJUNTOS (ou relações) inteiros, não só elementos:

    ∃V ∃A ∃G  ( ... )      V, A, G ⊆ conjunto de contas

Um solucionador precisa "inventar" subconjuntos do domínio. Para n contas
existem 2^n subconjuntos possíveis (3^n atribuições de 3 cores), logo a busca
cega é EXPONENCIAL.

4) Teorema de Fagin (1974):  ∃SO = NP
-------------------------------------
Uma propriedade de estruturas finitas é expressável em ∃SO se, e somente se,
está em NP.
  - A parte "∃ conjunto" é o CERTIFICADO: a solução que foi "chutada"
    (a coloração).
  - A parte de primeira ordem que vem depois é o VERIFICADOR, que confere
    o certificado em tempo polinomial.
NP = problemas cuja solução é rápida de VERIFICAR, mesmo que achá-la seja
(aparentemente) difícil. Isso explica a diferença entre as duas versões:
quantificar sobre elementos mantém o problema em P; quantificar sobre
conjuntos leva a NP.

5) 3-Coloração como fórmula ∃SO (Versão B)
------------------------------------------
Dividir contas em 3 grupos de risco (Vermelho, Azul, Verde) sem nenhuma
transferência direta entre contas do mesmo grupo:

  ∃V ∃A ∃G [ ∀x ( V(x) ∨ A(x) ∨ G(x) )                      (toda conta tem grupo)
           ∧ ∀x ( ¬(V(x)∧A(x)) ∧ ¬(V(x)∧G(x)) ∧ ¬(A(x)∧G(x)) )   (no máximo um grupo)
           ∧ ∀x ∀y ( E(x,y) → ¬(V(x)∧V(y)) ∧ ¬(A(x)∧A(y)) ∧ ¬(G(x)∧G(y)) ) ]

A 3-Coloração de Grafos é NP-completa. Para o solucionador, o conjunto V vira
um vetor de variáveis booleanas  v_i = "a conta i pertence a V". Cada
conjunto desconhecido é, portanto, um bloco de n booleanos, e a fórmula
vira um problema SAT.

SAT: decidir se uma fórmula booleana tem alguma atribuição verdadeira
(primeiro problema NP-completo; solucionadores modernos como o z3 usam
heurísticas muito eficientes). Resultado:
  - "sat"   -> existe partição; o modelo é o certificado (a coloração).
  - "unsat" -> NÃO existe partição; é a prova de que a rede não é 3-colorível.

6) Análise crítica: por que o SQL não tem o poder de ∃SO
--------------------------------------------------------
Bancos relacionais foram projetados com poder de primeira ordem (mais
agregações e recursão limitada) para ter desempenho previsível e polinomial.
Se qualquer usuário pudesse rodar consultas ∃SO, uma única query mal
formulada (por exemplo, uma 3-coloração sobre milhões de contas) poderia
ocupar o servidor por tempo exponencial, derrubando o serviço para todos.
Há um trade-off entre expressividade e previsibilidade de desempenho.

Observação: NP é complexidade de PIOR CASO. Solucionadores SAT resolvem muitas
instâncias reais rapidamente; uma rede de 15 contas é trivial para o z3.
"""

import random
import sqlite3
import time

from z3 import And, Bool, Not, Or, Solver, sat

CORES = ["Vermelho", "Azul", "Verde"]


# ---------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------
def criar_banco() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE Contas (id INTEGER PRIMARY KEY, titular TEXT NOT NULL);
        CREATE TABLE Transferencias (
            origem  INTEGER NOT NULL REFERENCES Contas(id),
            destino INTEGER NOT NULL REFERENCES Contas(id),
            valor   REAL    NOT NULL
        );
        CREATE INDEX idx_origem  ON Transferencias(origem);
        CREATE INDEX idx_destino ON Transferencias(destino);
        """
    )
    return conn


def popular_rede_grande(conn, n_contas=3000, n_transf=30000, seed=42):
    """Rede grande e aleatória; ~3 contas por titular (para haver casos Versão A)."""
    rng = random.Random(seed)
    n_titulares = n_contas // 3
    contas = [(i, f"Titular_{rng.randrange(n_titulares)}") for i in range(n_contas)]
    transf = []
    while len(transf) < n_transf:
        o, d = rng.randrange(n_contas), rng.randrange(n_contas)
        if o != d:
            transf.append((o, d, round(rng.uniform(10, 50_000), 2)))
    conn.executemany("INSERT INTO Contas VALUES (?, ?)", contas)
    conn.executemany("INSERT INTO Transferencias VALUES (?, ?, ?)", transf)
    conn.commit()


def popular_rede_pequena(conn, n_contas=15, com_clique=False, seed=7):
    """
    Rede pequena. Sem clique: grafo construído sobre uma partição oculta em 3
    grupos (garantidamente 3-colorível). Com clique: 4 contas que transferem
    entre si (K4), o que torna a 3-coloração impossível.
    """
    rng = random.Random(seed)
    grupo = [rng.randrange(3) for _ in range(n_contas)]
    arestas = set()
    while len(arestas) < 28:
        a, b = rng.sample(range(n_contas), 2)
        if grupo[a] != grupo[b]:
            arestas.add((a, b))
    if com_clique:
        for a in range(4):
            for b in range(4):
                if a != b:
                    arestas.add((a, b))
    conn.executemany(
        "INSERT INTO Contas VALUES (?, ?)", [(i, f"Titular_{i}") for i in range(n_contas)]
    )
    conn.executemany(
        "INSERT INTO Transferencias VALUES (?, ?, ?)",
        [(o, d, 1000.0) for o, d in arestas],
    )
    conn.commit()


# ---------------------------------------------------------------------
# Versão A: primeira ordem (SQL)
# ---------------------------------------------------------------------
QUERY_A = """
SELECT t1.origem AS x, t1.destino AS y, t2.destino AS z
FROM Transferencias t1
JOIN Transferencias t2 ON t1.destino = t2.origem   -- E(x,y) e E(y,z)
JOIN Contas cx ON cx.id = t1.origem
JOIN Contas cz ON cz.id = t2.destino
WHERE cx.titular = cz.titular                      -- titular(x) = titular(z)
  AND t1.origem <> t1.destino AND t2.origem <> t2.destino
"""


def versao_a():
    conn = criar_banco()
    popular_rede_grande(conn)
    n_c = conn.execute("SELECT COUNT(*) FROM Contas").fetchone()[0]
    n_t = conn.execute("SELECT COUNT(*) FROM Transferencias").fetchone()[0]

    print("=" * 60)
    print("VERSÃO A - Primeira ordem (SQL)")
    print("=" * 60)
    print(f"Rede: {n_c} contas, {n_t} transferências")

    inicio = time.perf_counter()
    resultado = conn.execute(QUERY_A).fetchall()
    tempo = time.perf_counter() - inicio

    print(f"Ciclos X -> Y -> Z com X e Z do mesmo titular: {len(resultado)}")
    print(f"Tempo: {tempo * 1000:.1f} ms")
    for x, y, z in resultado[:5]:
        print(f"  conta {x} -> conta {y} -> conta {z}")
    if len(resultado) > 5:
        print(f"  ... (+{len(resultado) - 5} resultados)")
    print()


# ---------------------------------------------------------------------
# Versão B: ∃SO via SAT (z3)
# ---------------------------------------------------------------------
def tres_coloracao(contas, arestas):
    """
    Variável booleana x[i, c]  <=>  conta i pertence ao conjunto da cor c.
    Os três conjuntos V, A, G são os 3 blocos de booleanos (c = 0, 1, 2).
    Retorna {conta: cor} ou None se não existir partição válida.
    """
    x = {(i, c): Bool(f"x_{i}_{c}") for i in contas for c in range(3)}
    s = Solver()

    for i in contas:
        s.add(Or(*(x[i, c] for c in range(3))))            # toda conta tem grupo
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                s.add(Not(And(x[i, c1], x[i, c2])))        # no máximo um grupo

    for o, d in arestas:
        for c in range(3):
            s.add(Not(And(x[o, c], x[d, c])))              # mesmo grupo proibido

    if s.check() != sat:
        return None
    m = s.model()
    return {i: next(c for c in range(3) if m.evaluate(x[i, c], model_completion=True)) for i in contas}


def analisar_rede(titulo, com_clique):
    conn = criar_banco()
    popular_rede_pequena(conn, com_clique=com_clique)

    # Lê a rede do próprio banco, como faria o auditor.
    contas = [r[0] for r in conn.execute("SELECT id FROM Contas ORDER BY id")]
    arestas = conn.execute("SELECT origem, destino FROM Transferencias").fetchall()

    print(f"--- {titulo}: {len(contas)} contas, {len(arestas)} transferências ---")
    inicio = time.perf_counter()
    coloracao = tres_coloracao(contas, arestas)
    tempo = time.perf_counter() - inicio

    if coloracao is None:
        print("UNSAT: não existe partição em 3 grupos de risco sem transferências internas.")
    else:
        print("SAT: partição encontrada.")
        for c, nome in enumerate(CORES):
            membros = [i for i in contas if coloracao[i] == c]
            print(f"  {nome:<9}: {membros}")
        # Verificador em tempo polinomial (o "V" de NP).
        valido = all(coloracao[o] != coloracao[d] for o, d in arestas)
        print(f"  Verificação do certificado: {'OK' if valido else 'FALHOU'}")
    print(f"Tempo: {tempo * 1000:.1f} ms\n")


def versao_b():
    print("=" * 60)
    print("VERSÃO B - ∃ Segunda ordem (3-coloração via SAT)")
    print("=" * 60)
    analisar_rede("Rede 1 (colorível)", com_clique=False)
    analisar_rede("Rede 2 (4 contas trocando entre si)", com_clique=True)


if __name__ == "__main__":
    versao_a()
    versao_b()