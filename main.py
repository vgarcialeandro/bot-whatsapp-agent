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

    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == os.environ.get("VERIFY_TOKEN")
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