# 🤖 QA Dispatcher Bot (Slack -> GitHub)
> **Automatización de disparos de pruebas QA mediante comandos y menús interactivos en Slack.**

Este proyecto es un bot de Slack construido con **Python (Flask + Slack Bolt SDK)** que permite a cualquier miembro del equipo ejecutar suites de pruebas automatizadas en diferentes repositorios sin salir de Slack.

---

## 🎯 Características Principales
*   **Selector de Proyectos**: Menú dinámico que lista los repositorios de QA configurados.
*   **Selección de Suite**: Carga dinámicamente las suites disponibles para cada proyecto.
*   **Gestión de Ramas**: Capacidad de disparar workflows en ramas específicas (develop, main, feature branch).
*   **Notificaciones en Tiempo Real**: Informa en un canal centralizado quién lanzó qué pruebas para evitar duplicidad de ejecuciones.
*   **Vercel Ready**: Configurado para desplegarse fácilmente en Vercel como un API serverless.

---

## 🏗️ Arquitectura & Stack Técnico
*   **Backend**: Python 3.12 + Flask.
*   **Integración Slack**: [Slack Bolt SDK](https://slack.dev/bolt-python/) (Modo Socket para local, HTTP para Vercel).
*   **Integración GitHub**: API de GitHub Actions (Workflow Dispatch).
*   **Infraestructura**: Despliegue en Vercel.

---

## 📂 Estructura del Proyecto
```text
.
├── api/
│   ├── services/      # Lógica de integración con GitHub
│   ├── utils/         # Generación de bloques de UI de Slack
│   ├── bot.py         # Inicialización de la App Slack
│   ├── config.py      # Configuración de repos, suites y canales
│   ├── handlers.py    # Manejadores de eventos, comandos y acciones
│   └── index.py       # Punto de entrada Flask y recepción de reportes
├── requirements.txt   # Dependencias de Python
└── vercel.json        # Configuración para despliegue serverless
```

---

## 🚀 Guía de Configuración de Slack

Para que el bot funcione, debes crear una **Slack App** en [Slack API](https://api.slack.com/apps).

### 1. Creación de la App
1. Crea una nueva App **"From scratch"**.
2. Dale un nombre (ej. `Lanzador QA`) y selecciona el Workspace.

### 2. Scopes (Permisos)
En **OAuth & Permissions**, agrega los siguientes **Bot Token Scopes**:
*   `chat:write`: Para que el bot pueda enviar mensajes.
*   `commands`: Para habilitar el comando `/qa_run_tests`.
*   `im:write`: Para responder por mensajes directos.

### 3. Interactivity & Shortcuts
1. Activa **Interactivity**.
2. **Request URL**: Poner la URL de tu servidor + `/api/slack/events` (ej: `https://tu-url.vercel.app/api/slack/events`).

### 4. Event Subscriptions
1. Activa **Events**.
2. **Request URL**: La misma URL que en el paso anterior.
3. Suscríbete a eventos de bot:
   *   `app_home_opened`: Para mostrar la interfaz en la pestaña Home.
   *   `app_mention`: Para responder cuando mencionen al bot.
   *   `message.im`: Para responder en chats privados.

### 5. Slash Commands
Crea un comando llamado `/qa_run_tests` apuntando a la misma URL de eventos.

---

## 🛠️ Variables de Entorno
Crea un archivo `.env` o configúralas en Vercel:

| Variable | Descripción |
| :--- | :--- |
| `SLACK_BOT_TOKEN` | Token `xoxb-...` obtenido en OAuth & Permissions. |
| `SLACK_SIGNING_SECRET` | Secret obtenido en Basic Information. |
| `GITHUB_PAT` | Personal Access Token de GitHub con permisos de `workflow`. |
| `SLACK_REPORT_CHANNEL` | ID del canal de Slack donde se enviarán todos los reportes de ejecución. |

---

## ⚙️ Configuración de Proyectos
Edita `api/config.py` para añadir nuevos repositorios:

```python
    "nombre-repo-github": {
        "nombre_visible": "Nombre en Slack",
        "workflow_name": "archivo_workflow.yml",
        "default_branch": "main",
        "workflow_input_key": "suite", # Nombre del input en el .yml
        "suites": ["All", "Smoke", "Regression"]
    }
```

---

## 📊 Integración con GitHub Actions (Reportes)

Para que el bot informe los resultados de los tests de vuelta a Slack, añade este paso al final de tu archivo `.yml` de GitHub Actions:

```yaml
- name: Reportar al Slack Bot
  if: always()
  run: |
    curl -X POST https://tu-url-del-bot.vercel.app/api/report \
    -H "Content-Type: application/json" \
    -d '{
      "repo": "${{ github.event.repository.name }}",
      "suite": "${{ github.event.inputs.suite || github.event.inputs.pipeline || 'Auto' }}", 
      "status": "${{ job.status }}",
      "run_url": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
    }'
```
> [!TIP]
> **Seguridad**: No es necesario enviar el `channel_id` en el JSON si ya lo configuraste en las variables de entorno del bot (`SLACK_REPORT_CHANNEL`). Esto mantiene tus archivos `.yml` limpios y seguros.

---

## 📦 Ejecución Local
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno
export SLACK_BOT_TOKEN=...
export SLACK_SIGNING_SECRET=...
export GITHUB_PAT=...

# 3. Correr la app
python api/index.py
```
> [!TIP]
> En local, la app intentará usar **Socket Mode** si detecta `SLACK_APP_TOKEN`. Si no, funcionará por HTTP normal.

---
### Contribuidores
*   **Flypass QA Team**
