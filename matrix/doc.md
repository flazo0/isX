# API Documentation v1

## Overview

Esta API permite o gerenciamento de dispositivos, incluindo o registro, atualização de status, verificação de conexão e controle de comandos. Abaixo estão as rotas disponíveis, incluindo detalhes sobre como usá-las.

---

## Base URL

```
http://<your-domain>/api/v1
```

---

## Endpoints
Beleza! Vou reescrever a documentação **corrigindo nomes, tipos e respostas**, seguindo o padrão que você está usando, e ajustando para o **Agent** que criamos com MongoDB/Mongoose:

---

### 1. Register o Agent

* **POST** `/create-agent`
* **Description**: Registra um novo Agent no sistema, armazenando informações da máquina e do usuário.
* **Request Body**:

```json
{
  "ipAddress": "string",          // Endereço IP da máquina
  "hostname": "string",           // Nome do computador
  "username": "string",           // Usuário logado na máquina
  "operatingSystem": "string",    // Sistema operacional (opcional, padrão: "unknown")
  "architecture": "string",       // Arquitetura da máquina (opcional, valores possíveis: "x86", "x64", "arm")
  "cpu": {                        // Informações da CPU (opcional)
    "model": "string",
    "cores": 0
  },
  "memory": {                     // Informações da memória RAM (opcional)
    "total": 0,
    "free": 0
  },
  "disk": {                       // Informações do disco (opcional)
    "total": 0,
    "free": 0
  }
}
```

* **Responses**:

  * **201 Created**: Agent registrado com sucesso.

  ```json
  {
    "message": "Agent registrado com sucesso.",
    "agentId": "string" // ID do Agent no MongoDB
  }
  ```

  * **400 Bad Request**: Campos obrigatórios faltando.

  ```json
  {
    "errors": true,
    "message": "ipAddress, hostname and username are required."
  }
  ```

  * **500 Internal Server Error**: Falha ao criar Agent.

  ```json
  {
    "message": "Falha ao registrar Agent",
    "error": "string"
  }
  ```

---

### 2. Update Device Returned Status

- **POST** `/post/returned/:computer_`
- **Description**: Atualiza o status de devolução do dispositivo.
- **Parameters**:
    - `computer_`: ID do computador (URL parameter).
- **Request Body**:
    ```json
    {
        "returned_": "boolean"
    }
    ```
- **Responses**:
    - **200 OK**: Status updated successfully.
    - **404 Not Found**: Device not found.
    - **500 Internal Server Error**: An error occurred.

---

### 3. Get Device Returned Status

- **GET** `/get/returned/:computer_`
- **Description**: Obtém o status de devolução do dispositivo.
- **Parameters**:
    - `computer_`: ID do computador (URL parameter).
- **Responses**:
    - **200 OK**: Returns the returned status.
        ```json
        {
            "returned": "boolean"
        }
        ```
    - **404 Not Found**: Device not found.
    - **500 Internal Server Error**: An error occurred.

---

### 4. Update Device Activity Timestamp

- **POST** `/update/activity/:computer_`
- **Description**: Atualiza a data e hora da última atividade do dispositivo.
- **Parameters**:
    - `computer_`: ID do computador (URL parameter).
- **Responses**:
    - **200 OK**: Activity timestamp updated successfully.
    - **404 Not Found**: Device not found.
    - **500 Internal Server Error**: An error occurred.

---

### 5. Check Device Status

- **GET** `/check/status/:computer_`
- **Description**: Verifica o status atual do dispositivo (online/offline).
- **Parameters**:
    - `computer_`: ID do computador (URL parameter).
- **Responses**:
    - **200 OK**: Returns the status and timestamps.
        ```json
        {
            "status": "online/offline",
            "currentTime": "ISO Date",
            "lastUpdate_": "ISO Date"
        }
        ```
    - **404 Not Found**: Device not found.
    - **500 Internal Server Error**: An error occurred.

---

### 6. Check If Device Exists

- **GET** `/check/device/:computer_`
- **Description**: Verifica se um dispositivo está registrado.
- **Parameters**:
    - `computer_`: ID do computador (URL parameter).
- **Responses**:
    - **200 OK**: Device exists.
    - **404 Not Found**: Device not found.
    - **500 Internal Server Error**: An error occurred.

---

### 7. Get All Connections

- **GET** `/connections`
- **Description**: Obtém a lista de todos os dispositivos registrados.
- **Responses**:
    - **200 OK**: Returns an array of devices.
        ```json
        [
            {
                "computer_": "string",
                "status_": "boolean",
                "lastUpdate_": "ISO Date",
                ...
            }
        ]
        ```
    - **500 Internal Server Error**: An error occurred.

---

### 8. Get Latest Code of Device

- **GET** `/get/lest/code/:computer_`
- **Description**: Obtém o último código associado a um dispositivo.
- **Parameters**:
    - `computer_`: ID do computador (URL parameter).
- **Responses**:
    - **200 OK**: Returns the last code.
        ```json
        {
            "code": "number"
        }
        ```
    - **404 Not Found**: Device not found.
    - **500 Internal Server Error**: An error occurred.

---

### 9. Get Device Command

- **GET** `/get/command/:computer_`
- **Description**: Obtém o comando associado a um dispositivo.
- **Parameters**:
    - `computer_`: ID do computador (URL parameter).
- **Responses**:
    - **200 OK**: Returns the command object.
        ```json
        {
            "command_": "string",
            "code_": "number",
            ...
        }
        ```
    - **404 Not Found**: Device not found.
    - **500 Internal Server Error**: An error occurred.

---

### 10. Connect to Device

- **POST** `/connect/:computer_`
- **Description**: Conecta a um dispositivo e obtém suas informações.
- **Parameters**:
    - `computer_`: ID do computador (URL parameter).
- **Responses**:
    - **200 OK**: Returns device information.
    - **404 Not Found**: Device not found.
    - **500 Internal Server Error**: An error occurred.

---

### 11. Send Command to Device

- **POST** `/:computer_`
- **Description**: Envia um comando para o dispositivo.
- **Parameters**:
    - `computer_`: ID do computador (URL parameter).
- **Request Body**:
    ```json
    {
        "command_": "string"
    }
    ```
- **Responses**:
    - **200 OK**: Command sent successfully.
    - **404 Not Found**: Device not found.
    - **500 Internal Server Error**: An error occurred.

---

## Error Handling

A API retornará os seguintes códigos de status HTTP para erros:

- **404 Not Found**: Quando o recurso não for encontrado.
- **500 Internal Server Error**: Quando ocorrer um erro inesperado no servidor.