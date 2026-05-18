import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from dotenv import load_dotenv
from fastapi import Request
import os

# Load environment variables
load_dotenv()

# =========================
# FASTAPI APP
# =========================

app = FastAPI()

VERIFY_TOKEN = "restaurant_ai_bot"


@app.get("/webhook")
async def verify_webhook(request: Request):

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return int(challenge)

    return {"message": "Webhook route working"}


@app.post("/webhook")
async def whatsapp_webhook(request: Request):

    data = await request.json()

    print(data)

    return {"status": "received"}
# =========================
# TELEGRAM CONFIG
# =========================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# =========================
# EMAIL CONFIG
# =========================

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")

EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# =========================
# GROQ API KEY
# =========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =========================
# webhook
# =========================

VERIFY_TOKEN = "restaurant_ai_bot"

# =========================
# ENABLE CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# REQUEST MODEL
# =========================

class ChatRequest(BaseModel):
    message: str

# =========================
# LOAD RESTAURANT DATA
# =========================

with open("data/restaurant_data.json", "r") as file:
    restaurant_data = json.load(file)

# =========================
# GOOGLE SHEETS SETUP
# =========================

# scope = [
#     "https://spreadsheets.google.com/feeds",
#     "https://www.googleapis.com/auth/drive"
# ]

# creds = ServiceAccountCredentials.from_json_keyfile_name(
#     "credentials.json",
#     scope
# )

# client = gspread.authorize(creds)

# sheet = client.open("Restaurant Bookings").sheet1

# =========================
# TEMP BOOKING MEMORY
# =========================

booking_sessions = {}

# =========================
# TELEGRAM FUNCTION
# =========================

def send_telegram_message(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    requests.post(url, data=payload)

# =========================
# EMAIL FUNCTION
# =========================

def send_email(to_email, subject, body):

    try:

        response = requests.post(

            "https://api.resend.com/emails",

            headers={
                "Authorization": f"Bearer {os.getenv('RESEND_API_KEY')}",
                "Content-Type": "application/json"
            },

            json={

                "from": "onboarding@resend.dev",

                "to": to_email,

                "subject": subject,

                "html": f"<p>{body}</p>"

            }

        )

        print(response.json())

    except Exception as e:

        print("Email Error:", e)

# =========================
# HOME ROUTE
# =========================

@app.get("/")
def home():
    return {
        "message": "Backend Running"
    }

# =========================
# CHAT ROUTE
# =========================

@app.post("/chat")
def chat(request: ChatRequest):

    user_message = request.message
    message_lower = user_message.lower()

    user_id = "default_user"

    # =========================
    # START BOOKING FLOW
    # =========================

    if (
        "book" in message_lower
        or "reservation" in message_lower
        or "table" in message_lower
    ):

        booking_sessions[user_id] = {
            "stage": "name"
        }

        return {
            "reply": "Sure 😊 May I know your name?"
        }

    # =========================
    # ACTIVE BOOKING SESSION
    # =========================

    if user_id in booking_sessions:

        session = booking_sessions[user_id]

        # NAME STEP
        if session["stage"] == "name":

            session["name"] = user_message
            session["stage"] = "phone"

            return {
                "reply": "Please share your phone number 😊"
            }

        # PHONE STEP
        elif session["stage"] == "phone":

            session["phone"] = user_message
            session["stage"] = "guests"

            return {
                "reply": "How many guests?"
            }

        # GUEST STEP
        elif session["stage"] == "guests":

            session["guests"] = user_message
            session["stage"] = "email"

            return {
                "reply": "Please share your email address 😊"
            }

        # EMAIL STEP
        elif session["stage"] == "email":

            session["email"] = user_message
            session["stage"] = "time"

            return {
                "reply": "What time would you like the reservation? 😊"
            }

        # TIME STEP
        elif session["stage"] == "time":

            session["time"] = user_message

            # SEND EMAIL
            email_body = f"""
Hello {session['name']},

Your table booking is confirmed 🎉

Guests: {session['guests']}
Time: {session['time']}

Thank you for choosing Spice Garden 🍕
"""

            send_email(
                session["email"],
                "Spice Garden Booking Confirmation",
                email_body
            )

            # SEND TELEGRAM ALERT
            telegram_message = f"""
🚨 New Table Booking

👤 Name: {session['name']}
📞 Phone: {session['phone']}
📧 Email: {session['email']}
🍽 Guests: {session['guests']}
⏰ Time: {session['time']}
"""

            send_telegram_message(telegram_message)

            # # SAVE TO GOOGLE SHEETS
            # sheet.append_row([
            #     session["name"],
            #     session["phone"],
            #     session["email"],
            #     session["guests"],
            #     session["time"]
            # ])

            # CONFIRMATION
            confirmation = f"""
🎉 Table Booking Confirmed

👤 Name: {session['name']}
📞 Phone: {session['phone']}
📧 Email: {session['email']}
🍽 Guests: {session['guests']}
⏰ Time: {session['time']}

Confirmation email sent successfully ✉️
"""

            # CLEAR SESSION
            del booking_sessions[user_id]

            return {
                "reply": confirmation
            }

    # =========================
    # COMPLAINT HANDLING
    # =========================

    complaint_keywords = [
        "complaint",
        "bad",
        "worst",
        "refund",
        "manager",
        "issue",
        "problem"
    ]

    if any(word in message_lower for word in complaint_keywords):

        return {
            "reply": "I’m sorry for the inconvenience 😔 Our support manager will contact you soon."
        }

    # =========================
    # MENU RECOMMENDATIONS
    # =========================

    if "recommend" in message_lower or "suggest" in message_lower:

        return {
            "reply": "😊 Our most popular dishes are Paneer Pizza 🍕, White Sauce Pasta 🍝 and Cold Coffee ☕"
        }

    # =========================
    # SYSTEM PROMPT
    # =========================

    system_prompt = f"""
You are a smart AI restaurant assistant.

Restaurant Information:

{restaurant_data}

Your responsibilities:
- Answer customer questions
- Help customers politely
- Explain menu prices
- Recommend dishes
- Help with restaurant services

Rules:
- Only answer using restaurant information
- Keep answers short and friendly
- Use emojis sometimes
"""

    # =========================
    # AI RESPONSE
    # =========================

    try:

        response = requests.post(

            url="https://api.groq.com/openai/v1/chat/completions",

            headers={

                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"

            },

            json={

                "model": "llama-3.3-70b-versatile",

                "messages": [

                    {
                        "role": "system",
                        "content": system_prompt
                    },

                    {
                        "role": "user",
                        "content": user_message
                    }

                ]

            }

        )

        data = response.json()

        print(data)

        if "choices" not in data:

            error_message = data.get(
                "error",
                {}
            ).get(
                "message",
                "Unknown API Error"
            )

            return {
                "reply": f"API Error: {error_message}"
            }

        ai_reply = data["choices"][0]["message"]["content"]

        return {
            "reply": ai_reply
        }

    except Exception as e:

        return {
            "reply": f"Backend Error: {str(e)}"
        }