import requests
import time
import socket
import platform
import getpass
import ctypes
from plyer import notification
from requests.exceptions import RequestException

# Configurações do servidor
SERVER_URL = "http://localhost:4000/api/v1"
LAST_CODE = None

def get_system_info():
    """
    Recupera informações básicas do sistema e usuário.
    """
    return {
        "ipAddress": socket.gethostbyname(socket.gethostname()),
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "operatingSystem": platform.system(),
        "architecture": platform.machine()
    }

def notify(title: str, message: str, timeout: int = 10):
    """
    Envia notificação para o usuário.
    """
    notification.notify(
        title=title,
        message=message,
        app_name="Monitor Agent",
        timeout=timeout
    )

def register_agent():
    """
    Registra o Agent no servidor se ainda não estiver registrado.
    """
    info = get_system_info()
    try:
        response = requests.get(f"{SERVER_URL}/check-agent/{info['hostname']}")
        if response.status_code == 200:
            print("Agent já registrado.")
        else:
            response_post = requests.post(f"{SERVER_URL}/create-agent", json=info)
            if response_post.status_code == 201:
                print("Agent registrado com sucesso.")
                notify("Monitor Agent", "Agent registrado com sucesso!")
            else:
                print(f"Falha ao registrar Agent: {response_post.text}")
                notify("Monitor Agent", "Erro ao registrar Agent.", timeout=20)
    except RequestException as e:
        print(f"Erro ao registrar Agent: {e}")
        notify("Monitor Agent", f"Erro de conexão: {e}", timeout=20)

def update_activity():
    """
    Atualiza a última atividade do Agent no servidor.
    """
    try:
        hostname = get_system_info()["hostname"]
        response = requests.post(f"{SERVER_URL}/activity/{hostname}")
        if response.status_code == 200:
            print("Atividade atualizada.")
        else:
            print(f"Falha ao atualizar atividade: {response.text}")
    except RequestException as e:
        print(f"Erro ao atualizar atividade: {e}")

def send_returned(result: str):
    """
    Envia resultado de comando (returned) para o servidor.
    """
    try:
        hostname = get_system_info()["hostname"]
        data = {"returned": result}
        response = requests.post(f"{SERVER_URL}/returned/{hostname}", json=data)
        if response.status_code == 200:
            print("Returned enviado com sucesso.")
        else:
            print(f"Falha ao enviar returned: {response.text}")
    except RequestException as e:
        print(f"Erro ao enviar returned: {e}")

def execute_command(command: str) -> str:
    """
    Executa comandos recebidos do servidor.
    """
    parts = command.split(" ")
    cmd = parts[0].lower()

    if cmd == "mensagem":
        message = " ".join(parts[1:])
        ctypes.windll.user32.MessageBoxW(0, message, "Mensagem do Servidor", 1)
        return "Mensagem exibida."
    else:
        return "Comando não reconhecido."

def check_command():
    """
    Verifica se há comando novo no servidor e executa.
    """
    global LAST_CODE
    try:
        hostname = get_system_info()["hostname"]
        code_resp = requests.get(f"{SERVER_URL}/last-code/{hostname}")
        command_resp = requests.get(f"{SERVER_URL}/command/{hostname}")

        if code_resp.status_code != 200 or command_resp.status_code != 200:
            return

        code_data = code_resp.json()
        command_data = command_resp.json()

        if code_data["code"] != LAST_CODE:
            LAST_CODE = code_data["code"]
            cmd = command_data.get("command")
            if cmd:
                print(f"Executando comando: {cmd}")
                result = execute_command(cmd)
                send_returned(result)

    except RequestException as e:
        print(f"Erro ao verificar comandos: {e}")
        notify("Monitor Agent", "Erro ao verificar comandos.", timeout=10)

def main_loop():
    """
    Loop principal do Agent.
    """
    register_agent()
    while True:
        update_activity()
        check_command()
        time.sleep(1)

if __name__ == "__main__":
    main_loop()
