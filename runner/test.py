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

def check_for_command():
    global LAST_CODE
    try:
        hostname = get_system_info()["hostname"]
        # Pega o último código do Agent
        new = requests.get(f'{SERVER_URL}/last-code/{hostname}').json()
        command_data = requests.get(f'{SERVER_URL}/command/{hostname}').json()

        # Se o código mudou, é um comando novo
        if new['code'] != LAST_CODE:
            LAST_CODE = new['code']
            command = command_data.get('command')
            print(f'Executando comando: {command}')
            
            # Executa o comando
            result = execute_command(command)
            
            # Envia o resultado
            send_returned(result)

            # Marca o comando como executado
            teste = requests.post(f'{SERVER_URL}/command-executed/{hostname}')

    except Exception as e:
        print(f"Erro ao checar comando: {e}")

def main_loop():
    """
    Loop principal do Agent.
    """
    register_agent()
    while True:
        update_activity()
        check_for_command()
        time.sleep(1)

if __name__ == "__main__":
    main_loop()
