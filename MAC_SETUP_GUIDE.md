# Mac Setup Guide - Hospital Management System

Complete step-by-step instructions to get the system running on your Mac after pulling the code.

---

## Prerequisites Check

First, verify you have these installed:

```bash
# Check Python (3.10 or higher required)
python3 --version

# Check PostgreSQL
psql --version

# Check Redis (optional but recommended)
redis-cli --version

# Check Git
git --version
```

---

## Step 1: Pull the Latest Code

```bash
# Navigate to your project directory
cd ~/projects/Hospital_ChatBot  # or wherever your repo is

# Pull the latest changes
git pull origin master
```

---

## Step 2: Backup Your Existing Database (IMPORTANT!)

```bash
# Create backup of existing database
pg_dump hospital_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup was created
ls -la backup_*.sql
```

---

## Step 3: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Verify activation (should show venv in prompt)
which python
```

---

## Step 4: Install Dependencies

```bash
# Install all required packages
pip install -r requirements_enhanced.txt

# This installs:
# - FastAPI, SQLAlchemy, PostgreSQL adapter
# - Redis client
# - AI/ML libraries (Groq, LangChain)
# - Testing tools (pytest)
# - Date utilities, fuzzy matching, etc.
```

---

## Step 5: Setup Environment Variables

```bash
# Create .env file
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/hospital_db

# Redis (optional - will use memory if not available)
REDIS_URL=redis://localhost:6379/0

# AI Model (Groq)
GROQ_API_KEY=your_groq_api_key_here

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_whatsapp_number

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# Server
PORT=8000
EOF

# Edit the file to add your actual credentials
nano .env  # or use TextEdit, VS Code, etc.
```

---

## Step 6: Start PostgreSQL

```bash
# Start PostgreSQL service
brew services start postgresql@14

# Or if using Postgres.app, just open the app

# Verify connection
psql $DATABASE_URL -c "SELECT 1;"
```

---

## Step 7: Run Database Migration

```bash
# IMPORTANT: Dry run first to see what will happen
python migrate_complete.py --dry-run

# If everything looks good, run the actual migration
python migrate_complete.py --confirm
```

This will:
- Create all new tables (IPD, Insurance, Pharmacy, etc.)
- Preserve existing patient data
- Seed default data (roles, departments, medicines)
- Create sample wards and beds

---

## Step 8: Verify Migration

```bash
# Check tables were created
psql $DATABASE_URL -c "\dt"

# You should see new tables like:
# - wards, beds, admissions
# - insurance_providers, insurance_policies
# - medicines, pharmacy_stock
# - invoices, payments
# - clinical_alerts

# Verify patient data preserved
psql $DATABASE_URL -c "SELECT COUNT(*) FROM patients;"
```

---

## Step 9: (Optional) Start Redis

```bash
# Install Redis if not already installed
brew install redis

# Start Redis
brew services start redis

# Test connection
redis-cli ping
# Should return: PONG
```

---

## Step 10: Run Tests

```bash
# Run all tests
python -m pytest tests/test_complete_system.py -v

# Or run the simple functional test
python test_system_simple.py
```

---

## Step 11: Start the Server

```bash
# Start the complete system
python -m app.main_complete

# You should see output like:
# ============================================================
# 🏥 MEDCARE HOSPITAL MANAGEMENT SYSTEM
# ============================================================
# 📱 WhatsApp Bot:        POST /whatsapp
# 🩺 Doctor Dashboard:    GET  /doctor
# 🏥 Admin Dashboard:     GET  /admin
# 📋 API Documentation:   GET  /api/docs
```

---

## Step 12: Access the System

Open your browser and go to:

```
Admin Dashboard:   http://localhost:8000/admin
Doctor Dashboard:  http://localhost:8000/doctor
API Documentation: http://localhost:8000/api/docs
Health Check:      http://localhost:8000/health
```

---

## Step 13: Test the WhatsApp Bot

The WhatsApp bot should still work! Test it:

1. Send "Hi" to your Twilio WhatsApp number
2. Book an appointment
3. Check that it creates PAT-YYYY-XXXXXX patient ID
4. Verify admin dashboard shows the new patient

---

## Common Issues on Mac

### Issue 1: PostgreSQL Connection Error

```bash
# Error: connection refused
# Solution: Start PostgreSQL
brew services start postgresql@14

# Or create database if missing
createdb hospital_db
```

### Issue 2: psycopg2 Installation Error

```bash
# Error: pg_config not found
# Solution: Install prerequisites
brew install postgresql libpq
export PATH="/opt/homebrew/opt/libpq/bin:$PATH"
pip install psycopg2-binary
```

### Issue 3: Redis Connection Error

```bash
# Error: Connection refused on localhost:6379
# Solution: Redis is optional - system will use in-memory
# Or start Redis: brew services start redis
```

### Issue 4: Port Already in Use

```bash
# Error: Address already in use
# Solution: Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
python -m app.main_complete --port 8001
```

### Issue 5: Permission Denied

```bash
# Error: Permission denied when running migration
# Solution: Make sure you're in the project directory
cd ~/projects/Hospital_ChatBot
source venv/bin/activate
```

---

## Development Workflow

### Daily Development

```bash
# 1. Navigate to project
cd ~/projects/Hospital_ChatBot

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start PostgreSQL (if not auto-starting)
brew services start postgresql@14

# 4. Start Redis (optional)
brew services start redis

# 5. Run server
python -m app.main_complete

# 6. Open browser tabs
copen http://localhost:8000/admin
copen http://localhost:8000/doctor
```

### Making Changes

```bash
# Edit files, then test
python -m pytest tests/test_complete_system.py -v

# Commit changes
git add .
git commit -m "Your commit message"
git push origin master
```

---

## Production Deployment (on Mac)

For production, use Gunicorn:

```bash
# Install gunicorn
pip install gunicorn

# Start with multiple workers
gunicorn app.main_complete:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Run in background
nohup gunicorn app.main_complete:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 > server.log 2>&1 &
```

---

## Useful Commands

```bash
# View server logs
tail -f server.log

# Check database status
psql $DATABASE_URL -c "SELECT COUNT(*) FROM patients;"

# Check Redis
redis-cli info stats

# Restart everything
brew services restart postgresql@14
brew services restart redis
pkill -f "python -m app.main_complete"
python -m app.main_complete

# Database console
psql $DATABASE_URL

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/admin/dashboard
```

---

## Next Steps

1. **Customize for your hospital**: Edit department names, wards, etc. in the migration
2. **Add users**: Create admin accounts in the database
3. **Configure WhatsApp**: Set up Twilio webhook with ngrok
4. **Test workflows**: Run through OPD → IPD → Discharge → Billing flow
5. **Add real data**: Import actual patient data (with consent)

---

## Need Help?

If you encounter issues:

1. Check logs in terminal
2. Verify `.env` credentials
3. Test database connection: `psql $DATABASE_URL`
4. Run functional test: `python test_system_simple.py`
5. Check this guide's "Common Issues" section

---

**You're all set! 🎉**

The complete Hospital Management System with all 31 features is now running on your Mac!
