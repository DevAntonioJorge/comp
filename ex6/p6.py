produtos = [400.5, 1000.1, 100]


def calculo_trad(preco, desconto, taxa):
    return (preco * (1 + taxa)) - desconto

aplicar_taxa = lambda taxa: lambda desconto: lambda preco: (preco * (1 + taxa)) - desconto
aplicar_desconto = aplicar_taxa(0.2)
calcular_preco_final = aplicar_desconto(100)

final = calcular_preco_final(400.5)
final2 = calcular_preco_final(1000.1)
final3 = calcular_preco_final(100)
print(f"Preço com função curried: {final:7.2f}")
print(f"Preço com função curried: {final2:7.2f}")
print(f"Preço com função curried: {final3:7.2f}")

final_trad = calculo_trad(400.5, 100, 0.2)
final_trad2 = calculo_trad(1000.1, 100, 0.2)
final_trad3 = calculo_trad(100, 100, 0.2)
print(f"Preço com função tradicional: {final_trad:7.2f}")
print(f"Preço com função tradicional: {final_trad2:7.2f}")
print(f"Preço com função tradicional: {final_trad3:7.2f}")
