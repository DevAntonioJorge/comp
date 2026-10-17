import sys
import time

# ==========================================
# PROJETO 10: O AVALIADOR DE TEOREMAS (LPO)
# ==========================================

# Funções base de quantificadores usando all() e any()
def para_todo(dominio, predicado):
    """Implementa o quantificador Universal (∀)"""
    return all(predicado(x) for x in dominio)

def existe(dominio, predicado):
    """Implementa o quantificador Existencial (∃)"""
    return any(predicado(x) for x in dominio)

# ==========================================
# VERSÃO A: Domínio Finito (10 Elementos)
# ==========================================
print("=== VERSÃO A: Domínio Finito (10 elementos) ===")

def versao_a():
    try:
        # Criando um domínio finito com 10 elementos (de 1 a 10)
        dominio_a = list(range(1, 11))
        print(f"Elementos criados no domínio A: {dominio_a}")
        print(f"Quantidade total de elementos criados: {len(dominio_a)}")

        # Fórmula a ser avaliada: ∀x ∃y (x < y) no domínio finito
        # Tradução: Para todo x, existe um y no domínio tal que x < y.
        def formula_a(x):
            return existe(dominio_a, lambda y: x < y)

        resultado_a = para_todo(dominio_a, formula_a)
        print(f"Resultado da avaliação da fórmula ∀x ∃y (x < y) na Versão A: {resultado_a}")
        print("(Retorna Falso porque para o último elemento x=10, não há nenhum y maior que ele no domínio).\n")
    except Exception as s:
        print(f"[erro na versão A]Ocorreu um erro inesperado durante a execulção do programa: {s}")


# ==========================================
# VERSÃO B: Domínio Infinito e Contagem
# ==========================================
print("=== VERSÃO B: Domínio Infinito (Gerador de Naturais) ===")
def versão_b():

    def gerador_naturais():
        """Gerador infinito de números naturais: 0, 1, 2, 3..."""
        n = 0
        while True:
            yield n
            n += 1

    try:
        elementos_testados_forall = 0
        gen_x = gerador_naturais()
    
        print(f"Iniciando avaliação em domínio infinito...")
    
        for x in gen_x:
            elementos_testados_forall += 1
            # Usando \r para atualizar a contagem de forma dinâmica na mesma linha,
            # ou impressão normal se preferir ver o histórico de linhas subindo.
            sys.stdout.write(f"\r[Versão B] Testando x = {x} | Total de elementos testados: {elementos_testados_forall}")
            sys.stdout.flush()
            # Pausa breve para acompanhar visualmente
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        # Captura exatamente a interrupção manual do usuário via Ctrl+C
        print("\n\n[Execução interrompida manualmente pelo usuário via Ctrl+C]")
        print(f"Quantidade total de elementos criados e testados pelo quantificador ∀ antes da interrupção: {elementos_testados_forall}")
    except Exception as s:
        print(f"\n[Erro na Versão B]: Ocorreu uma exceção: {s}")

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================

if __name__== "__main__":
    versao_a()
    time.sleep(20) #tempo para poder ser lido o resultado da versão A
    print("-"*20)
    versão_b()
    

