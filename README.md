<p align="center">
  <h1 align="center">✈️ JetSeeker — AI Travel Assistant</h1>
  <p align="center">
    <strong>WhatsApp-native AI chatbot for real-time flight search & trip planning</strong>
  </p>
  <p align="center">
    <em>Built in 24 hours at <a href="#">VibeHack Bucharest 2026</a> — Vola.ro AI Travel Challenge</em>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Twilio-F22F46?style=for-the-badge&logo=twilio&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenAI_API-412991?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" />
</p>

---

## 🚀 What It Does

JetSeeker is an AI-powered WhatsApp chatbot that helps users find and compare real flights in real time. Instead of switching between travel apps, users simply message the bot on WhatsApp — in natural language — and get instant flight results from **Vola.ro**, Romania's largest online travel agency.

### Key Features

- 🗣️ **Natural Language Flight Search** — Ask in plain text: *"Find me a flight from Bucharest to Paris next Friday"*
- 🔍 **Real-Time Pricing** — Fetches live flight data by integrating with Vola.ro's search API
- 📱 **WhatsApp Native** — Works in both direct messages and group chats via Twilio
- 🤖 **AI-Powered Intent Parsing** — Uses LLM function calling to extract cities, dates, and preferences
- 🧠 **Multi-Turn Context** — Maintains conversation state for follow-up questions
- 📸 **Vision Capabilities** — Can analyze booking screenshots and travel photos (planned)

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   WhatsApp   │────▶│    Twilio     │────▶│   FastAPI    │────▶│   LLM API    │
│   (User)     │◀────│   Webhook    │◀────│   Server     │◀────│  (Qwen3-8B)  │
└──────────────┘     └──────────────┘     └──────┬───────┘     └──────────────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │  Vola.ro API │
                                          │ (Flight Data)│
                                          └──────────────┘
```

**Flow:**
1. User sends a WhatsApp message → Twilio forwards it to our FastAPI webhook
2. The server sends the message to an LLM with function-calling tools defined
3. If the LLM detects a flight search intent, it calls `search_vola_flights` with extracted IATA codes & dates
4. The Vola.ro API integration fetches real-time flight prices
5. Results are formatted and sent back to the user via Twilio/WhatsApp

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.11+, FastAPI |
| AI/LLM | OpenAI-compatible API (Qwen3-8B via Featherless AI) |
| Messaging | Twilio WhatsApp API |
| Flight Data | Vola.ro Search API (reverse-engineered) |
| Deployment | ngrok (dev), ready for cloud deployment |

---

## 📁 Project Structure

```
├── main.py              # FastAPI server + Twilio webhook handler
├── vola_api.py          # Vola.ro flight search API integration
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
├── LICENSE              # MIT License
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- A [Twilio account](https://www.twilio.com/) with WhatsApp Sandbox enabled
- An LLM API key (OpenAI-compatible endpoint)

### Setup

```bash
# Clone the repo
git clone https://github.com/Stevenenson/JetSeeker-VibeHack2026.git
cd JetSeeker-VibeHack2026

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the server
uvicorn main:app --reload --port 8000
```

### Expose via ngrok (for Twilio webhook)
```bash
ngrok http 8000
```
Then set the ngrok URL as your Twilio WhatsApp webhook.

---

## 🔐 Security Notes

- All API keys and credentials are stored in environment variables (`.env`)
- Never commit `.env` files to version control
- The Vola.ro API integration was built through API analysis during the hackathon

---

## 🏆 Hackathon Context

**Event:** VibeHack Bucharest 2026
**Challenge:** Vola.ro AI Travel Challenge — Build a WhatsApp-native AI travel assistant
**Date:** March 14-15, 2026 (24-hour hackathon)
**Sponsor:** [Vola.ro](https://www.vola.ro/) — Romania's largest online travel agency

### What We Accomplished in 24 Hours:
- Reverse-engineered Vola.ro's flight search API for real-time data
- Built a complete WhatsApp chatbot pipeline (Twilio → FastAPI → LLM → Vola API)
- Implemented AI function calling for structured flight search
- Designed multi-turn conversation handling for group chats

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <sub>Built with ☕ and no sleep at VibeHack 2026</sub>
</p>
