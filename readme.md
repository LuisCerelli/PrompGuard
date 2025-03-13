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
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "OPENAI_ENDPOINT": "https://turecurso.openai.azure.com/",
    "OPENAI_KEY": "tu-clave-de-openai",
    "COGNITIVE_SERVICES_ENDPOINT": "https://turecurso.cognitiveservices.azure.com/",
    "COGNITIVE_SERVICES_KEY": "tu-clave-de-cognitive-services"
  }
}
```
### 🔜 **Próximos Pasos**  
✅ Integrar **Azure Cognitive Services - Language Service** con **Azure Functions**.  
✅ Implementar los endpoints `/api/validatePrompt` y `/api/generateResponse`.  
✅ Hacer pruebas iniciales para validar el flujo completo.  

