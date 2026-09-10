# Hospital ChatBot - Mac Setup Guide

Complete Mac-specific setup instructions.

---

## Step 1: Open Terminal in VS Code

1. Open VS Code
2. Press `` Cmd+` `` (backtick key - left of number 1)
3. Or go to menu: `Terminal > New Terminal`

---

## Step 2: Check Python Installation

```bash
python3 --version
```

**If you see:** `Python 3.8.x` or higher → **Proceed to Step 3**

**If you see:** `command not found` → **Install Python:**

```bash
# Install Homebrew first (package manager)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install Python
brew install python

# Verify
python3 --version
```

---

## Step 3: Create Virtual Environment (Recommended)

```bash
# Navigate to project folder (if not already there)
cd ~/path/to/hospital_bot

# Create virtual environment
python3 -m venv venv

# Activate it (you'll see (venv) in prompt)
source venv/bin/activate
```

**Your prompt should now show:** `(venv) username@macbook hospital_bot %`

---

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**This will take 2-3 minutes.** You'll see progress bars downloading packages.

**Expected final output:**
```
Successfully installed fastapi-0.x.x uvicorn-0.x.x ...
```

---

## Step 5: Create Environment File

```bash
# Copy the example file
cp .env.example .env
```

**Edit the .env file in VS Code:**

1. Click on `.env` in the Explorer (left sidebar)
2. Replace contents with:

```env
# Database
DATABASE_URL=sqlite:///./hospital.db

# Redis (optional - uses memory if not set)
REDIS_HOST=localhost
REDIS_PORT=6379

# AI Service (leave empty for mock mode, or get key from groq.com)
GROQ_API_KEY=

# Twilio (optional for now)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

3. Save (Cmd+S)

---

## Step 6: Initialize Database

```bash
# Create database tables
python3 << 'EOF'
from app.db.session import Base, engine
Base.metadata.create_all(bind=engine)
print("✅ Database created!")
EOF
```

You should see: `✅ Database created!`

---

## Step 7: Add Sample Data (Optional but Recommended)

```bash
python3 << 'EOF'
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

print(f"✅ Added {len(doctors)} doctors and 1 test user!")
db.close()
EOF
```

---

## Step 8: Run the Tests

```bash
python3 -m unittest tests.test_comprehensive -v
```

**Should show:**
```
test_user_creation ... [PASS] User creation test passed
test_doctor_creation ... [PASS] Doctor creation test passed
...
----------------------------------------------------------------------
Ran 25 tests

OK
```

---

## Step 9: Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

**Should show:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Keep this terminal running!**

---

## Step 10: Test the API

Open a **NEW terminal tab** (Cmd+Shift+`) and run:

```bash
# Test 1: Check if server is running
curl http://localhost:8000/docs
```

Should return HTML (Swagger UI page).

```bash
# Test 2: Send a test message
curl -X POST http://localhost:8000/whatsapp \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+919876543210" \
  -d "Body=Book appointment"
```

**Should return:**
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

---

## Step 11: Full Conversation Test

Copy and run this complete test:

```bash
python3 << 'EOF'
import asyncio
from app.api.webhook import handle_conversation_flow
from unittest.mock import MagicMock

mock_db = MagicMock()
mock_db.list_all_specialties.return_value = [("Cardiology",), ("Pediatrics",), ("Neurology",)]
mock_db.find_doctors_by_specialty.return_value = [
    MagicMock(id=1, name="Dr. Sarah Smith", consultation_fee=500),
    MagicMock(id=2, name="Dr. Emily Chen", consultation_fee=600)
]
mock_db.create_appointment.return_value = MagicMock(id=123)

async def demo():
    session = {"state": "START", "context": {}, "history": []}
    user_id = 1
    
    print("=== HOSPITAL CHATBOT DEMO ===\n")
    
    # Step 1
    print("1. USER: 'I want to book an appointment'")
    response = await handle_conversation_flow("Book appointment", "", session, mock_db, user_id)
    print(f"   BOT: {response[:80]}...")
    print(f"   STATE: {session['state']}\n")
    
    # Step 2
    print("2. USER: 'Cardiology'")
    response = await handle_conversation_flow("Cardiology", "", session, mock_db, user_id)
    print(f"   BOT: {response[:80]}...")
    print(f"   STATE: {session['state']}\n")
    
    # Step 3
    print("3. USER: 'Dr. Sarah Smith'")
    response = await handle_conversation_flow("Dr. Sarah Smith", "", session, mock_db, user_id)
    print(f"   BOT: {response[:80]}...")
    print(f"   STATE: {session['state']}\n")
    
    # Step 4
    print("4. USER: 'Tomorrow at 2 PM'")
    response = await handle_conversation_flow("Tomorrow at 2 PM", "", session, mock_db, user_id)
    print(f"   BOT: {response}")
    print(f"   STATE: {session['state']}\n")
    
    # Step 5
    print("5. USER: 'CONFIRM'")
    response = await handle_conversation_flow("CONFIRM", "", session, mock_db, user_id)
    print(f"   BOT: {response}")
    print(f"   STATE: {session['state']}\n")
    
    print("✅ DEMO COMPLETE - Appointment Booked Successfully!")

asyncio.run(demo())
EOF
```

---

## Common Mac Issues & Fixes

### Issue 1: "pip: command not found"
**Fix:**
```bash
python3 -m pip install -r requirements.txt
```

### Issue 2: "Permission denied"
**Fix:**
```bash
pip install --user -r requirements.txt
```

### Issue 3: "SSL certificate verify failed"
**Fix:**
```bash
# Install certificates
/Applications/Python\ 3.x/Install\ Certificates.command

# Or bypass for now (not recommended for production)
pip install --trusted-host pypi.org --trusted-host pypi.python.org -r requirements.txt
```

### Issue 4: "Port 8000 already in use"
Find and kill the process:
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process (replace <PID> with the number shown)
kill -9 <PID>
```

Or use a different port:
```bash
uvicorn app.main:app --reload --port 8080
```

### Issue 5: Cannot activate virtual environment
**Fix:** If you see "permission denied" on `source venv/bin/activate`:
```bash
# Make it executable
chmod +x venv/bin/activate

# Then try again
source venv/bin/activate
```

### Issue 6: "ModuleNotFoundError: No module named 'app'"
**Fix:** You're in the wrong directory
```bash
# Check current directory
pwd

# Should show: /Users/yourname/.../hospital_bot
# If not, navigate there:
cd ~/path/to/hospital_bot
```

---

## VS Code Mac Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Terminal | `` Cmd+` `` |
| New Terminal Tab | `Cmd+Shift+` ` |
| Command Palette | `Cmd+Shift+P` |
| Quick Open File | `Cmd+P` |
| Save File | `Cmd+S` |
| Start Debugging | `F5` |

---

## Quick Commands Reference

```bash
# Start server
uvicorn app.main:app --reload --port 8000

# Run tests
python3 -m unittest tests.test_comprehensive -v

# View database
sqlite3 hospital.db ".tables"

# Check what's running on port 8000
lsof -i :8000

# Kill Python processes
pkill -f uvicorn

# Deactivate virtual environment
deactivate
```

---

## Troubleshooting Checklist

If something doesn't work:

1. [ ] Virtual environment activated? (see `(venv)` in prompt)
2. [ ] In correct folder? (`pwd` should show `hospital_bot`)
3. [ ] Dependencies installed? (`pip list | grep fastapi`)
4. [ ] Server running? (check terminal with uvicorn)
5. [ ] Port 8000 free? (`lsof -i :8000`)

---

## Next Steps

1. ✅ Get Groq API key: https://console.groq.com/keys (optional - mock mode works)
2. ✅ Set up Twilio: https://twilio.com (optional for testing)
3. ✅ Read DEMO_GUIDE.md for client presentation

**You're all set!** The system is running on your Mac.
