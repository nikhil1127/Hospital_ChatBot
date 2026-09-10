# Hospital ChatBot - Fresh System Setup Guide

Complete steps to set up and run the project on a new machine.

---

## Step 1: Prerequisites Check

Make sure you have installed:

```bash
# Check Python (needs 3.8+)
python --version

# Check pip
pip --version

# Check if git is installed (optional)
git --version
```

**If Python is not installed:**
- Download from https://python.org/downloads
- **Windows:** Check "Add Python to PATH" during installation
- **Mac:** `brew install python3`
- **Linux:** `sudo apt install python3 python3-pip`

---

## Step 2: Install Dependencies

Open VS Code terminal (`` Ctrl+` ``) and run:

```bash
# Navigate to project folder (if not already there)
cd hospital_bot

# Install all dependencies
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi uvicorn python-dotenv ...
```

### If you get "pip is not recognized" (Windows):
```bash
python -m pip install -r requirements.txt
```

### Common Installation Issues:

| Issue | Solution |
|-------|----------|
| `Permission denied` | Add `--user` flag: `pip install --user -r requirements.txt` |
| `Microsoft Visual C++ required` | Install Build Tools from https://visualstudio.microsoft.com/visual-cpp-build-tools/ |
| Package conflicts | Use virtual environment (see Step 2A below) |

---

## Step 2A: Using Virtual Environment (Recommended)

To avoid package conflicts:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

You'll see `(venv)` in your terminal prompt when active.

---

## Step 3: Configure Environment Variables

Create `.env` file in the project root:

```bash
# Windows (PowerShell):
Copy-Item .env.example .env

# Mac/Linux:
cp .env.example .env
```

Then edit `.env` with VS Code:

```env
# Database (SQLite for testing - no setup needed)
DATABASE_URL=sqlite:///./hospital.db

# For PostgreSQL (production):
# DATABASE_URL=postgresql://user:password@localhost/hospital_db

# Redis (optional - uses memory if not available)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# AI Service
# Get free API key from: https://console.groq.com/keys
GROQ_API_KEY=your_groq_api_key_here

# Twilio (optional for testing)
# TWILIO_ACCOUNT_SID=your_account_sid
# TWILIO_AUTH_TOKEN=your_auth_token
# TWILIO_PHONE_NUMBER=whatsapp:+1234567890
```

**For initial testing, you only need:**
- `DATABASE_URL=sqlite:///./hospital.db`
- Leave `GROQ_API_KEY` empty (uses mock mode)

---

## Step 4: Initialize the Database

```bash
# Create database tables
python -c "from app.db.session import Base, engine; Base.metadata.create_all(bind=engine); print('Database created!')"
```

**Expected output:**
```
Database created!
```

This creates `hospital.db` file in your project folder.

---

## Step 5: Seed Test Data (Optional)

Add sample doctors and users for testing:

```bash
python << 'EOF'
from app.db.session import SessionLocal
from app.db.models import Doctor, User
from app.core.db_service import HospitalDBService

db = SessionLocal()
service = HospitalDBService(db)

# Add doctors
doctors = [
    Doctor(name="Dr. Sarah Smith", specialty="Cardiology", experience_years=15,
           consultation_fee=500.0, availability_slots="Mon-Fri 09:00-17:00", is_available=True),
    Doctor(name="Dr. James Wilson", specialty="Pediatrics", experience_years=10,
           consultation_fee=300.0, availability_slots="Tue-Thu 10:00-14:00", is_available=True),
    Doctor(name="Dr. Emily Chen", specialty="Neurology", experience_years=12,
           consultation_fee=600.0, availability_slots="Mon-Wed 15:00-18:00", is_available=True),
]
db.add_all(doctors)
db.commit()

# Create test user
service.get_or_create_user("whatsapp:+919876543210", name="Test Patient")

print(f"Added {len(doctors)} doctors and 1 test user!")
db.close()
EOF
```

---

## Step 6: Run the Tests

Verify everything works:

```bash
# Run all tests
python -m unittest tests.test_comprehensive -v
```

**Expected output:**
```
test_user_creation ... [PASS] User creation test passed
test_doctor_creation ... [PASS] Doctor creation test passed
...
----------------------------------------------------------------------
Ran 25 tests

OK
```

### If tests fail:

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | You're not in the right folder. `cd` to project root |
| `ImportError` | Dependencies not installed: `pip install -r requirements.txt` |
| Database errors | Delete `hospital.db` and recreate (Step 4) |

---

## Step 7: Start the Server

```bash
# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Server is running if you see:
- `Uvicorn running on http://127.0.0.1:8000`

### Test the server:

Open browser or use curl:
```bash
curl http://localhost:8000/docs
```

You should see the **Swagger UI** (API documentation).

---

## Step 8: Test the Webhook (Without WhatsApp)

Use this curl command to simulate a WhatsApp message:

```bash
curl -X POST http://localhost:8000/whatsapp \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+919876543210" \
  -d "Body=Book appointment"
```

**Expected response (XML):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Which specialty do you need?

• Cardiology
• Pediatrics
• Neurology

Please type the specialty name.</Message>
</Response>
```

### Continue the conversation:

```bash
# Step 2: Select specialty
curl -X POST http://localhost:8000/whatsapp \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+919876543210" \
  -d "Body=Cardiology"
```

---

## Step 9: VS Code Configuration

### Recommended Extensions

Install these VS Code extensions (Ctrl+Shift+X):

| Extension | Purpose |
|-----------|---------|
| Python | Python language support |
| Pylance | Better Python IntelliSense |
| Thunder Client | API testing (like Postman) |
| SQLite Viewer | View database file |
| GitLens | Git integration |

### Launch Configuration

Create `.vscode/launch.json` for debugging:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--port", "8000"],
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

Now you can press **F5** to start debugging!

---

## Step 10: Quick Test Script

Run this full demo in one command:

```bash
python << 'EOF'
import asyncio
from app.api.webhook import handle_conversation_flow
from unittest.mock import MagicMock

mock_db = MagicMock()
mock_db.list_all_specialties.return_value = [("Cardiology",), ("Pediatrics",)]
mock_db.find_doctors_by_specialty.return_value = [
    MagicMock(id=1, name="Dr. Sarah Smith", consultation_fee=500)
]
mock_db.create_appointment.return_value = MagicMock(id=123)

async def demo():
    session = {"state": "START", "context": {}, "history": []}
    
    tests = [
        ("Book appointment", "SELECT_SPECIALTY"),
        ("Cardiology", "SELECT_DOCTOR"),
        ("Dr. Sarah Smith", "SELECT_DATE"),
        ("Tomorrow 2pm", "CONFIRM"),
        ("CONFIRM", "START")
    ]
    
    print("=== FULL CONVERSATION FLOW TEST ===\n")
    for msg, expected_state in tests:
        print(f"User: {msg}")
        response = await handle_conversation_flow(msg, "", session, mock_db, 1)
        print(f"Bot: {response[:80]}...")
        print(f"State: {session['state']} (expected: {expected_state})")
        assert session["state"] == expected_state, f"State mismatch!"
        print()
    
    print("✅ All tests passed! System is working correctly.")

asyncio.run(demo())
EOF
```

---

## Troubleshooting Common Issues

### Issue 1: "No module named 'app'"

**Cause:** Running from wrong directory

**Fix:**
```bash
# Make sure you're in project root
pwd  # Should show .../hospital_bot

# Or add to PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%CD%  # Windows
export PYTHONPATH=$PWD:$PYTHONPATH  # Mac/Linux
```

### Issue 2: Port 8000 already in use

**Fix:**
```bash
# Use different port
uvicorn app.main:app --reload --port 8080
```

### Issue 3: Database is locked (Windows)

**Fix:** Close all Python processes and try again:
```bash
# Windows: Check Task Manager for Python processes
# Then delete and recreate database:
del hospital.db
python -c "from app.db.session import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Issue 4: Uvicorn not found

**Fix:**
```bash
pip install uvicorn --upgrade
```

### Issue 5: Cannot import name 'SessionManager'

**Fix:** Make sure `app/core/session.py` exists:
```bash
ls app/core/  # Should show session.py
```

If missing, re-clone the repository.

---

## Quick Reference Commands

```bash
# Start server
uvicorn app.main:app --reload --port 8000

# Run tests
python -m unittest tests.test_comprehensive -v

# Check database
python -c "
from app.db.session import SessionLocal
from app.db.models import Doctor
db = SessionLocal()
print([d.name for d in db.query(Doctor).all()])
"

# View API docs
open http://localhost:8000/docs  # Mac
start http://localhost:8000/docs  # Windows
```

---

## Next Steps After Setup

1. ✅ Get GROQ API key: https://console.groq.com/keys
2. ✅ Set up Twilio (if needed): https://twilio.com
3. ✅ Add hospital documents to `data/documents/` for RAG
4. ✅ Deploy to cloud (Heroku, Railway, etc.)

---

**Need help?** Check the `DEMO_GUIDE.md` for feature demonstrations.
