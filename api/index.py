import os
import json
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Importamos nuestra configuración y componentes modulares
try:
    from api.config import PIPELINES_CONFIG, SLACK_REPORT_CHANNEL
except ImportError:
    from config import PIPELINES_CONFIG, SLACK_REPORT_CHANNEL

from api.bot import slack_app
from api.handlers import register_handlers

# Registramos todos los manejadores (eventos, comandos, acciones)
register_handlers()

app = Flask(__name__)
flask_handler = SlackRequestHandler(slack_app)

@app.route("/", methods=["GET"])
def health_check():
    return "🚀 QA Bot is running and ready for Slack events!"

@app.route("/api/slack/events", methods=["POST"])
def slack_events():
    if os.environ.get("VERCEL"):
        print(f"📥 Received event on Vercel: {request.path}")
    return flask_handler.handle(request)

@app.route("/api/report", methods=["POST"])
def pipeline_report():
    data = request.json
    repo = data.get("repo", "Proyecto Desconocido")
    suite = data.get("suite", "N/A")
    status = data.get("status", "unknown").lower()
    run_url = data.get("run_url", "#")
    channel_id = data.get("channel_id", SLACK_REPORT_CHANNEL)
    
    emoji = "✅" if status == "success" else "❌"
    color = "#2eb886" if status == "success" else "#a30200"
    status_text = "PASÓ" if status == "success" else "FALLÓ"

    nombre_proyecto = PIPELINES_CONFIG.get(repo, {}).get("nombre_visible", repo)

    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"{emoji} *Resultado de Pruebas: {nombre_proyecto}*"}
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Suite:* {suite}"},
                {"type": "mrkdwn", "text": f"*Estado:* {status_text}"}
            ]
        },
        {
            "type": "actions",
            "elements": [{
                "type": "button",
                "text": {"type": "plain_text", "text": "Ver Detalle / Reporte 📊"},
                "url": run_url
            }]
        }
    ]

    try:
        slack_app.client.chat_postMessage(
            channel=channel_id,
            text=f"{emoji} Resultado de {nombre_proyecto}: {status_text}",
            attachments=[{"color": color, "blocks": blocks}]
        )
        return {"status": "ok"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    app_token = os.environ.get("SLACK_APP_TOKEN")
    port = int(os.environ.get("PORT", 3000))

    if app_token:
        print("⚡️ Starting QA Bot in Socket Mode (Local)...")
        from threading import Thread
        socket_handler = SocketModeHandler(slack_app, app_token)
        Thread(target=socket_handler.start, daemon=True).start()
        
    print(f"🚀 Starting HTTP server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)