# Ex1 — Conceitos de Computabilidade

Este exercício reúne demonstrações de conceitos fundamentais de computabilidade usando Python. O projeto começa pelas funções básicas de zero, sucessor e projeção, constrói funções recursivas primitivas, implementa a função de Ackermann e o operador de minimização não limitada, e compara duas formas de calcular a raiz quadrada de piso.

Além das demonstrações numéricas, o programa executa benchmarks simples e gera um gráfico da profundidade da pilha usada pela função de Ackermann.

## Organização do projeto

Os módulos principais estão no pacote `computabilidade`:

```text
computabilidade/
├── ackermann.py   # Ackermann e operador de minimização μ
├── basicas.py     # Zero, sucessor e projeção
├── benchmark.py   # Medições de tempo
├── frp.py         # Adição e multiplicação por FRP
├── grafico.py     # Profundidade da pilha de Ackermann
└── raiz.py        # Raiz quadrada limitada e por μ
```

O arquivo `main.py` é o ponto de entrada e executa todas as demonstrações em sequência.

## Preparação com `uv`

O projeto usa o formato tradicional de um projeto Python:

```bash
cd ex1
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

No Windows PowerShell, a ativação equivalente é:

```powershell
.venv\Scripts\Activate.ps1
```

Este exercício usa `matplotlib` para gerar o gráfico de profundidade da pilha. A dependência está declarada em `requirements.txt`.

## Executando

A demonstração completa pode ser executada com:

```bash
uv run --python .venv/bin/python main.py
```

O programa executa, nesta ordem:

1. funções básicas;
2. funções recursivas primitivas;
3. função de Ackermann e operador μ;
4. duas implementações da raiz quadrada de piso;
5. benchmark de desempenho;
6. gráfico da profundidade de chamadas de Ackermann.

Ao final, uma janela do `matplotlib` é aberta para exibir o gráfico. Em ambientes sem interface gráfica, pode ser necessário configurar um backend não interativo do `matplotlib`.

## Funções básicas

O módulo `basicas.py` implementa as funções iniciais usadas nas construções teóricas:

### Função zero

```text
Z(x) = 0
```

### Função sucessor

```text
S(x) = x + 1
```

### Função projeção

```text
P_i^n(x_1, ..., x_n) = x_i
```

A projeção usa indexação iniciada em 1, conforme a notação matemática. Por exemplo:

```text
P(2, 3, 10, 20, 30) = 20
```

O módulo também verifica se a quantidade de argumentos e o índice da projeção são válidos.

## Funções recursivas primitivas

O módulo `frp.py` constrói operações aritméticas por meio de sucessão e repetição limitada.

### Adição

```text
add(x, 0)     = x
add(x, y + 1) = S(add(x, y))
```

A implementação correspondente é `add_frp(x, y)`.

### Multiplicação

```text
mult(x, 0)     = 0
mult(x, y + 1) = add(mult(x, y), x)
```

A implementação correspondente é `mult_frp(x, y)`.

Exemplos exibidos pelo programa:

```text
add_frp(7, 8)  = 15
mult_frp(4, 5) = 20
```

## Ackermann e minimização

O módulo `ackermann.py` implementa a função de Ackermann-Péter:

```text
A(0, n)     = n + 1
A(m, 0)     = A(m - 1, 1)
A(m, n)     = A(m - 1, A(m, n - 1))
```

A função cresce muito rapidamente e usa chamadas recursivas aninhadas. Por isso, valores pequenos de entrada já produzem grandes profundidades de chamada.

O mesmo módulo implementa o operador de minimização não limitada:

```text
μy [f(y) = target]
```

A função `mu_operator` procura o menor natural `y` que satisfaz a condição. Como a busca não possui um limite superior, ela não termina quando nenhum valor satisfaz a condição.

## Raiz quadrada de piso

O módulo `raiz.py` compara duas abordagens para calcular a raiz quadrada de piso.

### Busca limitada por FRP

`sqrt_frp_bounded(x)` percorre os valores até `x` e retorna o maior `y` tal que:

```text
y² <= x
```

O limite imposto pela entrada garante a parada para números naturais.

### Busca por minimização não limitada

`sqrt_mu_unbounded(x)` usa o operador μ para procurar o menor `y` tal que:

```text
(y + 1)² > x
```

Esse valor é a raiz quadrada de piso. A implementação ilustra a diferença entre uma busca limitada e uma busca potencialmente não limitada.

Exemplo apresentado pelo programa:

```text
Raiz de piso de 20 = 4
```

As duas implementações produzem o mesmo resultado, mas usam estratégias conceitualmente diferentes.

## Benchmark

O módulo `benchmark.py` mede o tempo de execução de alguns valores da função de Ackermann:

```text
A(0, 0)
A(1, 2)
A(2, 2)
A(3, 3)
A(3, 4)
```

Também compara as duas implementações da raiz quadrada para:

```text
100
1000
5000
```

Os tempos variam conforme o computador e a versão do Python. O objetivo é observar o custo relativo das abordagens, não produzir uma medição de desempenho formal.

## Gráfico de profundidade da pilha

O módulo `grafico.py` avalia entradas de Ackermann com:

```text
0 <= m <= 4
0 <= n <= 2
```

Para cada entrada, ele mede o pico de profundidade das chamadas recursivas e exibe os resultados em escala logarítmica. O limite utilizado pelo programa é:

```text
100000
```

Quando uma entrada ultrapassa o limite de recursão, ela é marcada no gráfico como um possível estouro de pilha.

## Limitações didáticas

- A função de Ackermann só deve ser executada com entradas pequenas.
- O operador μ pode entrar em busca infinita quando a condição nunca é satisfeita.
- O benchmark não é uma avaliação científica de desempenho.
- O gráfico depende de `matplotlib` e de um ambiente capaz de abrir uma janela gráfica.
- O projeto não possui suíte de testes; o foco é executar e visualizar as construções de computabilidade.
