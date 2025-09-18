from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import requests
import asyncio
import json
import os
from datetime import datetime
import logging

# Initialize FastAPI
app = FastAPI()

# WhatsApp credentials (get from Meta Developer Console)
WHATSAPP_TOKEN = "EAASdGXbuJe0BPUZBoZBza0S01GQ167lv9BCr7yXBgBIJp3ztFUNtZBzj5Be1DDQlBlZB4zCVvIpRZCpMksrdYigIkqRwcfjySscg8ek5rsh6FXwnR85OelqxzepPFYj6UKTGSlbIrRZCx9QNaJozv5g1Awob69CiblZCUEaVG1DUnklWTEeOGrprjM6XEwWb4nZBKYfEKFXJvjcwXKQZAZAqmQRqLte52WXDsMty3hD40tGgZDZD"
VERIFY_TOKEN = "my_secret_token"
WHATSAPP_API_URL = "https://graph.facebook.com/v17.0/829624553567203/messages"

# Rasa server URL
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Verify webhook for WhatsApp"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

@app.post("/webhook")
async def handle_webhook(request: Request):
    """Handle incoming WhatsApp messages"""
    try:
        body = await request.json()
        
        # Extract message data
        if "messages" in body["entry"][0]["changes"][0]["value"]:
            messages = body["entry"][0]["changes"][0]["value"]["messages"]
            
            for message in messages:
                sender_id = message["from"]
                message_text = message.get("text", {}).get("body", "")
                
                if message_text:
                    # Send to Rasa for processing
                    rasa_response = await send_to_rasa(sender_id, message_text)
                    
                    # Send response back to WhatsApp
                    for response in rasa_response:
                        await send_whatsapp_message(sender_id, response["text"])
        
        return {"status": "ok"}
    
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error"}

async def send_to_rasa(sender_id: str, message: str):
    """Send message to Rasa and get response"""
    payload = {
        "sender": sender_id,
        "message": message
    }
    
    try:
        response = requests.post(RASA_URL, json=payload)
        return response.json()
    except Exception as e:
        print(f"Rasa error: {e}")
        return [{"text": "Sorry, I'm having technical difficulties. Please try again."}]

async def send_whatsapp_message(recipient_id: str, message: str):
    """Send message to WhatsApp user"""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "text": {"body": message}
    }
    
    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        print(f"WhatsApp send error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)