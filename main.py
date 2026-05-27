import os
import logging
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import PlainTextResponse

app = FastAPI(title="WhatsApp Webhook - Azure Container Apps")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/")
def home():
    return {"status": "Fase Inicial: Modo Eco Activo"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# ====================== GET /webhook ======================
@app.get("/webhook", response_class=PlainTextResponse)
@app.get("/webhook/", response_class=PlainTextResponse)
def verificar_webhook(
    request: Request,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    query_params = dict(request.query_params)
    user_agent = request.headers.get("user-agent", "")

    logger.info(f"Webhook GET recibido - Query params: {query_params}")

    # Health probe de Azure Container Apps
    if "Azure" in user_agent or not hub_mode:
        logger.info("Health probe de Azure detectada")
        return PlainTextResponse(content="OK", status_code=200)

    VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN") or "BotPrueba20260519"

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        logger.info("✅ Verificación WhatsApp exitosa")
        return PlainTextResponse(content=str(hub_challenge or ""), status_code=200)

    logger.warning("❌ Verificación fallida")
    return PlainTextResponse(content="Token inválido", status_code=403)


# ====================== POST /webhook ======================
@app.post("/webhook")
async def recibir_mensaje(request: Request):
    try:
        datos = await request.json()
        logger.info(f"Datos recibidos en POST: {datos}")

        # Event Grid puede enviar una lista o un objeto único
        eventos = datos if isinstance(datos, list) else [datos]

        for evento in eventos:
            event_type = evento.get("eventType")

            if event_type == "Microsoft.EventGrid.SubscriptionValidationEvent":
                validation_code = evento.get("data", {}).get("validationCode")
                if validation_code:
                    logger.info(f"✅ Validación Azure OK: {validation_code}")
                    return {"validationResponse": validation_code}

            elif event_type == "Microsoft.Communication.AdvancedMessageReceived":
                logger.info("💬 ¡Mensaje de WhatsApp recibido!")
                # Aquí irá tu lógica multi-agente
                # data = evento.get("data", {})
                # ... procesar mensaje

        return Response(status_code=200)

    except Exception as e:
        logger.error(f"❌ Error procesando webhook: {e}")
        return Response(status_code=200)   # Siempre 200 para Event Grid