# Ex2 — Diagonalização de Cantor e o Problema da Parada

Este exercício apresenta uma prova visual e interativa baseada na diagonalização de Cantor e no problema da parada de Turing. A aplicação é executada pela linha de comando e permite construir uma matriz de programas versus entradas, gerar uma sequência diagonal fora de uma lista e acompanhar a contradição produzida por um suposto analisador perfeito de código.

O projeto é propositalmente didático: os programas que param ou entram em loop são representados por resultados simbólicos (`HALT` e `LOOP`). Assim, a demonstração não bloqueia a aplicação com um loop infinito real.

## Preparação com `uv`

O projeto usa o formato tradicional de um projeto Python:

```bash
cd ex2
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

No Windows PowerShell, a ativação equivalente é:

```powershell
.venv\Scripts\Activate.ps1
```

O arquivo `requirements.txt` não possui dependências externas. O programa usa apenas a biblioteca padrão do Python.

## Executando

A aplicação completa pode ser executada com:

```bash
uv run --python .venv/bin/python main.py
```

O menu apresenta as seguintes opções:

```text
1 - Criar e mostrar matriz N x N
2 - Executar diagonalização de Cantor
3 - Testar analisador de parada
4 - Demonstrar contradição de Turing
5 - Executar demonstração completa
0 - Sair
```

## Matriz de programas e entradas

A opção `1` permite informar uma matriz `N x N`:

1. informe a quantidade de programas e entradas;
2. informe os nomes dos programas;
3. informe os nomes das entradas;
4. informe uma linha de resultados para cada programa.

Cada resultado deve ser `0` ou `1`:

```text
0 = não para
1 = para
```

Por exemplo, para dois programas e duas entradas:

```text
           E1      E2
      P1   0       1
      P2   1       0
```

A aplicação valida a quantidade de linhas, a quantidade de colunas e os valores da matriz antes de exibi-la.

## Diagonalização de Cantor

A opção `2` solicita uma lista finita de sequências binárias. Para representar uma matriz diagonal, o programa exige `N` sequências com exatamente `N` bits cada.

Para cada sequência `i`, o programa observa o bit da posição `i` e o inverte:

```text
0 -> 1
1 -> 0
```

Considere, por exemplo:

```text
1: 0000
2: 1010
3: 1100
4: 0111
```

Os bits diagonais são:

```text
sequência 1, posição 1: 0 -> 1
sequência 2, posição 2: 0 -> 1
sequência 3, posição 3: 0 -> 1
sequência 4, posição 4: 1 -> 0
```

A nova sequência é:

```text
1110
```

Ela difere da sequência 1 na posição 1, da sequência 2 na posição 2, da sequência 3 na posição 3 e da sequência 4 na posição 4. Portanto, não pode ser igual a nenhum item da lista original.

Essa matriz finita é uma visualização da ideia geral de Cantor. Na prova de `2^ℵ₀ > ℵ₀`, o mesmo argumento é aplicado a uma suposta enumeração de sequências binárias infinitas: a construção diagonal sempre produz uma sequência que não aparece na enumeração.

## Simulação do problema da parada

A aplicação define programas fictícios com dois resultados possíveis:

```python
programa_para(entrada)  # retorna HALT
programa_loop(entrada)  # retorna LOOP
```

Também há um programa condicional que retorna `HALT` somente para a entrada `"1"`.

O analisador utilizado na demonstração possui a interface:

```python
analisador_halting(programa, entrada)
```

Ele retorna:

```text
True  -> HALT
False -> LOOP
```

Como os programas são modelos simbólicos que retornam imediatamente, o analisador pode ser executado com segurança. Ele não representa um analisador real capaz de resolver o problema da parada para qualquer programa.

## Programa diagonal

A rotina:

```python
diagonal(programa)
```

consulta o analisador sobre o programa recebido usando o próprio programa como entrada e faz o oposto da resposta:

```text
se o analisador disser HALT -> DIAGONAL entra em LOOP
se o analisador disser LOOP -> DIAGONAL termina
```

A chamada paradoxal seria equivalente a:

```python
analisador_halting(diagonal, diagonal)
```

A aplicação não executa essa chamada literalmente, pois isso representaria o loop infinito do próprio paradoxo. Em vez disso, a função `LoopSimulado` interrompe controladamente o primeiro caso e permite visualizar os dois resultados possíveis.

## Os dois casos da contradição

### Caso 1: o analisador responde `HALT`

Se o analisador afirmar que `DIAGONAL` termina, o programa diagonal fará o contrário e entrará em loop.

```text
previsão: HALT
comportamento real: LOOP
```

Isso contradiz a resposta do analisador.

### Caso 2: o analisador responde `LOOP`

Se o analisador afirmar que `DIAGONAL` entra em loop, o programa diagonal fará o contrário e terminará.

```text
previsão: LOOP
comportamento real: HALT
```

Isso também contradiz a resposta do analisador.

Como os dois resultados possíveis levam a uma contradição, não pode existir um algoritmo perfeito que determine, para qualquer programa e qualquer entrada, se o programa irá parar.

## Relação com análise estática

Um analisador estático perfeito de código teria de responder corretamente se qualquer programa termina ou executa indefinidamente, sem necessariamente executar o programa.

A construção diagonal mostra que um analisador com essa capacidade universal não pode existir. Analisadores estáticos reais podem detectar padrões específicos, impor limites ou produzir respostas inconclusivas, mas não podem resolver corretamente o problema para todos os programas possíveis.

## Demonstração completa

A opção `5` executa, em sequência:

1. uma matriz `4 x 4` de exemplo;
2. a diagonalização da lista de sequências de exemplo;
3. os testes do analisador fictício;
4. a simulação completa da contradição de Turing.

O programa não possui suíte de testes nem dependências externas; o foco é a visualização interativa dos argumentos matemáticos e computacionais.
