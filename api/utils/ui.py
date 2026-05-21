import json
try:
    from api.config import PIPELINES_CONFIG
except ImportError:
    from config import PIPELINES_CONFIG

def get_selection_blocks(repo_seleccionado=None, for_modal=False):
    """Genera los bloques de selección basados en el estado actual."""
    opciones_api = [
        {
            "text": {"type": "plain_text", "text": data["nombre_visible"]},
            "value": repo
        } for repo, data in PIPELINES_CONFIG.items()
    ]
    
    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*🚀 Lanzador de Pruebas QA Flypass*"}
        },
        {
            "type": "input",
            "block_id": "repo_block",
            "element": {
                "type": "static_select",
                "action_id": "repo_action",
                "placeholder": {"type": "plain_text", "text": "1. Selecciona el Proyecto / API"},
                "options": opciones_api
            },
            "label": {"type": "plain_text", "text": "Proyecto"},
            "dispatch_action": True
        }
    ]

    if repo_seleccionado and repo_seleccionado in PIPELINES_CONFIG:
        # Actualizamos el select de repo para que tenga la opción inicial
        blocks[1]["element"]["initial_option"] = {
            "text": {"type": "plain_text", "text": PIPELINES_CONFIG[repo_seleccionado]["nombre_visible"]},
            "value": repo_seleccionado
        }
        
        suites_disponibles = PIPELINES_CONFIG[repo_seleccionado]["suites"]
        opciones_suites = [
            {
                "text": {"type": "plain_text", "text": suite},
                "value": suite
            } for suite in suites_disponibles
        ]
        
        blocks.append({
            "type": "input",
            "block_id": "suite_block",
            "element": {
                "type": "static_select",
                "action_id": "suite_action",
                "placeholder": {"type": "plain_text", "text": "2. Selecciona la Suite"},
                "options": opciones_suites
            },
            "label": {"type": "plain_text", "text": "Suite de Pruebas"}
        })
        
        # Agregamos el botón de ejecución solo para Home y Mensajes (no para Modales)
        if not for_modal:
            blocks.append({
                "type": "actions",
                "block_id": "execute_block",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Ejecutar 🚀"},
                        "style": "primary",
                        "action_id": "execute_action",
                        "value": json.dumps({"repo": repo_seleccionado})
                    }
                ]
            })
    else:
        blocks.append({
            "type": "section",
            "block_id": "suite_placeholder",
            "text": {"type": "mrkdwn", "text": "_Selecciona un proyecto primero para ver las suites disponibles_"}
        })
        
    return blocks
