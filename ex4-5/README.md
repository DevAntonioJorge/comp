# Teoria da Computabilidade — Projetos 04 e 05

Implementação em Python puro (stdlib) da **Codificação de Gödel & Função Beta** (Projeto 04) e do **Simulador Turing-Completo via μ-Recursão / Teorema da Forma Normal de Kleene** (Projeto 05).

> Extraído do notebook `teoria_computabilidade_p04_p05.ipynb`. O Projeto 05 **reaproveita** o código do Projeto 04 via `import` — sem duplicação.

## Estrutura

```
.
├── projeto04.py  # Produto de primos, tamanho/obter_elemento, Fibonacci com memória em N
├── projeto05.py  # Estado S, passo, T, U, μy — importa codificar/tamanho/obter_elemento de projeto04
├── teoria_computabilidade_p04_p05.ipynb  # notebook original (referência)
└── README.md
```

## Requisitos

* Python 3.10+ (usa `int | None` do notebook; para 3.9 troque por `Optional`)
* Nenhuma dependência externa — só `itertools` da stdlib.

## Como executar

Os dois arquivos são executáveis diretamente e também importáveis.

### Projeto 04 — Codificação de Gödel

```bash
python projeto04.py
```

Saída esperada:

```
=== Projeto 04 — Codificação de Gödel ===

1. Codificação de [3, 1, 4]
Lista original : [3, 1, 4]
N = 2^3 * 3^1 * 5^4 (com deslocamento +1) = 450000

2. Decodificação de N usando apenas funções primitivas
tamanho(N) = 3  (esperado: 3)
obter_elemento(N, 1) = 3  (esperado: 3)
...

3. Fibonacci com memória empacotada em um único N
F(0) = 0
...
F(9) = 34
```

Uso como biblioteca:

```python
from projeto04 import codificar, tamanho, obter_elemento, fibonacci_memo

N = codificar([3, 1, 4])  # 450000
tamanho(N)                 # 3
obter_elemento(N, 2)       # 1
fibonacci_memo(9)          # 34
```

### Projeto 05 — Simulador Turing-Completo

```bash
python projeto05.py
```

Saída esperada:

```
=== Projeto 05 — Simulador Turing-Completo via μ-Recursão ===

Teste 1 — Máquina que PARA ... y = 5, fita [1,1,1,1]
  T(e,S0,y=5) = True  <-- MENOR y
Teste 2 — Máquina em LOOP ... μy NÃO encontrou parada (limite 50)
```

Uso como biblioteca:

```python
from projeto05 import codificar_configuracao, simular

delta_sucessor = {(0,1):(0,1,1), (0,0):(1,1,0)}
y, fita = simular(delta_sucessor, [1,1,1])  # y=5, fita=[1,1,1,1]

delta_loop = {(0,0):(0,0,0), (0,1):(0,1,0)}
y, fita = simular(delta_loop, [1,0,1], limite_seguranca=50)  # y=None
```

> **Importante:** `projeto05.py` deve estar no mesmo diretório que `projeto04.py` (import relativo `from projeto04 import ...`). Se rodar de outra pasta, use `PYTHONPATH=. python caminho/projeto05.py`.

## Explicação do código

### Projeto 04 — `projeto04.py`

**Ideia central:** uma lista `[x1,...,xk]` vira um único natural `N` pelo Teorema Fundamental da Aritmética:

```
N = 2^(x1+1) * 3^(x2+1) * 5^(x3+1) * ... * p_k^(xk+1)
```

* `codificar(lista)` — multiplica potências de primos. O `+1` no expoente resolve a ambiguidade do `0`: sem ele, `xi=0` daria `p_i^0=1` e o primo sumiria de `N`, indistinguível de "lista acabou". Com `+1`, todo primo usado divide `N`.
* `_eh_primo` / `primo(i)` — gerador de primos por tentativa até `sqrt(n)`. A busca é limitada (Postulado de Bertrand) → permanece FRP. É auxiliar, não parte do enunciado.
* `_expoente_de(N,p)` — conta quantas vezes `p` divide `N` (divisões sucessivas). Cota `N.bit_length()+1 ≈ log2(N)` → minimização limitada.
* `tamanho(N)` — percorre `p1,p2,...` até achar o primeiro primo que **não** divide `N`; esse é o fim da lista. Limitado por `p > N` → FRP.
* `obter_elemento(N,i)` — expoente de `p_i` em `N` menos `1` (desfaz `+1`). Também limitado.
* `fibonacci_memo(n)` — demonstração de que FRP manipula estado: `N` empacota `[F0,...,Fk]`; a cada iteração decodifica `F(k-1),F(k-2)` via `obter_elemento`, soma e recodifica. Prova que "só Naturais como domínio" não impede estruturas complexas.

Todas as decodificações usam apenas sucessor/projeção/composição + minimização **limitada** — nenhuma busca é ilimitada.

### Projeto 05 — `projeto05.py`

Reaproveita `codificar/tamanho/obter_elemento` em **duas camadas**:

```
T_fita = codificar(fita)              # lista → N
S      = codificar([estado, posicao, T_fita])  # tripla → N
```

* `codificar_configuracao` / `decodificar_configuracao` — empacota/desempacota `(q, cabeça, fita)` em um único `S ∈ ℕ`.
* `passo(S, delta)` — uma transição: decodifica `S`, lê símbolo sob a cabeça (ou `0` branco), consulta `delta`, escreve, move `-1/0/+1`, recodifica. Se não há regra, retorna `None` (= máquina parou). Inteiramente limitado/FRP.
* `T(delta,S0,y)` — predicado de Kleene: simula exatamente `y-1` passos e verifica se o `y`-ésimo falha (`None`). Laço de tamanho `y` conhecido a priori → FRP / minimização limitada. É o coração do Teorema da Forma Normal.
* `U(delta,S0,y)` — dado que `T` é verdadeiro, reconstrói a fita final após `y-1` passos.
* `mu_busca_parada` — `μy[T(e,S0,y)]`: busca o **menor** `y` que satisfaz `T`. É a **única** operação não-FRP do simulador — não há cota a priori para `y` (Problema da Parada). `limite_seguranca` é apenas teto prático para o demo não travar; matematicamente `μ` rodaria para sempre se a máquina não parar.
* `simular` — forma normal completa `f(x)=U(μy[T(e,x,y)=0])`: codifica entrada, busca `y`, extrai fita.

**Demos:**
1. Sucessor unário ` [1,1,1] → [1,1,1,1]` prova `y=5` único e `T` falso em todos os outros `y`.
2. Loop ` (0,*)→(0,*,0)` com `limite 50` ilustra indecidibilidade — `μy` não decide.

Vale notar: toda lógica de fita/transição é FRP e sempre termina para `y` fixo; só a espera pelo `y` de parada exige `μ`.

## Notebook original

`teoria_computabilidade_p04_p05.ipynb` permanece no repositório como referência — rodar as células de cima para baixo reproduz as mesmas saídas dos `.py`.
