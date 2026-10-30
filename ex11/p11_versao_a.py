"""Projeto 11 - Versao A: Scanner sintatico (regex + AST)."""

import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REGEX_PERIGOSOS = [
    (re.compile(r"\beval\s*\("), "eval()"),
    (re.compile(r"\bexec\s*\("), "exec()"),
    (re.compile(r"\bos\s*\.\s*system\s*\("), "os.system()"),
    (re.compile(r"\bos\s*\.\s*popen\s*\("), "os.popen()"),
    (re.compile(r"\bsubprocess\s*\.\s*\w+\s*\("), "subprocess.*()"),
    (re.compile(r"\b__import__\s*\("), "__import__()"),
]

CHAMADAS_BLOQUEADAS = {
    "eval",
    "exec",
    "compile",
    "__import__",
    "os.system",
    "os.popen",
    "subprocess.run",
    "subprocess.Popen",
    "subprocess.call",
    "subprocess.check_output",
    "subprocess.getoutput",
}


@dataclass
class Achado:
    metodo: str
    regra: str
    linha: int


@dataclass
class Resultado:
    achados: list = field(default_factory=list)

    @property
    def bloqueado(self):
        return bool(self.achados)


def scan_regex(codigo):
    achados = []
    for numero, linha in enumerate(codigo.splitlines(), 1):
        for padrao, nome in REGEX_PERIGOSOS:
            if padrao.search(linha):
                achados.append(Achado("regex", nome, numero))
    return achados


class _Visitante(ast.NodeVisitor):
    def __init__(self):
        self.achados = []
        self.modulos = {}
        self.nomes = {}

    def visit_Import(self, no):
        for alias in no.names:
            self.modulos[alias.asname or alias.name] = alias.name
        self.generic_visit(no)

    def visit_ImportFrom(self, no):
        if no.module:
            for alias in no.names:
                self.nomes[alias.asname or alias.name] = f"{no.module}.{alias.name}"
        self.generic_visit(no)

    def _nome_qualificado(self, func):
        if isinstance(func, ast.Name):
            return self.nomes.get(func.id, func.id)
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            modulo = self.modulos.get(func.value.id, func.value.id)
            return f"{modulo}.{func.attr}"
        return None

    def visit_Call(self, no):
        nome = self._nome_qualificado(no.func)
        if nome in CHAMADAS_BLOQUEADAS:
            self.achados.append(Achado("ast", f"{nome}()", no.lineno))
        self.generic_visit(no)


def scan_ast(codigo):
    try:
        arvore = ast.parse(codigo)
    except SyntaxError:
        return []
    visitante = _Visitante()
    visitante.visit(arvore)
    return visitante.achados


def scan(codigo):
    return Resultado(scan_ast(codigo) + scan_regex(codigo))


def scan_arquivo(caminho):
    return scan(Path(caminho).read_text(encoding="utf-8"))


TESTES = [
    ("eval direto", 'print(eval("1 + 1"))', True),
    ("exec direto", 'exec("x = 1")', True),
    ("os.system", 'import os\nos.system("echo oi")', True),
    ("os.system com alias", 'import os as sistema\nsistema.system("echo oi")', True),
    ("from os import system", 'from os import system\nsystem("echo oi")', True),
    ("subprocess.run", 'import subprocess\nsubprocess.run(["ls"])', True),
    ("__import__", '__import__("os")', True),
    ("soma simples", "def soma(a, b):\n    return a + b\nprint(soma(1, 2))", False),
    ("leitura de arquivo", 'with open("a.txt") as f:\n    print(f.read())', False),
    ("nome parecido (medieval)", "def medieval(x):\n    return x\nmedieval(1)", False),
    ("lista e laco", "for i in range(3):\n    print(i)", False),
]


def executar_testes():
    falhas = 0
    print(f"{'Teste':<28}{'Esperado':<12}{'Obtido':<12}{'Regras':<28}Status")
    print("-" * 90)
    for nome, codigo, esperado in TESTES:
        resultado = scan(codigo)
        regras = ", ".join(sorted({a.regra for a in resultado.achados})) or "-"
        ok = resultado.bloqueado == esperado
        falhas += not ok
        print(
            f"{nome:<28}{'BLOQUEAR' if esperado else 'PERMITIR':<12}"
            f"{'BLOQUEADO' if resultado.bloqueado else 'PERMITIDO':<12}"
            f"{regras:<28}{'OK' if ok else 'FALHA'}"
        )
    print("-" * 90)
    print(f"{len(TESTES) - falhas}/{len(TESTES)} testes passaram")
    return falhas


def main():
    if len(sys.argv) > 1:
        codigo_saida = 0
        for caminho in sys.argv[1:]:
            resultado = scan_arquivo(caminho)
            if resultado.bloqueado:
                codigo_saida = 1
                print(f"[BLOQUEADO] {caminho}")
                for a in resultado.achados:
                    print(f"  linha {a.linha}: {a.regra} ({a.metodo})")
            else:
                print(f"[PERMITIDO] {caminho}")
        sys.exit(codigo_saida)
    sys.exit(1 if executar_testes() else 0)


if __name__ == "__main__":
    main()
