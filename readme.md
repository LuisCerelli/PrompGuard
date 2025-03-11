

# 1: Configurar Azure Functions en el entorno

Lo primero que haremos es configurarlo, ya que Azure Functions es un servicio de computación sin servidor que permite ejecutar código en respuesta a eventos HTTP: 

#### Pasos: 
1. Instalar Azure Functions Core Tools en tu máquina: 
``` 
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```
2. Instalamos Azure CLI(Si es que no lo tienes)
###### Para MacOS:
```
brew update && brew install azure-cli
``` 
3. Actualizamos (en caso de ser necesario)
```
brew upgrade
```
4. Verificamos que esté instalado correctamente:
```
az --version
```
5. Iniciamos sesión en Azure:
```
az login
```
6. Crear un nuevo proyecto ede Azure Functions:
```
func init myFunctionApp --worker-runtime python  # O usa "node" si prefieres JavaScript/TypeScript
cd myFunctionApp
```
7. Crear los endpoints requeridos:
```
func new --name validatePrompt --template "HTTP trigger"  
func new --name generateResponse --template "HTTP trigger"  
func new --name monitoring --template "HTTP trigger"  
```
###### <u> Nota:</u>
Cuando llegamos a este punto, se necesita seleccionar el nivel de autenticación adecuado para los endpoints, las opciones son: 

a. FUNCTION: Requiere una clave de función específica para invocar la función. Es bueno para APIs internas o servicios que necesitan un nivel moderado de seguridad.

b. ANONYMOUS: No requiere autenticación. Cualquiera puede llamar a tu función sin proporcionar una clave. Útil para APIs públicas o pruebas.

c. ADMIN: Requiere la clave maestra (master key) para invocar la función. Es el nivel más restrictivo, ideal para funciones administrativas o críticas.

Dada las características del Hackathon en el que participaremos todos y demás miembros y entendiendo el fin didáctico al momento de realizarce, entiendo que colocaremos la opción b: Anonymous, de tal forma que podamos realizar pruebas tranquilamente

# 2: Implementar ```validatePrompt``` con Azure Cognitive Services
Este endpoint recibe un prompt, valida su gramática y sugiere mejoras.

#### Pasos:
Configurar Azure Cognitive Services (Language API):

1. Ir a Azure Portal.
2. Crear un recurso de Azure Cognitive Services.
3. Seleccionar la opción de Language Services.
4. Copiar la clave de API y la URL del endpoint.
Editar ```validatePrompt/__init__.py``` y agrega la validación de gramática:

```
import logging
import json
import azure.functions as func
import requests

# Configuración de Azure Cognitive Services
AZURE_LANGUAGE_ENDPOINT = "TU_ENDPOINT"
AZURE_LANGUAGE_KEY = "TU_API_KEY"

def validate_grammar(text):
    """Llama a Azure Cognitive Services para validar gramática."""
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_LANGUAGE_KEY,
        "Content-Type": "application/json"
    }
    data = {"documents": [{"id": "1", "text": text}]}
    response = requests.post(f"{AZURE_LANGUAGE_ENDPOINT}/text/analytics/v3.1/spellCheck", headers=headers, json=data)
    return response.json()

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Validando prompt...")

    try:
        req_body = req.get_json()
        prompt = req_body.get("prompt")

        if not prompt:
            return func.HttpResponse("Falta el prompt.", status_code=400)

        correction = validate_grammar(prompt)
        corrected_text = correction["documents"][0]["suggestions"][0]["suggestedText"]  # Extrae la corrección

        response_data = {
            "correctedPrompt": corrected_text,
            "suggestions": correction["documents"][0]["suggestions"]
        }

        return func.HttpResponse(json.dumps(response_data), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error en validatePrompt: {str(e)}")
        return func.HttpResponse("Error interno del servidor.", status_code=500)
```

# 3: Implementar ```generateRespons``` con Azure OpenAI
Este endpoint toma el **prompt corregido** y lo envía a **Azure OpenAI** para generar una respuesta.

#### **Pasos:**
1. Configura Azure OpenAI en el portal de Azure.

    Crea un recurso de Azure OpenAI.
    Obtén la clave API y el endpoint.
    Asegúrate de habilitar el modelo GPT que usarás.
    Edita ```generateResponse/__init__.py``` para conectarlo con OpenAI:

```
import logging
import json
import azure.functions as func
import openai

# Configuración de Azure OpenAI
OPENAI_API_KEY = "TU_OPENAI_API_KEY"
OPENAI_ENDPOINT = "TU_OPENAI_ENDPOINT"

openai.api_key = OPENAI_API_KEY

def generate_ai_response(prompt):
    """Llama a Azure OpenAI para generar una respuesta."""
    response = openai.ChatCompletion.create(
        engine="gpt-4",  # Usa el modelo configurado en Azure
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    return response["choices"][0]["message"]["content"]

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Generando respuesta de IA...")

    try:
        req_body = req.get_json()
        corrected_prompt = req_body.get("prompt")

        if not corrected_prompt:
            return func.HttpResponse("Falta el prompt corregido.", status_code=400)

        response_text = generate_ai_response(corrected_prompt)

        return func.HttpResponse(json.dumps({"response": response_text}), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error en generateResponse: {str(e)}")
        return func.HttpResponse("Error interno del servidor.", status_code=500)
```
# 4: Implementar ```monitoring``` para medir rendimiento
Este endpoint devuelve métricas como latencia y precisión.

#### **Pasos:**
1. Edita ```monitoring/__init__.py```: 
```
import logging
import json
import azure.functions as func
import time

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Recopilando métricas de IA...")

    # Simulación de métricas
    metrics = {
        "latency": "120ms",
        "accuracy": "95%",
        "issuesDetected": "3"
    }

    return func.HttpResponse(json.dumps({"metrics": metrics}), mimetype="application/json")
```
# 5: Desplegar en Azure
Una vez que todo esté funcionando localmente, desplegar las funciones en Azure.

1. Inicia sesión en Azure:
```
az login
```
2. Crea un grupo de recursos y un Function App:
```
az group create --name MyResourceGroup --location "East US"
az functionapp create --resource-group MyResourceGroup --consumption-plan-location "East US" --runtime python --functions-version 4 --name MyFunctionApp --storage-account mystorageaccount
```
3. Desplegar el código:
```
func azure functionapp publish MyFunctionApp
```

### Con ésto hemos configurado el backend con Azure Functions, validación de prompts, integración con Azure Cognitive Services y OpenAI, y un sistema de monitoreo.