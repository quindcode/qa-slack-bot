import json
from api.bot import slack_app
from api.utils.ui import get_selection_blocks
from api.services.github import trigger_github_action

def register_handlers():
    """Registra todos los manejadores de eventos y acciones en la slack_app."""
    
    @slack_app.event("app_home_opened")
    def update_home_tab(client, event, logger):
        try:
            client.views_publish(
                user_id=event["user"],
                view={
                    "type": "home",
                    "blocks": get_selection_blocks()
                }
            )
        except Exception as e:
            logger.error(f"Error publishing home tab: {e}")

    @slack_app.message("")
    def handle_message(message, say):
        if message.get("channel_type") == "im":
            say(blocks=get_selection_blocks(), text="Lanzador de Pruebas QA")

    @slack_app.command("/qa_run_tests")
    def handle_cypress_command(ack, body, client):
        ack()
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "cypress_modal_submit",
                "private_metadata": json.dumps({"channel_id": body["channel_id"], "response_url": body["response_url"]}),
                "title": {"type": "plain_text", "text": "Lanzador QA Flypass"},
                "submit": {"type": "plain_text", "text": "Ejecutar"},
                "close": {"type": "plain_text", "text": "Cancelar"},
                "blocks": get_selection_blocks(for_modal=True)
            }
        )

    @slack_app.action("repo_action")
    def handle_repo_selection(ack, body, client):
        ack()
        repo_seleccionado = body["actions"][0]["selected_option"]["value"]
        
        if "view" in body:
            view_id = body["view"]["id"]
            view_type = body["view"]["type"]
            is_modal = (view_type == "modal")
            
            new_blocks = get_selection_blocks(repo_seleccionado, for_modal=is_modal)
            
            if view_type == "modal":
                client.views_update(
                    view_id=view_id,
                    view={
                        "type": "modal",
                        "callback_id": "cypress_modal_submit",
                        "private_metadata": body["view"]["private_metadata"],
                        "title": {"type": "plain_text", "text": "Lanzador QA Flypass"},
                        "submit": {"type": "plain_text", "text": "Ejecutar 🚀"},
                        "close": {"type": "plain_text", "text": "Cancelar"},
                        "blocks": new_blocks
                    }
                )
            elif view_type == "home":
                client.views_publish(
                    user_id=body["user"]["id"],
                    view={
                        "type": "home",
                        "blocks": new_blocks
                    }
                )
        elif "message" in body:
            new_blocks = get_selection_blocks(repo_seleccionado, for_modal=False)
            client.chat_update(
                channel=body["channel"]["id"],
                ts=body["message"]["ts"],
                blocks=new_blocks,
                text="Actualizando selección..."
            )

    @slack_app.event("app_mention")
    def handle_mention(event, say):
        say(blocks=get_selection_blocks(), text="Lanzador de Pruebas QA")

    @slack_app.action("suite_action")
    def handle_suite_selection(ack):
        ack()

    @slack_app.action("execute_action")
    def handle_execute_button(ack, body, client):
        ack()
        user_id = body["user"]["id"]
        channel_id = body.get("channel", {}).get("id") or user_id
        
        try:
            if "view" in body:
                values = body["view"]["state"]["values"]
            else:
                values = body["state"]["values"]
                
            repo_seleccionado = values["repo_block"]["repo_action"]["selected_option"]["value"]
            test_suite = values["suite_block"]["suite_action"]["selected_option"]["value"]
            
            # 1. Feedback inmediato
            loading_blocks = get_selection_blocks(repo_seleccionado)
            for i, block in enumerate(loading_blocks):
                if block.get("block_id") == "execute_block":
                    loading_blocks[i] = {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": "⏳ *Procesando... recibiendo confirmación de GitHub.*"}
                    }
            
            if "view" in body:
                client.views_publish(user_id=user_id, view={"type": "home", "blocks": loading_blocks})
            elif "message" in body:
                client.chat_update(channel=body["channel"]["id"], ts=body["message"]["ts"], blocks=loading_blocks, text="Procesando...")

            # 2. Ejecución
            trigger_github_action(repo_seleccionado, test_suite, user_id, channel_id, client)
            
            # 3. Reinicio
            if "view" in body:
                client.views_publish(user_id=user_id, view={"type": "home", "blocks": get_selection_blocks()})
            elif "message" in body:
                client.chat_update(channel=body["channel"]["id"], ts=body["message"]["ts"], blocks=get_selection_blocks(), text="Lanzador de Pruebas QA")
                
        except Exception as e:
            client.chat_postMessage(channel=user_id, text=f"⚠️ Error al ejecutar: `Falta seleccionar la Suite` o `{str(e)}`")

    @slack_app.view("cypress_modal_submit")
    def handle_view_submission(ack, body, view, client):
        user_id = body["user"]["id"]
        try:
            values = view["state"]["values"]
            if "repo_block" not in values or "suite_block" not in values:
                ack(response_action="errors", errors={"repo_block": "Por favor completa la selección"})
                return
            
            ack()
            repo_seleccionado = values["repo_block"]["repo_action"]["selected_option"]["value"]
            test_suite = values["suite_block"]["suite_action"]["selected_option"]["value"]
            
            metadata = json.loads(view.get("private_metadata", "{}"))
            channel_id = metadata.get("channel_id", user_id)
            response_url = metadata.get("response_url")
            
            trigger_github_action(repo_seleccionado, test_suite, user_id, channel_id, client, response_url)
        except Exception as e:
            client.chat_postMessage(channel=user_id, text=f"⚠️ Error al procesar: `{str(e)}`")
