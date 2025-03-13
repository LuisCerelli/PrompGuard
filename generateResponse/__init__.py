import logging
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Procesando una solicitud en generateResponse.")

    try:
        req_body = req.get_json()
        prompt = req_body.get("prompt", "")

        if not prompt:
            return func.HttpResponse("Falta el parámetro 'prompt'", status_code=400)

        response_text = f"Respuesta generada: {prompt}"  # Aquí iría la llamada real a OpenAI

        return func.HttpResponse(
            json.dumps({"response": response_text}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error procesando la solicitud: {e}")
        return func.HttpResponse("Error interno del servidor", status_code=500)
