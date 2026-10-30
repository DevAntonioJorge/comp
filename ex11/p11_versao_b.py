"""Projeto 11 - Versao B: codigo ofuscado, transpilador Python->JS e decisor com timeout."""

import ast
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from p11_versao_a import scan, scan_regex

PAYLOAD = "'SENHA_'+'VAZADA'"

DIRETO = f'print(eval("{PAYLOAD}"))\n'

OFUSCADOS = {
    "concatenacao 'ev'+'al'": (
        "import builtins\n"
        'alvo = "ev" + "al"\n'
        f'print(getattr(builtins, alvo)("{PAYLOAD}"))\n'
    ),
    "chr() em lista": (
        "import builtins\n"
        "alvo = ''.join(map(chr, [101, 118, 97, 108]))\n"
        f'print(getattr(builtins, alvo)("{PAYLOAD}"))\n'
    ),
    "string invertida": (
        "import builtins\n"
        'alvo = "lave"[::-1]\n'
        f'print(getattr(builtins, alvo)("{PAYLOAD}"))\n'
    ),
    "reflexao os.system": (
        "import importlib\n"
        'm = importlib.import_module("o" + "s")\n'
        'getattr(m, "sys" + "tem")("echo SENHA_VAZADA")\n'
    ),
}


def executar_sandbox(codigo, timeout):
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / "alvo.py"
        arquivo.write_text(codigo, encoding="utf-8")
        try:
            proc = subprocess.run(
                [sys.executable, "-I", str(arquivo)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=pasta,
            )
            return proc.stdout, False
        except subprocess.TimeoutExpired:
            return "", True


def prever_senha_vazada(codigo, timeout_inicial=0.25, timeout_maximo=2.0):
    timeout = timeout_inicial
    while True:
        saida, estourou = executar_sandbox(codigo, timeout)
        if not estourou:
            return ("SIM" if saida.strip() == "SENHA_VAZADA" else "NAO"), timeout
        if timeout >= timeout_maximo:
            return "INDECIDIVEL", timeout
        timeout = min(timeout * 2, timeout_maximo)


class Transpilador:
    def __init__(self):
        self.declaradas = set()

    def transpilar(self, codigo):
        arvore = ast.parse(codigo)
        linhas = [self._stmt(no) for no in arvore.body]
        return "\n".join(l for l in linhas if l) + "\n"

    def _stmt(self, no):
        if isinstance(no, ast.Import):
            if all(a.name == "builtins" for a in no.names):
                return None
            raise NotImplementedError("import nao suportado")
        if isinstance(no, ast.Assign) and len(no.targets) == 1 and isinstance(no.targets[0], ast.Name):
            nome = no.targets[0].id
            prefixo = "" if nome in self.declaradas else "let "
            self.declaradas.add(nome)
            return f"{prefixo}{nome} = {self._expr(no.value)};"
        if isinstance(no, ast.Expr):
            return f"{self._expr(no.value)};"
        raise NotImplementedError(type(no).__name__)

    def _expr(self, no):
        if isinstance(no, ast.Constant):
            return json.dumps(no.value) if isinstance(no.value, str) else repr(no.value)
        if isinstance(no, ast.Name):
            return no.id
        if isinstance(no, ast.List):
            return "[" + ", ".join(self._expr(e) for e in no.elts) + "]"
        if isinstance(no, ast.BinOp) and isinstance(no.op, ast.Add):
            return f"({self._expr(no.left)} + {self._expr(no.right)})"
        if isinstance(no, ast.Attribute):
            return f"{self._expr(no.value)}.{no.attr}"
        if isinstance(no, ast.Subscript) and isinstance(no.slice, ast.Slice):
            fatia = no.slice
            passo = fatia.step
            if (
                fatia.lower is None
                and fatia.upper is None
                and isinstance(passo, ast.UnaryOp)
                and isinstance(passo.op, ast.USub)
                and isinstance(passo.operand, ast.Constant)
                and passo.operand.value == 1
            ):
                return f"[...{self._expr(no.value)}].reverse().join('')"
            raise NotImplementedError("fatia nao suportada")
        if isinstance(no, ast.Call):
            return self._chamada(no)
        raise NotImplementedError(type(no).__name__)

    def _chamada(self, no):
        func = no.func
        args = no.args
        if isinstance(func, ast.Name):
            if func.id == "print":
                return f"console.log({', '.join(self._expr(a) for a in args)})"
            if func.id == "getattr" and len(args) == 2:
                if isinstance(args[0], ast.Name) and args[0].id == "builtins":
                    return f"globalThis[{self._expr(args[1])}]"
                return f"{self._expr(args[0])}[{self._expr(args[1])}]"
            if func.id == "chr":
                return f"String.fromCharCode({', '.join(self._expr(a) for a in args)})"
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "join"
            and len(args) == 1
            and isinstance(args[0], ast.Call)
            and isinstance(args[0].func, ast.Name)
            and args[0].func.id == "map"
            and isinstance(args[0].args[0], ast.Name)
            and args[0].args[0].id == "chr"
        ):
            return (
                f"Array.from({self._expr(args[0].args[1])})"
                f".map(c => String.fromCharCode(c)).join({self._expr(func.value)})"
            )
        return f"{self._expr(func)}({', '.join(self._expr(a) for a in args)})"


def titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


def rodar_python(codigo):
    saida, estourou = executar_sandbox(codigo, 5)
    return "(timeout)" if estourou else saida.strip()


def rodar_js(codigo):
    with tempfile.TemporaryDirectory() as pasta:
        arquivo = Path(pasta) / "alvo.js"
        arquivo.write_text(codigo, encoding="utf-8")
        proc = subprocess.run(["node", str(arquivo)], capture_output=True, text=True, timeout=5)
        return proc.stdout.strip()


def demo_scanner_vs_ofuscados():
    titulo("1. Scanner sintatico contra codigo direto e ofuscado")
    res = scan(DIRETO)
    print(f"{'Amostra':<28}{'Scanner':<12}{'Saida real'}")
    print("-" * 70)
    print(f"{'eval direto':<28}{'BLOQUEADO' if res.bloqueado else 'PERMITIDO':<12}{rodar_python(DIRETO)}")
    for nome, codigo in OFUSCADOS.items():
        res = scan(codigo)
        print(f"{nome:<28}{'BLOQUEADO' if res.bloqueado else 'PERMITIDO':<12}{rodar_python(codigo)}")


def demo_clique():
    titulo("2. O momento do clique")
    linha = 'alvo = "ev" + "al"'
    arvore = ast.parse(linha)
    literais = [n.value for n in ast.walk(arvore) if isinstance(n, ast.Constant)]
    ns = {}
    exec(linha, ns)
    print(f"Linha ofuscada        : {linha}")
    print(f"O scanner enxerga     : literais {literais} -> nenhum e 'eval'")
    print(f"A execucao produz     : alvo = {ns['alvo']!r}")
    print("O texto nunca contem a palavra proibida; ela so existe em tempo de execucao.")


def demo_transpilador():
    titulo("3. Transpilador Python -> JavaScript")
    tem_node = shutil.which("node") is not None
    for nome in list(OFUSCADOS)[:3]:
        py = OFUSCADOS[nome]
        js = Transpilador().transpilar(py)
        print(f"\n--- {nome} ---")
        print("JS gerado:")
        print(js.rstrip())
        achados_js = scan_regex(js)
        print(f"Scanner (regex) no JS : {'BLOQUEADO' if achados_js else 'PERMITIDO'}")
        print(f"Saida Python          : {rodar_python(py)}")
        print(f"Saida JavaScript      : {rodar_js(js) if tem_node else '(node nao encontrado)'}")
    js_direto = f'console.log(eval("{PAYLOAD}"));'
    print(f"\nJS com eval direto    : {'BLOQUEADO' if scan_regex(js_direto) else 'PERMITIDO'}")


AMOSTRAS_DECISAO = {
    "vazamento direto": ('print("SENHA_VAZADA")\n', "SIM"),
    "vazamento ofuscado": (OFUSCADOS["concatenacao 'ev'+'al'"], "SIM"),
    "saida inofensiva": ('print("ola")\n', "NAO"),
    "lento (1.2s) e vaza": ('import time\ntime.sleep(1.2)\nprint("SENHA_VAZADA")\n', "SIM"),
    "loop infinito": ('while True:\n    pass\nprint("SENHA_VAZADA")\n', "INDECIDIVEL"),
    "busca impar perfeito": (
        "def soma_divisores(n):\n"
        "    s = 1\n"
        "    i = 3\n"
        "    while i * i <= n:\n"
        "        if n % i == 0:\n"
        "            s += i\n"
        "            if i * i != n:\n"
        "                s += n // i\n"
        "        i += 2\n"
        "    return s\n"
        "n = 3\n"
        "while True:\n"
        "    if soma_divisores(n) == n:\n"
        '        print("SENHA_VAZADA")\n'
        "        break\n"
        "    n += 2\n",
        "INDECIDIVEL",
    ),
}


def demo_decisor():
    titulo("4. Decisor dinamico: a saida sera 'SENHA_VAZADA'?")
    print(f"{'Amostra':<24}{'Veredito':<14}{'Timeout final':<16}Esperado")
    print("-" * 70)
    for nome, (codigo, esperado) in AMOSTRAS_DECISAO.items():
        veredito, timeout = prever_senha_vazada(codigo)
        print(f"{nome:<24}{veredito:<14}{timeout:<16.2f}{esperado}")


def main():
    demo_scanner_vs_ofuscados()
    demo_clique()
    demo_transpilador()
    demo_decisor()


if __name__ == "__main__":
    main()
