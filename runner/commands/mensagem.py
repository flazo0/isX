name = "mensagem"

def run(args):
    import ctypes
    msg = " ".join(args) or "Mensagem vazia."
    ctypes.windll.user32.MessageBoxW(0, msg, "Mensagem do Servidor", 1)
    return f"Mensagem exibida: {msg}"
