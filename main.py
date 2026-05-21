import os
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Fase Inicial: Modo Eco Activo"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/webhook", response_class=PlainTextResponse)
def verificar_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    # Monitoreo nativo en consola
    print("--- SOLICITUD ENTRANTE ---")
    print("MODO EXTRAÍDO POR FASTAPI:", hub_mode)
    print("TOKEN EXTRAÍDO POR FASTAPI:", hub_verify_token)
    print("CHALLENGE EXTRAÍDO:", hub_challenge)

    TOKEN_FIJO_DE_PRUEBA = "BotPrueba20260519"

    if hub_mode == "subscribe" and hub_verify_token == TOKEN_FIJO_DE_PRUEBA:
        print("¡ÉXITO TOTAL! Coincidencia perfecta.")
        return hub_challenge

    print("¡FALLÓ! Los datos siguen llegando vacíos o no coinciden.")
    return Response(content="Token invalido", status_code=403)
    

@app.post("/webhook")
async def recibir_mensaje(request: Request):

    datos = await request.json()

    print("Mensaje recibido:", datos)

    return {"status": "recibido_y_clonado"}