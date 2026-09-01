from itertools import count


def _eh_primo(n):
    """Teste de primalidade por tentativa de divisão — busca limitada a sqrt(n)."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    for d in range(3, int(n ** 0.5) + 1, 2):
        if n % d == 0:
            return False
    return True


def primo(i):
    """
    Retorna o i-ésimo primo (indexado a partir de i=1 -> 2, i=2 -> 3, ...).

    A busca é limitada pelo Postulado de Bertrand (existe sempre um primo
    entre k e 2k), então o número de candidatos testados é computável a
    priori a partir de i — permanece FRP.
    """
    if i < 1:
        raise ValueError("índice de primo deve ser >= 1")
    encontrados = 0
    for candidato in count(2):
        if _eh_primo(candidato):
            encontrados += 1
            if encontrados == i:
                return candidato


def codificar(lista):
    """
    N = 2^(x1+1) * 3^(x2+1) * 5^(x3+1) * ... * p_k^(xk+1)

    Codifica uma lista de inteiros não-negativos em um único número
    natural via o Teorema Fundamental da Aritmética (fatoração única).

    Nota sobre o deslocamento (+1): se um xi pudesse ser 0, o primo
    correspondente teria expoente 0 e, portanto, NÃO dividiria N — tornando
    impossível distinguir "elemento com valor 0" de "lista terminou aqui"
    usando apenas divisibilidade (que é o teste que tamanho() precisa, para
    permanecer FRP). Deslocar cada expoente em +1 garante que todo primo
    p_1..p_k sempre divide N pelo menos uma vez, preservando a
    decodificabilidade sem sair de FRP.
    """
    N = 1
    for i, x in enumerate(lista, start=1):
        N *= primo(i) ** (x + 1)
    return N


def _expoente_de(N, p):
    """
    Extrai o expoente de um primo p na fatoração de N.

    FRP porque o expoente máximo possível é log_p(N), um teto calculável
    diretamente de N — a busca (divisões sucessivas) é, portanto, limitada.
    """
    if N == 0:
        return 0
    expoente = 0
    limite = N.bit_length() + 1  # cota superior segura para o expoente
    for _ in range(limite):
        if N % p == 0:
            N //= p
            expoente += 1
        else:
            break
    return expoente


def tamanho(N):
    """
    tamanho(N): quantidade de elementos armazenados em N.

    Estratégia FRP: percorre primos p_1, p_2, ... testando se p_i divide N.
    Graças ao deslocamento (+1) em codificar(), todo primo realmente usado
    na lista sempre divide N pelo menos uma vez — então o primeiro primo
    que NÃO divide N marca o fim confiável da lista. A busca é limitada
    porque nenhum primo maior que N pode dividir N, então o número de
    primos a testar é, no pior caso, limitado por N.
    """
    if N <= 1:
        return 0
    i = 1
    while True:
        p = primo(i)
        if p > N:
            return i - 1
        if N % p != 0:
            return i - 1
        i += 1


def obter_elemento(N, i):
    """
    obter_elemento(N, i): retorna o i-ésimo elemento armazenado em N,
    isto é, o expoente do i-ésimo primo na fatoração de N, menos o
    deslocamento (+1) aplicado em codificar().

    Usa minimização LIMITADA: o expoente procurado nunca excede
    log_2(N), cota calculável a partir do próprio N.
    """
    p_i = primo(i)
    return _expoente_de(N, p_i) - 1


def fibonacci_memo(n):
    """
    Calcula F(n) mantendo TODO o histórico de chamadas anteriores
    empacotado em um único número natural N (codificação de Gödel),
    demonstrando que uma FRP pode simular estado/memória sem sair de ℕ.

    N codifica a lista [F(0), F(1), ..., F(k)] computada até o momento.
    A cada passo, decodifica os dois últimos valores via obter_elemento,
    calcula o próximo e recodifica a lista estendida.
    """
    if n == 0:
        return 0
    if n == 1:
        return 1

    # Estado inicial: N codifica [F(0), F(1)] = [0, 1]
    N = codificar([0, 1])

    for k in range(2, n + 1):
        tam = tamanho(N)
        f_k_menos_2 = obter_elemento(N, tam - 1)  # F(k-2)
        f_k_menos_1 = obter_elemento(N, tam)      # F(k-1)
        f_k = f_k_menos_2 + f_k_menos_1

        # Reconstrói a lista completa a partir de N e adiciona o novo termo
        historico = [obter_elemento(N, j) for j in range(1, tam + 1)]
        historico.append(f_k)
        N = codificar(historico)

    return obter_elemento(N, tamanho(N))


if __name__ == "__main__":
    # Demonstração — Projeto 04
    print("=== Projeto 04 — Codificação de Gödel ===\n")

    print("1. Codificação de [3, 1, 4]")
    lista_exemplo = [3, 1, 4]
    N = codificar(lista_exemplo)
    print(f"Lista original : {lista_exemplo}")
    print(f"N = 2^3 * 3^1 * 5^4 (com deslocamento +1) = {N}\n")

    print("2. Decodificação de N usando apenas funções primitivas")
    print(f"tamanho(N) = {tamanho(N)}  (esperado: {len(lista_exemplo)})")
    for i in range(1, tamanho(N) + 1):
        print(f"obter_elemento(N, {i}) = {obter_elemento(N, i)}  (esperado: {lista_exemplo[i-1]})")

    print("\n3. Fibonacci com memória empacotada em um único N")
    for n in range(10):
        print(f"F({n}) = {fibonacci_memo(n)}")
