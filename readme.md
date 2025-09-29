# Documentação do Malware: RAT (Remote Access Trojan, ou “Trojan de Acesso Remoto”)
<br>

## Visão Geral

Um RAT (Remote Access Trojan) é um tipo de malware projetado para fornecer controle remoto total sobre um computador infectado. Ele funciona como um “Trojan” (Cavalo de Troia), enganando o usuário para que o execute, permitindo que um invasor acesse e manipule a máquina sem consentimento.

---

## Arquitetura do Sistema

O sistema é dividido nos seguintes módulos:

### 1. Runner

* **Linguagens**: Python, C
* **Descrição**:
  Malware que roda no computador do usuário final. Ele:

  * Estabelece conexão com o servidor.
  * Recebe e executa comandos enviados pelo painel.
  * Envia informações do sistema e status do computador.
* **Funções principais**:

  * Registro da máquina no servidor.
  * Atualização de status e timestamps de atividade.
  * Recebimento e execução de comandos remotos.
  * Comunicação com módulo de tela (screen) para transmissão de vídeo.

---

### 2. Console

* **Linguagem**: NodeJS
* **Descrição**:
  Interface web utilizada pelo atacante para controlar os computadores registrados.
  Funciona como **painel de gerenciamento central**, permitindo:

  * Visualizar todas as máquinas conectadas.
  * Verificar status online/offline.
  * Enviar comandos remotos.
  * Acompanhar a atividade em tempo real.
  * Receber transmissões de vídeo do módulo Screen.
* **Funcionalidades principais**:

  * Dashboard com todas as máquinas.
  * Histórico de comandos enviados.
  * Controle granular de cada máquina.

---

### 3. Screenshot

* **Linguagem**: Python
* **Descrição**:
  Módulo isolado que captura a tela do computador cliente e envia vídeo para o servidor.

  * Permite monitoramento remoto em tempo real.
  * Funciona de forma independente do cliente principal, garantindo menor interferência no sistema principal.
* **Funcionalidades principais**:

  * Captura de tela periódica ou contínua.
  * Compressão e envio de vídeo para o servidor.
  * Integração com Painel para exibição ao administrador.

---

### 4. Matrix

* **Linguagem**: NodeJS
* **Descrição**:
  Servidor central responsável pela comunicação entre Painel e Clients.

  * Recebe dados e status dos clientes.
  * Armazena informações de comandos e resultados.
  * Gerencia transmissões de vídeo.
  * Encaminha comandos do Painel para os Clients.
* **Funcionalidades principais**:

  * Registro e autenticação de máquinas.
  * Armazenamento de status, comandos e logs.
  * Transmissão em tempo real de dados para Painel.
  * Escalável para múltiplos clientes simultâneos.

---

### 5. Updater

* **Linguagem**: Python
* **Descrição**:
  Sistema de atualização automatizada para todos os módulos do sistema.

  * Verifica versões disponíveis no servidor.
  * Baixa e aplica atualizações nos clientes.
  * Garante consistência de versões entre Client, Screen e Server.
* **Funcionalidades principais**:

  * Atualização incremental ou completa.
  * Compatibilidade com múltiplos sistemas operacionais.
  * Registro de histórico de atualizações.

---

## Fluxo de Comunicação

```
[Client] <---> [Server] <---> [Painel]
   |                               ^
   |                               |
   +--> [Screen] ------------------+
```

* **Client** envia dados e recebe comandos do **Server**.
* **Screen** transmite vídeo para o **Server**, que repassa ao **Painel**.
* **Painel** envia comandos e visualiza status em tempo real.
* **Update** verifica novas versões e aplica em Client/Screen automaticamente.

---