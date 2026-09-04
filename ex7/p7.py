
def log_trad(gravidade, modulo, mensagem):
    return f"[{gravidade}] {modulo}: {mensagem}"

msg_sucesso = log_trad("INFO", "main", "Sucesso!")
msg_erro = log_trad("ERROR", "main", "Erro!")
msg_aviso = log_trad("WARNING", "main", "Aviso!")
print(msg_sucesso)
print(msg_erro)
print(msg_aviso)

adicionar_gravidade = lambda gravidade: lambda modulo: lambda mensagem: f"[{gravidade}] {modulo}: {mensagem}"

adicionar_modulo = adicionar_gravidade("INFO")

mensagem = adicionar_modulo("main")

mensagem_sucesso = mensagem("Sucesso(Curried)!")
mensagem_erro = mensagem("Erro(Curried)!")
mensagem_aviso = mensagem("Aviso(Curried)!")
print(mensagem_sucesso)
print(mensagem_erro)
print(mensagem_aviso)
