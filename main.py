import json
import os
import datetime
from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.responses import Response
from openai import OpenAI
from twilio.rest import Client
from vola_api import search_flights_real
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -- Configuration --
client = OpenAI(
    base_url=os.getenv('LLM_API_BASE_URL', 'https://api.featherless.ai/v1'),
    api_key=os.getenv('LLM_API_KEY')
)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', 'whatsapp:+14155238886')

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
app = FastAPI(
    title="JetSeeker — AI Travel Assistant",
    description="WhatsApp-native AI chatbot for real-time flight search",
    version="1.0.0"
)

# -- LLM Function Calling Tools --
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_vola_flights",
            "description": (
                "Search for real flight prices on Vola.ro. "
                "Use this when the user asks about a flight route or prices."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "origin_code": {
                        "type": "string",
                        "description": "IATA city code of departure (e.g., BUH for Bucharest)."
                    },
                    "dest_code": {
                        "type": "string",
                        "description": "IATA city code of destination (e.g., ROM, PAR, LON)."
                    },
                    "departure_date": {
                        "type": "string",
                        "description": "Departure date in YYYY-MM-DD format."
                    },
                    "return_date": {
                        "type": "string",
                        "description": "Return date in YYYY-MM-DD format."
                    }
                },
                "required": ["origin_code", "dest_code", "departure_date", "return_date"]
            }
        }
    }
]


def process_message(body: str, sender_phone: str):
    """
    Process an incoming WhatsApp message in the background.
    Uses LLM function calling to detect flight search intent and 
    fetches real-time results from Vola.ro API.
    """
    print(f"\n[BOT] Processing message from {sender_phone}: {body}")

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    messages = [
        {
            "role": "system",
            "content": (
                "You are JetSeeker, a friendly AI travel assistant powered by Vola.ro. "
                "You help users find flights by extracting cities as IATA codes and calling "
                "the flight search function. Be concise and helpful. "
                f"Today's date: {today}"
            )
        },
        {"role": "user", "content": body}
    ]

    try:
        # First LLM call — detect intent and extract parameters
        response = client.chat.completions.create(
            model=os.getenv('LLM_MODEL', 'Qwen/Qwen3-8B'),
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            # LLM wants to call the flight search function
            tool_call = assistant_message.tool_calls[0]
            arguments = json.loads(tool_call.function.arguments)

            print(f"[BOT] Searching flights: {arguments}")

            # Fetch real flight data from Vola.ro
            flight_results = search_flights_real(
                origin_code=arguments.get("origin_code"),
                dest_code=arguments.get("dest_code"),
                departure_date=arguments.get("departure_date"),
                return_date=arguments.get("return_date")
            )

            # Second LLM call — format the results for the user
            messages.append(assistant_message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": str(flight_results)
            })

            final_response = client.chat.completions.create(
                model=os.getenv('LLM_MODEL', 'Qwen/Qwen3-8B'),
                messages=messages
            )
            reply_text = final_response.choices[0].message.content
        else:
            reply_text = assistant_message.content

        if not reply_text:
            reply_text = "Sorry, I couldn't process that message. Please try again."

    except Exception as e:
        print(f"[ERROR] {e}")
        reply_text = "Something went wrong while processing your request. Please try again."

    # Send reply via Twilio WhatsApp
    try:
        twilio_client.messages.create(
            body=reply_text,
            from_=TWILIO_PHONE_NUMBER,
            to=sender_phone
        )
        print(f"[BOT] Reply sent to {sender_phone}")
    except Exception as e:
        print(f"[ERROR] Failed to send WhatsApp reply: {e}")


@app.post("/webhook")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Twilio WhatsApp webhook endpoint.
    Processes incoming messages asynchronously to avoid Twilio timeout.
    """
    print(f"[WEBHOOK] Received from {From}: {Body}")

    # Process in background to respond within Twilio's timeout
    background_tasks.add_task(process_message, Body, From)

    # Acknowledge receipt immediately
    return Response(
        content="<Response></Response>",
        media_type="application/xml"
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "JetSeeker AI Travel Assistant"}
