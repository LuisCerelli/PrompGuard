import azure.functions as func
import logging
import json
import os
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.exceptions import HttpResponseError
from azure.ai.openai import OpenAIClient, AzureKeyCredential
import time

app = func.FunctionApp()

# Función validatePrompt
@app.route(route="validatePrompt", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def validate_prompt(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('validatePrompt function processed a request.')

    # 1. Obtener el prompt de la solicitud
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "El cuerpo de la solicitud debe ser JSON válido"}),
            mimetype="application/json",
            status_code=400
        )

    prompt = req_body.get('prompt')
    if not prompt:
        return func.HttpResponse(
            json.dumps({"error": "El prompt es requerido"}),
            mimetype="application/json",
            status_code=400
        )

    try:
        # 2. Verificar gramática con Azure Cognitive Services
        grammar_result = check_grammar(prompt)
        
        # 3. Reescribir el prompt con Azure OpenAI
        corrected_prompt = rewrite_prompt(prompt, grammar_result)
        
        # 4. Filtrar contenido dañino con Azure Content Safety
        safety_result = check_content_safety(corrected_prompt)
        
        if safety_result['is_flagged']:
            return func.HttpResponse(
                json.dumps({"error": "El contenido ha sido marcado como inapropiado", "details": safety_result['details']}),
                mimetype="application/json",
                status_code=400
            )
        
        # 5. Generar sugerencias alternativas
        suggestions = generate_suggestions(prompt)
        
        # 6. Devolver el resultado
        return func.HttpResponse(
            json.dumps({
                "correctedPrompt": corrected_prompt,
                "suggestions": suggestions
            }),
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error en validatePrompt: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error al procesar el prompt", "details": str(e)}),
            mimetype="application/json",
            status_code=500
        )

# Función generateResponse
@app.route(route="generateResponse", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def generate_response(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('generateResponse function processed a request.')

    # 1. Obtener el prompt corregido de la solicitud
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "El cuerpo de la solicitud debe ser JSON válido"}),
            mimetype="application/json",
            status_code=400
        )

    corrected_prompt = req_body.get('prompt')
    if not corrected_prompt:
        return func.HttpResponse(
            json.dumps({"error": "El prompt corregido es requerido"}),
            mimetype="application/json",
            status_code=400
        )

    try:
        # 2. Generar respuesta utilizando Azure OpenAI
        response = generate_ai_response(corrected_prompt)
        
        # 3. Devolver el resultado
        return func.HttpResponse(
            json.dumps({
                "response": response
            }),
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error en generateResponse: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error al generar la respuesta", "details": str(e)}),
            mimetype="application/json",
            status_code=500
        )

# Función monitoring
@app.route(route="monitoring", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def monitoring(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('monitoring function processed a request.')

    try:
        # 1. Obtener métricas del sistema
        metrics = collect_system_metrics()
        
        # 2. Devolver las métricas
        return func.HttpResponse(
            json.dumps({
                "metrics": metrics
            }),
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error en monitoring: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Error al obtener métricas", "details": str(e)}),
            mimetype="application/json",
            status_code=500
        )

# Funciones auxiliares

def check_grammar(text):
    """Verifica la gramática utilizando Azure Cognitive Services"""
    endpoint = os.environ["COGNITIVE_SERVICES_ENDPOINT"]
    key = os.environ["COGNITIVE_SERVICES_KEY"]
    
    # Inicializar cliente de Text Analytics
    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    
    try:
        # Analizar el texto (simplificado para el ejemplo)
        response = text_analytics_client.analyze_sentiment([text])
        
        # En un caso real, se haría un análisis más profundo de la gramática
        return {
            "issues": [],
            "language_detected": "es"
        }
    except Exception as e:
        logging.error(f"Error en check_grammar: {str(e)}")
        # En caso de error, devolvemos un resultado que permite continuar
        return {
            "issues": [],
            "language_detected": "es"
        }

def rewrite_prompt(text, grammar_result):
    """Reescribe el prompt usando Azure OpenAI para mejorar la claridad"""
    endpoint = os.environ["OPENAI_ENDPOINT"]
    key = os.environ["OPENAI_KEY"]
    deployment = os.environ["OPENAI_DEPLOYMENT"]
    
    try:
        # Inicializar cliente de OpenAI
        openai_client = OpenAIClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        
        # Generar prompt mejorado
        response = openai_client.completions.create(
            model=deployment,
            prompt=f"Mejora la claridad y gramática del siguiente texto sin cambiar su significado: '{text}'",
            max_tokens=500,
            temperature=0.3
        )
        
        corrected_text = response.choices[0].text.strip()
        return corrected_text
    except Exception as e:
        logging.error(f"Error en rewrite_prompt: {str(e)}")
        # En caso de error, devolvemos el texto original
        return text

def check_content_safety(text):
    """Verifica el contenido para detectar lenguaje dañino o sesgado"""
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]
    key = os.environ["CONTENT_SAFETY_KEY"]
    
    try:
        # Inicializar cliente de Content Safety
        content_safety_client = ContentSafetyClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        
        # Analizar el texto en busca de contenido inapropiado
        result = content_safety_client.analyze_text(text=text)
        
        # Verificar si alguna categoría está por encima del umbral
        is_flagged = any(category.severity > 3 for category in result.categories)
        
        details = {}
        if is_flagged:
            for category in result.categories:
                if category.severity > 3:
                    details[category.category] = category.severity
        
        return {
            "is_flagged": is_flagged,
            "details": details
        }
    except Exception as e:
        logging.error(f"Error en check_content_safety: {str(e)}")
        # En caso de error, asumimos que el contenido es seguro
        return {"is_flagged": False, "details": {}}

def generate_suggestions(text):
    """Genera sugerencias alternativas para el prompt"""
    endpoint = os.environ["OPENAI_ENDPOINT"]
    key = os.environ["OPENAI_KEY"]
    deployment = os.environ["OPENAI_DEPLOYMENT"]
    
    try:
        # Inicializar cliente de OpenAI
        openai_client = OpenAIClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        
        # Generar sugerencias alternativas
        response = openai_client.completions.create(
            model=deployment,
            prompt=f"Genera 2 formas alternativas de expresar: '{text}'. Responde solo con las alternativas separadas por un delimitador '|'",
            max_tokens=500,
            temperature=0.7
        )
        
        # Procesar la respuesta para obtener las sugerencias
        suggestions_text = response.choices[0].text.strip()
        suggestions = suggestions_text.split("|")
        suggestions = [s.strip() for s in suggestions if s.strip()]
        
        return suggestions
    except Exception as e:
        logging.error(f"Error en generate_suggestions: {str(e)}")
        # En caso de error, devolvemos una lista vacía de sugerencias
        return []

def generate_ai_response(prompt):
    """Genera una respuesta utilizando Azure OpenAI"""
    endpoint = os.environ["OPENAI_ENDPOINT"]
    key = os.environ["OPENAI_KEY"]
    deployment = os.environ["OPENAI_RESPONSE_DEPLOYMENT"]
    
    try:
        # Inicializar cliente de OpenAI
        openai_client = OpenAIClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        
        # Generar respuesta
        response = openai_client.completions.create(
            model=deployment,
            prompt=prompt,
            max_tokens=800,
            temperature=0.5
        )
        
        ai_response = response.choices[0].text.strip()
        return ai_response
    except Exception as e:
        logging.error(f"Error en generate_ai_response: {str(e)}")
        # En caso de error, devolvemos un mensaje genérico
        return "Lo siento, no pude generar una respuesta en este momento."

def collect_system_metrics():
    """Recopila métricas del sistema"""
    # En un entorno real, estas métricas se obtendrían de Application Insights 
    # o de bases de datos que almacenen registros de las operaciones
    
    try:
        # Simulación de métricas para este ejemplo
        metrics = {
            "latency": f"{round(50 + time.time() % 50, 2)}ms",  # Latencia simulada entre 50-100ms
            "accuracy": f"{80 + (time.time() % 15)}%",  # Precisión simulada entre 80-95%
            "issuesDetected": str(int(time.time() % 10))  # Número simulado de problemas detectados
        }
        
        return metrics
    except Exception as e:
        logging.error(f"Error en collect_system_metrics: {str(e)}")
        # En caso de error, devolvemos métricas predeterminadas
        return {
            "latency": "0ms",
            "accuracy": "0%",
            "issuesDetected": "0"
        }