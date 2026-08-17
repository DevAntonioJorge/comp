# Ex3 — Mini-Interpretador de Funções Recursivas Primitivas

Este exercício implementa uma linguagem pequena baseada em **Funções Recursivas Primitivas (FRP)**. O objetivo é visualizar como composição e recursão primitiva são suficientes para construir funções conhecidas sem usar `while`, minimização ilimitada ou recursão geral.

O projeto é propositalmente simples: não possui sistema de tipos, suíte de testes ou dependências externas. O interpretador só verifica as aridades necessárias para conseguir executar uma composição ou uma recursão.

## Preparação com `uv`

O projeto usa o formato tradicional de um projeto Python:

```bash
cd ex3
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

No Windows PowerShell, a ativação equivalente é:

```powershell
.venv\Scripts\Activate.ps1
```

Como `requirements.txt` não possui pacotes, nenhuma instalação externa é necessária. O `uv` é usado para criar o ambiente virtual e executar o Python.

## Executando

A demonstração completa pode ser executada com:

```bash
uv run --python .venv/bin/python main.py --demo
```

Também é possível executar uma função diretamente:

```bash
uv run --python .venv/bin/python main.py --function ADD --args 7 5
uv run --python .venv/bin/python main.py --function FIB --args 10
uv run --python .venv/bin/python main.py --function DIV --args 17 5
uv run --python .venv/bin/python main.py --function PRIME --args 97
```

O arquivo carregado por padrão é `examples/programas.prf`. Para usar outro arquivo:

```bash
uv run --python .venv/bin/python main.py --file outro.prf --function ADD --args 2 3
```

## Sintaxe

As definições usam a forma:

```text
NOME = EXPRESSAO
```

Os construtores são:

```text
Z0, Z1, Z2, ...       função constante zero com a aridade indicada
S                     sucessor
P1_2                  primeira projeção de uma função de aridade 2
COMP(f, [g1, g2])     composição
REC(base, passo)      recursão primitiva
```

A notação usada pelo projeto para projeções é `Píndice_aridade`. Portanto, `P3_3` significa “retorne o terceiro argumento de uma função com três argumentos”.

### Soma

```text
ADD = REC(P1_1, COMP(S, [P3_3]))
```

A interpretação é:

```text
ADD(x, 0)     = x
ADD(x, y + 1) = S(ADD(x, y))
```

### Multiplicação

```text
MUL = REC(Z1, COMP(ADD, [P1_1, P3_3]))
```

A cada passo, o acumulador recebe mais uma parcela `x`.

## Os três exemplos

### Fibonacci

`FIB` usa o estado codificado como um par:

```text
(F(n), F(n + 1))
```

A transição da recursão é:

```text
(a, b) -> (b, a + b)
```

`PAIR`, `FST` e `SND` são auxiliares da biblioteca do interpretador que codificam dois naturais em um único natural pelo emparelhamento de Cantor. Assim, a própria linguagem continua trabalhando com números naturais.

### Divisão inteira

`DIV(n, d)` percorre o dividendo `n`. O quociente é incrementado somente quando o próximo múltiplo de `d` ainda cabe no valor percorrido. O caso `d = 0` foi definido como `0`, mantendo a demonstração total:

```text
DIV(17, 5) = 3
DIV(20, 5) = 4
DIV(10, 0) = 0
```

### Primalidade

`PRIME(n)` verifica divisores entre `2` e `n - 1`. Essa busca é limitada pelo próprio argumento de entrada e não usa minimização ilimitada:

```text
PRIME(2)  = 1
PRIME(17) = 1
PRIME(25) = 0
```

Os booleanos são representados por naturais: `0` para falso e `1` para verdadeiro.

## Por que não há laços infinitos?

A linguagem não oferece `while`, `for`, alteração de variáveis ou chamadas recursivas arbitrárias. A única recursão disponível é:

```text
REC(base, passo)
```

O interpretador começa no caso base e executa exatamente uma quantidade de passos determinada pelo argumento recursivo. Em cada passo, o contador se aproxima de zero. A composição também executa um número fixo de funções já definidas.

Logo, toda definição construída pelos operadores do núcleo é uma função recursiva primitiva: ela termina para toda entrada natural e não representa uma função parcial. O preço dessa segurança é que a linguagem não é Turing-completa e não consegue expressar minimização não limitada ou algoritmos que dependam de uma busca potencialmente infinita.

A implementação faz apenas as verificações de aridade indispensáveis à execução. O foco do exercício é a mecânica da linguagem, não a criação de um verificador estático completo.
