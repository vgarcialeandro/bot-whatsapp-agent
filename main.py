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

# Modifica el decorador para que acepte AMBAS variantes (con y sin barra)
@app.get("/webhook", response_class=PlainTextResponse)
@app.get("/webhook/", response_class=PlainTextResponse)
def verificar_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    # Ponemos una condición para ignorar las alertas de las sondas de Azure que vengan vacías
    if hub_mode is None and hub_verify_token is None:
        return Response(content="Sonda interna activa", status_code=200)

    print("--- ¡SOLICITUD REAL DETECTADA! ---")
    print("MODO:", hub_mode)
    print("TOKEN:", hub_verify_token)
    print("CHALLENGE:", hub_challenge)

    TOKEN_FIJO_DE_PRUEBA = "BotPrueba20260519"

    if hub_mode == "subscribe" and hub_verify_token == TOKEN_FIJO_DE_PRUEBA:
        print("¡CONEXIÓN EXITOSA CON META!")
        return hub_challenge

    print("¡VERIFICACIÓN FALLIDA! Datos incorrectos.")
    return Response(content="Token invalido", status_code=403)
    

@app.post("/webhook")
async def recibir_mensaje(request: Request):

    datos = await request.json()

    print("Mensaje recibido:", datos)

    return {"status": "recibido_y_clonado"}