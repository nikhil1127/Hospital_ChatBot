from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime
from app.api.webhook import router as webhook_router
from app.db.session import get_db
from app.db.models import Appointment, User, Doctor

app = FastAPI(title="Multispeciality Hospital Bot")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include the webhook routes
app.include_router(webhook_router)

@app.get("/")
async def root():
    return {"message": "Hospital Bot Server is running!"}

@app.get("/admin")
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """
    Admin dashboard to view all appointments
    """
    # Get all appointments with patient and doctor info
    appointments = db.query(Appointment).order_by(Appointment.appointment_date.desc()).all()

    # Format appointments for display
    formatted_appointments = []
    for apt in appointments:
        patient = db.query(User).filter(User.id == apt.user_id).first()
        doctor = db.query(Doctor).filter(Doctor.id == apt.doctor_id).first()

        formatted_appointments.append({
            "id": apt.id,
            "patient_name": patient.name if patient else "Unknown",
            "phone": patient.phone_number if patient else "N/A",
            "doctor_name": doctor.name if doctor else "Unknown",
            "specialty": doctor.specialty if doctor else "N/A",
            "date": apt.appointment_date.strftime("%Y-%m-%d %H:%M") if apt.appointment_date else "N/A",
            "fee": doctor.consultation_fee if doctor else 0,
            "status": apt.status
        })

    # Calculate stats
    total = len(appointments)
    confirmed = len([a for a in appointments if a.status == "confirmed"])
    pending = len([a for a in appointments if a.status == "pending"])

    # Today's appointments
    today = datetime.now().date()
    today_count = len([a for a in appointments if a.appointment_date and a.appointment_date.date() == today])

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "appointments": formatted_appointments,
        "total_appointments": total,
        "confirmed_count": confirmed,
        "pending_count": pending,
        "today_count": today_count
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
