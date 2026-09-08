from fastapi import APIRouter, Form, Response
from fastapi.responses import HTMLResponse
from app.core.ai import ai_service

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

@router.post("/")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    """
    This endpoint receives messages from Twilio/WhatsApp.
    It now uses Llama 3 via Groq to generate intelligent responses.
    """
    print(f"Incoming message from {From}: {Body}")

    # Get an intelligent response from the AI
    ai_response = await ai_service.get_response(Body)

    # Twilio expects TwiML (XML) as a response
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>{ai_response}</Message>
    </Response>
    """

    return Response(content=twiml_response, media_type="application/xml")
