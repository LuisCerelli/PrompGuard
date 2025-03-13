import azure.functions as func
import logging
import json
import os
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.exceptions import HttpResponseError
from azure.openai import OpenAIClient
import time

app = func.FunctionApp()

# ✅ Se usa @app.function_name en lugar de @app.route
@app.function_name(name="validatePrompt")
@app.route(route="validatePrompt", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def validate_prompt(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('validatePrompt function processed a request.')

    try:
        req_body = req.get_json()
        prompt = req_body.get('prompt')
        if not prompt:
            return func.HttpResponse(json.dumps({"error": "El prompt es requerido"}), mimetype="application/json", status_code=400)
        
        # ✅ Procesos de validación
        grammar_result = check_grammar(prompt)
        corrected_prompt = rewrite_prompt(prompt, grammar_result)
        safety_result = check_content_safety(corrected_prompt)

        if safety_result['is_flagged']:
            return func.HttpResponse(
                json.dumps({"error": "El contenido ha sido marcado como inapropiado", "details": safety_result['details']}),
                mimetype="application/json",
                status_code=400
            )
        
        suggestions = generate_suggestions(prompt)

        return func.HttpResponse(
            json.dumps({
                "correctedPrompt": corrected_prompt,
                "suggestions": suggestions
            }),
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error en validatePrompt: {str(e)}")
        return func.HttpResponse(json.dumps({"error": "Error al procesar el prompt", "details": str(e)}), mimetype="application/json", status_code=500)


# ✅ Segunda función correctamente decorada
@app.function_name(name="generateResponse")
@app.route(route="generateResponse", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def generate_response(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('generateResponse function processed a request.')

    try:
        req_body = req.get_json()
        corrected_prompt = req_body.get('prompt')
        if not corrected_prompt:
            return func.HttpResponse(json.dumps({"error": "El prompt corregido es requerido"}), mimetype="application/json", status_code=400)

        response = generate_ai_response(corrected_prompt)

        return func.HttpResponse(json.dumps({"response": response}), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error en generateResponse: {str(e)}")
        return func.HttpResponse(json.dumps({"error": "Error al generar la respuesta", "details": str(e)}), mimetype="application/json", status_code=500)


# ✅ Tercera función correctamente decorada
@app.function_name(name="monitoring")
@app.route(route="monitoring", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def monitoring(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('monitoring function processed a request.')

    try:
        metrics = collect_system_metrics()

        return func.HttpResponse(json.dumps({"metrics": metrics}), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error en monitoring: {str(e)}")
        return func.HttpResponse(json.dumps({"error": "Error al obtener métricas", "details": str(e)}), mimetype="application/json", status_code=500)
