"""
Projeto 09 - O Analisador Estático Enganado
Computabilidade e Complexidade Computacional

Arquivo único com as duas versões:
  Versão A - Analisador léxico/estático (olha o TEXTO do código).
  Versão B - Oráculo de parada por simulação (olha o COMPORTAMENTO)
             e a máquina paradoxal de Turing que o derrota.

Execução:  python projeto09.py
Seções:    1) testes da Versão A
           2) mesmos programas analisados por A e por B
           3) paradoxo de Turing contra o oráculo da Versão B
"""
import ast
import ctypes
import re
import textwrap
import threading
import time

LARGURA = 66


# ======================================================================
# Utilitários compartilhados
# ======================================================================
def linha(caractere="-"):
    print(caractere * LARGURA)


def titulo(texto):
    print()
    linha("=")
    print(texto)
    linha("=")


def rotulo(para):
    """Texto do veredito de parada (True = para)."""
    return "PARA" if para else "NÃO PARA"


def ok(condicao):
    return "OK" if condicao else "ERRO"


def preparar_codigo(codigo_fonte):
    """Remove indentação comum e espaços nas pontas."""
    return textwrap.dedent(codigo_fonte).strip()


# ======================================================================
# VERSÃO A - Analisador estático (léxico)
# ======================================================================
PADRAO_WHILE_TRUE = re.compile(r"\bwhile\s+True\s*:")
PADRAO_BREAK = re.compile(r"\bbreak\b")


def montar_resultado(suspeita, *mensagens):
    """Formato único de retorno de todas as heurísticas."""
    return {
        "suspeita_de_loop_infinito": suspeita,
        "mensagens": list(mensagens),
    }


def heuristica_while_true(codigo):
    """Procura 'while True:' sem 'break'.

    Retorna um resultado se o padrão aparecer; caso contrário, None
    (passa a vez para a próxima heurística). O 'break' é buscado em
    qualquer parte do texto: não há garantia de que pertença a esse laço
    nem de que seja alcançado.
    """
    if not PADRAO_WHILE_TRUE.search(codigo):
        return None

    if not PADRAO_BREAK.search(codigo):
        return montar_resultado(
            True,
            "ALERTA: foi encontrado 'while True:' sem um 'break' visível.",
            "O padrão pode indicar um laço infinito.",
        )

    return montar_resultado(
        False,
        "ATENÇÃO: há 'while True:' e também 'break' no código. "
        "A heurística não confirma se esse break encerra o laço analisado.",
    )


def verificar_sintaxe(codigo):
    """Última etapa: sintaxe válida não permite concluir que o programa termina."""
    try:
        ast.parse(codigo)
    except SyntaxError as erro:
        return montar_resultado(False, f"Erro de sintaxe detectado: {erro.msg}.")

    return montar_resultado(
        False,
        "Nenhum padrão óbvio de 'while True:' foi encontrado.",
        "O código parece sintaticamente válido, mas isso não garante "
        "que ele terminará.",
    )


# Heurísticas aplicadas em ordem; a primeira que reconhecer o padrão decide.
HEURISTICAS = [heuristica_while_true]


def analisador_estatico(codigo_fonte):
    """Recebe o código como string e procura padrões óbvios de não-terminação."""
    codigo = preparar_codigo(codigo_fonte)

    for heuristica in HEURISTICAS:
        resultado = heuristica(codigo)
        if resultado is not None:
            return resultado

    return verificar_sintaxe(codigo)


def suspeita_de_loop(codigo_fonte):
    """Atalho: só o veredito booleano do analisador."""
    return analisador_estatico(codigo_fonte)["suspeita_de_loop_infinito"]


# ======================================================================
# VERSÃO B - Oráculo de parada por simulação + máquina paradoxal
# ======================================================================
LIMITE_ORACULO = 1.0        # segundos que o oráculo espera pela simulação
LIMITE_OBSERVACAO = 3.0     # segundos que observamos a execução "real"


class _Abortar(BaseException):
    """BaseException, para não ser engolida por 'except Exception'."""


def _abortar(thread):
    """Injeta _Abortar na thread; interrompe até 'while True: pass'.
    Portável (Windows/Linux/macOS), sem depender de signal.SIGALRM."""
    ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_ulong(thread.ident), ctypes.py_object(_Abortar)
    )


def executar_com_limite(func, entrada, limite):
    """Roda func(entrada) em outra thread.
    True  -> terminou dentro do limite (retornou ou lançou exceção)
    False -> estourou o limite e foi abortada
    """
    def alvo():
        try:
            func(entrada)
        except BaseException:   # inclui _Abortar; terminar com erro também é "parar"
            pass

    t = threading.Thread(target=alvo, daemon=True)
    t.start()
    t.join(limite)
    if t.is_alive():
        _abortar(t)
        t.join(1.0)
        return False
    return True


def criar_oraculo(palpite_reentrante, limite=LIMITE_ORACULO):
    """Fabrica um oraculo_de_parada(func, entrada).

    Se o oráculo for chamado para analisar algo que ele JÁ está analisando
    (autorreferência), a simulação recursiva nunca terminaria. Todo oráculo
    real precisa de uma regra para esse caso: aqui, 'palpite_reentrante'.
    """
    em_analise = set()

    def oraculo_de_parada(func, entrada):
        """True = "ela vai PARAR"; False = "ela NÃO VAI parar"."""
        chave = (id(func), id(entrada))
        if chave in em_analise:
            return palpite_reentrante
        em_analise.add(chave)
        try:
            return executar_com_limite(func, entrada, limite)
        finally:
            em_analise.discard(chave)

    return oraculo_de_parada


def maquina_paradoxal(oraculo):
    """Constrói a máquina M que faz o OPOSTO do que o oráculo prevê sobre M(M)."""
    def M(programa):
        veredito = oraculo(programa, programa)   # "o que ESTE programa fará consigo mesmo?"
        if veredito:              # linha 1: oráculo disse "PARA"
            while True: pass      # linha 2: então M trava de propósito
        else:                     # linha 3: oráculo disse "NÃO PARA"
            return True           # linha 4: então M termina na hora
    return M


# ======================================================================
# Seção 1 - Testes da Versão A (exigidos no enunciado)
# ======================================================================
# (nome, código-fonte, esperado: True se deve haver suspeita de loop infinito)
CASOS_A = [
    (
        "Teste 1 - Função que termina",
        "def somar(a, b):\n    return a + b\n",
        False,
    ),
    (
        "Teste 2 - Laço com condição que termina",
        "def contar():\n    i = 0\n    while i < 5:\n        i += 1\n    return i\n",
        False,
    ),
    (
        "Teste 3 - Laço infinito óbvio",
        "def travar():\n    while True:\n        pass\n",
        True,
    ),
]


def executar_caso_a(nome, codigo, esperado):
    """Analisa um caso, imprime o relatório e devolve True se acertou."""
    resultado = analisador_estatico(codigo)
    acertou = resultado["suspeita_de_loop_infinito"] == esperado

    linha()
    print(nome)
    print("Código analisado:")
    print(preparar_codigo(codigo))
    print("\nResultado do analisador:")
    for mensagem in resultado["mensagens"]:
        print(f"- {mensagem}")
    print(
        f"Teste: {'ACERTOU' if acertou else 'NÃO ACERTOU'} "
        f"(esperado: {'suspeita' if esperado else 'sem alerta'})"
    )
    return acertou


def secao_versao_a():
    titulo("SEÇÃO 1 - VERSÃO A: ANALISADOR ESTÁTICO INGÊNUO (só lê o texto)")
    acertos = sum(executar_caso_a(*caso) for caso in CASOS_A)
    print()
    print(f"Resultado: {acertos}/{len(CASOS_A)} testes classificados como esperado.")


# ======================================================================
# Seção 2 - Os MESMOS programas analisados por A e por B
# ======================================================================
# (nome, código-fonte com def f(n), entrada, real_para)
PROGRAMAS = [
    ("termina (soma)",
     "def f(n):\n    return sum(range(n))\n", 1000, True),
    ("while True com break alcançável",
     "def f(n):\n    while True:\n        n += 1\n        if n > 10:\n            break\n",
     0, True),
    ("while True: pass",
     "def f(n):\n    while True:\n        pass\n", 0, False),
    ("while True com break inalcançável",
     "def f(n):\n    while True:\n        if n < 0:\n            break\n", 0, False),
    ("infinito sem 'while True'",
     "def f(n):\n    while n >= 0:\n        n += 1\n", 0, False),
    ("termina, mas leva 3 s",
     "import time\n\ndef f(n):\n    fim = time.time() + 3\n    while time.time() < fim:\n        pass\n",
     0, True),
]


def carregar_funcao(fonte):
    """Transforma o código-fonte (string) na função f, para a Versão B executar."""
    namespace = {}
    exec(fonte, namespace)
    return namespace["f"]


def secao_comparacao():
    titulo("SEÇÃO 2 - MESMOS PROGRAMAS: A (texto) x B (simulação, 1 s)")
    oraculo = criar_oraculo(palpite_reentrante=True)

    print(f"{'Programa':<36}{'Real':<10}{'A':<16}{'B':<16}")
    linha()
    acertos_a = acertos_b = 0
    for nome, fonte, entrada, real_para in PROGRAMAS:
        suspeita = suspeita_de_loop(fonte)
        b_para = oraculo(carregar_funcao(fonte), entrada)

        a_certo = suspeita == (not real_para)
        b_certo = b_para == real_para
        acertos_a += a_certo
        acertos_b += b_certo

        a_txt = "suspeita" if suspeita else "sem alerta"
        print(
            f"{nome:<36}{rotulo(real_para):<10}"
            f"{a_txt + ' ' + ok(a_certo):<16}{rotulo(b_para) + ' ' + ok(b_certo):<16}"
        )

    linha()
    total = len(PROGRAMAS)
    print(f"Acertos: A = {acertos_a}/{total} | B = {acertos_b}/{total}")
    print("A erra por olhar só o texto; B erra quando 'lento' parece 'infinito'.")


# ======================================================================
# Seção 3 - Paradoxo de Turing contra o oráculo da Versão B
# ======================================================================
def demonstrar_paradoxo(palpite):
    print(f"\n>> Palpite do oráculo para autorreferência: {rotulo(palpite)}")
    oraculo = criar_oraculo(palpite)
    M = maquina_paradoxal(oraculo)

    veredito = oraculo(M, M)
    print(f"   Oráculo prevê para M(M):    {rotulo(veredito)}")

    print(f"   Executando M(M) de verdade (observação de {LIMITE_OBSERVACAO:.0f} s)...")
    parou = executar_com_limite(M, M, LIMITE_OBSERVACAO)
    print(f"   Comportamento real de M(M): {rotulo(parou)}")

    if veredito != parou:
        print("   >>> CONTRADIÇÃO: o oráculo errou sobre M(M).")
    else:
        print("   >>> (sem contradição - não deveria acontecer)")


def secao_paradoxo():
    titulo("SEÇÃO 3 - VERSÃO B: A MÁQUINA PARADOXAL DE TURING")
    demonstrar_paradoxo(palpite=True)
    demonstrar_paradoxo(palpite=False)
    print(
        "\nQualquer regra que o oráculo adote é refutada por M: se prevê PARA, "
        "M trava;\nse prevê NÃO PARA, M termina. Logo, nenhum decisor total "
        "para a parada existe\n(Turing, 1936)."
    )


# ======================================================================
# Execução
# ======================================================================


if __name__ == "__main__":
    secao_versao_a()
    secao_comparacao()
    secao_paradoxo()