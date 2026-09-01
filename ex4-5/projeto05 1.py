from projeto04 import codificar, obter_elemento, tamanho

SIMBOLO_BRANCO = 0  # convenção: 0 representa a célula em branco


def codificar_configuracao(estado, posicao, fita):
    """
    Empacota uma configuração instantânea (q, h, fita) em um único S ∈ N.

    Reaproveita codificar() do Projeto 04 DUAS vezes em camadas:
      T = codificar(fita)             -> a fita vira um natural
      S = codificar([q, h, T])        -> a tripla (q, h, T) vira um natural
    """
    T_fita = codificar(fita)
    return codificar([estado, posicao, T_fita])


def decodificar_configuracao(S):
    """Operação inversa: extrai (estado, posição, fita) a partir de S."""
    estado = obter_elemento(S, 1)
    posicao = obter_elemento(S, 2)
    T_fita = obter_elemento(S, 3)
    tam = tamanho(T_fita)
    fita = [obter_elemento(T_fita, i) for i in range(1, tam + 1)] if tam > 0 else []
    return estado, posicao, fita


def passo(S, delta):
    """
    Aplica UMA transição a partir da configuração codificada S.

    delta: dict{(estado, simbolo): (novo_estado, novo_simbolo, movimento)}
           movimento ∈ {-1, 0, +1}  (esquerda, permanece, direita)

    Retorna a nova configuração S' codificada, ou None se não existe
    transição para (estado, símbolo) — convenção adotada para "a máquina
    parou". Esta função é inteiramente limitada/FRP: decodifica S
    (bounded), consulta a tabela delta (O(1), bounded) e recodifica
    (bounded) — nenhuma parte desta função busca sem cota.
    """
    estado, posicao, fita = decodificar_configuracao(S)

    simbolo_atual = fita[posicao] if 0 <= posicao < len(fita) else SIMBOLO_BRANCO

    regra = delta.get((estado, simbolo_atual))
    if regra is None:
        return None  # nenhuma transição aplicável -> máquina parada

    novo_estado, novo_simbolo, movimento = regra

    # garante que a fita tenha a célula 'posicao' antes de escrever nela
    while len(fita) <= posicao:
        fita.append(SIMBOLO_BRANCO)
    fita[posicao] = novo_simbolo

    nova_posicao = posicao + movimento
    if nova_posicao < 0:
        # fita "infinita à esquerda": insere branco no início e realinha
        fita.insert(0, SIMBOLO_BRANCO)
        nova_posicao = 0

    return codificar_configuracao(novo_estado, nova_posicao, fita)


def T(delta, S0, y):
    """
    T(e, S0, y): verifica se a máquina 'delta', partindo de S0, executa
    exatamente (y - 1) transições válidas e então PARA no y-ésimo passo
    (isto é, passo() aplicado à (y-1)-ésima configuração retorna None).

    Para um y FIXO, esta verificação percorre no máximo y configurações
    — um laço de tamanho conhecido a priori. Logo, T é estritamente FRP:
    usa apenas minimização LIMITADA (limitada por y, que já é dado).
    Isso é exatamente o predicado de Kleene do Teorema da Forma Normal.
    """
    if y < 1:
        return False

    S = S0
    for _ in range(y - 1):
        proxima = passo(S, delta)
        if proxima is None:
            return False  # já havia parado antes do passo y
        S = proxima

    return passo(S, delta) is None


def U(delta, S0, y):
    """
    U(y): dado que T(e, S0, y) é verdadeiro (a máquina para no passo y),
    decodifica e retorna o conteúdo final da fita.

    Reconstrói a configuração final aplicando (y - 1) transições válidas
    a partir de S0 — a mesma quantidade de passos verificada por T.
    """
    S = S0
    for _ in range(y - 1):
        S = passo(S, delta)
    _, _, fita_final = decodificar_configuracao(S)
    return fita_final


def mu_busca_parada(delta, S0, limite_seguranca=2000):
    """
    μy [T(e, S0, y)]: busca pelo MENOR y tal que a máquina para no passo y.

    Esta é a ÚNICA operação de todo o simulador que NÃO é primitiva
    recursiva: não existe, em geral, uma cota a priori sobre y — não há
    como saber de antemão quantos passos uma máquina arbitrária levará
    até parar (ou se algum dia vai parar). É exatamente esta busca
    ilimitada que introduz o Problema da Parada e a indecidibilidade.

    'limite_seguranca' NÃO faz parte da definição matemática de μ — é
    apenas um teto artificial para que a demonstração não trave num loop
    real. Matematicamente, μy roda para sempre se a máquina nunca parar.
    """
    y = 1
    while y <= limite_seguranca:
        if T(delta, S0, y):
            return y
        y += 1
    return None  # limite de segurança atingido: não decidimos (ilustra a indecidibilidade)


def simular(delta, fita_inicial, estado_inicial=0, posicao_inicial=0, limite_seguranca=2000):
    """
    Função universal completa: f(x) = U(μy [T(e, x, y) = 0])

    Retorna (y_parada, fita_final) ou (None, None) se não decidiu parar
    dentro do limite de segurança.
    """
    S0 = codificar_configuracao(estado_inicial, posicao_inicial, fita_inicial)
    y = mu_busca_parada(delta, S0, limite_seguranca)
    if y is None:
        return None, None
    fita_final = U(delta, S0, y)
    return y, fita_final


if __name__ == "__main__":
    print("=== Projeto 05 — Simulador Turing-Completo via μ-Recursão ===\n")

    # Teste 1 — Máquina que PARA (sucessor unário)
    print("Teste 1 — Máquina que PARA em N passos (sucessor unário)")
    # Alfabeto: 0 = branco, 1 = marca unária
    # Estado 0: percorre os 1's para a direita; ao achar branco, escreve 1
    #           e vai para o estado 1 (sem transição definida -> halt).
    delta_sucessor = {
        (0, 1): (0, 1, +1),   # continua andando enquanto lê 1
        (0, 0): (1, 1, 0),    # encontra o fim, escreve 1 extra, muda de estado
        # (1, *) : ausente de propósito -> qualquer símbolo no estado 1 para a máquina
    }
    fita_inicial = [1, 1, 1]  # representa o número unário 3
    print(f"Fita inicial : {fita_inicial}  (unário para 3)")

    y_parada, fita_final = simular(delta_sucessor, fita_inicial)
    print(f"y (nº de passos até parar) = {y_parada}")
    print(f"Fita final                 = {fita_final}  (unário para 4 = 3+1)\n")

    # Verificação direta do predicado T (Kleene)
    print("Verificação direta do predicado T (Kleene):")
    S0 = codificar_configuracao(0, 0, fita_inicial)
    for y_teste in range(1, y_parada + 3):
        resultado = T(delta_sucessor, S0, y_teste)
        marca = "  <-- MENOR y que satisfaz T (achado por μy)" if y_teste == y_parada else ""
        print(f"  T(e, S0, y={y_teste}) = {resultado}{marca}")

    # Teste 2 — Máquina que ENTRA EM LOOP INFINITO
    print("\nTeste 2 — Máquina que ENTRA EM LOOP INFINITO")
    # Estado 0: para qualquer símbolo lido, reescreve o mesmo símbolo e
    # NÃO se move — transição sempre definida, a máquina nunca para.
    delta_loop = {
        (0, 0): (0, 0, 0),
        (0, 1): (0, 1, 0),
    }
    fita_loop = [1, 0, 1]
    print(f"Fita inicial : {fita_loop}")
    print("Buscando y com limite de segurança = 50 (μy NÃO teria cota real)...")

    y_loop, fita_loop_final = simular(delta_loop, fita_loop, limite_seguranca=50)
    if y_loop is None:
        print("μy NÃO encontrou parada dentro do limite de segurança.")
        print("Isso ilustra o Problema da Parada: sem cota a priori, a busca")
        print("por μy pode, em geral, rodar indefinidamente — é exatamente")
        print("essa a operação que está FORA da classe FRP.")
    else:
        print(f"(inesperado) y = {y_loop}, fita = {fita_loop_final}")
