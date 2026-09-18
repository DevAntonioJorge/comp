import p8
def main ():
    x = int(input("Digite o primeiro número (x): "))
    y = int(input("Digite o segundo número (y): "))

    p8.rodar_versao_a(x, y)

    print("\n")

    try:
        p8.rodar_versao_b(x, y)
    except p8.TimeoutError as e:
        print(f"\n[ERRO CONTROLADO - Versão B] {e}")
    except ValueError as e:
        print(f"\n[ERRO - Versão B] {e}")
if __name__ == "__main__":
 main()