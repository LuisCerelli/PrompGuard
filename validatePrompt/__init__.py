import logging
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Procesando una solicitud en validatePrompt.")

    try:
        req_body = req.get_json()
        prompt = req_body.get("prompt", "")

        if not prompt:
            return func.HttpResponse("Falta el parámetro 'prompt'", status_code=400)

        corrected_prompt = f"Texto corregido: {prompt}"  # Aquí iría la lógica de corrección real

        return func.HttpResponse(
            json.dumps({"correctedPrompt": corrected_prompt, "suggestions": ["Mejorar claridad"]}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error procesando la solicitud: {e}")
        return func.HttpResponse("Error interno del servidor", status_code=500)
