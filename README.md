# 🏥 Multispeciality Hospital WhatsApp Bot

An intelligent AI-powered WhatsApp chatbot designed for multispeciality hospitals to automate appointment booking, doctor
discovery, and patient FAQs.

## 🌟 Features
- **AI-Powered Chat:** Built with Llama 3 (via Groq) for natural, empathetic patient interactions.
- **Automated Booking:** Integrated with PostgreSQL to manage doctor schedules and patient appointments.
- **Session Memory:** Uses Redis to track conversation state and maintain context across messages.
- **Medical Guardrails:** Strict system prompts to prevent medical diagnosis and prioritize emergencies.
- **WhatsApp Integration:** Connected via Twilio Sandbox for seamless mobile access.

## 🛠️ Tech Stack
- **Language:** Python 3.10+
- **Framework:** FastAPI
- **AI Engine:** Groq API (Llama 3)
- **Database:** PostgreSQL (Main Storage) & Redis (Session Cache)
- **Knowledge Base:** ChromaDB (Vector Database for RAG)
- **Gateway:** Twilio WhatsApp API
- **Tunneling:** Ngrok (for local development)

## 🚀 Quick Start Guide

### 1. Prerequisites
- Install **PostgreSQL** and create a database named `hospital_db`.
- Install **Redis** (locally or via Docker).
- Get a **Groq API Key** from [console.groq.com](https://console.groq.com/).
- Set up a **Twilio Sandbox** account.

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/nikhil1127/Hospital_ChatBot.git
cd Hospital_ChatBot

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_key_here
DATABASE_URL=postgresql://postgres:password@localhost:5432/hospital_db
REDIS_URL=redis://localhost:6379/0
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_twilio_number
```

### 4. Database Initialization
```bash
# Create tables
python -m app.db.init_db

# Seed the database with test doctors
python -m app.db.seed
```

### 5. Running the Bot
```bash
# Start the server
python -m app.main
```

### 6. Connecting to WhatsApp
1. Run `ngrok http 8000`.
2. Copy the public URL (e.g., `https://xxxx.ngrok-free.app`).
3. Paste `https://xxxx.ngrok-free.app/whatsapp` into the Twilio Sandbox "When a message comes in" field.
4. Send the "join" code to the Twilio number from your phone.

## 📁 Project Structure
- `app/api/`: Webhook endpoints.
- `app/core/`: AI logic, session management, and DB services.
- `app/db/`: Database models and initialization scripts.
- `data/`: Hospital knowledge base files.
