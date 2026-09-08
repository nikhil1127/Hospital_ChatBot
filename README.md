# 🏥 Multispeciality Hospital WhatsApp Bot

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green.svg)
![AI](https://img.shields.io/badge/AI-Llama%203-orange.svg)
![Database](https://img.shields.io/badge/DB-PostgreSQL-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

An intelligent, AI-powered WhatsApp chatbot designed for multispeciality hospitals to automate patient interactions, appointment bookings, and general inquiries.

## 🌟 Features

- **🤖 AI-Powered Conversations**: Built with Llama 3 (via Groq API) for natural, empathetic patient interactions
- **📅 Automated Appointment Booking**: Complete booking flow with doctor selection and scheduling
- **🔍 Smart Doctor Discovery**: Find specialists by department/specialty
- **💾 Session Memory**: Uses Redis to track conversation state and context
- **🗄️ Database Integration**: PostgreSQL for storing patients, doctors, and appointments
- **📱 WhatsApp Integration**: Direct integration with WhatsApp via Twilio
- **⚡ Emergency Detection**: Automatically identifies emergency symptoms and redirects to emergency services
- **🔒 Medical Guardrails**: Strict prompts to prevent AI from making medical diagnoses

## 🏗️ Architecture

```
Patient (WhatsApp)
    ↓
Twilio (WhatsApp API Gateway)
    ↓
Ngrok (Secure Tunnel)
    ↓
FastAPI Server (Python)
    ├── AI Service (Llama 3 via Groq)
    ├── Session Manager (Redis)
    └── Database Service (PostgreSQL)
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.10+ |
| **Web Framework** | FastAPI |
| **AI Model** | Llama 3.3 (via Groq API) |
| **Primary Database** | PostgreSQL |
| **Session Cache** | Redis |
| **Vector DB** | ChromaDB (for future RAG) |
| **WhatsApp Gateway** | Twilio API |
| **Tunneling** | Ngrok |
| **ORM** | SQLAlchemy |

## 🚀 Quick Start Guide

### Prerequisites

Before you begin, ensure you have:
- Python 3.10+ installed
- PostgreSQL installed and running
- Redis installed (or Docker for Redis)
- A Twilio account (free)
- A Groq API account (free tier available)
- Ngrok installed (for local development)

### 1. Clone the Repository

```bash
git clone https://github.com/nikhil1127/Hospital_ChatBot.git
cd Hospital_ChatBot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Setup

Create a `.env` file in the root directory:

```env
# AI Model (Groq)
GROQ_API_KEY=your_groq_api_key_here

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/hospital_db
REDIS_URL=redis://localhost:6379/0

# WhatsApp (Twilio) - Optional for local testing
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number

# Server
PORT=8000
```

**Get your Groq API Key:**
1. Visit [console.groq.com](https://console.groq.com/)
2. Create a free account
3. Generate an API key
4. Paste it in the `.env` file

### 4. Database Setup

```bash
# Create the database tables
python -m app.db.init_db

# Seed with sample doctors
python -m app.db.seed
```

**Sample Doctors Added:**
- Dr. Sarah Smith - Cardiology
- Dr. James Wilson - Pediatrics
- Dr. Emily Chen - Neurology
- Dr. Michael Brown - Orthopedics
- Dr. Priya Sharma - Dermatology
- Dr. Robert Taylor - General Medicine

### 5. Start the Server

```bash
python -m app.main
```

You should see: `Uvicorn running on http://0.0.0.0:8000`

### 6. Expose to Internet (Ngrok)

In a **new terminal**:

```bash
ngrok http 8000
```

Copy the `https://xxxx-xxxx.ngrok-free.app` URL.

### 7. Configure Twilio

1. Go to [Twilio Console](https://www.twilio.com/console)
2. Navigate to: **Messaging** → **Try it Out** → **Send a WhatsApp Message**
3. Click **Sandbox Settings**
4. In **"When a message comes in"**, paste:
   ```
   https://your-ngrok-url.ngrok-free.app/whatsapp
   ```
5. Click **Save**

### 8. Test on WhatsApp

1. Save the Twilio Sandbox number to your contacts
2. Send the "join" code shown in your Twilio console
3. Once confirmed, start chatting:
   - *"Hi, I need to book an appointment"*
   - *"Do you have a cardiologist?"*
   - *"I'm feeling dizzy"*

## 📁 Project Structure

```
hospital_bot/
├── app/
│   ├── api/
│   │   └── webhook.py          # WhatsApp webhook endpoint
│   ├── core/
│   │   ├── ai.py               # AI service with Groq/Llama
│   │   ├── session.py          # Redis session management
│   │   └── db_service.py       # Database operations
│   ├── db/
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── session.py          # DB connection
│   │   ├── init_db.py          # DB initialization
│   │   └── seed.py             # Sample data seeder
│   └── main.py                 # FastAPI entry point
├── data/                       # Knowledge base files
├── .env                        # Environment variables (not in git)
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── test_whatsapp.py            # Test script
└── README.md                   # This file
```

## 🧪 Testing Without WhatsApp

You can test the bot without setting up WhatsApp:

```bash
python test_whatsapp.py
```

This sends a simulated WhatsApp message to your server and prints the AI response.

## 💬 Conversation Flows

### 1. Doctor Discovery
```
User: "I need a heart doctor"
Bot: "We have Dr. Sarah Smith in Cardiology with 15 years experience. 
      Fee: ₹500. Available: Mon, Wed. Would you like to book?"
```

### 2. Appointment Booking
```
User: "Book Dr. Smith for tomorrow"
Bot: "Please confirm:
      • Doctor: Dr. Sarah Smith
      • Department: Cardiology
      • Date: [Tomorrow's Date]
      • Fee: ₹500
      Reply CONFIRM to proceed or CANCEL to abort."
```

### 3. Emergency Detection
```
User: "I have chest pain"
Bot: "🚨 This could be serious. Please call emergency services 
      (112/911) immediately or go to the nearest ER. 
      Do not wait for an appointment."
```

## 🔐 Security Features

- **PII Protection**: API keys stored in `.env` (excluded from git)
- **Medical Disclaimer**: AI explicitly states it cannot diagnose
- **Emergency Protocols**: Automatically redirects emergencies to 112/911
- **No Data Retention**: Conversations stored temporarily (30-min Redis TTL)

## 🚧 Known Limitations

- Currently uses Twilio Sandbox (limited to verified numbers in production)
- Requires Ngrok for local development (tunnel expires every 2 hours on free plan)
- AI responses depend on Groq API availability
- Database is local PostgreSQL (cloud DB recommended for production)

## 🚀 Deployment Options

### Option 1: Cloud VPS (Recommended)
- Deploy to AWS EC2 / Azure VM / DigitalOcean Droplet
- Use a proper domain with SSL
- Remove Ngrok, use direct webhook URL

### Option 2: Railway/Render
- Connect GitHub repo to Railway or Render
- Auto-deploy on git push
- Built-in PostgreSQL and Redis

### Option 3: Docker
```bash
docker-compose up --build
```
*(Dockerfile and docker-compose.yml coming soon)*

## 🛣️ Future Roadmap

- [ ] **RAG Implementation**: Connect to hospital PDFs/Documents
- [ ] **Payment Integration**: Razorpay/Stripe for booking fees
- [ ] **Admin Dashboard**: Web UI to manage doctors and appointments
- [ ] **Multi-language Support**: Hindi, Tamil, Telugu, etc.
- [ ] **SMS Fallback**: SMS notifications for confirmations
- [ ] **Analytics**: Dashboard for patient queries and bookings

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2026 Nikhil

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND...
```

## 🙏 Acknowledgments

- **Groq** for providing fast AI inference
- **Meta** for Llama 3 open-source model
- **Twilio** for WhatsApp Business API
- **FastAPI** for the amazing web framework

## 📞 Support

If you encounter issues:
1. Check the [Issues](../../issues) tab
2. Review the [Troubleshooting](#troubleshooting) section
3. Create a new issue with details

---

**Built with ❤️ for better healthcare access**
