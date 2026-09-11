# 🏥 Hospital Management System - Enhancement Guide

This guide helps you enhance your existing WhatsApp bot into a complete Hospital Management System with EHR, Doctor Dashboards, and Patient Portal.

## 📋 What's Been Added

### 1. **Enhanced Database Schema** (`app/db/models.py`)
- ✅ Patient Master Index (EMPI)
- ✅ Complete Patient Demographics
- ✅ Medical Encounters (OPD, Emergency, Follow-up)
- ✅ Vitals Tracking
- ✅ Prescriptions with Medications
- ✅ Laboratory Orders & Results
- ✅ Audit Logging (HIPAA compliant)
- ✅ Role-Based Access Control (RBAC)

### 2. **Enhanced DB Service** (`app/core/enhanced_db_service.py`)
- ✅ EMPI Duplicate Detection
- ✅ Patient Timeline Generation
- ✅ Doctor Dashboard Stats
- ✅ Token-based OPD Queue
- ✅ Appointment Scheduling with Slots
- ✅ Consultation Workflows

### 3. **Doctor Dashboard** (`app/api/dashboard.py` + `main_enhanced.py`)
- ✅ Real-time Patient Queue
- ✅ Patient Summary View
- ✅ Consultation Form (Vitals, Diagnosis, Prescription)
- ✅ Patient Timeline Sidebar
- ✅ AI-Powered Summaries
- ✅ Rx & Lab Order Generation

### 4. **Admin Dashboard APIs** (`app/api/dashboard.py`)
- ✅ Hospital-wide Statistics
- ✅ Department Stats
- ✅ Pending Lab Orders
- ✅ Patient Search

### 5. **Patient Portal APIs** (`app/api/dashboard.py`)
- ✅ Patient Registration with EMPI
- ✅ Appointment History
- ✅ Lab Results View
- ✅ Timeline

---

## 🚀 Migration Steps

### Step 1: Backup Your Database
```bash
# PostgreSQL backup
pg_dump hospital_db > hospital_db_backup_$(date +%Y%m%d).sql
```

### Step 2: Install New Dependencies
```bash
pip install -r requirements_enhanced.txt
```

### Step 3: Run Database Migration
```bash
# This will:
# 1. Create new tables
# 2. Migrate existing users to patients
# 3. Add enhanced columns to existing tables
# 4. Seed default data (roles, departments)

python -m app.db.migrate_to_enhanced --confirm
```

### Step 4: Update Your .env File
```env
# AI Model (Groq)
GROQ_API_KEY=your_groq_api_key

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/hospital_db
REDIS_URL=redis://localhost:6379/0

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_whatsapp_number

# Security
SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Step 5: Seed Enhanced Data
```bash
# Add sample departments, enhanced doctors, etc.
python -m app.db.seed_enhanced
```

### Step 6: Test the Enhanced System

#### Test WhatsApp Bot (Should Still Work)
```bash
# Start the server
python -m app.main_enhanced

# Test WhatsApp - it should continue working with new features:
- Patient registration now adds full demographics
- Appointments include tokens
- Follow-up with patient records
```

#### Test Doctor Dashboard
```
1. Open: http://localhost:8000/doctor
2. You should see the Doctor Dashboard
3. Book an appointment via WhatsApp
4. See it appear in the queue
5. Click on patient to start consultation
```

#### Test Admin APIs
```bash
# Get dashboard stats
curl http://localhost:8000/dashboard/admin/stats

# Get today's overview
curl http://localhost:8000/dashboard/admin/today

# Search patients
curl "http://localhost:8000/dashboard/search/patients?q=Rahul"
```

---

## 🏗️ Project Structure After Enhancement

```
hospital_bot/
├── app/
│   ├── api/
│   │   ├── webhook.py              # WhatsApp webhook (unchanged)
│   │   └── dashboard.py            # NEW: Doctor/Admin/Patient APIs
│   ├── core/
│   │   ├── ai.py                   # AI service (unchanged)
│   │   ├── session.py              # Redis session (unchanged)
│   │   ├── db_service.py           # Original DB service
│   │   └── enhanced_db_service.py  # NEW: Complete DB service
│   ├── db/
│   │   ├── models.py               # UPDATE: Enhanced models
│   │   ├── session.py              # DB connection (unchanged)
│   │   ├── init_db.py              # DB initialization
│   │   ├── seed.py                 # Original seed
│   │   ├── migrate_to_enhanced.py  # NEW: Migration script
│   │   └── seed_enhanced.py        # NEW: Enhanced seed data
│   ├── main.py                     # Original FastAPI app
│   └── main_enhanced.py            # NEW: Enhanced FastAPI app
├── data/                           # Knowledge base (unchanged)
├── requirements.txt                # Original requirements
├── requirements_enhanced.txt       # NEW: Enhanced requirements
└── ENHANCEMENT_GUIDE.md           # This file
```

---

## 📱 Feature Integration: WhatsApp + Dashboard

### Patient Registration Flow
```
1. Patient messages on WhatsApp
2. Bot detects new patient
3. Old: Just saves name + phone
4. NEW: Creates full patient record with generated Patient ID (PAT-YYYY-XXXXXX)
5. NEW: Can collect: DOB, Blood Group, Address, Emergency Contact
```

### Appointment Booking Flow
```
1. WhatsApp: "Book cardiology appointment"
2. Bot guides through doctor selection
3. NEW: Generates token number for OPD
4. NEW: Creates Medical Encounter on check-in
5. Doctor sees patient in queue on dashboard
6. Doctor clicks patient - loads full history
7. Doctor completes consultation
8. Rx & Lab orders generated
9. Patient gets notification on WhatsApp
```

### Follow-up Flow
```
1. Existing patient messages
2. Bot retrieves patient ID by phone
3. Bot shows patient's last visit
4. "Dr. Smith saw you on 2026-09-10 for chest pain"
5. Easy follow-up booking
```

---

## 🔐 Security Considerations

### Implemented
- ✅ Audit logging for all patient data access
- ✅ Role-based access control
- ✅ Patient data encryption in transit (HTTPS)

### TODO for Production
```python
# Add to dashboard.py routes:

# 1. JWT Authentication
depends = [Depends(get_current_user)]

# 2. Patient Authorization Check
def verify_patient_access(doctor_id: int, patient_id: str, db: Session):
    # Check if doctor is assigned to this patient
    # or if patient is in doctor's queue
    pass

# 3. Rate Limiting
# Add to main_enhanced.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter

# 4. Data Masking for non-privileged users
# Don't show full SSN, etc.
```

---

## 🎯 Usage Examples

### Register Patient via API
```bash
curl -X POST http://localhost:8000/dashboard/patient/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Rahul",
    "last_name": "Sharma",
    "date_of_birth": "1995-01-12",
    "gender": "male",
    "blood_group": "O+",
    "primary_phone": "+919876543210",
    "emergency_name": "Sunita Sharma",
    "emergency_relationship": "Mother",
    "emergency_phone": "+919876543211"
  }'
```

Response:
```json
{
  "success": true,
  "patient_id": "PAT-2026-000001",
  "name": "Rahul Sharma"
}
```

### Book Appointment
```bash
curl -X POST http://localhost:8000/dashboard/doctor/1/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PAT-2026-000001",
    "date": "2026-09-15",
    "time": "10:00",
    "chief_complaint": "Chest pain"
  }'
```

### Get Patient Timeline
```bash
curl http://localhost:8000/dashboard/patient/PAT-2026-000001
```

Response:
```json
{
  "patient": {
    "patient_id": "PAT-2026-000001",
    "name": "Rahul Sharma",
    "age": 31,
    "blood_group": "O+"
  },
  "upcoming_appointments": [...],
  "timeline": [
    {
      "type": "encounter",
      "date": "2026-09-11T10:00:00",
      "title": "OPD - Dr. Sarah Smith",
      "details": {
        "chief_complaint": "Chest pain",
        "diagnosis": "Hypertension"
      }
    }
  ]
}
```

---

## 🔧 Customization

### Add New Department
```python
# In admin dashboard or via seed script
new_dept = Department(
    name="Oncology",
    code="ONCO",
    is_active=True
)
db.add(new_dept)
db.commit()
```

### Configure Doctor Schedule
```json
{
  "weekly_schedule": {
    "monday": ["09:00", "09:30", "10:00", "10:30", "11:00"],
    "tuesday": ["09:00", "09:30", "10:00"],
    "wednesday": [],
    "thursday": ["09:00", "09:30", "10:00", "10:30"],
    "friday": ["09:00", "09:30", "10:00"],
    "saturday": ["10:00", "10:30"],
    "sunday": []
  },
  "slot_duration_minutes": 30
}
```

### Add Custom Alert Rules
```python
# In enhanced_db_service.py

def _generate_patient_alerts(self, patient, encounter):
    alerts = []

    # Your custom rules
    if encounter and encounter.vital_bp:
        try:
            sys, dia = encounter.vital_bp.split("/")
            if int(sys) > 180 or int(dia) > 110):
                alerts.append("🚨 CRITICAL: Hypertensive crisis!")
        except:
            pass

    # Drug interaction check
    if patient.current_medications:
        meds = patient.current_medications.lower()
        if "warfarin" in meds and "aspirin" in meds:
            alerts.append("⚠️ Drug interaction: Warfarin + Aspirin")

    return alerts
```

---

## 🐛 Troubleshooting

### Migration Fails
```bash
# Check if you have existing data that conflicts
# Option 1: Reset database (DELETES ALL DATA)
dropdb hospital_db
createdb hospital_db
python -m app.db.init_db
python -m app.db.seed

# Option 2: Manual migration
# Look at the error and fix specific conflicts
```

### Dashboard Not Loading
```bash
# Check if server is running on correct port
curl http://localhost:8000/doctor

# Check browser console for JavaScript errors
# Ensure doctor ID 1 exists in database
```

### WhatsApp Bot Stopped Working
```bash
# Check webhook is still responding
curl -X POST http://localhost:8000/whatsapp \
  -d "From=whatsapp:+1234567890" \
  -d "Body=hello"

# Check database connection
# Check Redis connection
```

---

## 🚀 Production Deployment

### 1. Update Configuration
```env
# Production database
DATABASE_URL=postgresql://hospital_user:strong_password@db.hospital.internal:5432/hospital_prod

# Production Redis
REDIS_URL=redis://redis.hospital.internal:6379/0

# Strong secret key
SECRET_KEY=$(openssl rand -hex 32)

# Disable debug
DEBUG=false
```

### 2. Database Setup
```bash
# Run migrations
python -m app.db.migrate_to_enhanced --confirm

# Create indexes for performance
psql $DATABASE_URL -f app/db/production_indexes.sql
```

### 3. Start Services
```bash
# Option 1: Direct
python -m app.main_enhanced

# Option 2: With Gunicorn (recommended)
gunicorn app.main_enhanced:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# Option 3: Docker
docker-compose up -d
```

### 4. Configure Twilio Webhook
```
WhatsApp Webhook URL: https://yourdomain.com/whatsapp
```

### 5. SSL/HTTPS
```bash
# Use Let's Encrypt
certbot --nginx -d yourdomain.com
```

---

## 📊 Performance Considerations

### Database Indexes (Optional)
```sql
-- Add to production_indexes.sql
CREATE INDEX idx_patients_phone ON patients(primary_phone);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_doctor_date ON appointments(doctor_id, appointment_date);
CREATE INDEX idx_encounters_patient ON medical_encounters(patient_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
```

### Redis Caching
```python
# Cache patient summaries
@cache.memoize(timeout=300)
def get_patient_summary(self, patient_id: str):
    ...
```

---

## 📞 Support

If you encounter issues:

1. Check logs: `tail -f app.log`
2. Verify database: `psql $DATABASE_URL -c "\\dt"`
3. Test APIs: `curl http://localhost:8000/dashboard/admin/stats`
4. Check migrations: `python -m app.db.migrate_to_enhanced --dry-run`

---

## ✅ Success Checklist

After migration, verify:

- [ ] WhatsApp bot still responds to messages
- [ ] New patient registration generates PAT-YY-XXXXXX ID
- [ ] Doctor dashboard loads at /doctor
- [ ] Patient queue shows appointments
- [ ] Clicking patient loads consultation form
- [ ] Saving consultation creates encounter
- [ ] Patient timeline shows visit history
- [ ] Admin stats API returns data
- [ ] Lab orders can be created

---

**Built with ❤️ for better healthcare**
