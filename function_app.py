import azure.functions as func
import logging
import json
import os
import requests
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.exceptions import HttpResponseError
import openai

# Inicializar la aplicación de Azure Functions
app = func.FunctionApp()

# Cargar variables de entorno
CONTENT_SAFETY_ENDPOINT = os.getenv("CONTENT_SAFETY_ENDPOINT")
CONTENT_SAFETY_KEY = os.getenv("CONTENT_SAFETY_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

def check_content_safety(prompt):
    """
    Envía el prompt a Azure Content Safety y devuelve si fue marcado como inseguro.
    """
    if not CONTENT_SAFETY_ENDPOINT or not CONTENT_SAFETY_KEY:
        logging.error("Faltan las credenciales de Azure Content Safety")
        return {"is_flagged": True, "details": "Credenciales no configuradas"}

    try:
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": CONTENT_SAFETY_KEY
        }
        data = {"text": prompt}

        response = requests.post(
            f"{CONTENT_SAFETY_ENDPOINT}/contentsafety/text:analyze?api-version=2023-10-01",
            headers=headers,
            json=data
        )

        if response.status_code != 200:
            logging.error(f"Error en Content Safety: {response.text}")
            return {"is_flagged": True, "details": f"Error en API: {response.status_code}"}

        result = response.json()
        is_flagged = any(item["isFlagged"] for item in result.get("categoriesAnalysis", []))

        return {"is_flagged": is_flagged, "details": result}

    except Exception as e:
        logging.error(f"Error en check_content_safety: {str(e)}")
        return {"is_flagged": True, "details": f"Excepción: {str(e)}"}

# 🔹 **Función para validar el prompt**
@app.function_name(name="validatePrompt")
@app.route(route="validatePrompt", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def validate_prompt(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('validatePrompt function processed a request.')

    try:
        req_body = req.get_json()
        prompt = req_body.get('prompt')
        if not prompt:
            return func.HttpResponse(json.dumps({"error": "El prompt es requerido"}), mimetype="application/json", status_code=400)

        # Validar seguridad del contenido
        safety_result = check_content_safety(prompt)
        if safety_result['is_flagged']:
            return func.HttpResponse(
                json.dumps({"error": "El contenido ha sido marcado como inapropiado", "details": safety_result['details']}), 
                mimetype="application/json", 
                status_code=400
            )

        return func.HttpResponse(json.dumps({"message": "Prompt validado correctamente"}), mimetype="application/json")

    except Exception as e:
        logging.error(f"Error en validatePrompt: {str(e)}")
        return func.HttpResponse(json.dumps({"error": "Error al procesar el prompt", "details": str(e)}), mimetype="application/json", status_code=500)

# 🔹 **Función para generar respuesta con OpenAI**
@app.function_name(name="generateResponse")
@app.route(route="generateResponse", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def generate_response(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('generateResponse function processed a request.')

    try:
        req_body = req.get_json()
        prompt = req_body.get("prompt")

        if not prompt:
            return func.HttpResponse(
                json.dumps({"error": "Falta el prompt en la solicitud"}), 
                status_code=400, 
                mimetype="application/json"
            )

        # Generar respuesta con OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Cambia el modelo si es necesario
            messages=[{"role": "user", "content": prompt}]
        )

        return func.HttpResponse(
            json.dumps({"response": response["choices"][0]["message"]["content"]}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error en generateResponse: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error en la generación de respuesta", "details": str(e)}), 
            status_code=500, 
            mimetype="application/json"
        )
