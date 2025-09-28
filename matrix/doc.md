# API Documentation v2

## Overview

Esta API permite o gerenciamento de **Agents**, incluindo registro, atualização de status, verificação de conexão, envio de comandos e monitoramento de atividade.

---

## Base URL

```
http://<your-domain>/api/v1
```

---

## Endpoints

### 1. Register Agent

* **POST** `/create-agent`

* **Description**: Registra um novo Agent no sistema, armazenando informações da máquina e do usuário.

* **Request Body**:

```json
{
  "ipAddress": "string",
  "hostname": "string",
  "username": "string",
  "operatingSystem": "string",
  "architecture": "string",
  "cpu": {
    "model": "string",
    "cores": 0
  },
  "memory": {
    "total": 0,
    "free": 0
  },
  "disk": {
    "total": 0,
    "free": 0
  }
}
```

* **Responses**:

  * **201 Created**

  ```json
  {
    "errors": false,
    "message": ["Agent registrado com sucesso."],
    "agentId": "string"
  }
  ```

  * **400 Bad Request**

  ```json
  {
    "errors": true,
    "message": ["ipAddress, hostname and username are required."]
  }
  ```

  * **500 Internal Server Error**

  ```json
  {
    "errors": true,
    "message": ["Falha ao registrar Agent", "string"]
  }
  ```

---

### 2. Check if Agent Exists

* **GET** `/check-agent/:pc`

* **Description**: Verifica se um Agent está registrado.

* **Responses**:

  * **200 OK**

  ```json
  {
    "errors": false,
    "exists": true,
    "agentId": "string",
    "hostname": "string",
    "status": "online/offline",
    "message": ["success"]
  }
  ```

  * **404 Not Found**

  ```json
  {
    "errors": true,
    "exists": false,
    "message": ["Agent with hostname \"pc\" not found."]
  }
  ```

---

### 3. Check Agent Status

* **GET** `/check-status/:pc`

* **Description**: Retorna o status atual do Agent (online/offline) e timestamps de atividade.

* **Responses**:

  * **200 OK**

  ```json
  {
    "errors": false,
    "status": "online/offline",
    "currentTime": "ISO Date",
    "lastUpdate": "ISO Date",
    "message": ["success"]
  }
  ```

  * **404 Not Found**

  ```json
  {
    "errors": true,
    "message": ["Agent with hostname \"pc\" not found."]
  }
  ```

---

### 4. Get All Connections

* **GET** `/connections`

* **Description**: Retorna todos os Agents registrados.

* **Responses**:

  * **200 OK**

  ```json
  {
    "errors": false,
    "message": ["success"],
    "agents": [
      {
        "_id": "string",
        "hostname": "string",
        "status": "online/offline",
        "lastActivity": "ISO Date",
        "returned": "string",
        "commandQueue": []
      }
    ]
  }
  ```

---

### 5. Send Command to Agent

* **POST** `/:pc`

* **Description**: Envia um comando para o Agent.

* **Request Body**:

```json
{
  "command": "string"
}
```

* **Responses**:

  * **200 OK**

  ```json
  {
    "errors": false,
    "message": ["Command sent successfully."]
  }
  ```

  * **404 Not Found**

  ```json
  {
    "errors": true,
    "message": ["Agent with hostname \"pc\" not found."]
  }
  ```

---

### 6. Connect to Agent

* **POST** `/connect/:pc`

* **Description**: Retorna os dados completos de um Agent.

* **Responses**:

  * **200 OK**

  ```json
  {
    "errors": false,
    "message": ["success"],
    "agent": { ... }
  }
  ```

  * **404 Not Found**

  ```json
  {
    "errors": true,
    "message": ["Agent \"pc\" not found."]
  }
  ```

---

### 7. Get Agent Command

* **GET** `/command/:pc`

* **Description**: Retorna o próximo comando não executado do Agent.

* **Responses**:

  * **200 OK**

  ```json
  {
    "errors": false,
    "message": ["success"],
    "command": "string",
    "payload": {},
    "createdAt": "ISO Date"
  }
  ```

  * **404 Not Found**

  ```json
  {
    "errors": true,
    "message": ["Agent \"pc\" not found."]
  }
  ```

  * **200 OK (sem comandos)**

  ```json
  {
    "errors": true,
    "message": ["No pending commands."]
  }
  ```

---

### 8. Update Returned Status

* **POST** `/returned/:pc`

* **Description**: Atualiza a string enviada pelo Agent (`returned`).

* **Request Body**:

```json
{
  "returned": "string"
}
```

* **Responses**:

  * **200 OK**

  ```json
  {
    "errors": false,
    "message": ["Return updated successfully."]
  }
  ```

---

### 9. Get Returned Status

* **GET** `/returned/:pc`

* **Description**: Retorna a última string de retorno enviada pelo Agent.

* **Responses**:

  * **200 OK**

  ```json
  {
    "errors": false,
    "message": ["success"],
    "returned": "string"
  }
  ```

---

### 10. Update Agent Activity

* **POST** `/activity/:pc`

* **Description**: Atualiza o timestamp da última atividade do Agent.

* **Responses**:

  * **200 OK**

  ```json
  {
    "errors": false,
    "message": ["Last activity updated successfully."]
  }
  ```

---

### 11. Get Last Code

* **GET** `/last-code/:pc`

* **Description**: Retorna o último código gerado para o Agent.

* **Responses**:

  * **200 OK**

  ```json
  {
    "errors": false,
    "message": ["success"],
    "code": 123456789
  }
  ```

---

### Error Handling

* **404 Not Found**: Agent não encontrado.
* **400 Bad Request**: Parâmetro inválido ou campo obrigatório ausente.
* **500 Internal Server Error**: Erro interno no servidor.