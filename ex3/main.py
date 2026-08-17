"""Mini-interpretador didático para funções recursivas primitivas."""

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


class PRFError(Exception):
    """Erro de sintaxe ou de execução da linguagem."""


@dataclass
class Expr:
    kind: str
    value: object = None
    args: object = None


@dataclass
class Function:
    name: str
    arity: int
    implementation: object
    cache: object = None

    def __post_init__(self):
        if self.cache is None:
            self.cache = {}

    def __call__(self, values):
        if len(values) != self.arity:
            raise PRFError(
                f"{self.name} espera {self.arity} argumento(s), "
                f"mas recebeu {len(values)}"
            )
        if any(not isinstance(value, int) or value < 0 for value in values):
            raise PRFError("a linguagem trabalha apenas com números naturais")
        key = tuple(values)
        if key not in self.cache:
            self.cache[key] = self.implementation(values)
        return self.cache[key]


class Parser:
    token_pattern = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+|[=(),\[\]]")

    def __init__(self, source):
        source = re.sub(r"#.*", "", source)
        self.tokens = self.token_pattern.findall(source)
        self.position = 0

    def current(self):
        if self.position >= len(self.tokens):
            return None
        return self.tokens[self.position]

    def take(self, expected=None):
        token = self.current()
        if token is None:
            raise PRFError("fim inesperado do arquivo")
        if expected is not None and token != expected:
            raise PRFError(f"esperado {expected!r}, recebido {token!r}")
        self.position += 1
        return token

    def parse(self):
        definitions = {}
        while self.current() is not None:
            name = self.take()
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                raise PRFError(f"nome inválido: {name}")
            self.take("=")
            if name in definitions:
                raise PRFError(f"definição duplicada: {name}")
            definitions[name] = self.expression()
        return definitions

    def expression(self):
        token = self.take()

        if token == "S":
            return Expr("successor")

        if token in ("COMP", "REC"):
            operation = token
            self.take("(")
            first = self.expression()
            self.take(",")
            if operation == "COMP":
                self.take("[")
                parts = []
                if self.current() != "]":
                    while True:
                        parts.append(self.expression())
                        if self.current() != ",":
                            break
                        self.take(",")
                        if self.current() == "]":
                            break
                self.take("]")
                self.take(")")
                return Expr("compose", args=[first, parts])
            second = self.expression()
            self.take(")")
            return Expr("recursion", args=[first, second])

        zero_match = re.fullmatch(r"Z(\d+)", token)
        if zero_match:
            return Expr("zero", int(zero_match.group(1)))

        projection_match = re.fullmatch(r"P(\d+)_(\d+)", token)
        if projection_match:
            index = int(projection_match.group(1))
            arity = int(projection_match.group(2))
            return Expr("projection", value=(index, arity))

        return Expr("reference", token)


class Program:
    """Programa carregado e compilado a partir de definições da DSL."""

    def __init__(self, definitions):
        self.definitions = definitions
        self.compiled = {}
        self.compiling = set()

    def function(self, name):
        if name not in self.definitions and name not in BUILTINS:
            raise PRFError(f"função desconhecida: {name}")
        return self.compile_name(name)

    def compile_name(self, name):
        if name in self.compiled:
            return self.compiled[name]
        if name in self.compiling:
            raise PRFError(f"referência circular envolvendo {name}")
        if name in BUILTINS:
            return BUILTINS[name]

        self.compiling.add(name)
        try:
            function = self.compile_expression(name, self.definitions[name])
            self.compiled[name] = function
            return function
        finally:
            self.compiling.remove(name)

    def compile_expression(self, name, expression):
        kind = expression.kind

        if kind == "reference":
            referenced = self.compile_name(expression.value)
            return Function(name, referenced.arity, referenced.implementation)

        if kind == "successor":
            return Function(name, 1, lambda values: values[0] + 1)

        if kind == "zero":
            arity = expression.value
            return Function(name, arity, lambda values: 0)

        if kind == "projection":
            index, arity = expression.value
            if index < 1 or index > arity:
                raise PRFError(f"projeção P{index}_{arity} é inválida")
            return Function(name, arity, lambda values: values[index - 1])

        if kind == "compose":
            outer_expression, inner_expressions = expression.args
            outer = self.compile_expression(name + ".outer", outer_expression)
            inner = [
                self.compile_expression(name + f".inner{index}", item)
                for index, item in enumerate(inner_expressions)
            ]
            if len(inner) != outer.arity:
                raise PRFError(
                    f"COMP precisa de {outer.arity} função(ões), "
                    f"mas recebeu {len(inner)}"
                )
            if not inner:
                arity = 0
            else:
                arity = inner[0].arity
                if any(item.arity != arity for item in inner):
                    raise PRFError("todas as funções de COMP devem ter a mesma aridade")

            def composed(values):
                return outer([item(values) for item in inner])

            return Function(name, arity, composed)

        if kind == "recursion":
            base_expression, step_expression = expression.args
            base = self.compile_expression(name + ".base", base_expression)
            step = self.compile_expression(name + ".step", step_expression)
            expected_step_arity = base.arity + 2
            if step.arity != expected_step_arity:
                raise PRFError(
                    "o passo de REC deve receber os argumentos fixos, "
                    "o contador e o acumulador"
                )

            def recursive(values):
                fixed = values[:-1]
                counter = values[-1]
                result = base(fixed)
                for current in range(counter):
                    result = step(fixed + [current, result])
                return result

            return Function(name, base.arity + 1, recursive)

        raise PRFError(f"expressão desconhecida: {kind}")


def pair(values):
    first, second = values
    total = first + second
    return total * (total + 1) // 2 + second


def first(values):
    encoded = values[0]
    diagonal = 0
    while (diagonal + 1) * (diagonal + 2) // 2 <= encoded:
        diagonal += 1
    triangular = diagonal * (diagonal + 1) // 2
    return diagonal - (encoded - triangular)


def second(values):
    encoded = values[0]
    diagonal = 0
    while (diagonal + 1) * (diagonal + 2) // 2 <= encoded:
        diagonal += 1
    triangular = diagonal * (diagonal + 1) // 2
    return encoded - triangular


BUILTINS = {
    # Pairing de Cantor: uma biblioteca auxiliar para representar o estado
    # duplo da sequência de Fibonacci usando apenas um natural.
    "PAIR": Function("PAIR", 2, pair),
    "FST": Function("FST", 1, first),
    "SND": Function("SND", 1, second),
}


def load_program(path):
    source = Path(path).read_text(encoding="utf-8")
    return Program(Parser(source).parse())


def run_demo(program):
    print("--- Mini-Interpretador FRP ---")
    print("Soma e multiplicação definidas na DSL:")
    print(f"ADD(7, 5)  = {program.function('ADD')([7, 5])}")
    print(f"MUL(6, 7)  = {program.function('MUL')([6, 7])}")

    print("\nProblemas práticos:")
    fib = program.function("FIB")
    division = program.function("DIV")
    prime = program.function("PRIME")
    print("Fibonacci:", ", ".join(f"FIB({n})={fib([n])}" for n in range(11)))
    print(f"DIV(17, 5) = {division([17, 5])}")
    print(f"DIV(20, 5) = {division([20, 5])}")
    print("Primos até 20:", [n for n in range(21) if prime([n])])


def main():
    parser = argparse.ArgumentParser(description="Interpretador didático de FRPs")
    parser.add_argument(
        "--file",
        default=Path(__file__).parent / "examples" / "programas.prf",
        help="arquivo com definições da linguagem",
    )
    parser.add_argument("--function", help="função a executar")
    parser.add_argument("--args", nargs="*", type=int, default=[])
    parser.add_argument("--demo", action="store_true", help="executa os exemplos")
    options = parser.parse_args()

    program = load_program(options.file)
    if options.demo or options.function is None:
        run_demo(program)
        return

    function = program.function(options.function)
    print(f"{options.function}{tuple(options.args)} = {function(options.args)}")


if __name__ == "__main__":
    main()
