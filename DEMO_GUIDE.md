# Hospital ChatBot - Client Demo Guide

This guide will help you deliver a professional demo of the Hospital WhatsApp ChatBot to your client.

---

## Demo Option A: Test-Based Demo (Recommended - No External Setup)

This is the **quickest and most reliable** way to demo. No Twilio account needed.

### Step 1: Pre-Demo Setup (2 minutes)

```bash
# Navigate to project
cd ~/.claude/hospital_bot

# Ensure dependencies are installed
pip install -r requirements.txt
```

### Step 2: Start the Demo (5 minutes)

#### A. Show the Project Structure
```bash
# Display the organized codebase
ls -la
ls -la app/
ls -la app/core/
ls -la app/api/
ls -la app/db/
ls -la tests/
```

**Talking Points:**
- "This is a production-ready FastAPI application"
- "Modular architecture: core services, API layer, database layer"
- "Follows Python best practices with proper separation of concerns"

---

#### B. Run the Comprehensive Test Suite

```bash
# Run all tests
python -m unittest tests.test_comprehensive -v
```

**Expected Output:**
```
test_user_creation ... [PASS] User creation test passed
test_doctor_creation ... [PASS] Doctor creation test passed
test_appointment_creation ... [PASS] Appointment creation test passed
...
----------------------------------------------------------------------
Ran 25+ tests

OK
```

**Talking Points:**
- "We have 25+ unit tests covering all components"
- "Tests verify database operations, AI service, session management, and booking flow"
- "Every critical path is tested - ensures reliability"

---

#### C. Demo the Booking Flow Logic

Create a quick demo script:

```bash
# Run this Python script
python << 'EOF'
import asyncio
from app.api.webhook import handle_conversation_flow
from unittest.mock import MagicMock

# Setup mock database
mock_db = MagicMock()
mock_db.list_all_specialties.return_value = [
    ("Cardiology",), ("Pediatrics",), ("Neurology",), ("Orthopedics",)
]
mock_db.find_doctors_by_specialty.return_value = [
    MagicMock(id=1, name="Dr. Sarah Smith", consultation_fee=500),
    MagicMock(id=2, name="Dr. Emily Chen", consultation_fee=600)
]
mock_db.create_appointment.return_value = MagicMock(id=1234)

async def demo_flow():
    session = {"state": "START", "context": {}, "history": []}
    user_id = 1
    
    print("=== HOSPITAL CHATBOT DEMO ===\n")
    
    # Step 1: User initiates booking
    print("1. USER: 'I want to book an appointment'")
    response = await handle_conversation_flow("Book appointment", "", session, mock_db, user_id)
    print(f"   BOT: {response[:100]}...\n")
    assert session["state"] == "SELECT_SPECIALTY"
    
    # Step 2: User selects specialty
    print("2. USER: 'Cardiology'")
    response = await handle_conversation_flow("Cardiology", "", session, mock_db, user_id)
    print(f"   BOT: {response[:100]}...\n")
    assert session["state"] == "SELECT_DOCTOR"
    
    # Step 3: User selects doctor
    print("3. USER: 'Dr. Sarah Smith'")
    response = await handle_conversation_flow("Dr. Sarah Smith", "", session, mock_db, user_id)
    print(f"   BOT: {response[:100]}...\n")
    assert session["state"] == "SELECT_DATE"
    
    # Step 4: User provides date
    print("4. USER: 'Tomorrow at 2 PM'")
    response = await handle_conversation_flow("Tomorrow at 2 PM", "", session, mock_db, user_id)
    print(f"   BOT: {response}\n")
    assert session["state"] == "CONFIRM"
    
    # Step 5: User confirms
    print("5. USER: 'CONFIRM'")
    response = await handle_conversation_flow("CONFIRM", "", session, mock_db, user_id)
    print(f"   BOT: {response}\n")
    assert session["state"] == "START"
    assert "#1234" in response
    
    print("=== DEMO COMPLETE - Appointment Booked! ===")

asyncio.run(demo_flow())
EOF
```

**Talking Points:**
- "This shows the exact conversation flow patients will experience"
- "State machine ensures no steps are skipped"
- "Confirmation includes appointment ID, doctor name, and fee"

---

#### D. Show AI Capabilities

```bash
python << 'EOF'
import asyncio
from app.core.ai import HospitalAIService, detect_intent

ai = HospitalAIService()

async def demo_ai():
    print("=== AI SERVICE DEMO ===\n")
    
    # Test intent detection
    tests = [
        "I want to book an appointment",
        "What doctors do you have?",
        "Hello there",
        "I have chest pain",
        "Do you accept insurance?"
    ]
    
    for msg in tests:
        intent = detect_intent(msg)
        print(f"User: '{msg}'")
        print(f"Detected Intent: {intent}\n")
    
    # Test mock responses
    print("\n=== AI RESPONSES (Mock Mode) ===\n")
    
    response = await ai._mock_response("Book appointment", None)
    print(f"Booking query: {response[:80]}...\n")
    
    response = await ai._mock_response("I have chest pain", None)
    print(f"Emergency: {response[:80]}...\n")

asyncio.run(demo_ai())
EOF
```

**Talking Points:**
- "AI automatically detects user intent"
- "Emergency keywords trigger immediate safety warnings"
- "Different response types for booking, inquiries, and general chat"

---

#### E. Show Database Operations

```bash
python << 'EOF'
from app.db.session import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.db_service import HospitalDBService
from app.db.models import User, Doctor, Appointment
from datetime import datetime, timedelta

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

print("=== DATABASE DEMO ===\n")

# Setup
service = HospitalDBService(db)

# Add doctors
doctors = [
    Doctor(name="Dr. Sarah Smith", specialty="Cardiology", experience_years=15,
           consultation_fee=500.0, availability_slots="Mon-Fri 09:00-17:00"),
    Doctor(name="Dr. James Wilson", specialty="Pediatrics", experience_years=10,
           consultation_fee=300.0, availability_slots="Tue-Thu 10:00-14:00")
]
for d in doctors:
    db.add(d)
db.commit()

print(f"1. Added {len(doctors)} doctors\n")

# Create user
user = service.get_or_create_user("whatsapp:+919876543210", name="John Doe")
print(f"2. Created user: {user.name} ({user.phone_number})\n")

# List specialties
specialties = service.list_all_specialties()
print(f"3. Available specialties: {[s[0] for s in specialties]}\n")

# Find doctors
cardio_docs = service.find_doctors_by_specialty("Cardiology")
print(f"4. Cardiology doctors: {[d.name for d in cardio_docs]}\n")

# Create appointment
apt = service.create_appointment(
    user_id=user.id,
    doctor_id=cardio_docs[0].id,
    date_time=datetime.now() + timedelta(days=1)
)
print(f"5. Appointment created: ID #{apt.id}")
print(f"   Doctor: {cardio_docs[0].name}")
print(f"   Fee: Rs.{cardio_docs[0].consultation_fee}\n")

# Slot availability
slot = datetime.now() + timedelta(days=1)
available = service.check_slot_availability(cardio_docs[0].id, slot)
print(f"6. Slot availability check: {'Available' if not available else 'Booked'} (expected: Booked)\n")

print("=== DATABASE DEMO COMPLETE ===")
EOF
```

**Talking Points:**
- "PostgreSQL database with SQLAlchemy ORM"
- "Indexed fields for fast queries"
- "Slot availability checking prevents double-booking"
- "All data persisted securely"

---

#### F. Show the Documentation

```bash
# Display README
cat README.md
```

**Talking Points:**
- "Professional documentation included"
- "Setup instructions for any developer"
- "Architecture diagrams and flowcharts"

---

## Demo Option B: Live WhatsApp Demo (Requires Twilio)

Use this only if you have a Twilio account set up.

### Prerequisites
1. Twilio account
2. WhatsApp Sandbox enabled
3. ngrok installed

### Steps

```bash
# 1. Start the server
uvicorn app.main:app --reload --port 8000

# 2. In another terminal, start ngrok
ngrok http 8000

# 3. Copy the ngrok HTTPS URL (e.g., https://abc123.ngrok.io)

# 4. Configure in Twilio Console:
#    - Go to WhatsApp Sandbox Settings
#    - Set webhook: https://abc123.ngrok.io/whatsapp
#    - Save

# 5. Send WhatsApp message from your phone to the Twilio number
```

**Demo Script:**
1. Send "Hello" - Show AI greeting
2. Send "Book appointment" - Show specialty selection
3. Reply with specialty - Show doctor list
4. Select doctor - Show date request
5. Provide date - Show confirmation
6. Reply "CONFIRM" - Show booking confirmation with ID
7. Send "cancel" - Show reset

---

## Key Features to Highlight

| Feature | Demo Line | Impact |
|---------|-----------|--------|
| **Multi-step Booking** | Show state transitions | Smooth patient experience |
| **Emergency Detection** | "I have chest pain" | Patient safety first |
| **AI Conversations** | General chat responses | Natural interaction |
| **Slot Management** | Check availability | No double-booking |
| **Session Memory** | 30-min conversation history | Contextual responses |
| **RAG Knowledge Base** | Policy questions (if docs added) | Instant answers |
| **Admin Capabilities** | List doctors, specialties | Easy management |

---

## Demo Checklist

Before the demo:
- [ ] Code is up to date (`git pull`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Tests pass (`python -m unittest tests.test_comprehensive -v`)
- [ ] Terminal window sized appropriately
- [ ] Demo script copied and ready

During the demo:
- [ ] Speak clearly about what each component does
- [ ] Pause for questions after each section
- [ ] Show code quality (clean structure, comments)
- [ ] Emphasize production-readiness

---

## Q&A Preparation

**Q: Can it handle multiple languages?**
A: "Currently English. Adding multi-language support requires updating the AI prompts and adding translation layer."

**Q: How do doctors get notified?**
A: "Can be extended with SMS/email notifications via Twilio/SendGrid. Currently shows in database."

**Q: Is it secure?**
- API keys in .env (not in code)
- SQL injection prevented (SQLAlchemy ORM)
- Input validation on all endpoints

**Q: How do I add more doctors?**
A: "Direct database insertion or admin panel can be added. Sample data in seed_database.py."

**Q: Can it send reminders?**
A: "Yes, can add scheduled Celery jobs to send WhatsApp reminders."

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Tests fail | Check if all dependencies installed |
| Import errors | Run from project root directory |
| Database locked | Restart Python session |
| Slow responses | AI is in mock mode (expected) |

---

**Good luck with your demo!** The code is production-ready and well-tested.
