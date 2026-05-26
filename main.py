import os
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import PlainTextResponse
import logging

app = FastAPI(title="WhatsApp Webhook - Azure Container Apps")

# Configuración de logs (importante para Azure Container Apps)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/")
def home():
    return {"status": "Fase Inicial: Modo Eco Activo"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/webhook", response_class=PlainTextResponse)
@app.get("/webhook/", response_class=PlainTextResponse)
def verificar_webhook(
    request: Request,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    # Logging completo para diagnóstico en Azure
    query_params = dict(request.query_params)
    user_agent = request.headers.get("user-agent", "")

    logger.info(f"Webhook GET recibido - Query params: {query_params}")
    logger.info(f"User-Agent: {user_agent}")

    # Ignorar health probes / sondas de Azure
    if ("Azure" in user_agent or "HealthCheck" in str(request.url)) and not hub_mode:
        logger.info("Health probe de Azure detectada")
        return PlainTextResponse(content="OK", status_code=200)

    logger.info(f"hub.mode={hub_mode} | hub.verify_token={hub_verify_token} | hub.challenge={hub_challenge}")

    # === TOKEN DE VERIFICACIÓN (flexible - soporta ambos nombres comunes) ===
    VERIFY_TOKEN = (
        os.getenv("WHATSAPP_VERIFY_TOKEN") 
        or os.getenv("VERIFY_TOKEN") 
        or "BotPrueba20260519"
    )

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        logger.info("✅ Verificación exitosa con Meta")
        return PlainTextResponse(content=str(hub_challenge or ""), status_code=200)

    logger.warning("❌ Verificación fallida - Token o modo incorrecto")
    return PlainTextResponse(content="Token inválido", status_code=403)


@app.post("/webhook")
async def recibir_mensaje(request: Request):
    try:
        datos = await request.json()
        logger.info(f"Datos recibidos en el webhook: {datos}")
        
        # 1. Detectar si los datos vienen envueltos en una lista (común en Event Grid)
        evento = datos[0] if isinstance(datos, list) and len(datos) > 0 else datos

        # 2. 🔑 CAPTURAR EL APRETÓN DE MANOS (Esto destrabará los 6 minutos en Azure)
        if evento.get("eventType") == "Microsoft.EventGrid.SubscriptionValidationEvent":
            validation_code = evento["data"]["validationCode"]
            logger.info(f"✅ Respondiendo validación de Azure con el código: {validation_code}")
            return {"validationResponse": validation_code}

        # 3. 💬 CAPTURAR MENSAJES REALES DE WHATSAPP
        # (Este evento ocurrirá cuando tú o un cliente escriban al número)
        elif evento.get("eventType") == "Microsoft.Communication.AdvancedMessageReceived":
            logger.info("💬 ¡Mensaje entrante real de WhatsApp detectado!")
            
            # Aquí procesarás el texto con tus agentes de ventas más adelante
            # datos_mensaje = evento["data"]
            
        return Response(status_code=200)

    except Exception as e:
        logger.error(f"❌ Error interno procesando el webhook: {e}")
        return Response(status_code=400)