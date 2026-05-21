import os
import json
import urllib.request
import urllib.error
try:
    from api.config import PIPELINES_CONFIG, SLACK_REPORT_CHANNEL
except ImportError:
    from config import PIPELINES_CONFIG, SLACK_REPORT_CHANNEL

def trigger_github_action(repo_seleccionado, test_suite, user_id, channel_id, client, response_url=None):
    """Dispara un workflow de GitHub y notifica al usuario."""
    workflow_name = PIPELINES_CONFIG[repo_seleccionado]["workflow_name"]
    default_branch = PIPELINES_CONFIG[repo_seleccionado].get("default_branch", "develop")
    input_key = PIPELINES_CONFIG[repo_seleccionado].get("workflow_input_key", "suite")
    github_token = os.environ.get("GITHUB_PAT")
    
    url = f"https://api.github.com/repos/f2x-flypass/{repo_seleccionado}/actions/workflows/{workflow_name}/dispatches"
    
    payload = json.dumps({
        "ref": default_branch, 
        "inputs": {input_key: test_suite}
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {github_token}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            response_text = response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        status_code = e.code
        response_text = e.read().decode("utf-8")
    
    texto_final = ""
    if status_code == 204:
        nombre_vis = PIPELINES_CONFIG[repo_seleccionado]['nombre_visible']
        texto_final = f"✅ ¡Perfecto! He lanzado el pipeline de `{nombre_vis}` con la suite `{test_suite}` en la rama `{default_branch}`."
        
        # Notificación al canal de reportes/comunidad
        report_text = f"🚀 <@{user_id}> ha lanzado las pruebas de *{nombre_vis}*\n> *Suite:* `{test_suite}`\n> *Rama:* `{default_branch}`"
        try:
            client.chat_postMessage(channel=SLACK_REPORT_CHANNEL, text=report_text)
        except Exception as e:
            print(f"Error enviando notificación al canal de reportes: {e}")
    else:
        texto_final = f"❌ GitHub rechazó la petición ({status_code}): {response_text}"

    if response_url:
        try:
            resp_payload = json.dumps({"text": texto_final, "response_type": "in_channel"}).encode("utf-8")
            resp_req = urllib.request.Request(response_url, data=resp_payload, method="POST")
            resp_req.add_header("Content-Type", "application/json")
            urllib.request.urlopen(resp_req)
        except:
            client.chat_postMessage(channel=channel_id, text=texto_final)
    else:
        client.chat_postMessage(channel=channel_id, text=texto_final)
