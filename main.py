import os
from fastapi import FastAPI, Request, Response

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Fase Inicial: Modo Eco Activo"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/webhook")
def verificar_webhook(request: Request):

    params = request.query_params

    # 1. Imprimimos en los logs de Azure exactamente qué está llegando de Meta para auditarlo
    print("MODO RECIBIDO:", params.get("hub.mode"))
    print("TOKEN RECIBIDO DE META:", params.get("hub.verify_token"))
    
    # Coloca aquí en texto plano la misma palabra exacta que configuraste en Meta
    TOKEN_FIJO_DE_PRUEBA = "BotPrueba20260519"

    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == TOKEN_FIJO_DE_PRUEBA
    ):
        return Response(
            content=params.get("hub.challenge"),
            media_type="text/plain"
        )

    return Response(
        content="Token invalido",
        status_code=403
    )

@app.post("/webhook")
async def recibir_mensaje(request: Request):

    datos = await request.json()

    print("Mensaje recibido:", datos)

    return {"status": "recibido_y_clonado"}