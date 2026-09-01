produtos = [400.5, 1000.1, 100]


def calculo_trad(preco, desconto, taxa):
    return (preco * (1 + taxa)) - desconto

Preco_Final = lambda taxa: lambda desconto: lambda preco: (preco * (1 + taxa)) - desconto
Taxa = Preco_Final(0.2)
Desconto = Taxa(100)
for preco in produtos:
    final = Desconto(preco)
    print(f"Preço com função curried: {final:7.2f}")
    final_trad = calculo_trad(preco, 100, 0.2)
    print(f"Preço com função tradicional: {final_trad:7.2f}")
