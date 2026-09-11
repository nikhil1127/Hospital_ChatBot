"""
Doctor, Admin, and Patient Dashboard API Routes
FastAPI routes for web dashboards
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.db.session import get_db
from app.core.enhanced_db_service import HospitalDBService
from app.db.models import Doctor, Patient, Appointment, MedicalEncounter, User


router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# ==================== DOCTOR DASHBOARD ====================

@router.get("/doctor")
async def doctor_dashboard_redirect():
    """Redirect to doctor dashboard"""
    return {"message": "Doctor Dashboard", "url": "/doctor/1"}


@router.get("/doctor/{doctor_id}")
async def get_doctor_dashboard(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Get complete doctor dashboard data"""
    db_service = HospitalDBService(db)

    # Get doctor info
    doctor = db_service.get_doctor_by_id(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Get dashboard stats
    dashboard_data = db_service.get_doctor_dashboard(doctor_id)

    return {
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "specialty": doctor.specialty,
            "qualification": doctor.qualification,
            "experience_years": doctor.experience_years
        },
        **dashboard_data
    }


@router.get("/doctor/{doctor_id}/schedule")
async def get_doctor_schedule(
    doctor_id: int,
    schedule_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get doctor schedule for a date"""
    db_service = HospitalDBService(db)

    if schedule_date:
        date_obj = datetime.strptime(schedule_date, "%Y-%m-%d").date()
    else:
        date_obj = date.today()

    schedule = db_service.get_doctor_schedule(doctor_id, date_obj)
    return schedule


@router.post("/doctor/patient/{patient_id}/summary")
async def get_patient_summary_for_doctor(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get patient summary for doctor consultation"""
    db_service = HospitalDBService(db)
    summary = db_service.get_patient_summary(patient_id)
    return summary


# ==================== CONSULTATION API ====================

@router.get("/consultation/{appointment_id}")
async def get_consultation_view(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Get consultation view data"""
    db_service = HospitalDBService(db)

    # Get appointment
    appointment = db_service.get_appointment_by_id(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Get patient summary
    patient_id = appointment.patient.patient_id
    patient_summary = db_service.get_patient_summary(patient_id)

    # Get patient timeline
    timeline = db_service.get_patient_timeline(patient_id)

    return {
        "appointment": {
            "id": appointment.appointment_number,
            "token": appointment.token_number,
            "patient": appointment.patient.first_name + " " + appointment.patient.last_name,
            "patient_id": appointment.patient.patient_id,
            "chief_complaint": appointment.chief_complaint,
            "status": appointment.status,
            "time": appointment.start_time.strftime("%H:%M")
        },
        "patient_summary": patient_summary,
        "timeline": timeline
    }


@router.post("/consultation/{appointment_id}/start")
async def start_consultation(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Start patient consultation"""
    db_service = HospitalDBService(db)

    # Check in patient (creates encounter)
    appointment = db_service.check_in_patient(
        db.query(Appointment).filter(Appointment.id == appointment_id).first().appointment_number
    )

    # Get the encounter
    encounter = db.query(MedicalEncounter).filter(
        MedicalEncounter.appointment_id == appointment_id
    ).first()

    if encounter:
        encounter = db_service.start_consultation(encounter.id)
        return {
            "success": True,
            "encounter_id": encounter.id,
            "encounter_number": encounter.encounter_number,
            "status": encounter.status
        }

    return {"success": False, "error": "Could not create encounter"}


@router.post("/consultation/{encounter_id}/save")
async def save_consultation_data(
    encounter_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Save consultation progress"""
    db_service = HospitalDBService(db)

    encounter = db_service.save_consultation(encounter_id, data)

    return {
        "success": True,
        "encounter_id": encounter.id,
        "status": encounter.status
    }


@router.post("/consultation/{encounter_id}/complete")
async def complete_consultation(
    encounter_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Complete consultation with prescription and lab orders"""
    db_service = HospitalDBService(db)

    encounter = db_service.complete_consultation(
        encounter_id=encounter_id,
        prescription_data=data.get("prescriptions", []),
        lab_orders=data.get("lab_orders", [])
    )

    return {
        "success": True,
        "encounter_number": encounter.encounter_number,
        "status": encounter.status
    }


# ==================== ADMIN DASHBOARD ====================

@router.get("/admin/stats")
async def get_admin_dashboard_stats(
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    db_service = HospitalDBService(db)
    stats = db_service.get_dashboard_stats()
    return stats


@router.get("/admin/today")
async def get_today_overview(
    db: Session = Depends(get_db)
):
    """Get today's hospital overview"""
    db_service = HospitalDBService(db)

    # Get all appointments for today
    appointments = db_service.get_today_appointments()

    # Get pending lab orders
    pending_labs = db_service.get_pending_lab_orders()

    return {
        "appointments": appointments,
        "pending_labs": pending_labs,
        "stats": db_service.get_dashboard_stats()
    }


# ==================== PATIENT PORTAL ====================

@router.get("/patient/{patient_id}")
async def get_patient_portal(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get patient portal data"""
    db_service = HospitalDBService(db)

    patient = db_service.get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get upcoming appointments
    upcoming = db.query(Appointment).filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date >= date.today(),
        Appointment.status.in_(["CONFIRMED", "SCHEDULED"])
    ).order_by(Appointment.appointment_date).all()

    # Get timeline
    timeline = db_service.get_patient_timeline(patient_id)

    # Get pending lab results
    pending_labs = db.query(LabOrder).filter(
        LabOrder.patient_id == patient.id,
        LabOrder.status == "COMPLETED"
    ).order_by(LabOrder.ordered_at.desc()).limit(5).all()

    return {
        "patient": {
            "patient_id": patient.patient_id,
            "name": f"{patient.first_name} {patient.last_name}",
            "age": db_service._calculate_age(patient.date_of_birth),
            "blood_group": patient.blood_group,
            "phone": patient.primary_phone
        },
        "upcoming_appointments": [
            {
                "appointment_number": a.appointment_number,
                "doctor": a.doctor.name if a.doctor else "",
                "specialty": a.doctor.specialty if a.doctor else "",
                "date": a.appointment_date.strftime("%Y-%m-%d"),
                "time": a.start_time.strftime("%H:%M"),
                "token": a.token_number,
                "status": a.status
            } for a in upcoming
        ],
        "recent_lab_results": [
            {
                "order_number": l.order_number,
                "ordered_at": l.ordered_at.strftime("%Y-%m-%d"),
                "tests": [t.test_name for t in l.tests]
            } for l in pending_labs
        ],
        "timeline": timeline[:10]  # Last 10 events
    }


# ==================== PATIENT REGISTRATION API ====================

@router.post("/patient/register")
async def register_patient(
    patient_data: dict,
    db: Session = Depends(get_db)
):
    """Register new patient"""
    db_service = HospitalDBService(db)

    try:
        patient = db_service.create_patient(patient_data)
        return {
            "success": True,
            "patient_id": patient.patient_id,
            "name": f"{patient.first_name} {patient.last_name}"
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "potential_duplicates": []
        }


@router.get("/search/patients")
async def search_patients(
    q: str,
    db: Session = Depends(get_db)
):
    """Search patients by name, phone, or patient ID"""
    db_service = HospitalDBService(db)

    # Search by patient ID
    patient = db_service.get_patient_by_id(q)
    if patient:
        return [{
            "patient_id": patient.patient_id,
            "name": f"{patient.first_name} {patient.last_name}",
            "phone": patient.primary_phone,
            "age": db_service._calculate_age(patient.date_of_birth),
            "gender": patient.gender
        }]

    # Search by phone
    patient = db_service.get_patient_by_phone(q)
    if patient:
        return [{
            "patient_id": patient.patient_id,
            "name": f"{patient.first_name} {patient.last_name}",
            "phone": patient.primary_phone,
            "age": db_service._calculate_age(patient.date_of_birth),
            "gender": patient.gender
        }]

    # Search by name (fuzzy)
    patients = db.query(Patient).filter(
        Patient.first_name.ilike(f"%{q}%") |
        Patient.last_name.ilike(f"%{q}%")
    ).limit(10).all()

    return [{
        "patient_id": p.patient_id,
        "name": f"{p.first_name} {p.last_name}",
        "phone": p.primary_phone,
        "age": db_service._calculate_age(p.date_of_birth),
        "gender": p.gender
    } for p in patients]


# ==================== LAB DASHBOARD ====================

@router.get("/lab/pending")
async def get_pending_labs(
    db: Session = Depends(get_db)
):
    """Get all pending lab orders"""
    db_service = HospitalDBService(db)
    pending = db_service.get_pending_lab_orders()
    return pending


@router.post("/lab/{order_id}/results")
async def submit_lab_results(
    order_id: int,
    results: dict,
    db: Session = Depends(get_db)
):
    """Submit lab results - simplified for demo"""
    db_service = HospitalDBService(db)

    # Demo: Assume verified by doctor ID 1
    order = db_service.enter_lab_results(order_id, results.get("tests", []), 1)

    return {
        "success": True,
        "order_number": order.order_number,
        "status": order.status
    }
