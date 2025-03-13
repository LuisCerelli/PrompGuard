## 📝 Proyecto: AI-Prompt-Validator  

### 📌 **Objetivo del Proyecto**  

El objetivo de este proyecto es diseñar un **sistema que valide y corrija los prompts antes de enviarlos a la IA**. Esto ayuda a optimizar las respuestas generadas, asegurando que sean **claras, conformes y libres de riesgos potenciales** (por ejemplo, sesgo, lenguaje dañino o datos sensibles).  

Para lograr esto, configuramos diferentes servicios en **Azure** y creamos una **arquitectura backend** basada en **Azure Functions** y **Azure OpenAI**.  

---

## ⚙️ **Configuración Paso a Paso**  

### 1️⃣ **Crear Azure Function App**  
💡 **Función principal donde correrá nuestra validación.**  

1. Ir al **Portal de Azure** [🔗 Azure Portal](https://portal.azure.com).  
2. En la barra de búsqueda, escribir **Function App** ó **Aplicacion de Funcion** si está en español y hacer clic en **"Crear"**.  

**Nota:** en caso que la barra de <u>Marketplace</u> no lo encuentre usar este link luego de loguearse:  
```
https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Web%2Fsites/kind/functionapp
```
3. Configurar los siguientes valores:  
   - **Suscripción:** Seleccionar la suscripción activa.  
   - **Grupo de recursos:** **AI-Prompt-Validator-RG** (si no existe, crearlo).  
   - **Nombre de la Function App:** **prompt-validator-function**.  
   - **Región:** **East US 2**.  
   - **Pila de tiempo de ejecución:** **Python 3.10**.  
   - **Tamaño de instancia:** **2048 MB** (para optimizar costos).  
4. En la pestaña **Monitoreo**, seleccionar:  
   - **Habilitar Application Insights:** **Sí**.  
   - **Application Insights Resource:** **prompt-validator-function-openai-b083** (creado automáticamente).  
5. Hacer clic en **"Revisar y Crear"** → **"Crear"** y esperar la implementación.  

---

### 2️⃣ **Habilitar Azure OpenAI**  
💡 **Este servicio procesará las correcciones y validaciones de los prompts.**  

1. En el Portal de Azure, buscar **"Azure OpenAI"**.  
2. Hacer clic en **"Habilitar Azure OpenAI"**.  
3. Configurar los siguientes valores:  
   - **Región:** **East US 2** (misma que Function App).  
   - **Recurso creado:** **prompt-validator-function-openai-b083**.  
   - **Almacenamiento vectorial:** Seleccionar **"Configurar más tarde"**.  
4. Hacer clic en **"Revisar y Crear"** → **"Crear"** y esperar la implementación.  

---

### 3️⃣ **Configurar Azure Cognitive Services - Language Service**  
💡 **Este servicio nos permitirá corregir la gramática y optimizar el texto.**  

1. En el Portal de Azure, buscar **"Language Service"**.  
2. Hacer clic en **"Crear"**.  
3. Configurar los siguientes valores:  
   - **Suscripción:** Seleccionar la suscripción activa.  
   - **Grupo de recursos:** **AI-Prompt-Validator-RG**.  
   - **Nombre del servicio:** **prompt-language-service**.  
   - **Región:** **East US 2**.  
   - **Plan de tarifa:** **S (Standard, 1K llamadas/minuto)**.  
4. Hacer clic en **"Revisar y Crear"** → **"Crear"** y esperar la implementación.  

---

### 4️⃣ **Obtener las Claves y Endpoint de los Servicios**  
💡 **Necesitamos estas credenciales para integrarlas en nuestro código.**  

📌 **Para Azure OpenAI:**  
1. Ir a **Azure OpenAI** → **prompt-validator-function-openai-b083**.  
2. En el menú lateral, hacer clic en **"Keys and Endpoint"**.  
3. Copiar:  
   - **Endpoint:** `https://turecurso.openai.azure.com/`  
   - **Key:** `tu-clave-de-openai`  

📌 **Para Azure Cognitive Services - Language Service:**  
1. Ir a **Language Service** → **prompt-language-service**.  
2. En el menú lateral, hacer clic en **"Keys and Endpoint"**.  
3. Copiar:  
   - **Endpoint:** `https://turecurso.cognitiveservices.azure.com/`  
   - **Key:** `tu-clave-de-cognitive-services`  

---

### 5️⃣ **Actualizar el archivo `local.settings.json` en Azure Functions**  
💡 **Para que nuestra función use las credenciales correctas.**  

1. Abrir el proyecto en **Visual Studio Code**.  
2. Dentro de la carpeta de Azure Functions, localizar **`local.settings.json`**.  
3. Reemplazar el contenido con las credenciales copiadas:  

```json
{
  "IsEncrypted": false,
  "Values": {
   ...
    "CONTENT_SAFETY_ENDPOINT": "https://turecurso.cognitiveservices.azure.com/",
    "CONTENT_SAFETY_KEY": "tu-clave-de-content-safety"
   ...
  }
}
```

Después de haber configurado los servicios base en Azure, ahora hemos **implementado los modelos en Azure OpenAI** y actualizado nuestra función en Azure Functions para conectarse correctamente con estos recursos.  

---

## ⚙️ **5️⃣ Implementación de Modelos en Azure OpenAI**  

💡 Para validar y generar respuestas optimizadas, implementamos **GPT-35-Turbo** en **Azure AI Foundry** con dos configuraciones:  

1. **Corrección de Prompts** → `corrector-deployment`.  
2. **Generación de Respuestas** → `respuesta-deployment`.  

📌 **Pasos seguidos:**  

1. Entramos en **Azure AI Foundry** desde el **Portal de Azure**.  
2. En la pestaña **Implementaciones**, hicimos clic en **"Nueva implementación"**.  
3. **Configuramos cada implementación** con:  
   - **Modelo:** `gpt-35-turbo`.  
   - **Tipo de implementación:** `Estándar`.  
   - **Versión del modelo:** `0125` (última estable).  
   - **Filtro de contenido:** `DefaultV2`.  
   - **Cuota dinámica:** **Activada**.  
   - **Tokens por minuto (TPM):** **Reducido a 10K** (para evitar problemas de cuota).  
4. Esperamos la activación y verificamos que ambas implementaciones aparezcan en la lista de **Implementaciones Activas**.  

---

## 🔑 **6️⃣ Obtención de Credenciales de Azure OpenAI**  

Después de implementar los modelos, **obtenemos las claves y el endpoint** para integrarlos en nuestro backend.  

📌 **Pasos seguidos:**  

1. En el **Portal de Azure**, buscamos el recurso **`prompt-validator-function-openai-b083`**.  
2. Hicimos clic en **"Click here to view endpoints"** y copiamos la URL del endpoint.  
3. Hicimos clic en **"Click here to manage keys"** y copiamos la **Key 1**.  

📌 **Ejemplo de credenciales obtenidas:**  
- **Endpoint:** `https://turecurso.openai.azure.com/`  
- **Key:** `tu-clave-de-openai`  

---

## 🛠 **7️⃣ Configuración de Azure Functions (`local.settings.json`)**  

Ahora, actualizamos **Azure Functions** para conectar correctamente OpenAI con nuestra API.  

📌 **Pasos seguidos:**  

1. Abrimos el proyecto en **Visual Studio Code**.  
2. Modificamos el archivo **`local.settings.json`** para incluir las claves y endpoints de OpenAI.  

📌 **Ejemplo de `local.settings.json` actualizado:**  

```json
{
  "IsEncrypted": false,
  "Values": {
   ...
    "OPENAI_ENDPOINT": "https://turecurso.openai.azure.com/",#-> Aquí colocamos el Endpoint
    "OPENAI_KEY": "tu-clave-de-openai",#-> Aquí colocamos la KEY 1
    "OPENAI_CORRECTOR_DEPLOYMENT": "corrector-deployment",
    "OPENAI_RESPUESTA_DEPLOYMENT": "respuesta-deployment",
   ...
  }
}
```

## 📌 **8️⃣ Verificación en Azure Functions**  

Antes de continuar con el desarrollo del backend, verificamos que **Azure Functions esté correctamente configurado**.  

📌 **Pasos seguidos:**  

1. Entramos a **Azure Functions** en el **Portal de Azure**.  
2. Buscamos nuestra función **`prompt-validator-function`**.  
3. En el menú lateral, fuimos a **Configuración > Variables de Aplicación**.  
4. **Verificamos que las claves y endpoints de OpenAI y Cognitive Services estén correctamente cargados.**  

🚀 **Con esto, Azure Functions ya está listo para conectarse con OpenAI.**  


## 🛠 **9️⃣ Implementación de los Endpoints en Azure Functions**  

Después de configurar correctamente OpenAI en Azure, implementamos los endpoints para **validación de prompts** y **generación de respuestas** en nuestra función de Azure.  

📌 **Endpoints creados:**  
- `POST /api/validatePrompt` → Valida el contenido del prompt asegurando seguridad y claridad.  
- `POST /api/generateResponse` → Genera respuestas usando **GPT-4** en Azure OpenAI.  

### 📂 **Estructura del Proyecto**  

Después de la implementación, nuestro proyecto tiene la siguiente estructura:  

```bash
myFunctionApp
├── PromtGuard
│   ├── bin/
│   ├── include/
│   ├── lib/
│   └── pyvenv.cfg
├── __pycache__/
├── function_app.py
├── function_app.zip
├── generateResponse/
│   ├── __init__.py
│   └── function.json
├── host.json
├── local.settings.json
├── readme.md
├── requirements.txt
└── validatePrompt/
    ├── __init__.py
    └── function.json
```

---

## 🚀 **🔟 Ejecución de la API Localmente**  

Una vez que todo está configurado, podemos **ejecutar la API localmente** usando **Azure Functions Core Tools**.  

### ✅ **Pasos para Iniciar la API**  

1️⃣ **Abrir la terminal y navegar al proyecto:**  
```sh
cd myFunctionApp
```

2️⃣ **Activar el entorno virtual:**  
```sh
source PromtGuard/bin/activate  # Mac/Linux
```

3️⃣ **Ejecutar Azure Functions:**  
```sh
func start
```

📌 **Ejemplo de salida esperada:**  
```bash
Azure Functions Core Tools
Function Runtime Version: 4.1036.1.23224

Functions:

        generateResponse: [POST] http://localhost:7071/api/generateResponse
        validatePrompt: [POST] http://localhost:7071/api/validatePrompt
```

Si ves estas rutas en la terminal, **las funciones están activas y listas para recibir solicitudes**. 🎉  

---

## 🧪 **1️⃣1️⃣ Pruebas de los Endpoints**  

📌 Para probar que la API funciona correctamente, enviamos solicitudes con `curl` o Postman.  

### 🔹 **Validación de Prompt** (`/api/validatePrompt`)  

```sh
curl -X POST "http://localhost:7071/api/validatePrompt" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hola, ¿cómo estás?"}'
```

🔹 **Ejemplo de respuesta esperada:**  
```json
{
  "correctedPrompt": "Hola, ¿cómo estás?",
  "suggestions": ["Reformula la pregunta para mayor claridad."]
}
```

---

### 🔹 **Generación de Respuesta** (`/api/generateResponse`)  

```sh
curl -X POST "http://localhost:7071/api/generateResponse" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Escribe un resumen sobre el cambio climático."}'
```

🔹 **Ejemplo de respuesta esperada:**  
```json
{
  "response": "El cambio climático es un fenómeno global causado por la emisión de gases de efecto invernadero..."
}
```

---

## 🚑 **1️⃣2️⃣ Solución de Problemas**  

Si la API no responde o tienes errores, revisa lo siguiente:  

❌ **Error:** `Worker failed to index functions`  
🔹 **Solución:** Asegúrate de que `app` está correctamente definido en `function_app.py`.  

❌ **Error:** `No job functions found`  
🔹 **Solución:** Verifica que cada función tiene correctamente el decorador `@app.function_name()`.  

❌ **Error 500 al llamar a OpenAI**  
🔹 **Solución:** Revisa tu clave de OpenAI en `local.settings.json` y confirma que está activa.  

---

## 🎯 **1️⃣3️⃣ Próximos Pasos**  

✅ **Mejorar la validación del contenido para reducir falsos positivos.**  
✅ **Optimizar la integración con OpenAI para mejorar respuestas.**  
✅ **Desplegar en Azure Function App y probar en producción.**  





